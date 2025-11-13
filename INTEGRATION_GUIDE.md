# 🔌 Integration Guide

## Overview

This guide explains how to integrate the Stock Prediction Pipeline into your existing infrastructure or use it as a standalone system.

## 🚀 Quick Integration

### Option 1: Standalone Deployment (Recommended for Testing)

```bash
# Clone or copy the project
cd /path/to/your/projects

# Start everything with one command
./scripts/manage.sh start

# Access the dashboard
open http://localhost:8501
```

### Option 2: Integration with Existing Infrastructure

The pipeline is designed to be modular. You can integrate individual components:

#### Use Only the Producer
```python
from services.producer.producer import generate_tick, connect_kafka

# Connect to your Kafka cluster
producer = connect_kafka()
tick = generate_tick("AAPL")
producer.send("your-topic", tick)
```

#### Use Only the Spark Jobs
```bash
# Submit streaming job to your Spark cluster
spark-submit \
  --master spark://your-spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  services/spark/jobs/streaming_ingest.py
```

#### Use Only the Dashboard
```bash
# Point to your Cassandra cluster
export CASSANDRA_HOST=your-cassandra-host
streamlit run services/streamlit/app.py
```

## 📋 Integration Scenarios

### Scenario 1: Add to Existing Kafka Cluster

**Steps:**

1. **Update Kafka Configuration**
   ```yaml
   # In docker-compose.yml, update producer service:
   producer:
     environment:
       KAFKA_BROKER: your-kafka-broker:9092  # Your existing Kafka
   ```

2. **Use Existing Topics**
   ```bash
   # Remove Kafka service from docker-compose.yml
   # Update TOPIC_IN in spark-submit service to your topic
   ```

3. **Start Only Required Services**
   ```bash
   docker-compose up -d cassandra spark-master spark-worker-1 spark-worker-2
   ```

### Scenario 2: Use Existing Cassandra Cluster

**Steps:**

1. **Update Connection Settings**
   ```yaml
   # In docker-compose.yml
   spark-submit:
     environment:
       CASSANDRA_HOST: your-cassandra-host
       CASSANDRA_PORT: 9042
   ```

2. **Create Schema in Your Cluster**
   ```bash
   cqlsh your-cassandra-host < init/cassandra-init.cql
   ```

3. **Remove Cassandra Service**
   ```yaml
   # Comment out cassandra service in docker-compose.yml
   ```

### Scenario 3: Deploy to Kubernetes

**Steps:**

1. **Create Kubernetes Manifests**
   ```bash
   # Convert docker-compose.yml to Kubernetes
   kompose convert -f docker-compose.yml
   ```

2. **Update Service Discovery**
   - Replace service names with Kubernetes service names
   - Update network configurations

3. **Deploy**
   ```bash
   kubectl apply -f k8s/
   ```

### Scenario 4: Cloud Deployment (AWS/GCP/Azure)

**Recommended Architecture:**

```
Cloud Storage (S3/GCS/Azure Blob)
    ↓
Kafka (Managed Service: MSK/Confluent Cloud)
    ↓
Spark (EMR/Dataproc/HDInsight)
    ↓
Cassandra (Managed: Keyspaces/Cosmos DB)
    ↓
Dashboard (ECS/Cloud Run/App Service)
```

**Steps:**

1. **Update Environment Variables**
   ```bash
   export KAFKA_BROKER=your-managed-kafka-endpoint
   export CASSANDRA_HOST=your-managed-cassandra-endpoint
   export HDFS_URI=s3://your-bucket/  # Or gs://, azure://
   ```

2. **Update Spark Configuration**
   ```python
   # In streaming_ingest.py
   spark = SparkSession.builder \
       .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
       .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY")) \
       .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_KEY")) \
       .getOrCreate()
   ```

3. **Deploy Dashboard**
   ```bash
   # Example: Deploy Streamlit to Cloud Run
   gcloud run deploy stock-dashboard \
     --source services/streamlit \
     --set-env-vars CASSANDRA_HOST=your-cassandra-host
   ```

## 🔧 Configuration Management

### Environment Variables

Create a `.env` file:

