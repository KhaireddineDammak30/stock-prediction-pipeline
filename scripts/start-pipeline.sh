#!/usr/bin/env bash
# Automated Pipeline Startup Script
# This script starts the entire pipeline with health checks and status monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MAX_WAIT_TIME=300  # 5 minutes max wait
CHECK_INTERVAL=5    # Check every 5 seconds

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

wait_for_service() {
    local service=$1
    local check_cmd=$2
    local max_wait=${3:-$MAX_WAIT_TIME}
    local elapsed=0
    
    print_info "Waiting for $service to be ready..."
    
    while [ $elapsed -lt $max_wait ]; do
        if eval "$check_cmd" > /dev/null 2>&1; then
            print_success "$service is ready!"
            return 0
        fi
        sleep $CHECK_INTERVAL
        elapsed=$((elapsed + CHECK_INTERVAL))
        echo -n "."
    done
    
    print_error "$service failed to start within ${max_wait}s"
    return 1
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Docker is available"
}

# Main execution
main() {
    print_header "🚀 Stock Prediction Pipeline - Automated Startup"
    
    # Check prerequisites
    print_header "Checking Prerequisites"
    check_docker
    
    # Step 1: Start Docker services
    print_header "Step 1: Starting Docker Services"
    cd "$PROJECT_DIR"
    
    print_info "Starting all services with docker-compose..."
    
    # Use docker compose (newer) or docker-compose (older)
    if docker compose version &> /dev/null 2>&1; then
        docker compose up -d
    elif command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        print_error "Neither 'docker compose' nor 'docker-compose' is available"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        print_error "Failed to start docker-compose services"
        exit 1
    fi
    
    print_success "Docker services started"
    
    # Step 2: Wait for critical services
    print_header "Step 2: Waiting for Services to be Healthy"
    
    # Wait for Cassandra (most critical, takes longest)
    wait_for_service "Cassandra" \
        "docker exec cassandra cqlsh -e 'DESCRIBE KEYSPACES' localhost 9042" \
        120
    
    # Wait for Kafka
    wait_for_service "Kafka" \
        "docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092" \
        60
    
    # Wait for Spark Master
    wait_for_service "Spark Master" \
        "curl -s http://localhost:8080 > /dev/null" \
        60
    
    # Wait for Prometheus
    wait_for_service "Prometheus" \
        "curl -s http://localhost:9090/-/healthy > /dev/null" \
        30
    
    # Step 3: Initialize Infrastructure
    print_header "Step 3: Initializing Infrastructure"
    
    # Initialize Kafka topics
    print_info "Creating Kafka topics..."
    if [ -f "$PROJECT_DIR/init/kafka-create-topics.sh" ]; then
        bash "$PROJECT_DIR/init/kafka-create-topics.sh" || print_warning "Kafka topics may already exist"
    else
        print_warning "Kafka topic creation script not found"
    fi
    
    # Initialize HDFS
    print_info "Creating HDFS directories..."
    if [ -f "$PROJECT_DIR/init/hdfs-bootstrap.sh" ]; then
        bash "$PROJECT_DIR/init/hdfs-bootstrap.sh" || print_warning "HDFS directories may already exist"
    else
        print_warning "HDFS bootstrap script not found"
    fi
    
    # Initialize Cassandra schema
    print_info "Initializing Cassandra schema..."
    if [ -f "$PROJECT_DIR/init/cassandra-init.cql" ]; then
        docker exec -i cassandra cqlsh < "$PROJECT_DIR/init/cassandra-init.cql" || \
            print_warning "Cassandra schema may already exist"
    else
        print_warning "Cassandra init script not found"
    fi
    
    print_success "Infrastructure initialized"
    
    # Step 4: Verify Producer
    print_header "Step 4: Verifying Data Producer"
    
    sleep 5  # Give producer time to start
    
    if docker ps | grep -q "producer"; then
        print_success "Producer is running"
        print_info "Check producer logs: docker logs producer -f"
    else
        print_warning "Producer container not found"
    fi
    
    # Step 5: Display Status
    print_header "Step 5: Pipeline Status"
    
    echo ""
    echo "Service URLs:"
    echo "  📊 Streamlit Dashboard:  http://localhost:8501"
    echo "  🔥 Spark Master UI:      http://localhost:8080"
    echo "  📈 Prometheus:            http://localhost:9090"
    echo "  📉 Grafana:               http://localhost:3000 (admin/admin)"
    echo ""
    
    echo "Next Steps:"
    echo "  1. Start Spark Streaming Job:"
    echo "     docker exec -it spark-submit bash -c 'cd /opt/spark/app && /opt/spark/bin/spark-submit \\"
    echo "       --master spark://spark-master:7077 \\"
    echo "       --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \\"
    echo "       --conf spark.cassandra.connection.host=cassandra \\"
    echo "       --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \\"
    echo "       streaming_ingest.py'"
    echo ""
    echo "  2. Or use the management script:"
    echo "     ./scripts/manage.sh start-streaming"
    echo ""
    echo "  3. View dashboard: http://localhost:8501"
    echo ""
    
    print_success "Pipeline startup complete! 🎉"
    print_info "Run './scripts/manage.sh status' to check service status"
}

# Run main function
main "$@"

