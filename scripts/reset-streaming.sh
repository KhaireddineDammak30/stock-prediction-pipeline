#!/usr/bin/env bash
# Reset Spark Streaming Checkpoints
# Use this when you get Kafka offset errors

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HDFS_URI="${HDFS_URI:-hdfs://namenode:8020}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-/data/checkpoints/ingest}"

echo "⚠️  WARNING: This will delete all Spark streaming checkpoints!"
echo "This will reset your streaming job to start from the latest Kafka offset."
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo "Deleting checkpoint directories from HDFS..."

# Delete checkpoints
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/raw" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/sma5_parquet" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/sma20_parquet" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/sma5_debug" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/sma20_debug" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/features_static_join" 2>/dev/null || true
docker exec namenode hdfs dfs -rm -r -f "${HDFS_URI}${CHECKPOINT_DIR}/features_state" 2>/dev/null || true

echo "✅ Checkpoints deleted!"
echo ""
echo "You can now restart the streaming job:"
echo "  ./scripts/manage.sh start-streaming"

