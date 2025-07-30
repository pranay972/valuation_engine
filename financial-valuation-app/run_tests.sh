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
    python -m pytest tests/ -v --tb=short
    print_status $? "Backend tests"
else
    echo "No tests directory found, skipping backend tests"
fi

# Test API endpoints
echo -e "\n${YELLOW}Testing API endpoints...${NC}"

# Start Flask server in background
echo "Starting Flask server..."
python app.py > /dev/null 2>&1 &
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

echo -e "\n${GREEN}🎉 All tests completed!${NC}" 