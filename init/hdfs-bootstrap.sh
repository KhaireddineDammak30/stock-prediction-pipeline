#!/usr/bin/env bash
set -euo pipefail
RAW_DIR=${HDFS_RAW_DIR:-/data/raw/ticks}
CHK_DIR=${HDFS_CHECKPOINT_DIR:-/data/checkpoints/ingest}

docker exec -i $(docker ps -qf name=namenode) hdfs dfs -mkdir -p "$RAW_DIR"
docker exec -i $(docker ps -qf name=namenode) hdfs dfs -mkdir -p "$CHK_DIR"
docker exec -i $(docker ps -qf name=namenode) hdfs dfs -ls -R /data || true
