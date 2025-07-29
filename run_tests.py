#!/usr/bin/env python3
"""
Test runner script for the entire valuation project.
This script runs all tests locally, similar to the CI/CD pipeline.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"🔄 Running: {command}")
    if cwd:
        print(f"📁 Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        print(f"✅ Success: {command}")
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return e

def test_finance_core():
    """Test the finance_core module."""
    print("\n" + "="*60)
    print("🧮 Testing Finance Core")
    print("="*60)
    
    # Run tests
    result = run_command("poetry run python -m pytest finance_core/test_finance_calculator.py -v", check=False)
    return result.returncode == 0

def test_backend():
    """Test the backend API."""
    print("\n" + "="*60)
    print("🌐 Testing Backend API")
    print("="*60)
    
    # Run tests
    result = run_command("poetry run python -m pytest backend/tests/ -v", check=False)
    return result.returncode == 0

def test_api_integration():
    """Test API integration."""
    print("\n" + "="*60)
    print("🔗 Testing API Integration")
    print("="*60)
    
    # Start server in background
    print("🚀 Starting Flask server...")
    server_process = subprocess.Popen(
        ["poetry", "run", "python", "backend/run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(10)
    
    try:
        # Test API endpoints
        result = run_command("poetry run python backend/test_swagger.py", check=False)
        
        # Test Swagger UI
        run_command("curl -f http://localhost:5001/health")
        run_command("curl -f http://localhost:5001/static/swagger.json")
        run_command("curl -f http://localhost:5001/api/docs")
        
        return result.returncode == 0
    finally:
        # Stop server
        print("🛑 Stopping Flask server...")
        server_process.terminate()
        server_process.wait()

def run_linting():
    """Run code quality checks."""
    print("\n" + "="*60)
    print("🔍 Running Code Quality Checks")
    print("="*60)
    
    # Install linting tools
    run_command("pip install black flake8 isort mypy")
    
    # Check formatting
    run_command("black --check --diff finance_core/ backend/", check=False)
    
    # Check imports
    run_command("isort --check-only --diff finance_core/ backend/", check=False)
    
    # Lint code
    run_command("flake8 finance_core/ backend/ --max-line-length=88 --extend-ignore=E203,W503", check=False)
    
    # Type check
    run_command("mypy finance_core/ backend/ --ignore-missing-imports", check=False)

def main():
    """Run all tests."""
    print("🚀 Starting comprehensive test suite...")
    print(f"📁 Project root: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not (Path("finance_core").exists() and Path("backend").exists()):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    results = []
    
    # Test finance_core
    results.append(test_finance_core())
    
    # Test backend
    results.append(test_backend())
    
    # Test API integration
    results.append(test_api_integration())
    
    # Run linting (optional)
    if len(sys.argv) > 1 and sys.argv[1] == "--lint":
        run_linting()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    tests = ["Finance Core", "Backend API", "API Integration"]
    for test, result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test}: {status}")
    
    all_passed = all(results)
    if all_passed:
        print("\n🎉 All tests passed!")
        print("🚀 Your code is ready for deployment!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 