#!/bin/bash

echo "🚀 Quick Start - Financial Valuation Application"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Complete rebuild process
echo "🔄 Starting complete rebuild process..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Clean up Docker system
echo "🧹 Cleaning up Docker system..."
docker system prune -a --volumes -f

# Set environment variable for production
echo "🌐 Setting production API URL..."
export REACT_APP_API_URL=https://valuationengine.app/api
echo "   REACT_APP_API_URL=${REACT_APP_API_URL}"

# Rebuild all services from scratch
echo "🔨 Rebuilding all services (no cache)..."
docker-compose build --no-cache

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for all services to be ready
echo "⏳ Waiting for all services to be ready..."
sleep 20

echo ""
echo "🎉 Application is ready!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: https://valuationengine.app"
echo "   Backend API: https://valuationengine.app/api"
echo "   Celery Flower (Monitoring): http://34.228.202.230:5555"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f [service_name]"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Complete rebuild: ./quick-start.sh"
echo ""
echo "📊 The application is now running with production HTTPS configuration!" 