"""
Spark Batch Training and Prediction Job
Trains a Random Forest model on historical stock data and generates predictions
"""

import os
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

HDFS_URI = os.getenv("HDFS_URI", "hdfs://namenode:8020")
RAW_DIR = os.getenv("RAW_DIR", "/data/raw/ticks")
KEYSPACE = os.getenv("KEYSPACE", "market")
TABLE_PRED = os.getenv("TABLE_PRED", "predictions")

spark = (SparkSession.builder
    .appName("batch_train_predict")
    .config("spark.sql.shuffle.partitions", "8")
    .getOrCreate())

spark.sparkContext.setLogLevel("WARN")

base = spark.read.parquet(f"{HDFS_URI}{RAW_DIR}")

w = Window.partitionBy("symbol").orderBy("ts")
feat = (base
    .withColumn("close_lag1", F.lag("close", 1).over(w))
    .withColumn("close_lag2", F.lag("close", 2).over(w))
    .withColumn("ret1", (F.col("close") - F.col("close_lag1")) / F.col("close_lag1"))
    .withColumn("ret2", (F.col("close_lag1") - F.col("close_lag2")) / F.col("close_lag2"))
    .dropna())

assembler = VectorAssembler(
    inputCols=["open","high","low","volume","close_lag1","close_lag2","ret1","ret2"],
    outputCol="features")
vec = assembler.transform(feat)

train, test = vec.randomSplit([0.8, 0.2], seed=42)
rf = RandomForestRegressor(featuresCol="features", labelCol="close", numTrees=64, maxDepth=8)
model = rf.fit(train)

pred = model.transform(test)

for metric in ["rmse", "mae", "r2"]:
    ev = RegressionEvaluator(labelCol="close", predictionCol="prediction", metricName=metric)
    val = ev.evaluate(pred)
    print(f"{metric.upper()}: {val:.4f}")

out = (pred.select(
            "symbol",
            F.col("ts").alias("ts"),
            F.col("prediction").alias("y_pred"))
        .withColumn("model", F.lit("RandomForestRegressor"))
        .withColumn("horizon", F.lit("t+0")))

(out.write
    .format("org.apache.spark.sql.cassandra")
    .option("keyspace", KEYSPACE)
    .option("table", TABLE_PRED)
    .mode("append")
    .save())
