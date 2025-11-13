"""
Spark Streaming Ingestion Job
Consumes stock tick data from Kafka, computes technical indicators,
and writes to HDFS (raw data) and Cassandra (features)
"""

import os
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType
)
from py4j.protocol import Py4JJavaError

# ==========================================================
#  ENVIRONMENT CONFIGURATION
# ==========================================================
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC_IN        = os.getenv("TOPIC_IN", "ticks")
HDFS_URI        = os.getenv("HDFS_URI", "hdfs://namenode:8020")
RAW_DIR         = os.getenv("RAW_DIR", "/data/raw/ticks")
CHECKPOINT      = os.getenv("CHECKPOINT_DIR", "/data/checkpoints/ingest")
KEYSPACE        = os.getenv("KEYSPACE", "market")
TABLE_FEATURES  = os.getenv("TABLE_FEATURES", "features")

# Intermediate folders for SMA5 / SMA20 snapshots
SMA5_DIR  = f"{HDFS_URI}/data/intermediate/sma5"
SMA20_DIR = f"{HDFS_URI}/data/intermediate/sma20"

# Window/Watermark configuration (env-driven)
WIN5_DURATION   = os.getenv("WIN5_DURATION", "6 seconds")
WIN5_SLIDE      = os.getenv("WIN5_SLIDE",    "3 seconds")
WIN20_DURATION  = os.getenv("WIN20_DURATION","9 seconds")
WIN20_SLIDE     = os.getenv("WIN20_SLIDE",   "3 seconds")
WATERMARK       = os.getenv("WATERMARK",     "5 seconds")

# Limit static-join to recent data to avoid huge batches (in minutes)
TIME_FILTER_MINUTES = int(os.getenv("TIME_FILTER_MINUTES", "10"))

# Triggers (stream & driver/foreachBatch)
STREAM_TRIGGER  = os.getenv("STREAM_TRIGGER", "5 seconds")
DRIVER_TRIGGER  = os.getenv("DRIVER_TRIGGER", "20 seconds")

# Console debug toggle
DEBUG_CONSOLE   = os.getenv("DEBUG_CONSOLE", "1") in ("1", "true", "True")

# State dir for idempotent sink (last processed bucket_start)
STATE_DIR       = f"{HDFS_URI}{CHECKPOINT}/features_state"
LAST_BSTART_FN  = "last_bstart.txt"

# ==========================================================
#  SPARK SESSION INITIALIZATION
# ==========================================================
spark = (
    SparkSession.builder
    .appName("streaming_ingest")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
    .config("spark.cassandra.connection.host", os.getenv("CASSANDRA_HOST", "cassandra"))
    .config("spark.cassandra.connection.port", os.getenv("CASSANDRA_PORT", "9042"))
    .config("spark.cassandra.output.consistency.level", os.getenv("CASSANDRA_CL", "LOCAL_ONE"))
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

print("[BOOT] "
      f"WIN5_DURATION={WIN5_DURATION}, WIN5_SLIDE={WIN5_SLIDE}, "
      f"WIN20_DURATION={WIN20_DURATION}, WIN20_SLIDE={WIN20_SLIDE}, "
      f"WATERMARK={WATERMARK}, TIME_FILTER_MINUTES={TIME_FILTER_MINUTES}, "
      f"STREAM_TRIGGER={STREAM_TRIGGER}, DRIVER_TRIGGER={DRIVER_TRIGGER}, "
      f"DEBUG_CONSOLE={DEBUG_CONSOLE}", flush=True)

# ==========================================================
#  DEFINE INPUT SCHEMA (KAFKA JSON)
# ==========================================================
schema = StructType([
    StructField("symbol", StringType()),
    StructField("ts", StringType()),      # ISO8601 string with 'Z'
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", IntegerType()),
])

# ==========================================================
#  READ STREAM FROM KAFKA
# ==========================================================
raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", TOPIC_IN)
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")  # Don't fail if Kafka data was aged out
    .load()
)

json_df = (
    raw.select(F.col("value").cast("string").alias("json"))
       .select(F.from_json("json", schema).alias("r"))
       .select("r.*")
)

# ==========================================================
#  PARSE TIMESTAMP + ADD DATE COLUMN
# ==========================================================
# Handle multiple timestamp formats for robustness
parsed_df = (
    json_df
    .withColumn("ts_clean", F.regexp_replace("ts", "Z$", ""))  # strip trailing Z if present
    .withColumn("ts", 
        F.coalesce(
            F.to_timestamp("ts_clean", "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"),  # with microseconds
            F.to_timestamp("ts_clean", "yyyy-MM-dd'T'HH:mm:ss.SSS"),     # with milliseconds
            F.to_timestamp("ts_clean", "yyyy-MM-dd'T'HH:mm:ss"),         # without fractional seconds
            F.to_timestamp("ts_clean", "yyyy-MM-dd HH:mm:ss")            # space instead of T
        )
    )
    .drop("ts_clean")
)

