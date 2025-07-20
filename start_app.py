#!/usr/bin/env python3
"""
Startup script for the Financial Valuation Web Application
This script starts both the FastAPI backend and React frontend
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def run_api():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return None
    
    # Install API dependencies if needed
    try:
        subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install API dependencies: {e}")
        return None
    
    # Start the API server
    try:
        process = subprocess.Popen([
            "python3", "-m", "uvicorn", "backend.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        print("✅ FastAPI backend started on http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
        return None

def run_frontend():
    """Run the React frontend"""
    print("🚀 Starting React frontend...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    # Install frontend dependencies if needed
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return None
    
    # Start the React development server
    try:
        process = subprocess.Popen(["npm", "start"], cwd="frontend")
        print("✅ React frontend started on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main function to start both services"""
    print("🎯 Financial Valuation Web Application")
    print("=" * 50)
    
    # Check if Node.js is installed
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed. Please install Node.js first.")
        print("   Download from: https://nodejs.org/")
        return
    
    # Start API
    api_process = run_api()
    if not api_process:
        print("❌ Failed to start API. Exiting.")
        return
    
    # Wait a moment for API to start
    time.sleep(2)
    
    # Start frontend
    frontend_process = run_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping API...")
        api_process.terminate()
        return
    
    print("\n🎉 Application started successfully!")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to stop both services...")
    
    try:
        # Wait for both processes
        api_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        api_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped.")

if __name__ == "__main__":
    main() 