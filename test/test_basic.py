"""
Basic tests for the Financial Valuation Engine

This module contains basic tests to validate core functionality
and ensure the application works correctly.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from backend.core.models.params import ValuationParams
from backend.core.valuation.dcf import calc_dcf_series, calc_apv
from backend.core.financial.drivers import project_ebit, project_fcf, project_revenue
from backend.core.valuation.monte_carlo import run_monte_carlo
from backend.core.valuation.multiples import run_multiples_analysis
from backend.core.valuation.scenario import run_scenarios
from backend.core.valuation.sensitivity import run_sensitivity_analysis

class TestValuationParams:
    """Test the ValuationParams data structure"""
    
    def test_create_basic_params(self):
        """Test creating basic ValuationParams"""
        params = ValuationParams(
            revenue=[100, 110, 120],
            ebit_margin=0.20,
            wacc=0.10,
            tax_rate=0.21,
            terminal_growth=0.02,
            share_count=100
        )
        
        assert params.revenue == [100, 110, 120]
        assert params.ebit_margin == 0.20
        assert params.wacc == 0.10
        assert params.tax_rate == 0.21
        assert params.terminal_growth == 0.02
        assert params.share_count == 100

class TestDrivers:
    """Test the financial projection drivers"""
    
    def test_project_ebit(self):
        """Test EBIT projection"""
        revenue = [100.0, 110.0, 120.0]
        margin = 0.20
        ebit = project_ebit(revenue, margin)
        
        assert ebit == [20.0, 22.0, 24.0]
    
    def test_project_fcf(self):
        """Test FCF projection"""
        revenue = [100.0, 110.0, 120.0]
        ebit = [20.0, 22.0, 24.0]
        capex = [10.0, 11.0, 12.0]
        depreciation = [5.0, 6.0, 7.0]
        nwc_changes = [2.0, 2.0, 2.0]
        tax_rate = 0.21
        
        fcf = project_fcf(revenue, ebit, capex, depreciation, nwc_changes, tax_rate)
        
        # Expected: NOPAT + Depreciation - CapEx - ΔNWC
        # NOPAT = EBIT * (1 - tax_rate)
        expected_nopat = [20 * 0.79, 22 * 0.79, 24 * 0.79]
        expected_fcf = [
            expected_nopat[0] + 5 - 10 - 2,
            expected_nopat[1] + 6 - 11 - 2,
            expected_nopat[2] + 7 - 12 - 2
        ]
        
        assert len(fcf) == 3
        assert all(abs(actual - expected) < 0.01 for actual, expected in zip(fcf, expected_fcf))

class TestValuation:
    """Test core valuation functions"""
    
    def test_calc_dcf_series_direct_fcf(self):
        """Test DCF calculation with direct FCF input"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100
        )
        
        ev, equity, ps = calc_dcf_series(params)
        
        # Basic validation
        assert ev > 0
        assert equity > 0
        assert ps is not None and ps > 0
        assert abs(equity - ev) < 0.01  # No debt in this case
    
    def test_calc_dcf_series_driver_based(self):
        """Test DCF calculation with driver-based input"""
        params = ValuationParams(
            revenue=[100, 110, 120],
            ebit_margin=0.20,
            capex=[10, 11, 12],
            depreciation=[5, 6, 7],
            nwc_changes=[2, 2, 2],
            tax_rate=0.21,
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100
        )
        
        ev, equity, ps = calc_dcf_series(params)
        
        # Basic validation
        assert ev > 0
        assert equity > 0
        assert ps is not None and ps > 0
    
    def test_calc_apv(self):
        """Test APV calculation"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100,
            cost_of_debt=0.05,
            debt_schedule={0: 50, 1: 40, 2: 30}
        )
        
        ev, equity, ps = calc_apv(params)
        
        # Basic validation
        assert ev > 0
        assert equity > 0
        assert ps is not None and ps > 0

class TestMonteCarlo:
    """Test Monte Carlo simulation"""
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100,
            variable_specs={
                "wacc": {
                    "dist": "normal",
                    "params": {"loc": 0.10, "scale": 0.01}
                }
            }
        )
        
        results = run_monte_carlo(params, runs=10)  # Small number for testing
        
        assert "WACC" in results
        assert "APV" in results
        assert len(results["WACC"]) == 10
        assert len(results["APV"]) == 10
        assert "EV" in results["WACC"].columns
        assert "Equity" in results["WACC"].columns
        assert "PS" in results["WACC"].columns

class TestMultiples:
    """Test comparable multiples analysis"""
    
    def test_multiples_analysis(self):
        """Test multiples analysis"""
        params = ValuationParams(
            revenue=[100, 110, 120],
            ebit_margin=0.20,
            capex=[10, 11, 12],
            depreciation=[5, 6, 7],
            nwc_changes=[2, 2, 2],
            tax_rate=0.21
        )
        
        # Create sample comparable companies data
        comps_data = {
            "EV/EBITDA": [15.2, 18.5, 12.8],
            "P/E": [25.1, 28.3, 22.1],
            "EV/FCF": [12.8, 15.2, 10.5],
            "EV/Revenue": [2.1, 2.5, 1.8]
        }
        comps_df = pd.DataFrame(comps_data)
        
        results = run_multiples_analysis(params, comps_df)
        
        assert not results.empty
        assert "Mean Implied EV" in results.columns
        assert "Median Implied EV" in results.columns

class TestScenarios:
    """Test scenario analysis"""
    
    def test_scenario_analysis(self):
        """Test scenario analysis"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100,
            scenarios={
                "Base": {},
                "Optimistic": {"wacc": 0.09, "terminal_growth": 0.03},
                "Pessimistic": {"wacc": 0.12, "terminal_growth": 0.01}
            }
        )
        
        results = run_scenarios(params)
        
        assert not results.empty
        assert "Base" in results.index
        assert "Optimistic" in results.index
        assert "Pessimistic" in results.index
        assert "EV" in results.columns

class TestSensitivity:
    """Test sensitivity analysis"""
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100,
            sensitivity_ranges={
                "wacc": [0.08, 0.09, 0.10, 0.11, 0.12],
                "terminal_growth": [0.01, 0.015, 0.02, 0.025, 0.03]
            }
        )
        
        results = run_sensitivity_analysis(params)
        
        assert not results.empty
        assert "wacc" in results.columns
        assert "terminal_growth" in results.columns
        assert len(results) == 5  # Should have 5 rows for the test values

class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_invalid_terminal_growth(self):
        """Test error when terminal growth >= WACC"""
        params = ValuationParams(
            fcf_series=[50, 55, 60],
            wacc=0.10,
            terminal_growth=0.12,  # Greater than WACC
            share_count=100
        )
        
        with pytest.raises(ValueError, match="Terminal growth rate.*must be less than WACC"):
            calc_dcf_series(params)
    
    def test_empty_fcf_series(self):
        """Test error when no FCF series is provided"""
        params = ValuationParams(
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100
        )
        
        with pytest.raises(ValueError, match="No FCF series available"):
            calc_dcf_series(params)
    
    def test_invalid_ebit_margin(self):
        """Test error when EBIT margin is invalid"""
        with pytest.raises(ValueError, match="EBIT margin.*must be between 0% and 100%"):
            project_ebit([100, 110], 1.5)  # Margin > 100%

if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"]) 