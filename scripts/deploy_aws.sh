#!/bin/bash
# ==============================================================================
# AWS EC2 Deployment Automation Script - Day 27
# ==============================================================================
# This script installs Docker/Docker Compose, sets up directories, configures
# environment variables, pulls images, and launches the FastAPI & Metabase services.
#
# Usage on EC2:
#   chmod +x deploy_aws.sh
#   ./deploy_aws.sh
# ==============================================================================

set -e

echo "=== 1. Updating System Packages ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== 2. Installing Docker & Docker Compose ==="
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    # Add current user to docker group to avoid sudo for docker commands
    sudo usermod -aG docker $USER
else
    echo "Docker is already installed."
fi

# Install docker-compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose is already installed."
fi

echo "=== 3. Setting Up Workspace Directories ==="
WORKSPACE_DIR="$HOME/customer-churn-engine"
mkdir -p "$WORKSPACE_DIR/nginx"
mkdir -p "$WORKSPACE_DIR/logs"

# Copy files over or prompt user to configure environment
echo "Checking environment file..."
if [ ! -f "$WORKSPACE_DIR/.env" ]; then
    echo "WARNING: .env file not found in $WORKSPACE_DIR."
    echo "Please create $WORKSPACE_DIR/.env based on .env.production.example"
    echo "Creating a dummy/placeholder .env..."
    cat <<EOT >> "$WORKSPACE_DIR/.env"
# AWS RDS / PostgreSQL credentials
DB_USER=postgres
DB_PASSWORD=secret_rds_password
DB_HOST=your-rds-endpoint.c1234567.rds.amazonaws.com
DB_PORT=5432
DB_NAME=churn_ltv_prod

APP_ENV=production
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "fallback_secret_key_1005")
EOT
fi

echo "=== 4. Creating Docker Compose Deployment Manifest ==="
cat <<EOT > "$WORKSPACE_DIR/docker-compose.prod.yml"
version: '3.8'

services:
  api:
    image: santoshgadale005/churn-api:latest
    container_name: churn-api-prod
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: redis-cache-prod
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - redis_data_prod:/data

  metabase:
    image: metabase/metabase:latest
    container_name: metabase-prod
    restart: always
    ports:
      - "3000:3000"
    environment:
      - MB_DB_TYPE=postgres
      - MB_DB_DBNAME=churn_ltv_prod
      - MB_DB_PORT=5432
      - MB_DB_USER=postgres
      - MB_DB_PASS=secret_rds_password
      - MB_DB_HOST=your-rds-endpoint.c1234567.rds.amazonaws.com
    depends_on:
      - api

volumes:
  redis_data_prod:
EOT

echo "=== 5. Launching Stack via Docker Compose ==="
cd "$WORKSPACE_DIR"
# In a real environment, we'd pull first:
# docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

echo "=== 6. Verifying Services ==="
docker ps

echo "=== DEPLOYMENT COMPLETED SUCCESSFULY ==="
echo "FastAPI API: http://localhost:8000/docs"
echo "Metabase Dashboard: http://localhost:3000"
