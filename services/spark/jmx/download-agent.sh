#!/usr/bin/env bash
set -euo pipefail

AGENT_VER=0.20.0
AGENT_URL="https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/${AGENT_VER}/jmx_prometheus_javaagent-${AGENT_VER}.jar"

echo ">>> Downloading JMX Prometheus Java Agent ${AGENT_VER}"
curl -fL -o /opt/jmx_prometheus_javaagent.jar "${AGENT_URL}"

echo ">>> Creating /opt/jmx and default jmx_spark.yaml if missing"
mkdir -p /opt/jmx

# If you want to maintain this file externally, just COPY it in Dockerfile (we’ll do that).
# This snippet keeps a minimal default fallback.
if [ ! -s /opt/jmx/jmx_spark.yaml ]; then
  cat >/opt/jmx/jmx_spark.yaml <<'YAML'
---
rules:
  - pattern: ".*"
YAML
fi

echo ">>> Done."