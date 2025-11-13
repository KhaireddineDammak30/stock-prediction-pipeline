# 🎯 What To Do Now - Step-by-Step Guide

## ✅ Current Status

Your pipeline is **successfully started**! All services are running.

## 📋 Next Steps (In Order)

### Step 1: Reset Streaming Checkpoints (If Needed)

**You're currently here!** The script is asking if you want to reset checkpoints.

**Answer:** Type `yes` and press Enter

This clears old checkpoints so streaming can start fresh. It's safe to do this.

```bash
# You're already running this:
./scripts/reset-streaming.sh
# Type: yes
```

---

### Step 2: Start Spark Streaming Job

**Open a NEW terminal window** (keep the first one open)

```bash
cd ~/projects/stock-prediction-pipeline
./scripts/manage.sh start-streaming
```

**What to expect:**
- You'll see Spark downloading packages (first time only)
- Then you'll see: `[BOOT] WIN5_DURATION=...` messages
- Batch processing logs will appear
- **Keep this terminal open!** The job runs continuously.

**Wait for:** You should see messages like:
```
[🔄] Batch 1: starting static join & Cassandra write
[✅] Joined NEW rows: 10
[💾] Wrote 10 rows to Cassandra.
```

---

### Step 3: Wait for Data Collection (5-10 minutes)

**Let the streaming job run for 5-10 minutes** to collect data.

**While waiting, you can:**
- Check Spark UI: http://localhost:8080
- Check producer logs: `docker logs producer -f`
- Check streaming progress in the terminal

**How to know it's working:**
- You see batch processing messages
- Spark UI shows the streaming job running
- No error messages

---

### Step 4: Start Batch Training Job

**After 5-10 minutes, open ANOTHER terminal window**

```bash
cd ~/projects/stock-prediction-pipeline
./scripts/manage.sh start-batch
```

**What to expect:**
- Model training will start
- You'll see: `RMSE: X.XXXX`, `MAE: X.XXXX`, `R2: X.XXXX`
- Then: "Wrote predictions to Cassandra"

**This job will complete** (unlike streaming which runs forever).

---

### Step 5: View Your Dashboard! 🎉

**Open your web browser:**

```
http://localhost:8501
```

**What you'll see:**
- Stock Prediction Dashboard
- Select a symbol (AAPL, MSFT, GOOGL)
- View predictions, charts, and statistics!

---

## 🎬 Quick Command Summary

```bash
# Terminal 1: Already done ✅
./scripts/manage.sh start

# Terminal 1: Reset checkpoints (if needed)
./scripts/reset-streaming.sh
# Type: yes

# Terminal 2: Start streaming (NEW terminal)
./scripts/manage.sh start-streaming
# Keep this running!

# Wait 5-10 minutes...

# Terminal 3: Start batch training (NEW terminal)
./scripts/manage.sh start-batch
# This will complete

# Browser: View dashboard
open http://localhost:8501
```

---

## 📊 What You Can Do Right Now

### Option A: Start Streaming Immediately

1. **Answer the reset prompt:**
   - Type `yes` and press Enter

2. **Start streaming in a new terminal:**
   ```bash
   ./scripts/manage.sh start-streaming
   ```

3. **Check it's working:**
   - Open http://localhost:8080 (Spark UI)
   - Look for "streaming_ingest" application

### Option B: Explore First

1. **Check the dashboard:**
   - Open http://localhost:8501
   - (Won't have predictions yet, but you can see the UI)

2. **Check Spark UI:**
   - Open http://localhost:8080
   - See Spark cluster status

3. **Check Prometheus:**
   - Open http://localhost:9090
   - View metrics

---

## ⏱️ Timeline

```
Now:           Pipeline started ✅
+ 0 min:       Start streaming job
+ 5-10 min:    Enough data collected
+ + 1 min:     Run batch training
+ + 1 min:     View predictions in dashboard! 🎉
```

**Total time: ~10-15 minutes to see predictions**

---

## 🎯 Your Immediate Action

**Right now, you should:**

1. **Answer the reset prompt:**
   ```
   Type: yes
   Press: Enter
   ```

2. **Then start streaming:**
   ```bash
   # In a NEW terminal:
   ./scripts/manage.sh start-streaming
   ```

3. **Wait 5-10 minutes**

4. **Run batch training:**
   ```bash
   # In another NEW terminal:
   ./scripts/manage.sh start-batch
   ```

5. **View dashboard:**
   ```
   http://localhost:8501
   ```

---

## ✅ Success Checklist

After following these steps, you should have:

- [ ] Pipeline services running
- [ ] Checkpoints reset (if needed)
- [ ] Streaming job running
- [ ] Data being collected (wait 5-10 min)
- [ ] Batch training completed
- [ ] Predictions visible in dashboard

---

## 🆘 If Something Goes Wrong

1. **Check logs:**
   ```bash
   ./scripts/manage.sh logs <service-name>
   ```

2. **Check status:**
   ```bash
   ./scripts/manage.sh status
   ```

3. **See troubleshooting:**
   - Read `TROUBLESHOOTING.md`

---

## 🎉 You're Almost There!

Just follow these steps and you'll see your predictions in the dashboard soon!

**Next action:** Type `yes` to the reset prompt, then start streaming! 🚀

