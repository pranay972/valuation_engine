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

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Are you in the correct directory?"
    exit 1
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

# Build new images
echo "🔨 Building new Docker images..."
docker-compose build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
else
    echo "❌ Some services failed to start"
    docker-compose logs
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
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Restart: docker-compose restart"
echo "   Stop: docker-compose down"
echo "   Update: ./deploy/deploy.sh"
echo ""
echo "📊 Container status:"
docker-compose ps 