```bash
# Kafka
KAFKA_BROKER=kafka:9092
TOPIC=ticks

# Cassandra
CASSANDRA_HOST=cassandra
CASSANDRA_KEYSPACE=market

# Spark
SPARK_MASTER=spark://spark-master:7077
HDFS_URI=hdfs://namenode:8020

# Producer
SYMBOLS=AAPL,MSFT,GOOGL
INTERVAL_SEC=5
```

### Configuration Files

- `docker-compose.yml` - Service orchestration
- `monitoring/prometheus.yml` - Metrics collection
- `init/cassandra-init.cql` - Database schema
- `services/*/requirements.txt` - Python dependencies

## 🔌 API Integration

### REST API Wrapper (Optional)

Create a REST API to interact with the pipeline:

```python
# api/server.py
from flask import Flask, jsonify
from cassandra.cluster import Cluster

app = Flask(__name__)

@app.route('/api/predictions/<symbol>')
def get_predictions(symbol):
    # Query Cassandra
    session = get_cassandra_session()
    rows = session.execute(f"SELECT * FROM predictions WHERE symbol='{symbol}'")
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Webhook Integration

Send predictions to external systems:

```python
# In batch_train_predict.py, after saving predictions
import requests

def send_webhook(predictions):
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json=predictions)
```

## 📊 Monitoring Integration

### Integrate with Existing Monitoring

**Prometheus Federation:**
```yaml
# In your main Prometheus
scrape_configs:
  - job_name: 'federate-stock-pipeline'
    scrape_interval: 15s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="spark-*"}'
        - '{job="kafka-*"}'
    static_configs:
      - targets:
        - 'stock-pipeline-prometheus:9090'
```

**Grafana Data Source:**
- Add Prometheus as data source pointing to pipeline Prometheus
- Import dashboards from `monitoring/grafana/dashboards/`

## 🔐 Security Integration

### Authentication

1. **Kafka SASL/SSL**
   ```python
   producer = KafkaProducer(
       bootstrap_servers=KAFKA_BROKER,
       security_protocol='SASL_SSL',
       sasl_mechanism='PLAIN',
       sasl_plain_username='user',
       sasl_plain_password='pass'
   )
   ```

2. **Cassandra Authentication**
   ```python
   cluster = Cluster(
       [HOST],
       auth_provider=PlainTextAuthProvider(
           username='user',
           password='pass'
       )
   )
   ```

3. **Dashboard Authentication**
   - Use Streamlit's built-in authentication
   - Or deploy behind a reverse proxy (nginx) with auth

## 🚦 Health Checks

### Service Health Endpoints

```python
# health.py
from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/health')
def health():
    checks = {
        'kafka': check_kafka(),
        'cassandra': check_cassandra(),
        'spark': check_spark()
    }
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    return jsonify({'status': status, 'checks': checks})
```

## 📦 Container Registry Integration

### Build and Push Images

```bash
# Build images
docker-compose build

# Tag for your registry
docker tag stock-prediction-pipeline_producer:latest \
  your-registry/stock-pipeline-producer:latest

# Push
docker push your-registry/stock-pipeline-producer:latest
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker-compose build
          docker-compose push
          # Deploy to your infrastructure
```

## 🎯 Best Practices

1. **Use Environment Variables** - Never hardcode credentials
2. **Separate Configs** - Different configs for dev/staging/prod
3. **Health Checks** - Implement health endpoints for all services
4. **Logging** - Centralize logs (ELK, CloudWatch, etc.)
5. **Monitoring** - Set up alerts for critical metrics
6. **Backup** - Regular backups of Cassandra data
7. **Testing** - Run tests before deploying
8. **Documentation** - Keep integration docs updated

## 🆘 Troubleshooting Integration

### Common Issues

1. **Network Connectivity**
   ```bash
   # Test connections
   docker exec producer ping kafka
   docker exec spark-submit ping cassandra
   ```

2. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :9092
   ```

3. **Configuration Mismatch**
   ```bash
   # Verify environment variables
   docker exec producer env | grep KAFKA
   ```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Kafka Integration Guide](https://kafka.apache.org/documentation/)
- [Cassandra Best Practices](https://cassandra.apache.org/doc/latest/cassandra/getting_started/index.html)
- [Spark Deployment Guide](https://spark.apache.org/docs/latest/cluster-overview.html)

## 💬 Support

For integration questions:
1. Check this guide
2. Review README.md
3. Check troubleshooting sections
4. Review code comments

