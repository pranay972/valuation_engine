#!/usr/bin/env python3
"""
Test script to verify all imports work correctly after reorganization
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test backend imports
        print("  Testing backend imports...")
        from backend.core.models.params import ValuationParams
        from backend.core.valuation.dcf import calc_dcf_series, calc_apv
        from backend.core.valuation.monte_carlo import run_monte_carlo
        from backend.core.valuation.sensitivity import run_sensitivity_analysis
        from backend.core.valuation.scenario import run_scenarios
        from backend.core.valuation.multiples import run_multiples_analysis
        from backend.core.financial.drivers import project_ebit, project_fcf
        from backend.core.financial.wacc import calculate_wacc
        from backend.utils.exceptions import ValuationError, InvalidInputError
        from backend.utils.validation import validate_financial_data
        from backend.utils.cache import cached
        from backend.config.logging import get_logger
        from backend.services.valuation_service import valuation_service
        print("  ✅ Backend imports successful")
        
        # Test creating a simple valuation
        print("  Testing basic valuation...")
        params = ValuationParams(
            revenue=[100, 110, 121],
            ebit_margin=0.20,
            capex=[15, 16, 18],
            depreciation=[12, 13, 14],
            nwc_changes=[5, 5, 6],
            terminal_growth=0.02,
            wacc=0.10,
            tax_rate=0.21,
            share_count=100000000
        )
        
        ev, equity, ps = calc_dcf_series(params)
        print(f"  ✅ Basic DCF calculation successful: EV=${ev:,.0f}, Equity=${equity:,.0f}")
        
        # Test service layer
        print("  Testing service layer...")
        input_data = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.20,
            'capex': [15, 16, 18],
            'depreciation': [12, 13, 14],
            'nwc_changes': [5, 5, 6],
            'terminal_growth': 0.02,
            'wacc': 0.10,
            'tax_rate': 0.21,
            'share_count': 100000000
        }
        
        validated_data = valuation_service.validate_input_data(input_data)
        params = valuation_service.create_valuation_params(validated_data)
        results = valuation_service.run_valuation_analyses(params, ["WACC DCF"])
        print(f"  ✅ Service layer test successful: {results}")
        
        print("🎉 All tests passed! The application should run correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 