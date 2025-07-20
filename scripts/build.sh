#!/bin/bash

# Build script for Financial Valuation Engine
# This script builds both the backend and frontend for production

set -e

echo "🔨 Building Financial Valuation Engine..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
make clean

# Build backend
echo "🔨 Building backend..."
source .venv/bin/activate
python setup.py build

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
echo "📁 Frontend build output: frontend/build/"
echo "📁 Backend build output: build/" 