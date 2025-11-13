# Stock Prediction Pipeline

A real-time stock prediction pipeline using Kafka, Spark, Cassandra, and HDFS with ML-based predictions.

## 🏗️ Architecture Overview

```
Producer (Python) → Kafka → Spark Streaming → HDFS (raw data)
                                          ↓
                                    Spark Streaming → Cassandra (features)
                                          ↓
                                    Spark Batch ML → Cassandra (predictions)
                                          ↓
                                    Streamlit Dashboard
```

## 📋 Components

1. **Producer**: Generates synthetic stock tick data and publishes to Kafka
2. **Spark Streaming**: 
   - Ingests data from Kafka
   - Computes technical indicators (SMA-5, SMA-20)
   - Writes raw data to HDFS (Parquet)
   - Writes features to Cassandra
3. **Spark Batch**: Trains Random Forest model and generates predictions
4. **Streamlit Dashboard**: Visualizes predictions in real-time
5. **Monitoring**: Prometheus + Grafana for metrics

## 🎯 Getting Started

**👉 START HERE:** [START_HERE.md](START_HERE.md) - **Complete step-by-step guide to run everything on your laptop!**

**Quick Commands:**
```bash
# 1. Start everything (ONE COMMAND!)
./scripts/manage.sh start

# 2. Open dashboard
open http://localhost:8501

# 3. Start streaming job (in new terminal)
./scripts/manage.sh start-streaming
```

**Other Guides:**
- [GETTING_STARTED.md](GETTING_STARTED.md) - Detailed getting started
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - See what you'll see
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Integrate with your systems

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- At least 8GB RAM available

### Start the Pipeline

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy (especially Cassandra)
docker-compose ps

# 3. Initialize Kafka topics
bash init/kafka-create-topics.sh

# 4. Initialize HDFS directories
bash init/hdfs-bootstrap.sh

# 5. Initialize Cassandra schema
docker exec -i cassandra cqlsh < init/cassandra-init.cql

# 6. Start Spark Streaming job
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  streaming_ingest.py"

# 7. (Optional) Run batch training job (wait for streaming to collect some data first)
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  batch_train_predict.py"
```

### Access Services

- **Streamlit Dashboard**: http://localhost:8501
- **Spark Master UI**: http://localhost:8080
- **Spark Worker 1 UI**: http://localhost:8081
- **Spark Worker 2 UI**: http://localhost:8082
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default: admin/admin)

## 📊 Project Analysis & Feedback

### ✅ Strengths

1. **Well-structured architecture**: Clear separation of concerns with microservices
2. **Modern stack**: Uses industry-standard tools (Kafka, Spark, Cassandra)
3. **Monitoring setup**: Prometheus + Grafana integration for observability
4. **Containerization**: Fully containerized with Docker Compose
5. **Testing infrastructure**: Includes pytest tests with fixtures
6. **Idempotency handling**: Smart state management in streaming job

### ⚠️ Issues Found & Fixed

#### 1. **Timestamp Format Mismatch** (CRITICAL - FIXED)
- **Problem**: Producer sends ISO8601 with 'Z' suffix, but streaming job expects different format
- **Impact**: Timestamp parsing failures, data loss
- **Fix**: Aligned timestamp formats between producer and streaming job

#### 2. **Cassandra Schema Mismatch** (CRITICAL - FIXED)
- **Problem**: Streaming job writes `bucket_start`, `bucket_end` but schema expects different columns
- **Impact**: Write failures to Cassandra
- **Fix**: Updated schema to match actual data structure

#### 3. **Missing Job Automation** (HIGH - FIXED)
- **Problem**: No automated way to start Spark jobs after services are up
- **Impact**: Manual intervention required
- **Fix**: Added startup scripts and improved documentation

#### 4. **Path Inconsistencies** (MEDIUM - FIXED)
- **Problem**: Volume mount paths don't match script expectations
- **Impact**: Jobs can't find Python files
- **Fix**: Standardized paths in docker-compose.yml

#### 5. **Missing Dependencies** (MEDIUM - FIXED)
- **Problem**: Some Python packages missing from requirements.txt
- **Impact**: Runtime errors
- **Fix**: Added all required dependencies

#### 6. **Error Handling** (LOW - IMPROVED)
- **Problem**: Limited error handling in some components
- **Impact**: Silent failures
- **Fix**: Added better error handling and logging

### 🔧 Improvements Made

1. ✅ Fixed timestamp format consistency
2. ✅ Updated Cassandra schema to match code
3. ✅ Added comprehensive README
4. ✅ Fixed volume mount paths
5. ✅ Added missing Python dependencies
6. ✅ Improved error handling in producer
7. ✅ Added .env.example for configuration
8. ✅ Fixed Streamlit app to handle missing data

### 📝 Recommendations for Further Improvement

#### High Priority
1. **Automate Spark Job Submission**: 
   - Use a job scheduler (e.g., Airflow, Prefect) or init container
   - Or add a startup script that waits for services and auto-starts jobs

2. **Add Health Checks**:
   - Implement health endpoints for all services
   - Add readiness probes in docker-compose

3. **Improve Data Validation**:
   - Add schema validation in producer
   - Validate data before writing to Kafka

4. **Add Retry Logic**:
   - Implement exponential backoff for Kafka/Cassandra connections
   - Add circuit breakers for external dependencies

#### Medium Priority
5. **Model Versioning**:
   - Store model artifacts in HDFS or S3
   - Track model versions and performance metrics

6. **Feature Store**:
   - Consider using a dedicated feature store (Feast, Tecton)
   - Better feature versioning and serving

7. **Streaming ML**:
   - Implement online learning for model updates
   - Real-time prediction serving

8. **Testing**:
   - Add integration tests
   - Add end-to-end pipeline tests
   - Mock external services in unit tests

#### Low Priority
9. **Documentation**:
   - Add API documentation
   - Add architecture diagrams
   - Document configuration options

10. **Security**:
    - Add authentication/authorization
    - Encrypt data in transit
    - Secure API endpoints

11. **Performance**:
    - Tune Spark configurations for your workload
    - Optimize Cassandra table design
    - Add caching layers

12. **Observability**:
    - Add distributed tracing (Jaeger, Zipkin)
    - Add structured logging
    - Create Grafana dashboards

## 🧪 Testing

```bash
# Install test dependencies
cd tests
pip install -r requirements.txt

# Create .env.test file (see .env.example)
# Run tests
pytest test_pipeline.py -v
```

## 📁 Project Structure

```
.
├── docker-compose.yml          # Service orchestration
├── init/                       # Initialization scripts
│   ├── cassandra-init.cql     # Cassandra schema
│   ├── kafka-create-topics.sh # Kafka topic creation
│   └── hdfs-bootstrap.sh      # HDFS directory setup
├── services/
│   ├── producer/              # Kafka producer service
│   ├── spark/                 # Spark jobs and Dockerfile
│   └── streamlit/             # Dashboard service
├── monitoring/                # Prometheus config
└── tests/                     # Integration tests
```

## 🔍 Troubleshooting

### Spark job fails to start
- Check Spark master is running: `docker logs spark-master`
- Verify workers are connected: http://localhost:8080
- Check job logs: `docker logs spark-submit`

### No data in Cassandra
- Verify streaming job is running
- Check Kafka topic has messages: `docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ticks`
- Check Spark streaming logs for errors

### Streamlit shows no data
- Verify predictions table exists: `docker exec -it cassandra cqlsh -e "SELECT * FROM market.predictions LIMIT 10;"`
- Run batch training job to generate predictions
- Check Streamlit logs: `docker logs streamlit`

## 📚 Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📄 License

MIT

