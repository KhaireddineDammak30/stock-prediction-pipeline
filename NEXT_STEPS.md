# 🚀 Next Steps - Action Plan

## Immediate Actions (Do First - Today)

### 1. ✅ Verify All Fixes Are Applied
```bash
# Check that all files are updated
git status  # or just verify files exist

# Key files to verify:
# - services/producer/producer.py (timestamp fix)
# - services/spark/jobs/streaming_ingest.py (timestamp parsing)
# - init/cassandra-init.cql (schema fix)
# - docker-compose.yml (path fixes)
# - services/streamlit/app.py (error handling)
```

### 2. 🧪 Test the Pipeline End-to-End

#### Step 1: Start Infrastructure
```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (especially Cassandra - takes 30-60s)
watch -n 2 'docker-compose ps'

# When Cassandra shows "healthy", proceed
```

#### Step 2: Initialize Services
```bash
# Create Kafka topics
bash init/kafka-create-topics.sh

# Create HDFS directories
bash init/hdfs-bootstrap.sh

# Initialize Cassandra schema
docker exec -i cassandra cqlsh < init/cassandra-init.cql
```

#### Step 3: Verify Producer is Working
```bash
# Check producer logs
docker logs producer -f

# You should see messages like:
# [Producer] ✅ Sent tick: {'symbol': 'AAPL', 'ts': '...', ...}

# Verify Kafka has messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ticks \
  --from-beginning \
  --max-messages 5
```

#### Step 4: Start Spark Streaming Job
```bash
# Start streaming job (runs in foreground - use screen/tmux if needed)
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  streaming_ingest.py"
```

**Expected Output:**
- `[BOOT] WIN5_DURATION=...` messages
- No errors about timestamp parsing
- Messages about batches being processed

#### Step 5: Verify Data Flow
```bash
# Check Spark UI: http://localhost:8080
# Look for "streaming_ingest" application

# Check Cassandra for features (wait 1-2 minutes first)
docker exec -it cassandra cqlsh -e "SELECT COUNT(*) FROM market.features;"

# Check HDFS for raw data
docker exec -it namenode hdfs dfs -ls -R /data/raw/ticks
```

#### Step 6: Run Batch Training (After 5+ minutes of streaming)
```bash
# In a new terminal, run batch training
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  batch_train_predict.py"
```

#### Step 7: View Results in Streamlit
```bash
# Open browser: http://localhost:8501
# Enter symbol: AAPL
# Should see predictions if batch job completed successfully
```

### 3. 🔍 Verify Monitoring Setup

```bash
# Check Prometheus
curl http://localhost:9090/-/healthy
# Should return: Prometheus is Healthy.

# Check targets
open http://localhost:9090/targets
# All Spark targets should be "UP" (when jobs are running)

# Check Grafana
open http://localhost:3000
# Login: admin/admin
# Prometheus datasource should be auto-configured
```

### 4. 🐛 Troubleshoot Any Issues

If something doesn't work:

