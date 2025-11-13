#!/bin/bash
set -e

APP_DIR="/opt/spark-jobs"
SPARK_BIN="/opt/spark/bin/spark-submit"

echo "🚀 Spark Submit Script"
echo "Mode: $1"
echo "Using Spark at: $SPARK_BIN"
echo "--------------------------------------------------------"

if [ "$1" == "streaming" ]; then
    echo "Starting Spark Structured Streaming job..."
    $SPARK_BIN \
        --master "$SPARK_MASTER" \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
        --conf spark.cassandra.connection.host="$CASSANDRA_HOST" \
        --conf spark.hadoop.fs.defaultFS="$HDFS_URI" \
        "$APP_DIR/streaming_ingest.py"

elif [ "$1" == "train" ]; then
    echo "Running Spark ML training job..."
    $SPARK_BIN \
        --master "$SPARK_MASTER" \
        --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
        --conf spark.cassandra.connection.host="$CASSANDRA_HOST" \
        --conf spark.hadoop.fs.defaultFS="$HDFS_URI" \
        "$APP_DIR/batch_train_predict.py"

else
    echo "❌ Usage: $0 [streaming|train]"
    exit 1
fi
