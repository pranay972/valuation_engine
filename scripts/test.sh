#!/bin/bash

# Test script for Financial Valuation Engine
# This script runs all tests for both backend and frontend

set -e

echo "🧪 Running tests for Financial Valuation Engine..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Run backend tests
echo "🧪 Running backend tests..."
python -m pytest backend/tests/ -v --cov=backend --cov-report=term-missing

# Run frontend tests
echo "🧪 Running frontend tests..."
cd frontend
npm test -- --watchAll=false --coverage
cd ..

echo "✅ All tests completed!" 