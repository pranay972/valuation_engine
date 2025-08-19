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

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start Redis first
echo "🔴 Starting Redis..."
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 5

# Start Celery services (they only need Redis)
echo "🐛 Starting Celery services..."
docker-compose up -d celery celery-beat celery-flower

# Wait for Celery services to be ready
echo "⏳ Waiting for Celery services to be ready..."
sleep 10

# Start Backend
echo "🔧 Starting Backend..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for Backend to be ready..."
sleep 10

# Start Frontend
echo "⚛️  Starting Frontend..."
docker-compose up -d frontend

echo ""
echo "⏳ Waiting for all services to be ready..."
sleep 15

echo ""
echo "🎉 Application is ready!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3001"
echo "   Backend API: http://localhost:8001"
echo "   Celery Flower (Monitoring): http://localhost:5555"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f [service_name]"
echo "   Stop: docker-compose down"
echo "   Restart: docker-compose restart"
echo ""
echo "📊 The application is now running with Celery worker and monitoring!" 