# 🚀 START HERE - Complete Guide to Run Your Pipeline

## 📋 What You Need

- ✅ Docker installed on your laptop
- ✅ Docker Compose installed
- ✅ Terminal/Command Prompt
- ✅ Web browser
- ✅ At least 8GB RAM available

## 🎯 Quick Start (5 Minutes)

### Step 1: Open Terminal

**On Mac/Linux:**
- Open Terminal app

**On Windows:**
- Open PowerShell or Command Prompt
- Or use WSL (Windows Subsystem for Linux)

### Step 2: Go to Your Project

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
```

### Step 3: Start Everything (ONE COMMAND!)

```bash
./scripts/manage.sh start
```

**What this does:**
- ✅ Starts all services (Kafka, Spark, Cassandra, etc.)
- ✅ Waits for services to be ready
- ✅ Initializes databases and topics
- ✅ Shows you status and URLs

**Wait for:** You'll see "✅ Pipeline startup complete! 🎉"

### Step 4: Open Your Dashboard

Open your web browser and go to:
```
http://localhost:8501
```

**You should see:** The Stock Prediction Dashboard! 📊

---

## 📊 Viewing Your Pipeline

### Main Dashboard (What You'll See)

1. **Stock Symbol Selector** - Choose a stock (AAPL, MSFT, etc.)
2. **Key Metrics** - Total predictions, latest price, average
3. **Price Chart** - Beautiful graph showing predictions over time
4. **Statistics** - Mean, median, standard deviation
5. **Recent Predictions Table** - Latest data

### Other Views You Can Access

| Service | URL | What You'll See |
|---------|-----|-----------------|
| **Main Dashboard** | http://localhost:8501 | Stock predictions and charts |
| **Spark UI** | http://localhost:8080 | Spark cluster status and jobs |
| **Prometheus** | http://localhost:9090 | Metrics and monitoring |
| **Grafana** | http://localhost:3000 | Advanced dashboards (admin/admin) |

---

## 🔑 Key Points of Your Work

### What Your Pipeline Does

```
1. Producer → Generates stock data
   ↓
2. Kafka → Stores messages
   ↓
3. Spark Streaming → Processes data in real-time
   ↓
4. Cassandra → Stores features and predictions
   ↓
5. Dashboard → Shows you everything!
```

### Key Features

✅ **Real-time Processing** - Data flows continuously  
✅ **Machine Learning** - Predicts stock prices  
✅ **Professional Dashboard** - Beautiful visualizations  
✅ **Monitoring** - Track everything with Prometheus/Grafana  
✅ **Scalable** - Can handle lots of data  

---

## 🛠️ Complete Step-by-Step Guide

### Part 1: Starting the Pipeline

#### 1.1 Check Docker is Running

```bash
docker ps
```

**Expected:** Should show running containers or empty list (both OK)

#### 1.2 Navigate to Project

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
```

#### 1.3 Make Scripts Executable (First Time Only)

```bash
chmod +x scripts/*.sh
chmod +x QUICK_TEST.sh
```

#### 1.4 Start Everything

```bash
./scripts/manage.sh start
```

**Watch for:**
- Services starting...
- Waiting for Cassandra... (takes 30-60 seconds)
- ✅ Services ready
- ✅ Infrastructure initialized
- ✅ Pipeline startup complete!

**Time:** About 2-3 minutes total

#### 1.5 Verify Everything Started

```bash
./scripts/manage.sh status
```

**Expected:** All services show "Up" status

---

### Part 2: Starting Data Processing

#### 2.1 Start Spark Streaming Job

**Open a NEW terminal window** (keep the first one open)

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
./scripts/manage.sh start-streaming
```

**What you'll see:**
- Spark job starting
- Processing messages from Kafka
- Writing to Cassandra
- Batch processing logs

**Keep this running!** (Press Ctrl+C to stop later)

#### 2.2 Wait for Data Collection

**Wait 5-10 minutes** for data to accumulate

**Check progress:**
- Open http://localhost:8080 (Spark UI)
- Look for "streaming_ingest" application
- Check "Streaming" tab for processed records

---

### Part 3: Generating Predictions

#### 3.1 Start Batch Training Job

**Open ANOTHER terminal window**

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
./scripts/manage.sh start-batch
```

**What this does:**
- Trains ML model on collected data
- Generates predictions
- Saves to Cassandra

**Wait for:** "RMSE: X.XXXX" and "Wrote predictions to Cassandra"

---

### Part 4: Viewing Results

#### 4.1 Open Dashboard

Open browser: **http://localhost:8501**

#### 4.2 Select a Symbol

- Use dropdown or type: **AAPL**
- Click or press Enter

#### 4.3 View Predictions

You'll see:
- 📊 Price chart
- 📈 Statistics
- 📋 Recent predictions table

---

## 🎯 Key Points to Explore

### 1. Dashboard Features

**Try these:**
- Select different symbols (AAPL, MSFT, GOOGL)
- Click "🔄 Refresh Data" button
- Check sidebar for pipeline status
- View statistics panel

