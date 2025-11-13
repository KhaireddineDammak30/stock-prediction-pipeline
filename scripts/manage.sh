#!/usr/bin/env bash
# Pipeline Management CLI Tool
# Provides easy commands to manage the entire pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
show_help() {
    cat << EOF
Stock Prediction Pipeline - Management Tool

Usage: $0 <command> [options]

Commands:
  start           Start all services and initialize infrastructure
  stop            Stop all services
  restart         Restart all services
  status          Show status of all services
  logs <service>  Show logs for a service (use 'all' for all services)
  start-streaming Start Spark streaming job
  start-batch     Start Spark batch training job
  test            Run health checks
  clean           Stop services and remove volumes (WARNING: deletes data)
  shell <service> Open shell in a service container

Services:
  producer, kafka, cassandra, spark-master, spark-worker-1, spark-worker-2,
  spark-submit, streamlit, prometheus, grafana, namenode, datanode

Examples:
  $0 start
  $0 status
  $0 logs producer
  $0 start-streaming
  $0 shell cassandra

EOF
}

start_pipeline() {
    echo -e "${BLUE}Starting pipeline...${NC}"
    bash "$SCRIPT_DIR/start-pipeline.sh"
}

stop_pipeline() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    cd "$PROJECT_DIR"
    if docker compose version &> /dev/null 2>&1; then
        docker compose down
    elif command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        echo -e "${RED}Error: Docker Compose not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}Services stopped${NC}"
}

restart_pipeline() {
    echo -e "${YELLOW}Restarting pipeline...${NC}"
    stop_pipeline
    sleep 2
    start_pipeline
}

show_status() {
    echo -e "${BLUE}Service Status:${NC}\n"
    cd "$PROJECT_DIR"
    if docker compose version &> /dev/null 2>&1; then
        docker compose ps
    elif command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        echo -e "${RED}Error: Docker Compose not found${NC}"
        exit 1
    fi
    
    echo -e "\n${BLUE}Service URLs:${NC}"
    echo "  📊 Streamlit:   http://localhost:8501"
    echo "  🔥 Spark UI:     http://localhost:8080"
    echo "  📈 Prometheus:   http://localhost:9090"
    echo "  📉 Grafana:      http://localhost:3000"
    echo ""
    
    # Check if services are responding
    echo -e "${BLUE}Health Checks:${NC}"
    
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Streamlit is accessible"
    else
        echo -e "  ${RED}❌${NC} Streamlit is not accessible"
    fi
    
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Spark Master is accessible"
    else
        echo -e "  ${RED}❌${NC} Spark Master is not accessible"
    fi
    
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Prometheus is healthy"
    else
        echo -e "  ${RED}❌${NC} Prometheus is not healthy"
    fi
}

show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Service name required${NC}"
        echo "Usage: $0 logs <service>"
        echo "Use 'all' to show all logs"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}Error: Docker Compose not found${NC}"
        exit 1
    fi
    
    if [ "$service" == "all" ]; then
        $DOCKER_COMPOSE_CMD logs -f
    else
        $DOCKER_COMPOSE_CMD logs -f "$service"
    fi
}

start_streaming() {
    echo -e "${BLUE}Starting Spark Streaming Job...${NC}"
    docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
        --conf spark.cassandra.connection.host=cassandra \
        --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
        streaming_ingest.py"
}

start_batch() {
    echo -e "${BLUE}Starting Spark Batch Training Job...${NC}"
    echo -e "${YELLOW}Note: If streaming job is running, it may need to be stopped first.${NC}"
    docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
        --conf spark.cassandra.connection.host=cassandra \
        --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
        --conf spark.cores.max=2 \
        --conf spark.executor.cores=1 \
        --conf spark.executor.memory=1g \
        batch_train_predict.py" || true
}

run_tests() {
    echo -e "${BLUE}Running health checks...${NC}"
    bash "$PROJECT_DIR/QUICK_TEST.sh"
}

clean_all() {
    echo -e "${RED}WARNING: This will delete all data!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" == "yes" ]; then
        cd "$PROJECT_DIR"
        if docker compose version &> /dev/null 2>&1; then
            docker compose down -v
        elif command -v docker-compose &> /dev/null; then
            docker-compose down -v
        else
            echo -e "${RED}Error: Docker Compose not found${NC}"
            exit 1
        fi
        echo -e "${GREEN}All services and data removed${NC}"
    else
        echo -e "${YELLOW}Cancelled${NC}"
    fi
}

open_shell() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Service name required${NC}"
        echo "Usage: $0 shell <service>"
        exit 1
    fi
    
    docker exec -it "$service" /bin/bash || docker exec -it "$service" /bin/sh
}

# Main command dispatcher
case "${1:-help}" in
    start)
        start_pipeline
        ;;
    stop)
        stop_pipeline
        ;;
    restart)
        restart_pipeline
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    start-streaming)
        start_streaming
        ;;
    start-batch)
        start_batch
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_all
        ;;
    shell)
        open_shell "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}\n"
        show_help
        exit 1
        ;;
esac