with_date = parsed_df.withColumn("date", F.to_date("ts"))

# ==========================================================
#  WRITE RAW DATA TO HDFS
# ==========================================================
raw_query = (
    with_date.writeStream
    .format("parquet")
    .option("path", f"{HDFS_URI}{RAW_DIR}")
    .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/raw")
    .partitionBy("symbol", "date")
    .outputMode("append")
    .trigger(processingTime=STREAM_TRIGGER)
    .start()
)

# ==========================================================
#  COMPUTE SMA-5 AND SMA-20 WINDOWS (from env)
# ==========================================================
stream = with_date.withWatermark("ts", WATERMARK)

sma5 = (
    stream.groupBy(
        F.col("symbol"),
        F.window("ts", WIN5_DURATION, WIN5_SLIDE).alias("w5")
    )
    .agg(F.avg("close").alias("sma_5"))
    .select(
        F.col("symbol"),
        F.col("w5.start").alias("start5"),
        F.col("w5.end").alias("end5"),
        F.col("sma_5")
    )
)

sma20 = (
    stream.groupBy(
        F.col("symbol"),
        F.window("ts", WIN20_DURATION, WIN20_SLIDE).alias("w20")
    )
    .agg(F.avg("close").alias("sma_20"))
    .select(
        F.col("symbol"),
        F.col("w20.start").alias("start20"),
        F.col("w20.end").alias("end20"),
        F.col("sma_20")
    )
)

# ==========================================================
#  DEBUG CONSOLE OUTPUT (optional via env)
# ==========================================================
if DEBUG_CONSOLE:
    sma5_debug_query = (
        sma5.writeStream
        .outputMode("update")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 5)
        .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/sma5_debug")
        .trigger(processingTime=STREAM_TRIGGER)
        .start()
    )
    sma20_debug_query = (
        sma20.writeStream
        .outputMode("update")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 5)
        .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/sma20_debug")
        .trigger(processingTime=STREAM_TRIGGER)
        .start()
    )

# ==========================================================
#  MATERIALIZE SMA5 / SMA20 TO HDFS AS PARQUET
# ==========================================================
sma5_to_hdfs_query = (
    sma5.writeStream
    .format("parquet")
    .option("path", SMA5_DIR)
    .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/sma5_parquet")
    .outputMode("append")
    .trigger(processingTime=STREAM_TRIGGER)
    .start()
)

sma20_to_hdfs_query = (
    sma20.writeStream
    .format("parquet")
    .option("path", SMA20_DIR)
    .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/sma20_parquet")
    .outputMode("append")
    .trigger(processingTime=STREAM_TRIGGER)
    .start()
)

# ==========================================================
#  HELPER: ROBUST SAVE WITH RETRY
# ==========================================================
def save_with_retry(df, keyspace, table, max_retries=5, base_sleep=2.0):
    attempt = 1
    while True:
        try:
            (df.write
               .format("org.apache.spark.sql.cassandra")
               .mode("append")
               .option("keyspace", keyspace)
               .option("table", table)
               .save())
            return True
        except (Py4JJavaError, Exception) as e:
            if attempt >= max_retries:
                print(f"[❌] Cassandra write failed after {attempt} attempts: {e}")
                raise
            sleep = base_sleep * (2 ** (attempt - 1))
            print(f"[⚠️] Write failed (attempt {attempt}), retrying in {sleep:.1f}s ...")
            time.sleep(sleep)
            attempt += 1

# ==========================================================
#  HDFS STATE HELPERS (for idempotent sink)
# ==========================================================
def _get_fs_and_path():
    from py4j.java_gateway import java_import
    java_import(spark._jvm, "org.apache.hadoop.fs.FileSystem")
    java_import(spark._jvm, "org.apache.hadoop.fs.Path")
    java_import(spark._jvm, "java.net.URI")
    hadoop_conf = spark._jsc.hadoopConfiguration()
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark._jvm.java.net.URI(HDFS_URI), hadoop_conf
    )
    Path = spark._jvm.org.apache.hadoop.fs.Path
    return fs, Path

def read_last_bstart():
    fs, Path = _get_fs_and_path()
    state_dir = Path(STATE_DIR)
    if not fs.exists(state_dir):
        fs.mkdirs(state_dir)
    marker = Path(f"{STATE_DIR}/{LAST_BSTART_FN}")
    if not fs.exists(marker):
        return None
    in_stream = fs.open(marker)
    try:
        content = spark._jvm.org.apache.commons.io.IOUtils.toString(in_stream, "UTF-8").strip()
        return content if content else None
    finally:
        in_stream.close()

def write_last_bstart(ts_str):
    fs, Path = _get_fs_and_path()
    marker = Path(f"{STATE_DIR}/{LAST_BSTART_FN}")
    out = fs.create(marker, True)
    try:
        out.write(bytearray(ts_str.encode("utf-8")))
        out.hflush()
    finally:
        out.close()

