#!/bin/bash

# Start script for Financial Valuation Engine
# This script starts both the backend API and frontend development servers

set -e

echo "🚀 Starting Financial Valuation Engine..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Install Python dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing Python dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start the application
echo "🎯 Starting application..."
python3 start_app.py 