.PHONY: help install test lint clean build run docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the application"
	@echo "  run         - Run the application"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run   - Run with Docker Compose"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run tests
test:
	@echo "Running backend tests..."
	python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false

# Run linting
lint:
	@echo "Running backend linting..."
	flake8 backend/
	black --check backend/
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	cd frontend && npm run clean

# Build the application
build: clean
	@echo "Building backend..."
	python setup.py build
	@echo "Building frontend..."
	cd frontend && npm run build

# Run the application
run:
	@echo "Starting the application..."
	python start_app.py

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose build

# Run with Docker Compose
docker-run:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

# Stop Docker services
docker-stop:
	@echo "Stopping Docker services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Production build
prod-build:
	@echo "Building for production..."
	docker-compose -f docker-compose.prod.yml build

# Production run
prod-run:
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d 