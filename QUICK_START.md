# Quick Start Guide

## Prerequisites Check
```bash
# Verify Docker is running
docker ps

# Check available resources (recommended: 8GB+ RAM)
free -h
```

## Step-by-Step Startup

### 1. Start All Services
```bash
docker-compose up -d
```

### 2. Wait for Services to be Healthy
```bash
# Check service status
docker-compose ps

# Wait for Cassandra (most critical, takes ~30-60 seconds)
docker logs -f cassandra
# Look for: "Startup complete" message, then Ctrl+C
```

### 3. Initialize Infrastructure

```bash
# Create Kafka topics
bash init/kafka-create-topics.sh

# Create HDFS directories
bash init/hdfs-bootstrap.sh

# Initialize Cassandra schema
docker exec -i cassandra cqlsh < init/cassandra-init.cql
```

### 4. Verify Producer is Running
```bash
# Check producer logs (should see messages being sent)
docker logs producer

# Verify Kafka has messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ticks \
  --from-beginning \
  --max-messages 5
```

### 5. Start Spark Streaming Job
```bash
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  streaming_ingest.py"
```

**Note**: This will run in the foreground. For background execution, add `&` or use `screen`/`tmux`.

### 6. Verify Data Flow

```bash
# Check Spark UI: http://localhost:8080
# Look for "streaming_ingest" application

# Check Cassandra for features
docker exec -it cassandra cqlsh -e "SELECT COUNT(*) FROM market.features;"

# Check HDFS for raw data
docker exec -it namenode hdfs dfs -ls -R /data/raw/ticks
```

### 7. Run Batch Training (After ~5 minutes of streaming)

```bash
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  batch_train_predict.py"
```

### 8. View Predictions in Streamlit

Open browser: http://localhost:8501

Enter a symbol (e.g., AAPL) and view predictions.

## Common Issues

### "No predictions found"
- Make sure batch training job completed successfully
- Check predictions table: `docker exec -it cassandra cqlsh -e "SELECT * FROM market.predictions LIMIT 10;"`

### Spark job fails to connect
- Verify Spark Master is running: `docker logs spark-master`
- Check workers are connected: http://localhost:8080

### Cassandra connection errors
- Wait longer for Cassandra to start (can take 1-2 minutes)
- Check logs: `docker logs cassandra`
- Verify health: `docker exec -it cassandra cqlsh -e "DESCRIBE KEYSPACES;"`

### No data in Kafka
- Check producer logs: `docker logs producer`
- Verify Kafka is running: `docker logs kafka`
- Check topic exists: `docker exec -it kafka kafka-topics.sh --list --bootstrap-server localhost:9092`

## Monitoring

- **Spark Master UI**: http://localhost:8080
- **Spark Worker 1 UI**: http://localhost:8081
- **Spark Worker 2 UI**: http://localhost:8082
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default: admin/admin)
- **Streamlit**: http://localhost:8501

## Stopping the Pipeline

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```