# ==========================================================
#  STATIC JOIN + WRITE TO CASSANDRA (recent window only) + IDEMPOTENT
# ==========================================================
def join_and_write_to_cassandra(_, batchId):
    print(f"\n[🔄] Batch {batchId}: starting static join & Cassandra write")

    # Ensure SMA parquet exists
    fs, Path = _get_fs_and_path()
    def has_parquet_files(path):
        p = Path(path)
        if not fs.exists(p):
            return False
        files = fs.listStatus(p)
        for f in files:
            name = f.getPath().getName()
            if name.endswith(".parquet"):
                return True
        return False

    if not has_parquet_files(SMA5_DIR) or not has_parquet_files(SMA20_DIR):
        print("[⚠️] Waiting for SMA5/SMA20 parquet files — skipping this batch.")
        return

    # Load recent SMA parquet
    df5_all = spark.read.parquet(SMA5_DIR)
    df20_all = spark.read.parquet(SMA20_DIR)

    cutoff = F.expr(f"timestampadd(minute, -{TIME_FILTER_MINUTES}, current_timestamp())")
    df5 = df5_all.where(F.col("start5")  >= cutoff)
    df20 = df20_all.where(F.col("start20") >= cutoff)

    c5 = df5.count()
    c20 = df20.count()
    print(f"[ℹ️] SMA5 rows (recent {TIME_FILTER_MINUTES}m): {c5}, SMA20 rows: {c20}")
    if c5 == 0 or c20 == 0:
        print("[⚠️] No recent rows yet, retrying next batch.")
        return

    joined = (
        df5.alias("a")
        .join(
            df20.alias("b"),
            (F.col("a.symbol") == F.col("b.symbol")) &
            (F.abs(F.unix_timestamp("a.start5") - F.unix_timestamp("b.start20")) <= 15),
            "inner"
        )
        .select(
            F.col("a.symbol").alias("symbol"),
            F.col("a.start5").alias("bucket_start"),
            F.col("a.end5").alias("bucket_end"),
            F.col("a.sma_5"),
            F.col("b.sma_20")
        )
        .dropDuplicates(["symbol", "bucket_start"])
    )

    # ---------- IDEMPOTENCY FILTER (only new buckets) ----------
    last_bstart_str = read_last_bstart()
    if last_bstart_str:
        print(f"[STATE] last_bstart marker = {last_bstart_str}")
        joined = joined.where(F.col("bucket_start") > F.to_timestamp(F.lit(last_bstart_str)))
    else:
        print("[STATE] No last_bstart marker found (first run or cleared state).")

    n = joined.count()
    print(f"[✅] Joined NEW rows (after marker filter): {n}")
    if n == 0:
        return

    if DEBUG_CONSOLE:
        joined.orderBy("symbol", "bucket_start").show(10, truncate=False)

    # -------- DIFFERENT PROJECTION PER TARGET TABLE --------
    if TABLE_FEATURES == "features_by_bucket":
        out = (
            joined.select(
                "symbol",
                "bucket_start",
                "bucket_end",
                F.col("sma_5").cast("double").alias("sma_5"),
                F.col("sma_20").cast("double").alias("sma_20"),
            )
            .dropDuplicates(["symbol", "bucket_start"])
            .repartition("symbol")
        )
    else:
        out = (
            joined
            .withColumn("ts", F.col("bucket_start"))
            .select(
                "symbol",
                "ts",
                "bucket_start",
                "bucket_end",
                F.col("sma_5").cast("double").alias("sma_5"),
                F.col("sma_20").cast("double").alias("sma_20"),
            )
            .dropDuplicates(["symbol", "ts"])
            .repartition("symbol")
        )

    save_with_retry(out, KEYSPACE, TABLE_FEATURES)
    wrote = out.count()
    print(f"[💾] Wrote {wrote} rows to Cassandra.")

    # ---------- UPDATE MARKER ----------
    max_bstart = out.agg(F.max("bucket_start").alias("mx")).collect()[0]["mx"]
    if max_bstart is not None:
        ts_str = max_bstart.strftime("%Y-%m-%d %H:%M:%S")
        write_last_bstart(ts_str)
        print(f"[STATE] Updated last_bstart marker -> {ts_str}")

# ==========================================================
#  DRIVER STREAM TO TRIGGER FOREACHBATCH
# ==========================================================
cassandra_sink_driver = (
    with_date.writeStream
    .outputMode("append")
    .trigger(processingTime=DRIVER_TRIGGER)
    .foreachBatch(join_and_write_to_cassandra)
    .option("checkpointLocation", f"{HDFS_URI}{CHECKPOINT}/features_static_join")
    .start()
)

# ==========================================================
#  KEEP STREAM ACTIVE
# ==========================================================
spark.streams.awaitAnyTermination()