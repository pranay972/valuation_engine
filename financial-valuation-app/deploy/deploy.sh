#!/bin/bash

# Deployment Script for Financial Valuation Application
# This script updates and deploys the application

set -e

echo "🚀 Starting deployment of Financial Valuation Application..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

cd "$APP_DIR"

echo "📁 Working directory: $(pwd)"

# Clean up system for lightweight EC2 instances
echo "🧹 Cleaning up system for lightweight deployment..."

# Stop and remove all containers
echo "🛑 Stopping all running containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Remove all images
echo "🗑️  Removing all Docker images..."
docker rmi $(docker images -aq) 2>/dev/null || true

# Remove all volumes
echo "🗑️  Removing all Docker volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || true

# Remove all networks
echo "🗑️  Removing all Docker networks..."
docker network prune -f 2>/dev/null || true

# Clean up Docker system
echo "🧹 Cleaning up Docker system..."
docker system prune -af --volumes 2>/dev/null || true

# Clean up system packages and cache
echo "🧹 Cleaning up system packages and cache..."
sudo yum clean all 2>/dev/null || true
sudo rm -rf /var/cache/yum 2>/dev/null || true
sudo rm -rf /var/cache/dnf 2>/dev/null || true

# Clean up log files
echo "🧹 Cleaning up log files..."
sudo find /var/log -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
sudo find /var/log -name "*.gz" -type f -mtime +7 -delete 2>/dev/null || true

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
sudo rm -rf /tmp/* 2>/dev/null || true
sudo rm -rf /var/tmp/* 2>/dev/null || true

# Clean up journal logs
echo "🧹 Cleaning up journal logs..."
sudo journalctl --vacuum-time=7d 2>/dev/null || true

# Clean up old kernel versions (keep only current)
echo "🧹 Cleaning up old kernel versions..."
sudo package-cleanup --oldkernels --count=1 -y 2>/dev/null || true

# Show available disk space
echo "💾 Available disk space:"
df -h /

# Run deployment validation
if [ -f "deploy/validate-deployment.sh" ]; then
    echo "🔍 Running deployment validation..."
    ./deploy/validate-deployment.sh
    echo "✅ Deployment validation passed!"
else
    echo "⚠️  Deployment validation script not found, running basic checks..."
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ Error: docker-compose.yml not found. Are you in the correct directory?"
        exit 1
    fi

    # Check if backend run.py exists (Flask entry point)
    if [ ! -f "backend/run.py" ]; then
        echo "❌ Error: backend/run.py not found. Flask entry point is missing!"
        exit 1
    fi
fi

# Pull latest changes if this is a git repository
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes from git..."
    git pull origin main
else
    echo "⚠️  Not a git repository, skipping git pull"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build new images with optimization for lightweight instances
echo "🔨 Building new Docker images with optimization..."

# Set Docker build arguments for optimization
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with memory and CPU limits for lightweight instances
docker-compose build --no-cache \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --parallel

# Start containers with resource limits for lightweight instances
echo "🚀 Starting containers with resource optimization..."

# Start containers with resource constraints
docker-compose up -d

# Set resource limits for running containers
echo "⚙️  Setting resource limits for containers..."

# Backend container limits
docker update --memory=512m --memory-swap=1g --cpus=0.5 financial_valuation_backend 2>/dev/null || true

# Frontend container limits  
docker update --memory=256m --memory-swap=512m --cpus=0.3 financial_valuation_frontend 2>/dev/null || true

# Celery worker limits
docker update --memory=256m --memory-swap=512m --cpus=0.3 financial_valuation_celery 2>/dev/null || true

# Redis container limits
docker update --memory=128m --memory-swap=256m --cpus=0.2 financial_valuation_redis 2>/dev/null || true

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
else
    echo "❌ Some services failed to start"
    docker-compose logs
    exit 1
fi

# Test backend health endpoint
echo "🔍 Testing backend health endpoint..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s --max-time 10 http://localhost:8001/health > /dev/null; then
        echo "✅ Backend health check passed!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⏳ Backend not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES)..."
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend health check failed after $MAX_RETRIES attempts"
    docker-compose logs backend
    exit 1
fi

# Get the public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://$PUBLIC_IP"
echo "   Backend API: http://$PUBLIC_IP/api"
echo "   Swagger UI: http://$PUBLIC_IP/api/docs"
echo "   Health Check: http://$PUBLIC_IP/health"
echo "   Celery Flower: http://$PUBLIC_IP:5555"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Restart: docker-compose restart"
echo "   Stop: docker-compose down"
echo "   Update: ./deploy/deploy.sh"
echo ""
echo "📊 Container status:"
docker-compose ps

# Final cleanup and optimization for lightweight instances
echo ""
echo "🧹 Performing final cleanup and optimization..."

# Clean up Docker build cache
echo "🗑️  Cleaning up Docker build cache..."
docker builder prune -af 2>/dev/null || true

# Clean up any dangling images
echo "🗑️  Cleaning up dangling images..."
docker image prune -f 2>/dev/null || true

# Show final resource usage
echo ""
echo "💾 Final disk space and resource usage:"
df -h /
echo ""
echo "🐳 Docker disk usage:"
docker system df
echo ""
echo "📊 Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "Resource monitoring not available" 