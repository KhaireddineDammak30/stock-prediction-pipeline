#!/bin/bash
# Quick test script to verify the pipeline is working

set -e

echo "🧪 Testing Stock Prediction Pipeline"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_service() {
    local service=$1
    if docker ps | grep -q "$service"; then
        echo -e "${GREEN}✅${NC} $service is running"
        return 0
    else
        echo -e "${RED}❌${NC} $service is NOT running"
        return 1
    fi
}

test_endpoint() {
    local url=$1
    local name=$2
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name is accessible"
        return 0
    else
        echo -e "${RED}❌${NC} $name is NOT accessible"
        return 1
    fi
}

test_kafka_topic() {
    if docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null | grep -q "ticks"; then
        echo -e "${GREEN}✅${NC} Kafka topic 'ticks' exists"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} Kafka topic 'ticks' not found (may need to create)"
        return 1
    fi
}

test_cassandra_table() {
    if docker exec cassandra cqlsh -e "SELECT COUNT(*) FROM market.features;" 2>/dev/null | grep -q "count"; then
        echo -e "${GREEN}✅${NC} Cassandra table 'features' exists"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} Cassandra table 'features' not found (may need to initialize)"
        return 1
    fi
}

# Run tests
echo "1. Testing Services..."
test_service "zookeeper" || exit 1
test_service "kafka" || exit 1
test_service "namenode" || exit 1
test_service "datanode" || exit 1
test_service "cassandra" || exit 1
test_service "spark-master" || exit 1
test_service "spark-worker-1" || exit 1
test_service "spark-worker-2" || exit 1
test_service "producer" || exit 1
test_service "prometheus" || exit 1
test_service "grafana" || exit 1
test_service "streamlit" || exit 1
echo ""

echo "2. Testing Endpoints..."
test_endpoint "http://localhost:8080" "Spark Master UI" || echo -e "${YELLOW}⚠️${NC} Spark Master UI not accessible (may be starting)"
test_endpoint "http://localhost:9090/-/healthy" "Prometheus" || echo -e "${YELLOW}⚠️${NC} Prometheus not accessible"
test_endpoint "http://localhost:3000/api/health" "Grafana" || echo -e "${YELLOW}⚠️${NC} Grafana not accessible"
test_endpoint "http://localhost:8501" "Streamlit" || echo -e "${YELLOW}⚠️${NC} Streamlit not accessible"
echo ""

echo "3. Testing Infrastructure..."
test_kafka_topic || echo -e "${YELLOW}💡${NC} Run: bash init/kafka-create-topics.sh"
test_cassandra_table || echo -e "${YELLOW}💡${NC} Run: docker exec -i cassandra cqlsh < init/cassandra-init.cql"
echo ""

echo "4. Checking Data Flow..."
# Check if producer is sending data
if docker logs producer 2>&1 | tail -20 | grep -q "Sent tick"; then
    echo -e "${GREEN}✅${NC} Producer is sending data"
else
    echo -e "${YELLOW}⚠️${NC} No recent producer activity (check logs: docker logs producer)"
fi

# Check if Spark job is running
if docker ps | grep -q "spark-submit"; then
    echo -e "${GREEN}✅${NC} Spark submit container is running"
    echo -e "${YELLOW}💡${NC} Check if streaming job is active: docker logs spark-submit"
else
    echo -e "${YELLOW}⚠️${NC} Spark submit container not running (start streaming job manually)"
fi
echo ""

echo "===================================="
echo -e "${GREEN}✅ Basic tests completed!${NC}"
echo ""
echo "Next steps:"
echo "1. If any services failed, check: docker compose ps (or docker-compose ps)"
echo "2. Initialize infrastructure: bash init/kafka-create-topics.sh && bash init/hdfs-bootstrap.sh"
echo "3. Start Spark streaming job (see QUICK_START.md)"
echo "4. View dashboards:"
echo "   - Streamlit: http://localhost:8501"
echo "   - Spark UI: http://localhost:8080"
echo "   - Grafana: http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"

