#!/usr/bin/env python3
"""
Test script for Swagger UI endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_swagger_json():
    """Test swagger.json endpoint"""
    print("\n🔍 Testing swagger.json endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/static/swagger.json")
        print(f"✅ Swagger JSON: {response.status_code}")
        if response.status_code == 200:
            swagger_data = response.json()
            print(f"   Title: {swagger_data.get('info', {}).get('title')}")
            print(f"   Version: {swagger_data.get('info', {}).get('version')}")
            print(f"   Endpoints: {len(swagger_data.get('paths', {}))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Swagger JSON failed: {e}")
        return False

def test_analysis_types():
    """Test analysis types endpoint"""
    print("\n🔍 Testing analysis types endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/types")
        print(f"✅ Analysis types: {response.status_code}")
        if response.status_code == 200:
            types = response.json()
            print(f"   Found {len(types)} analysis types:")
            for analysis_type in types:
                print(f"     - {analysis_type['name']} ({analysis_type['id']})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Analysis types failed: {e}")
        return False

def test_create_analysis():
    """Test create analysis endpoint"""
    print("\n🔍 Testing create analysis endpoint...")
    try:
        data = {
            "analysis_type": "dcf_wacc",
            "company_name": "Test Company"
        }
        response = requests.post(f"{BASE_URL}/api/analysis", json=data)
        print(f"✅ Create analysis: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Analysis ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Create analysis failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Financial Valuation API with Swagger UI")
    print("=" * 50)
    
    # Wait a moment for the server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_health,
        test_swagger_json,
        test_analysis_types,
        test_create_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Swagger UI is working correctly.")
        print(f"\n📖 Access Swagger UI at: {BASE_URL}/api/docs")
        print(f"📄 API Documentation at: {BASE_URL}/static/swagger.json")
    else:
        print("❌ Some tests failed. Check the server logs.")
    
    return passed == total

if __name__ == "__main__":
    main() 