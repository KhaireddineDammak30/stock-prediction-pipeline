#!/bin/bash
# Stop Spark Streaming Job

set -e

echo "🛑 Stopping Spark Streaming Job..."

# Find and stop the streaming query
docker exec spark-submit bash -c "
    # Try to find running streaming queries
    if command -v ps &> /dev/null; then
        # Kill any running streaming_ingest processes
        pkill -f streaming_ingest.py || true
    fi
" || true

# Alternative: Stop the spark-submit container's streaming job
# This will stop all jobs, but streaming should be restarted anyway
echo "ℹ️  Note: You may need to manually stop the streaming job if it's running in a separate terminal"
echo "ℹ️  Or restart the spark-submit container: docker restart spark-submit"

echo "✅ Done. You can now run batch training."

