#!/usr/bin/env python3
"""
Simple test script for the valuation API.
"""

import requests
import json
import time

def test_api():
    """Test the valuation API endpoints."""
    
    base_url = "http://localhost:5001"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 5001.")
        return
    
    # Test sample data endpoint
    print("\nTesting sample data endpoint...")
    try:
        response = requests.get(f"{base_url}/api/valuation/sample")
        print(f"Sample data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Company: {data.get('company_name')}")
            print(f"Revenue: {data.get('financial_inputs', {}).get('revenue', [])[:2]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test valuation calculation
    print("\nTesting valuation calculation...")
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
            "terminal_growth": 0.025,
            "wacc": 0.10,
            "share_count": 10.0,
            "cost_of_debt": 0.06
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/valuation/calculate",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Valuation calculation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Enterprise Value: ${result.get('dcf_valuation', {}).get('enterprise_value', 0):,.0f}")
            print(f"Equity Value: ${result.get('dcf_valuation', {}).get('equity_value', 0):,.0f}")
            print(f"Price per Share: ${result.get('dcf_valuation', {}).get('price_per_share', 0):.2f}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Valuation API Backend")
    print("=" * 40)
    test_api() 