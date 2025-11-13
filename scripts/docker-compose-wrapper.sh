#!/usr/bin/env bash
# Docker Compose wrapper - handles both docker-compose and docker compose

# Check which command is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "Error: Neither 'docker-compose' nor 'docker compose' is available" >&2
    exit 1
fi

# Execute the command with all arguments
exec $DOCKER_COMPOSE_CMD "$@"

