# 🔧 Batch Job Resource Allocation Fix

## Problem

Your batch job is stuck with warnings:
```
WARN TaskSchedulerImpl: Initial job has not accepted any resources
```

**Root Cause:** The streaming job is using all available Spark resources (4 cores), leaving no resources for the batch job.

## ✅ Solution

You have **2 options**:

### Option 1: Stop Streaming Job Temporarily (Recommended)

**Stop the streaming job, run batch training, then restart streaming:**

```bash
# 1. Stop streaming job (press Ctrl+C in the terminal where streaming is running)
# OR if it's running in background, find and stop it:
docker exec spark-submit pkill -f streaming_ingest.py || true

# 2. Wait 10 seconds for resources to free up
sleep 10

# 3. Run batch training
./scripts/manage.sh start-batch

# 4. After batch completes, restart streaming
./scripts/manage.sh start-streaming
```

### Option 2: Configure Batch Job to Use Fewer Resources

**I've already updated the batch job to request fewer resources.** Try running it again:

```bash
./scripts/manage.sh start-batch
```

The batch job now requests:
- Max 2 cores (instead of all 4)
- 1 core per executor
- 1GB memory per executor

This should allow it to run alongside streaming (if streaming uses 2 cores).

## 🔍 How to Check Resource Usage

### Check Spark UI

Open: **http://localhost:8080**

**Look at:**
- **Applications tab** - See which apps are running
- **Executors tab** - See resource allocation
- **Workers tab** - See total available resources

### Check via Command Line

```bash
# Check what's using resources
docker exec spark-master curl -s http://localhost:8080 | grep -A 5 "Application ID"
```

## 📊 Understanding Resource Allocation

**Your Spark Cluster:**
- 2 workers
- 2 cores per worker = **4 cores total**
- 2GB RAM per worker = **4GB RAM total**

**Current Situation:**
- Streaming job: Using 2 executors (likely 2-4 cores)
- Batch job: Needs resources but can't get them

**Solution:**
- Option 1: Stop streaming → Run batch → Restart streaming
- Option 2: Configure batch to use fewer resources (already done)

## 🎯 Recommended Workflow

### For Development/Testing:

```bash
# 1. Start pipeline
./scripts/manage.sh start

# 2. Start streaming (collect data)
./scripts/manage.sh start-streaming

# 3. Wait 5-10 minutes for data

# 4. Stop streaming (Ctrl+C or kill process)
# In the terminal where streaming is running, press Ctrl+C

# 5. Run batch training
./scripts/manage.sh start-batch

# 6. Restart streaming (optional)
./scripts/manage.sh start-streaming
```

### For Production:

- Use separate Spark clusters for streaming and batch
- Or use Spark's dynamic allocation
- Or schedule batch jobs during off-peak hours

## 🛠️ Quick Fix Right Now

**If you want to run batch training immediately:**

1. **Find and stop streaming:**
   ```bash
   # Check if streaming is running
   docker exec spark-submit ps aux | grep streaming
   
   # If found, stop it
   docker exec spark-submit pkill -f streaming_ingest.py
   ```

2. **Wait 10 seconds:**
   ```bash
   sleep 10
   ```

3. **Run batch:**
   ```bash
   ./scripts/manage.sh start-batch
   ```

4. **It should work now!** ✅

## ✅ Verification

After stopping streaming, you should see:

1. **In Spark UI (http://localhost:8080):**
   - Streaming app disappears or shows "FINISHED"
   - Batch app gets executors allocated

2. **In batch job logs:**
   - Executor allocation messages
   - Task execution
   - Model training output

## 💡 Why This Happens

Spark's standalone mode doesn't automatically share resources between applications. When one app (streaming) uses all resources, other apps (batch) must wait.

**Solutions:**
- Stop one app to free resources (simplest)
- Configure resource limits (already done)
- Use resource pools (advanced)

## 🎯 Next Steps

1. **Stop streaming job** (if running)
2. **Run batch training** - should work now
3. **Restart streaming** (after batch completes)

The batch job should complete successfully! 🎉

