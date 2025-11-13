# 🚀 Getting Started - Complete Guide

## Welcome!

This guide will help you get your Stock Prediction Pipeline up and running in minutes.

## 📋 Prerequisites

- Docker & Docker Compose installed
- At least 8GB RAM available
- 10GB free disk space
- Terminal/Command line access

## ⚡ Quick Start (3 Steps)

### Step 1: Start the Pipeline
```bash
./scripts/manage.sh start
```

This single command will:
- ✅ Start all services
- ✅ Wait for services to be healthy
- ✅ Initialize infrastructure
- ✅ Show you status and URLs

### Step 2: Start Spark Streaming
```bash
./scripts/manage.sh start-streaming
```

### Step 3: Open Dashboard
Open your browser: **http://localhost:8501**

That's it! 🎉

## 📖 Detailed Steps

### Option A: Automated (Recommended)

```bash
# 1. Start everything
./scripts/manage.sh start

# 2. Check status
./scripts/manage.sh status

# 3. Start streaming job
./scripts/manage.sh start-streaming

# 4. View dashboard
open http://localhost:8501
```

### Option B: Manual

```bash
# 1. Start services
docker-compose up -d

# 2. Initialize infrastructure
bash init/kafka-create-topics.sh
bash init/hdfs-bootstrap.sh
docker exec -i cassandra cqlsh < init/cassandra-init.cql

# 3. Start streaming (see QUICK_START.md for full command)
```

## 🎯 What You Get

### Services Running
- **Producer** - Generates stock data
- **Kafka** - Message queue
- **Spark** - Data processing
- **Cassandra** - Database
- **HDFS** - Data storage
- **Streamlit** - Dashboard
- **Prometheus** - Metrics
- **Grafana** - Visualization

### Access Points
- 📊 **Dashboard**: http://localhost:8501
- 🔥 **Spark UI**: http://localhost:8080
- 📈 **Prometheus**: http://localhost:9090
- 📉 **Grafana**: http://localhost:3000

## 🛠️ Management Commands

```bash
# Start everything
./scripts/manage.sh start

# Check status
./scripts/manage.sh status

# View logs
./scripts/manage.sh logs producer
./scripts/manage.sh logs spark-submit

# Start jobs
./scripts/manage.sh start-streaming
./scripts/manage.sh start-batch

# Stop everything
./scripts/manage.sh stop

# Get help
./scripts/manage.sh help
```

## 🧪 Verify It's Working

### Quick Test
```bash
./QUICK_TEST.sh
```

### Manual Checks

1. **Check Services**
   ```bash
   docker-compose ps
   ```
   All services should show "Up"

2. **Check Producer**
   ```bash
   docker logs producer | tail -20
   ```
   Should see messages being sent

3. **Check Kafka**
   ```bash
   docker exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic ticks \
     --max-messages 5
   ```
   Should see JSON messages

4. **Check Dashboard**
   - Open http://localhost:8501
   - Enter symbol: AAPL
   - Should see predictions (after batch job runs)

## 📊 Understanding the Dashboard

### Main View
- **Symbol Selector** - Choose stock symbol
- **Key Metrics** - Total predictions, latest price, average
- **Price Chart** - Visual prediction timeline
- **Statistics** - Mean, median, std dev
- **Recent Predictions** - Latest data table

### Sidebar
- **Configuration** - Symbol selection
- **Refresh** - Update data
- **Pipeline Status** - Service health
- **Quick Links** - Other UIs

## 🔄 Typical Workflow

1. **Start Pipeline**
   ```bash
   ./scripts/manage.sh start
   ```

2. **Start Streaming** (collects data)
   ```bash
   ./scripts/manage.sh start-streaming
   ```

3. **Wait 5-10 minutes** (for data collection)

4. **Run Batch Training** (generates predictions)
   ```bash
   ./scripts/manage.sh start-batch
   ```

5. **View Results**
   - Open dashboard: http://localhost:8501
   - Select symbol
   - See predictions!

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check Docker
docker ps

# Check logs
docker-compose logs

# Restart
./scripts/manage.sh restart
```

### No Data in Dashboard
1. Check streaming job is running
2. Wait for data collection (5+ minutes)
3. Run batch training job
4. Refresh dashboard

### Connection Errors
```bash
# Test connectivity
docker exec producer ping kafka
docker exec spark-submit ping cassandra

# Check network
docker network inspect stock-prediction-pipeline_bigdata_net
```

## 📚 Next Steps

1. **Read Documentation**
   - README.md - Overview
   - QUICK_START.md - Detailed steps
   - INTEGRATION_GUIDE.md - Integration

2. **Explore Features**
   - Try different symbols
   - Check Spark UI
   - Explore Grafana

3. **Customize**
   - Adjust producer settings
   - Modify model parameters
   - Create custom dashboards

## 💡 Tips

1. **Use Management Script** - It handles everything
2. **Check Logs** - When something doesn't work
3. **Monitor Resources** - Watch memory/CPU usage
4. **Backup Data** - Before making changes
5. **Read Docs** - Most questions are answered there

## 🎓 Learning Path

### Day 1: Basics
- Start the pipeline
- Understand the flow
- Explore the dashboard

### Day 2: Operations
- Learn management commands
- Check monitoring
- Understand logs

### Day 3: Customization
- Modify configurations
- Add features
- Create dashboards

### Day 4: Integration
- Read integration guide
- Plan your deployment
- Test integrations

## 🆘 Need Help?

1. Check this guide
2. Read README.md
3. Review troubleshooting sections
4. Check service logs
5. Review documentation

## ✅ Success Checklist

- [ ] Pipeline starts successfully
- [ ] All services are running
- [ ] Dashboard is accessible
- [ ] Data is flowing
- [ ] Predictions are visible

**Once all checked, you're ready to go!** 🎉

## 🎉 Congratulations!

You now have a fully functional stock prediction pipeline running!

**What's Next?**
- Explore the dashboard
- Check out monitoring
- Read integration guide
- Customize for your needs

Happy predicting! 📈

