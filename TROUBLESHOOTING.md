# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Kafka Offset Out of Range Error

**Error Message:**
```
Cannot fetch offset 37070... Some data may have been lost because they are not 
available in Kafka any more; either the data was aged out by Kafka or the topic 
may have been deleted before all the data in the topic was processed.
```

**Cause:**
- Spark checkpoint references an old Kafka offset
- Kafka deleted that data (retention policy: 12 hours)
- Job tries to resume from non-existent offset

**Solution 1: Reset Checkpoints (Recommended)**
```bash
./scripts/reset-streaming.sh
```

Then restart streaming:
```bash
./scripts/manage.sh start-streaming
```

**Solution 2: The fix is already applied**
The streaming job now has `failOnDataLoss: false` which will skip missing data.
Just restart the job:
```bash
./scripts/manage.sh start-streaming
```

---

### Issue 2: Docker Compose Command Not Found

**Error:**
```
docker-compose: command not found
```

**Solution:**
The scripts now automatically detect and use `docker compose` (newer) or `docker-compose` (older).
If you still see this error, update your scripts or use:
```bash
docker compose up -d
```

---

### Issue 3: Services Won't Start

**Symptoms:**
- Services show as "Exited" or "Restarting"
- Port conflicts

**Solutions:**

1. **Check logs:**
   ```bash
   docker-compose logs <service-name>
   # or
   ./scripts/manage.sh logs <service-name>
   ```

2. **Check port conflicts:**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep 8501  # Streamlit
   netstat -tulpn | grep 8080  # Spark
   netstat -tulpn | grep 9090  # Prometheus
   ```

3. **Restart services:**
   ```bash
   ./scripts/manage.sh restart
   ```

4. **Clean start (removes all data):**
   ```bash
   ./scripts/manage.sh clean
   ./scripts/manage.sh start
   ```

---

### Issue 4: Cassandra Connection Errors

**Error:**
```
Failed to connect to Cassandra
```

**Solutions:**

1. **Wait longer** - Cassandra takes 30-60 seconds to start
   ```bash
   docker logs cassandra
   # Wait for "Startup complete"
   ```

2. **Check health:**
   ```bash
   docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES;"
   ```

3. **Restart Cassandra:**
   ```bash
   docker restart cassandra
   ```

---

### Issue 5: No Data in Dashboard

**Symptoms:**
- Dashboard loads but shows "No predictions found"
- Empty charts

**Solutions:**

1. **Check streaming job is running:**
   ```bash
   docker logs spark-submit | tail -50
   ```

2. **Verify producer is sending data:**
   ```bash
   docker logs producer | tail -20
   ```

3. **Check Kafka has messages:**
   ```bash
   docker exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic ticks \
     --max-messages 5
   ```

4. **Wait for data collection:**
   - Streaming needs 5-10 minutes to collect data
   - Then run batch training job

5. **Run batch training:**
   ```bash
   ./scripts/manage.sh start-batch
   ```

---

### Issue 6: Spark Job Fails to Start

**Error:**
```
Failed to connect to Spark master
```

**Solutions:**

1. **Check Spark Master is running:**
   ```bash
   docker logs spark-master
   curl http://localhost:8080
   ```

2. **Check workers are connected:**
   - Open http://localhost:8080
   - Look for workers in UI

3. **Restart Spark:**
   ```bash
   docker restart spark-master spark-worker-1 spark-worker-2
   ```

---

### Issue 7: Out of Memory

**Symptoms:**
- Containers keep restarting
- "OOMKilled" in logs

**Solutions:**

1. **Reduce Docker memory:**
   - Docker Desktop → Settings → Resources
   - Increase memory allocation (8GB+ recommended)

2. **Close other applications**

3. **Reduce Spark worker memory** (in docker-compose.yml):
   ```yaml
   SPARK_WORKER_MEMORY=1G  # Instead of 2G
   ```

---

### Issue 8: HDFS Connection Errors

**Error:**
```
Failed to connect to HDFS
```

**Solutions:**

1. **Check HDFS is running:**
   ```bash
   docker logs namenode
   docker logs datanode
   ```

2. **Initialize HDFS directories:**
   ```bash
   bash init/hdfs-bootstrap.sh
   ```

3. **Check HDFS status:**
   ```bash
   docker exec namenode hdfs dfsadmin -report
   ```

---

### Issue 9: Timestamp Parsing Errors

**Error:**
```
Cannot parse timestamp
```

**Solution:**
This should be fixed. If you still see it:
1. Check producer timestamp format
2. Verify streaming job has latest code
3. Restart both producer and streaming job

---

### Issue 10: Checkpoint Errors

**Error:**
```
Checkpoint location already exists
```

**Solution:**
```bash
# Delete checkpoints
./scripts/reset-streaming.sh

# Or manually:
docker exec namenode hdfs dfs -rm -r -f /data/checkpoints/ingest/*
```

---

## Quick Diagnostic Commands

### Check All Services
```bash
./scripts/manage.sh status
```

### Health Check
```bash
./QUICK_TEST.sh
```

### View All Logs
```bash
./scripts/manage.sh logs all
```

### Check Specific Service
```bash
docker logs <service-name> -f
```

### Network Connectivity
```bash
docker network inspect stock-prediction-pipeline_bigdata_net
```

---

## Recovery Procedures

### Complete Reset (Nuclear Option)

**WARNING: This deletes ALL data!**

```bash
# Stop everything
./scripts/manage.sh stop

# Remove all data
./scripts/manage.sh clean

# Start fresh
./scripts/manage.sh start

# Initialize
bash init/kafka-create-topics.sh
bash init/hdfs-bootstrap.sh
docker exec -i cassandra cqlsh < init/cassandra-init.cql
```

### Reset Just Streaming

```bash
# Reset checkpoints
./scripts/reset-streaming.sh

# Restart streaming
./scripts/manage.sh start-streaming
```

### Reset Just Kafka

```bash
# Delete Kafka topic
docker exec kafka kafka-topics.sh --delete \
  --bootstrap-server localhost:9092 \
  --topic ticks

# Recreate
bash init/kafka-create-topics.sh
```

---

## Getting Help

1. **Check logs first:**
   ```bash
   ./scripts/manage.sh logs <service>
   ```

2. **Run health check:**
   ```bash
   ./QUICK_TEST.sh
   ```

3. **Check service status:**
   ```bash
   ./scripts/manage.sh status
   ```

4. **Review documentation:**
   - README.md
   - START_HERE.md
   - This file

---

## Prevention Tips

1. **Regular restarts** - Restart services weekly
2. **Monitor disk space** - HDFS and Kafka use disk
3. **Check logs regularly** - Catch issues early
4. **Backup checkpoints** - Before major changes
5. **Use management script** - Don't use docker-compose directly

---

## Still Having Issues?

1. Check all logs: `./scripts/manage.sh logs all`
2. Verify network: `docker network ls`
3. Check resources: `docker stats`
4. Review error messages carefully
5. Check service dependencies

Most issues are resolved by:
- Restarting services
- Resetting checkpoints
- Waiting for services to be ready
- Checking logs for specific errors

