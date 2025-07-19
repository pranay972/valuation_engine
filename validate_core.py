#!/usr/bin/env python3
"""
Core functionality validation script

This script tests the core valuation functions without requiring
Streamlit or other UI dependencies.
"""

import sys
import traceback

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    
    try:
        from params import ValuationParams
        print("✓ ValuationParams imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ValuationParams: {e}")
        return False
    
    try:
        from drivers import project_ebit, project_fcf
        print("✓ Drivers module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import drivers: {e}")
        return False
    
    try:
        from valuation import calc_dcf_series, calc_apv
        print("✓ Valuation module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import valuation: {e}")
        return False
    
    try:
        from montecarlo import run_monte_carlo
        print("✓ Monte Carlo module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import monte carlo: {e}")
        return False
    
    try:
        from multiples import run_multiples_analysis
        print("✓ Multiples module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import multiples: {e}")
        return False
    
    try:
        from scenario import run_scenarios
        print("✓ Scenario module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import scenario: {e}")
        return False
    
    try:
        from sensitivity import run_sensitivity_analysis
        print("✓ Sensitivity module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import sensitivity: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from params import ValuationParams
        from drivers import project_ebit, project_fcf
        from valuation import calc_dcf_series
        
        # Test ValuationParams creation
        params = ValuationParams(
            revenue=[100.0, 110.0, 120.0],
            ebit_margin=0.20,
            capex=[10.0, 11.0, 12.0],
            depreciation=[5.0, 6.0, 7.0],
            nwc_changes=[2.0, 2.0, 2.0],
            wacc=0.10,
            tax_rate=0.21,
            terminal_growth=0.02,
            share_count=100.0
        )
        print("✓ ValuationParams created successfully")
        
        # Test EBIT projection
        ebit = project_ebit([100.0, 110.0, 120.0], 0.20)
        assert ebit == [20.0, 22.0, 24.0]
        print("✓ EBIT projection works correctly")
        
        # Test FCF projection
        fcf = project_fcf(
            [100.0, 110.0, 120.0],
            [20.0, 22.0, 24.0],
            [10.0, 11.0, 12.0],
            [5.0, 6.0, 7.0],
            [2.0, 2.0, 2.0],
            0.21
        )
        assert len(fcf) == 3
        print("✓ FCF projection works correctly")
        
        # Test DCF calculation
        ev, equity, ps = calc_dcf_series(params)
        assert ev > 0
        assert equity > 0
        assert ps is not None and ps > 0
        print("✓ DCF calculation works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_functionality():
    """Test advanced functionality"""
    print("\nTesting advanced functionality...")
    
    try:
        from params import ValuationParams
        from montecarlo import run_monte_carlo
        from scenario import run_scenarios
        from sensitivity import run_sensitivity_analysis
        
        # Test Monte Carlo
        params = ValuationParams(
            fcf_series=[50.0, 55.0, 60.0],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100.0,
            variable_specs={
                "wacc": {
                    "dist": "normal",
                    "params": {"loc": 0.10, "scale": 0.01}
                }
            }
        )
        
        mc_results = run_monte_carlo(params, runs=5)  # Small number for testing
        assert "WACC" in mc_results
        assert "APV" in mc_results
        print("✓ Monte Carlo simulation works correctly")
        
        # Test scenarios
        params.scenarios = {
            "Base": {},
            "Optimistic": {"wacc": 0.09, "terminal_growth": 0.03},
            "Pessimistic": {"wacc": 0.12, "terminal_growth": 0.01}
        }
        
        scen_results = run_scenarios(params)
        assert not scen_results.empty
        assert "Base" in scen_results.index
        print("✓ Scenario analysis works correctly")
        
        # Test sensitivity
        params.sensitivity_ranges = {
            "wacc": [0.08, 0.09, 0.10, 0.11, 0.12]
        }
        
        sens_results = run_sensitivity_analysis(params)
        assert not sens_results.empty
        assert "wacc" in sens_results.columns
        print("✓ Sensitivity analysis works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main validation function"""
    print("Financial Valuation Engine - Core Validation")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import validation failed")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality validation failed")
        sys.exit(1)
    
    # Test advanced functionality
    if not test_advanced_functionality():
        print("\n❌ Advanced functionality validation failed")
        sys.exit(1)
    
    print("\n✅ All core functionality validated successfully!")
    print("\nThe Financial Valuation Engine is ready for use.")
    print("To run the Streamlit app, install dependencies and run:")
    print("  pip install -r requirements.txt")
    print("  streamlit run app.py")

if __name__ == "__main__":
    main() 