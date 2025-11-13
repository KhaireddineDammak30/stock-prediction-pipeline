# Monitoring Setup Guide

## Overview

This directory contains all monitoring configuration files for the stock prediction pipeline.

## Structure

```
monitoring/
├── prometheus.yml              # Prometheus scrape configuration
├── spark-metrics.properties     # Spark metrics configuration (legacy, using JMX now)
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml  # Auto-configure Prometheus datasource
│   │   └── dashboards/
│   │       └── dashboards.yml  # Auto-load dashboards
│   └── dashboards/
│       └── spark-overview.json # Example Spark dashboard
└── README.md                   # This file
```

## Quick Start

### 1. Start Services

```bash
docker-compose up -d prometheus grafana
```

### 2. Access Grafana

1. Open http://localhost:3000
2. Login with:
   - Username: `admin`
   - Password: `admin` (change on first login)
3. Prometheus datasource should be auto-configured

### 3. Verify Prometheus

1. Open http://localhost:9090
2. Check targets: http://localhost:9090/targets
3. All Spark targets should be "UP"

### 4. Import Dashboards

The example dashboard (`spark-overview.json`) should auto-load. To create custom dashboards:

1. Go to Grafana → Dashboards → New Dashboard
2. Add panels with Prometheus queries
3. Save dashboard

## Available Metrics

### Spark Metrics

- `jvm_memory_bytes_used` - JVM memory usage (heap/non-heap)
- `jvm_os_ProcessCpuLoad` - CPU usage
- `jvm_os_SystemCpuLoad` - System CPU load
- `spark_streaming_*` - Spark streaming metrics
- `jvm_gc_*` - Garbage collection metrics

### Query Examples

```promql
# Memory usage
jvm_memory_bytes_used{area="HeapMemoryUsage"}

# CPU usage
jvm_os_ProcessCpuLoad

# Streaming throughput
spark_streaming_processedRowsPerSecond

# GC collections
rate(jvm_gc_CollectionCount[5m])
```

## Adding More Metrics

### Kafka Metrics

Add Kafka Exporter to `docker-compose.yml`:

```yaml
kafka-exporter:
  image: danielqsj/kafka-exporter:latest
  command: ['--kafka.server=kafka:9092']
  ports: ['9308:9308']
  networks: [bigdata_net]
```

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-exporter:9308']
```

### Cassandra Metrics

Use JMX exporter or Cassandra Exporter. See MONITORING_ANALYSIS.md for details.

## Troubleshooting

### Prometheus not scraping targets

1. Check network connectivity: `docker network inspect stock-prediction-pipeline_bigdata_net`
2. Verify ports are accessible: `docker exec prometheus wget -qO- http://spark-master:8090/metrics`
3. Check Prometheus logs: `docker logs prometheus`

### Grafana can't connect to Prometheus

1. Verify Prometheus is running: `docker ps | grep prometheus`
2. Check datasource URL: Should be `http://prometheus:9090` (not localhost)
3. Test connection in Grafana: Configuration → Data Sources → Prometheus → Test

### No metrics appearing

1. Verify Spark jobs are running (JMX only active when jobs run)
2. Check JMX agent is loaded: `docker logs spark-master | grep jmx`
3. Verify ports are correct in `prometheus.yml`

## Next Steps

See `MONITORING_ANALYSIS.md` for:
- Complete analysis of current setup
- Future improvements
- Best practices
- Implementation checklist

