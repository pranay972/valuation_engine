#!/bin/bash

# Deployment Validation Script for Financial Valuation Application
# This script validates the application locally before deployment

set -e

echo "🔍 Validating Financial Valuation Application deployment..."

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

# Check if backend run.py exists (Flask entry point)
if [ ! -f "backend/run.py" ]; then
    echo "❌ Error: backend/run.py not found. Flask entry point is missing!"
    exit 1
fi

echo "✅ Flask entry point found: backend/run.py"

# Check if required backend files exist
echo "🔍 Checking backend files..."
REQUIRED_FILES=(
    "backend/app/__init__.py"
    "backend/app/api/analysis.py"
    "backend/app/api/valuation.py"
    "backend/app/api/results.py"
    "backend/app/services/finance_core_service.py"
    "backend/finance_core/finance_calculator.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Error: Required file not found: $file"
        exit 1
    fi
    echo "✅ Found: $file"
done

# Check if frontend files exist
echo "🔍 Checking frontend files..."
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json not found"
    exit 1
fi
echo "✅ Found: frontend/package.json"

# Test Flask app creation (if Python is available)
if command -v python3 &> /dev/null; then
    echo "🔍 Testing Flask app creation..."
    cd backend
    
    # Set testing environment variables
    export FLASK_ENV=testing
    export SECRET_KEY=test-secret-key
    export DATABASE_URL=sqlite:///test.db
    export DEV_DATABASE_URL=sqlite:///test.db
    export TEST_DATABASE_URL=sqlite:///test.db
    
    # Test app creation
    if python3 -c "from app import create_app; app = create_app('testing'); print('✅ Flask app created successfully')" 2>/dev/null; then
        echo "✅ Flask app creation test passed!"
    else
        echo "❌ Flask app creation test failed!"
        exit 1
    fi
    
    cd ..
else
    echo "⚠️  Python3 not available, skipping Flask app creation test"
fi

# Check Docker configuration
echo "🔍 Checking Docker configuration..."
if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ Error: backend/Dockerfile not found"
    exit 1
fi
echo "✅ Found: backend/Dockerfile"

if [ ! -f "frontend/Dockerfile" ]; then
    echo "❌ Error: frontend/Dockerfile not found"
    exit 1
fi
echo "✅ Found: frontend/Dockerfile"

# Validate docker-compose.yml structure
echo "🔍 Validating docker-compose.yml..."
if ! grep -q "backend:" docker-compose.yml; then
    echo "❌ Error: Backend service not found in docker-compose.yml"
    exit 1
fi

if ! grep -q "frontend:" docker-compose.yml; then
    echo "❌ Error: Frontend service not found in docker-compose.yml"
    exit 1
fi

if ! grep -q "redis:" docker-compose.yml; then
    echo "❌ Error: Redis service not found in docker-compose.yml"
    exit 1
fi

echo "✅ Docker Compose configuration validated"

# Check environment files
echo "🔍 Checking environment files..."
if [ -f "backend/env.example" ]; then
    echo "✅ Found: backend/env.example"
else
    echo "⚠️  backend/env.example not found (optional)"
fi

if [ -f "frontend/env.example" ]; then
    echo "✅ Found: frontend/env.example"
else
    echo "⚠️  frontend/env.example not found (optional)"
fi

# Check if this is a git repository
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    echo "📋 Current branch: $(git branch --show-current)"
    echo "📋 Last commit: $(git log -1 --oneline)"
else
    echo "⚠️  Not a git repository"
fi

echo ""
echo "🎉 Deployment validation completed successfully!"
echo ""
echo "📋 Validation Summary:"
echo "   ✅ Flask entry point (run.py)"
echo "   ✅ Required backend files"
echo "   ✅ Frontend files"
echo "   ✅ Docker configuration"
echo "   ✅ Docker Compose services"
echo ""
echo "🚀 Ready for deployment!"
echo "   Run: ./deploy/deploy.sh"
