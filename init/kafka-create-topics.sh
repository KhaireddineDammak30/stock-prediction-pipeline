#!/usr/bin/env bash
set -euo pipefail
BROKER="${1:-kafka:9092}"
TOPICS="${KAFKA_TOPICS:-ticks,predictions}"

for t in $(echo "$TOPICS" | tr ',' '\n'); do
  echo "Creating topic $t"
  docker exec -i $(docker ps -qf name=kafka) kafka-topics.sh \
    --bootstrap-server "$BROKER" \
    --create --if-not-exists \
    --replication-factor 1 --partitions 3 \
    --topic "$t" || true
done
