#!/usr/bin/env bash
# Script to start Spark Streaming job
set -e

echo "🚀 Starting Spark Streaming Job..."
echo "Waiting for Spark Master to be ready..."

# Wait for Spark Master
until curl -s http://spark-master:8080 > /dev/null 2>&1; do
    echo "Waiting for Spark Master..."
    sleep 5
done

echo "✅ Spark Master is ready"

cd /opt/spark/app

/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host="${CASSANDRA_HOST:-cassandra}" \
  --conf spark.cassandra.connection.port="${CASSANDRA_PORT:-9042}" \
  --conf spark.hadoop.fs.defaultFS="${HDFS_URI:-hdfs://namenode:8020}" \
  --conf spark.sql.streaming.checkpointLocation="${HDFS_URI:-hdfs://namenode:8020}${CHECKPOINT_DIR:-/data/checkpoints/ingest}" \
  --conf spark.driver.extraJavaOptions="${SPARK_DRIVER_EXTRA_JAVA_OPTIONS:-}" \
  streaming_ingest.py