### 2. Spark UI

**Go to:** http://localhost:8080

**See:**
- Active applications
- Worker status
- Resource usage
- Job history

### 3. Monitoring

**Prometheus:** http://localhost:9090
- Query metrics
- Check targets
- View graphs

**Grafana:** http://localhost:3000
- Login: admin/admin
- View dashboards
- Create custom visualizations

---

## 📊 Understanding What's Happening

### Data Flow

```
Producer (generates data)
    ↓
Kafka (stores messages)
    ↓
Spark Streaming (processes in real-time)
    ↓
HDFS (stores raw data)
    ↓
Cassandra (stores features)
    ↓
Spark Batch (trains model)
    ↓
Cassandra (stores predictions)
    ↓
Dashboard (shows you everything!)
```

### What Each Service Does

| Service | Purpose |
|---------|---------|
| **Producer** | Creates synthetic stock data |
| **Kafka** | Message queue for data |
| **Spark Master** | Coordinates Spark jobs |
| **Spark Workers** | Process data |
| **Cassandra** | Database for features & predictions |
| **HDFS** | File storage for raw data |
| **Streamlit** | Web dashboard |
| **Prometheus** | Metrics collection |
| **Grafana** | Metrics visualization |

---

## 🧪 Testing Your Setup

### Quick Health Check

```bash
./QUICK_TEST.sh
```

**Checks:**
- ✅ All services running
- ✅ Endpoints accessible
- ✅ Infrastructure ready

### Manual Checks

#### Check Producer is Sending Data

```bash
docker logs producer | tail -20
```

**Expected:** See messages like "✅ Sent tick: ..."

#### Check Kafka Has Messages

```bash
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ticks \
  --max-messages 5
```

**Expected:** See JSON messages with stock data

#### Check Cassandra Has Data

```bash
docker exec -it cassandra cqlsh -e "SELECT COUNT(*) FROM market.predictions;"
```

**Expected:** Number of predictions (0 if batch job hasn't run)

---

## 🛑 Stopping Everything

### Stop Services

```bash
./scripts/manage.sh stop
```

### Stop and Remove Everything (Deletes Data!)

```bash
./scripts/manage.sh clean
```

**Warning:** This deletes all data!

---

## 🐛 Troubleshooting

### Problem: Services Won't Start

**Solution:**
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart
./scripts/manage.sh restart
```

### Problem: Dashboard Shows "No Data"

**Solution:**
1. Make sure streaming job is running
2. Wait 5-10 minutes for data collection
3. Run batch training job
4. Refresh dashboard

### Problem: Can't Connect to Services

**Solution:**
```bash
# Check services are running
docker-compose ps

# Check ports aren't in use
netstat -tulpn | grep 8501
netstat -tulpn | grep 8080

# Restart services
./scripts/manage.sh restart
```

### Problem: Out of Memory

**Solution:**
- Close other applications
- Reduce Docker memory limit
- Or increase system RAM

---

## 📝 Daily Workflow

### Starting Your Day

```bash
# 1. Start pipeline
./scripts/manage.sh start

# 2. Check status
./scripts/manage.sh status

# 3. Start streaming (in separate terminal)
./scripts/manage.sh start-streaming

# 4. Open dashboard
open http://localhost:8501
```

### During Work

- Monitor dashboard: http://localhost:8501
- Check Spark UI: http://localhost:8080
- View logs: `./scripts/manage.sh logs <service>`

### Ending Your Day

```bash
# Stop everything
./scripts/manage.sh stop
```

---

## 🎓 Learning Your Project

### Key Files to Understand

1. **`scripts/manage.sh`** - How to control everything
2. **`services/streamlit/app.py`** - Dashboard code
3. **`services/producer/producer.py`** - Data generation
4. **`services/spark/jobs/streaming_ingest.py`** - Real-time processing
5. **`services/spark/jobs/batch_train_predict.py`** - ML training

### Key Concepts

- **Streaming** - Real-time data processing
- **Batch** - Periodic model training
- **Features** - Technical indicators (SMA-5, SMA-20)
- **Predictions** - ML model outputs

---

## ✅ Success Checklist

After following this guide, you should have:

- [ ] All services running
- [ ] Dashboard accessible at http://localhost:8501
- [ ] Spark streaming job running
- [ ] Data flowing through pipeline
- [ ] Predictions visible in dashboard
- [ ] Monitoring accessible (Prometheus, Grafana)

---

## 🎉 Congratulations!

You now know how to:
- ✅ Start your pipeline
- ✅ View the dashboard
- ✅ Understand what's happening
- ✅ Troubleshoot issues

**Your pipeline is running!** 🚀

---

## 📚 Next Steps

1. **Explore Dashboard** - Try different symbols, check features
2. **Check Monitoring** - See metrics in Prometheus/Grafana
3. **Read Documentation** - Learn more in other guides
4. **Customize** - Modify configurations, add features

**Happy exploring!** 📈

