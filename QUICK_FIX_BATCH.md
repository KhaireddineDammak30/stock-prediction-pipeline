# ⚡ Quick Fix: Batch Job Resource Issue

## 🎯 The Problem

Your batch job can't get resources because **streaming job is using all 4 cores**.

## ✅ Solution: Stop Streaming, Run Batch, Restart Streaming

### Step 1: Stop Streaming Job

**Option A: If streaming is running in a terminal**
- Go to that terminal
- Press **Ctrl+C** to stop it

**Option B: Stop it via Docker**
```bash
# Find the streaming process
docker exec spark-submit ps aux | grep streaming

# Stop it (replace PID with actual process ID)
docker exec spark-submit kill -9 <PID>

# OR stop the entire spark-submit container temporarily
docker stop spark-submit
docker start spark-submit
```

### Step 2: Wait 10 Seconds

```bash
sleep 10
```

This allows Spark to free up resources.

### Step 3: Run Batch Training

```bash
./scripts/manage.sh start-batch
```

**It should work now!** ✅

### Step 4: After Batch Completes, Restart Streaming

```bash
./scripts/manage.sh start-streaming
```

## 🔍 Verify Resources Are Free

**Check Spark UI:** http://localhost:8080

**Look for:**
- Streaming app should be gone or show "FINISHED"
- Batch app should get executors allocated

## 📊 What I've Already Fixed

1. ✅ Updated batch job to request fewer resources (2 cores max)
2. ✅ Added resource limits to batch job configuration

**But you still need to stop streaming first** because it's holding all resources.

## 🎯 Right Now - Do This:

```bash
# 1. Stop streaming (choose one method above)

# 2. Wait
sleep 10

# 3. Run batch
./scripts/manage.sh start-batch

# 4. After it completes, restart streaming
./scripts/manage.sh start-streaming
```

## 💡 Why This Happens

Spark standalone mode doesn't share resources between apps. When streaming uses all 4 cores, batch can't get any.

**Solutions:**
- ✅ Stop streaming → Run batch → Restart streaming (simplest)
- ✅ Use resource limits (already configured)
- ✅ Use separate Spark clusters (production)

## ✅ After This Fix

Your batch job should:
- Get executors allocated
- Start processing
- Train the model
- Generate predictions
- Complete successfully! 🎉

