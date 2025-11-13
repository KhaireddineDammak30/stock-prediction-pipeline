# 👀 Visual Guide - See Your Pipeline in Action

## 🎬 Step-by-Step Visual Walkthrough

### Step 1: Start Everything

**In Terminal, type:**
```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
./scripts/manage.sh start
```

**You'll see:**
```
🚀 Stock Prediction Pipeline - Automated Startup
========================================

Checking Prerequisites
✅ Docker is available

Step 1: Starting Docker Services
ℹ️  Starting all services with docker-compose...
✅ Docker services started

Step 2: Waiting for Services to be Healthy
ℹ️  Waiting for Cassandra to be ready...
✅ Cassandra is ready!
✅ Kafka is ready!
✅ Spark Master is ready!

Step 3: Initializing Infrastructure
✅ Infrastructure initialized

✅ Pipeline startup complete! 🎉
```

**Time:** 2-3 minutes

---

### Step 2: Open Your Dashboard

**Open Browser:** http://localhost:8501

**You'll see:**

```
┌─────────────────────────────────────────────────────────┐
│  📈 Stock Prediction Dashboard                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⚙️ Configuration                                      │
│  ┌─────────────────────────────────────┐              │
│  │ Select Stock Symbol: [AAPL ▼]      │              │
│  │                                      │              │
│  │ [🔄 Refresh Data]                   │              │
│  └─────────────────────────────────────┘              │
│                                                         │
│  📊 Key Metrics                                        │
│  ┌──────┬──────┬──────┬──────┬──────┐                │
│  │Total │Latest│Avg   │Range │Model │                │
│  │1,234 │$150.2│$149.8│$10.5 │RF    │                │
│  └──────┴──────┴──────┴──────┴──────┘                │
│                                                         │
│  📈 Price Predictions                                  │
│  ┌─────────────────────────────────────┐              │
│  │     Price Chart (Interactive)      │              │
│  │     ┌─────────────────────────┐    │              │
│  │     │                         │    │              │
│  │     │    📈 Line Graph        │    │              │
│  │     │                         │    │              │
│  │     └─────────────────────────┘    │              │
│  └─────────────────────────────────────┘              │
│                                                         │
│  📋 Recent Predictions                                 │
│  ┌─────────────────────────────────────┐              │
│  │ Timestamp    │ Price │ Model │Horizon│             │
│  │ 2024-01-01   │$150.2 │ RF    │ t+0   │             │
│  │ ...          │ ...   │ ...   │ ...   │             │
│  └─────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

### Step 3: Start Data Processing

**Open NEW Terminal:**

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
./scripts/manage.sh start-streaming
```

**You'll see:**
```
🚀 Starting Spark Streaming Job...
Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
...
[BOOT] WIN5_DURATION=6 seconds, WIN5_SLIDE=3 seconds...
Streaming query made progress: batch 1
Streaming query made progress: batch 2
...
```

**Keep this running!**

---

### Step 4: View Spark UI

**Open Browser:** http://localhost:8080

**You'll see:**

```
┌─────────────────────────────────────────┐
│  Spark Master at spark://...            │
├─────────────────────────────────────────┤
│                                         │
│  Applications (1)                      │
│  ┌───────────────────────────────────┐ │
│  │ streaming_ingest                 │ │
│  │ Status: RUNNING                   │ │
│  │ Cores: 4                          │ │
│  │ Memory: 4.0 GB                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  Workers (2)                           │
│  ┌───────────────────────────────────┐ │
│  │ spark-worker-1: ALIVE             │ │
│  │ spark-worker-2: ALIVE             │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

### Step 5: Generate Predictions

**After 5-10 minutes, open ANOTHER Terminal:**

```bash
cd /home/khaireddine/projects/stock-prediction-pipeline
./scripts/manage.sh start-batch
```

**You'll see:**
```
🚀 Starting Spark Batch Training Job...
Training Random Forest model...
RMSE: 2.3456
MAE: 1.7890
R2: 0.9234
Wrote predictions to Cassandra.
✅ Batch job completed!
```

---

### Step 6: View Results in Dashboard

**Go back to:** http://localhost:8501

**Now you'll see:**
- ✅ Predictions chart with data
- ✅ Statistics populated
- ✅ Recent predictions table filled

**Try:**
- Select different symbols
- Click refresh
- Hover over chart for details

---

## 🎯 Key Points to See

### 1. Data Flow Visualization

```
┌─────────┐
│Producer │ → Generating stock ticks
└────┬────┘
     │
     ▼
┌─────────┐
│  Kafka  │ → Storing messages
└────┬────┘
     │
     ▼
┌─────────┐
│  Spark  │ → Processing in real-time
│Streaming│
└────┬────┘
     │
     ├──→ ┌─────────┐
     │    │  HDFS   │ → Raw data storage
     │    └─────────┘
     │
     └──→ ┌──────────┐
          │Cassandra │ → Features storage
          └────┬─────┘
               │
               ▼
          ┌──────────┐
          │  Batch   │ → Model training
          │ Training │
          └────┬─────┘
               │
               ▼
          ┌──────────┐
          │Predictions│ → Results
          └────┬─────┘
               │
               ▼
          ┌──────────┐
          │Dashboard │ → You see everything!
          └──────────┘
```

### 2. Dashboard Features

**Main View:**
- 📊 Symbol selector
- 📈 Price prediction chart
- 📉 Technical indicators
- 📋 Data table

**Sidebar:**
- ⚙️ Configuration
- 🔄 Refresh button
- 📊 Pipeline status
- 🔗 Quick links

### 3. Monitoring Views

**Prometheus (http://localhost:9090):**
- Metrics queries
- Target status
- Graphs

**Grafana (http://localhost:3000):**
- Pre-built dashboards
- Custom visualizations
- Alerts

---

## 🖥️ What You'll See in Each Service

### Producer Logs
```
[Producer] ✅ Connected to kafka:9092
[Producer] 🚀 Sending stock ticks to topic 'ticks' every 3s
[Producer] ✅ Sent tick: {'symbol': 'AAPL', 'ts': '...', 'close': 150.25}
```

### Spark Streaming Logs
```
[BOOT] WIN5_DURATION=6 seconds...
[🔄] Batch 1: starting static join & Cassandra write
[✅] Joined NEW rows: 10
[💾] Wrote 10 rows to Cassandra.
```

### Dashboard
- Interactive charts
- Real-time updates
- Professional UI
- Statistics

---

## 📱 Quick Access URLs

Copy these to your browser:

```
Dashboard:    http://localhost:8501
Spark UI:     http://localhost:8080
Prometheus:   http://localhost:9090
Grafana:      http://localhost:3000
```

---

## 🎓 Understanding What You See

### In Dashboard:
- **Price Chart** = Predictions over time
- **Statistics** = Data analysis
- **Table** = Raw prediction data

### In Spark UI:
- **Applications** = Running jobs
- **Workers** = Processing nodes
- **Streaming** = Real-time processing stats

### In Prometheus:
- **Metrics** = System performance
- **Targets** = Service health
- **Graphs** = Visual metrics

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Dashboard loads without errors
2. ✅ Can select symbols and see data
3. ✅ Charts show predictions
4. ✅ Spark UI shows running jobs
5. ✅ Prometheus shows metrics
6. ✅ No error messages in logs

---

## 🎉 You're All Set!

Now you can:
- ✅ See your pipeline running
- ✅ View predictions
- ✅ Monitor performance
- ✅ Explore features

**Enjoy exploring your pipeline!** 🚀

