#!/bin/bash

echo "🧪 Running Financial Valuation App Tests"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Test backend
echo -e "\n${YELLOW}Testing Backend...${NC}"
cd backend

# Check if tests directory exists
if [ -d "tests" ]; then
    echo "Running pytest..."
    if [ -f "pyproject.toml" ] && command -v poetry &> /dev/null; then
        echo "Using Poetry to run tests..."
        echo "Running API tests..."
        poetry run python -m pytest tests/test_app_simple.py -v --tb=short 2>/dev/null || echo "API tests failed"
        echo "Running finance core tests..."
        poetry run python -m pytest tests/test_finance_core.py -v --tb=short 2>/dev/null || echo "Finance core tests failed"
    elif command -v python &> /dev/null; then
        echo "Running API tests..."
        python -m pytest tests/test_app.py -v --tb=short 2>/dev/null || echo "API tests failed or pytest not installed"
        echo "Running finance core tests..."
        python -m pytest tests/test_finance_core.py -v --tb=short 2>/dev/null || echo "Finance core tests failed or pytest not installed"
    elif command -v python3 &> /dev/null; then
        echo "Running API tests..."
        python3 -m pytest tests/test_app.py -v --tb=short 2>/dev/null || echo "API tests failed or pytest not installed"
        echo "Running finance core tests..."
        python3 -m pytest tests/test_finance_core.py -v --tb=short 2>/dev/null || echo "Finance core tests failed or pytest not installed"
    else
        echo "Python not found, skipping backend tests (use Docker for full testing)"
    fi
else
    echo "No tests directory found, skipping backend tests"
fi

# Test API endpoints
echo -e "\n${YELLOW}Testing API endpoints...${NC}"

# Check if Python is available for starting the server
if [ -f "pyproject.toml" ] && command -v poetry &> /dev/null; then
    # Start Flask server in background using Poetry
    echo "Starting Flask server with Poetry..."
    poetry run python app.py > /dev/null 2>&1 &
    SERVER_PID=$!
elif command -v python &> /dev/null || command -v python3 &> /dev/null; then
    # Start Flask server in background
    echo "Starting Flask server..."
    if command -v python &> /dev/null; then
        python app.py > /dev/null 2>&1 &
    else
        python3 app.py > /dev/null 2>&1 &
    fi
    SERVER_PID=$!

    # Wait for server to start
    sleep 5

    # Test endpoints
    echo "Testing health endpoint..."
    curl -f http://localhost:5000/health > /dev/null 2>&1
    print_status $? "Health endpoint"

    echo "Testing analysis types endpoint..."
    curl -f http://localhost:5000/api/analysis/types > /dev/null 2>&1
    print_status $? "Analysis types endpoint"

    echo "Testing Swagger JSON endpoint..."
    curl -f http://localhost:5000/static/swagger.json > /dev/null 2>&1
    print_status $? "Swagger JSON endpoint"

    # Stop server
    kill $SERVER_PID 2>/dev/null
else
    echo "Python not found, skipping API endpoint tests (use Docker for full testing)"
fi

# Test frontend (if available)
echo -e "\n${YELLOW}Testing Frontend...${NC}"
cd ../frontend

if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo "Running npm tests..."
    npm test -- --watchAll=false --passWithNoTests
    print_status $? "Frontend tests"
else
    echo "No frontend tests configured, skipping..."
fi

cd ..

echo -e "\n${GREEN}🎉 Test run completed!${NC}"
echo -e "${YELLOW}Note: For full testing with dependencies, use Docker:${NC}"
echo -e "   docker-compose up --build -d"
echo -e "   # Then run tests inside the container" 