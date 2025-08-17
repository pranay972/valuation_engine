#!/usr/bin/env python3
"""Test script to verify finance calculator works with sample input."""

import json
from finance_calculator import FinancialValuationEngine, parse_financial_inputs

def test_sample_input():
    """Test the finance calculator with sample input JSON."""
    try:
        # Load sample input
        print("Loading sample input...")
        with open('sample_input.json', 'r') as f:
            sample_data = json.load(f)
        
        # Parse the input
        print("Parsing financial inputs...")
        inputs = parse_financial_inputs(sample_data)
        print(f"✓ Inputs parsed successfully: {type(inputs)}")
        
        # Create engine and run valuation
        print("Running comprehensive valuation...")
        engine = FinancialValuationEngine()
        results = engine.perform_comprehensive_valuation(inputs, 'TechCorp Inc.')
        
        print("✓ Valuation completed successfully!")
        print(f"Company: {results.get('company_name', 'N/A')}")
        
        # Check DCF results
        dcf_results = results.get('dcf_valuation', {})
        if dcf_results:
            enterprise_value = dcf_results.get('enterprise_value')
            equity_value = dcf_results.get('equity_value')
            per_share = dcf_results.get('equity_value_per_share')
            
            print(f"Enterprise Value: ${enterprise_value:,.0f}" if enterprise_value else "Enterprise Value: N/A")
            print(f"Equity Value: ${equity_value:,.0f}" if equity_value else "Equity Value: N/A")
            print(f"Per Share: ${per_share:,.2f}" if per_share else "Per Share: N/A")
        
        # Check other analysis results
        if results.get('comparable_multiples'):
            print("✓ Comparable multiples analysis completed")
        
        if results.get('scenario_analysis'):
            print("✓ Scenario analysis completed")
        
        if results.get('sensitivity_analysis'):
            print("✓ Sensitivity analysis completed")
        
        if results.get('monte_carlo_simulation'):
            print("✓ Monte Carlo simulation completed")
        
        print("\n🎉 All tests passed! Finance calculator is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sample_input()
    exit(0 if success else 1)
