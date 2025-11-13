from pyspark.sql import functions as F
from pyspark.sql.window import Window

def add_technical_indicators(df, price_col="close", time_col="ts"):
    """
    Compute basic technical indicators (SMA, RSI) using time windows,
    which are compatible with Structured Streaming.
    """

    # Define time-based windows
    window_5min  = F.window(time_col, "5 minutes")
    window_20min = F.window(time_col, "20 minutes")

    # Compute moving averages (SMA)
    sma_5_df = (
        df.groupBy("symbol", window_5min)
          .agg(F.avg(price_col).alias("sma_5"))
          .withColumnRenamed("window", "window_5")
    )

    sma_20_df = (
        df.groupBy("symbol", window_20min)
          .agg(F.avg(price_col).alias("sma_20"))
          .withColumnRenamed("window", "window_20")
    )

    # RSI calculation (based on delta averages per 5-minute window)
    delta = F.col(price_col) - F.lag(price_col).over(Window.partitionBy("symbol").orderBy(time_col))
    gain = F.when(delta > 0, delta).otherwise(0.0)
    loss = F.when(delta < 0, -delta).otherwise(0.0)

    rsi_df = (
        df.withColumn("gain", gain)
          .withColumn("loss", loss)
          .groupBy("symbol", F.window(time_col, "5 minutes"))
          .agg(
              F.avg("gain").alias("avg_gain"),
              F.avg("loss").alias("avg_loss")
          )
          .withColumn("rs", F.col("avg_gain") / F.when(F.col("avg_loss") == 0, None).otherwise(F.col("avg_loss")))
          .withColumn("rsi_14", 100 - (100 / (1 + F.col("rs"))))
          .withColumnRenamed("window", "window_rsi")
    )

    # Join the three DataFrames safely (renamed window columns prevent ambiguity)
    result = (
        df
        .join(sma_5_df, "symbol", "left")
        .join(sma_20_df, "symbol", "left")
        .join(rsi_df, "symbol", "left")
        .dropDuplicates(["symbol", time_col])
    )

    return result