1. **Check logs:**
   ```bash
   docker logs producer
   docker logs spark-submit
   docker logs cassandra
   docker logs kafka
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

3. **Check network connectivity:**
   ```bash
   docker network inspect stock-prediction-pipeline_bigdata_net
   ```

4. **See troubleshooting section in README.md**

## Short-Term Improvements (This Week)

### Priority 1: Complete Monitoring Setup

1. **Add Kafka Metrics**
   ```bash
   # Add to docker-compose.yml (see MONITORING_ANALYSIS.md)
   # Add kafka-exporter service
   # Update prometheus.yml
   ```

2. **Create Custom Dashboards**
   - Spark Streaming Dashboard
   - Pipeline Health Dashboard
   - Business Metrics Dashboard

3. **Set Up Basic Alerting**
   - Alert when Spark job fails
   - Alert when Kafka lag is high
   - Alert when Cassandra is down

### Priority 2: Improve Error Handling

1. **Add Retry Logic**
   - Kafka producer retries
   - Cassandra write retries
   - HDFS write retries

2. **Add Data Validation**
   - Validate schema in producer
   - Validate data before processing
   - Handle malformed messages

3. **Improve Logging**
   - Structured logging
   - Log levels
   - Error tracking

### Priority 3: Add Application Metrics

Create custom metrics for:
- Records processed per second
- Processing latency
- Prediction accuracy
- Error rates

See `MONITORING_ANALYSIS.md` for implementation details.

## Medium-Term Improvements (This Month)

### 1. Automate Job Submission
- Use Airflow/Prefect for orchestration
- Or create init containers that auto-start jobs
- Schedule batch training jobs

### 2. Add More Tests
- Integration tests for each component
- End-to-end pipeline tests
- Performance tests

### 3. Improve Model Management
- Model versioning
- Model artifact storage
- A/B testing framework

### 4. Add Data Quality Checks
- Schema validation
- Data freshness checks
- Anomaly detection

## Long-Term Improvements (Next Quarter)

### 1. Production Readiness
- Security hardening
- Authentication/authorization
- Encryption in transit
- Backup and recovery

### 2. Scalability
- Horizontal scaling
- Load balancing
- Auto-scaling

### 3. Advanced Features
- Real-time model updates
- Feature store
- Distributed tracing
- Log aggregation

## 📋 Development Workflow

### Daily Workflow

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Make code changes:**
   - Edit files in `services/`
   - Rebuild containers if needed: `docker-compose build <service>`
   - Restart service: `docker-compose restart <service>`

3. **Test changes:**
   - Run tests: `pytest tests/`
   - Check logs: `docker logs <service>`
   - Verify in UI: Streamlit, Spark UI, Grafana

4. **Stop services:**
   ```bash
   docker-compose down
   # Or to remove volumes: docker-compose down -v
   ```

### Testing Workflow

1. **Unit Tests:**
   ```bash
   cd tests
   pytest test_pipeline.py -v
   ```

2. **Integration Tests:**
   ```bash
   # Start services
   docker-compose up -d
   
   # Run tests
   pytest tests/test_pipeline.py::test_sma5_exact_average -v
   ```

3. **Manual Testing:**
   - Follow QUICK_START.md
   - Verify each component works
   - Check data flow end-to-end

## 🎯 Success Criteria

Your project is working correctly when:

- [ ] Producer sends data to Kafka successfully
- [ ] Spark streaming job processes data without errors
- [ ] Data appears in Cassandra (features table)
- [ ] Data appears in HDFS (raw data)
- [ ] Batch training job completes successfully
- [ ] Predictions appear in Streamlit dashboard
- [ ] Prometheus collects metrics from Spark
- [ ] Grafana displays dashboards
- [ ] All tests pass

## 📚 Documentation to Review

1. **README.md** - Project overview and quick start
2. **QUICK_START.md** - Step-by-step startup guide
3. **IMPROVEMENTS.md** - All fixes applied
4. **MONITORING_ANALYSIS.md** - Monitoring setup analysis
5. **monitoring/README.md** - Monitoring setup guide

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker logs <service-name>`
2. Review troubleshooting section in README.md
3. Check service health: `docker-compose ps`
4. Verify network: `docker network ls`
5. Check resource usage: `docker stats`

## 🎓 Learning Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboard Examples](https://grafana.com/grafana/dashboards/)

## ✅ Checklist Before Moving Forward

- [ ] All services start successfully
- [ ] Producer sends data to Kafka
- [ ] Spark streaming job runs without errors
- [ ] Data appears in Cassandra
- [ ] Batch training completes
- [ ] Streamlit shows predictions
- [ ] Prometheus collects metrics
- [ ] Grafana is accessible
- [ ] All tests pass

Once all checkboxes are checked, you're ready to continue development! 🎉

