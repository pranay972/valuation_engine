#!/usr/bin/env python3
"""
Test script for Swagger UI and API endpoints.
"""

import requests
import json
import time

def test_swagger_ui():
    """Test Swagger UI and API endpoints."""
    
    base_url = "http://localhost:5001"
    
    print("🚀 Testing Valuation API with Swagger UI")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Status: {data.get('status')}")
            print(f"   💬 Message: {data.get('message')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test swagger.json
    print("\n2. Testing Swagger JSON...")
    try:
        response = requests.get(f"{base_url}/static/swagger.json")
        print(f"   ✅ Swagger JSON: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 API Title: {data.get('info', {}).get('title')}")
            print(f"   📝 Version: {data.get('info', {}).get('version')}")
            print(f"   🔗 Endpoints: {len(data.get('paths', {}))}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Swagger UI
    print("\n3. Testing Swagger UI...")
    try:
        response = requests.get(f"{base_url}/api/docs")
        print(f"   ✅ Swagger UI: {response.status_code}")
        if response.status_code == 200:
            print("   🌐 Swagger UI is accessible")
            print(f"   🔗 Visit: {base_url}/api/docs")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test sample data endpoint
    print("\n4. Testing sample data endpoint...")
    try:
        response = requests.get(f"{base_url}/api/valuation/sample")
        print(f"   ✅ Sample data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🏢 Company: {data.get('company_name')}")
            print(f"   📅 Date: {data.get('valuation_date')}")
            revenue = data.get('financial_inputs', {}).get('revenue', [])
            print(f"   💰 Revenue (first 2 years): {revenue[:2]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test valuation calculation
    print("\n5. Testing valuation calculation...")
    sample_data = {
        "company_name": "Test Corp",
        "valuation_date": "2024-01-01",
        "financial_inputs": {
            "revenue": [1000.0, 1100.0, 1210.0],
            "ebit_margin": 0.15,
            "tax_rate": 0.25,
            "capex": [150.0, 165.0, 181.5],
            "depreciation": [100.0, 110.0, 121.0],
            "nwc_changes": [50.0, 55.0, 60.5],
            "amortization": [10.0, 11.0, 12.1],
            "other_non_cash": [5.0, 5.5, 6.1],
            "other_working_capital": [2.0, 2.2, 2.4],
            "terminal_growth": 0.025,
            "wacc": 0.10,
            "share_count": 10.0,
            "cost_of_debt": 0.06,
            "scenarios": {
                "optimistic": {
                    "ebit_margin": 0.20,
                    "terminal_growth_rate": 0.03
                },
                "pessimistic": {
                    "ebit_margin": 0.10,
                    "terminal_growth_rate": 0.015
                }
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/valuation/calculate",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   ✅ Valuation calculation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            ev = result.get('dcf_valuation', {}).get('enterprise_value', 0)
            eqv = result.get('dcf_valuation', {}).get('equity_value', 0)
            pps = result.get('dcf_valuation', {}).get('price_per_share', 0)
            print(f"   🏢 Enterprise Value: ${ev:,.0f}M")
            print(f"   💼 Equity Value: ${eqv:,.0f}M")
            print(f"   💵 Price per Share: ${pps:.2f}")
        else:
            print(f"   ❌ Error response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing Complete!")
    print(f"📖 Swagger UI: {base_url}/api/docs")
    print(f"📋 API Spec: {base_url}/static/swagger.json")
    print("=" * 50)

if __name__ == "__main__":
    test_swagger_ui() 