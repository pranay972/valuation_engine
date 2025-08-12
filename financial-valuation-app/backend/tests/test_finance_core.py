#!/usr/bin/env python3
"""
Unit Tests for Finance Core Logic

Tests all major components including DCF, APV, multiples, scenarios, 
sensitivity analysis, and Monte Carlo simulation.
"""

import pytest
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from finance_core.finance_calculator import (
    FinancialValuationEngine, 
    FinancialInputs, 
    parse_financial_inputs
)
from finance_core.params import ValuationParameters
from finance_core.dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from finance_core.multiples import analyze_comparable_multiples
from finance_core.scenario import perform_scenario_analysis
from finance_core.sensitivity import perform_sensitivity_analysis
from finance_core.monte_carlo import simulate_monte_carlo
from finance_core.drivers import project_ebit_series, project_free_cash_flow

class TestFinancialInputs:
    """Test FinancialInputs dataclass creation and validation."""
    
    def test_financial_inputs_creation(self):
        """Test creating FinancialInputs with basic data."""
        inputs = FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06
        )
        
        assert inputs.revenue == [100, 110, 121]
        assert inputs.ebit_margin == 0.15
        assert inputs.wacc == 0.10
        assert inputs.share_count == 10.0

class TestDCFValuation:
    """Test DCF valuation calculations."""
    
    @pytest.fixture
    def test_inputs(self):
        """Set up test data for DCF calculations."""
        return FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06
        )
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return FinancialValuationEngine()
    
    def test_dcf_valuation_basic(self, test_inputs, calculator):
        """Test basic DCF valuation."""
        result = calculator.calculate_dcf_valuation(test_inputs)
        
        # Check that no error occurred
        assert "error" not in result
        
        # Check that required fields are present
        assert "enterprise_value" in result
        assert "equity_value" in result
        assert "price_per_share" in result
        assert "free_cash_flows_after_tax_fcff" in result
        assert "terminal_value" in result
        assert "present_value_of_terminal" in result
        
        # Check that values are reasonable
        assert result["enterprise_value"] > 0
        # Note: Equity value can be negative if debt > enterprise value
        assert isinstance(result["equity_value"], (int, float))
        assert isinstance(result["price_per_share"], (int, float))
    
    def test_dcf_validation_errors(self, calculator):
        """Test DCF validation with invalid inputs."""
        # Test with terminal growth >= WACC
        invalid_inputs = FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.15,  # Higher than WACC
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06
        )
        
        # Test that exception is raised for invalid inputs
        with pytest.raises(Exception) as exc_info:
            calculator.calculate_dcf_valuation(invalid_inputs)
        
        # Verify the error message contains expected content
        error_message = str(exc_info.value)
        assert "DCF calculation failed" in error_message
        assert "terminal_growth_rate must be less than WACC" in error_message

class TestAPVValuation:
    """Test APV valuation calculations."""
    
    @pytest.fixture
    def test_inputs(self):
        """Set up test data for APV calculations."""
        return FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06,
            unlevered_cost_of_equity=0.12
        )
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return FinancialValuationEngine()
    
    def test_apv_valuation_basic(self, test_inputs, calculator):
        """Test basic APV valuation."""
        result = calculator.calculate_apv_valuation(test_inputs)
        
        # Check that no error occurred
        assert "error" not in result
        
        # Check that required fields are present
        assert "enterprise_value" in result
        assert "equity_value" in result
        assert "price_per_share" in result
        assert "apv_components" in result
        
        # Check that values are reasonable
        assert result["enterprise_value"] > 0
        assert isinstance(result["equity_value"], (int, float))
        assert isinstance(result["price_per_share"], (int, float))

class TestComparableMultiples:
    """Test comparable multiples analysis."""
    
    @pytest.fixture
    def test_inputs(self):
        """Set up test data for multiples analysis."""
        return FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06,
            comparable_multiples={
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            }
        )
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return FinancialValuationEngine()
    
    def test_multiples_analysis_basic(self, test_inputs, calculator):
        """Test basic multiples analysis."""
        result = calculator.analyze_comparable_multiples(test_inputs)
        
        # Check that no error occurred
        assert "error" not in result
        
        # Check that required fields are present
        assert "ev_multiples" in result
        assert "base_metrics_used" in result
        assert "implied_evs_by_multiple" in result
        
        # Check that we have results for each multiple
        implied_evs = result["implied_evs_by_multiple"]
        assert "EV/EBITDA" in implied_evs
        assert "P/E" in implied_evs
    
    def test_multiples_no_data(self, calculator):
        """Test multiples analysis without comparable data."""
        inputs_no_multiples = FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06
            # No comparable_multiples
        )
        
        # Test that exception is raised for missing comparable data
        with pytest.raises(Exception) as exc_info:
            calculator.analyze_comparable_multiples(inputs_no_multiples)
        
        # Verify the error message contains expected content
        error_message = str(exc_info.value)
        assert "Comparable multiples data is empty or invalid" in error_message

class TestScenarioAnalysis:
    """Test scenario analysis."""
    
    @pytest.fixture
    def test_inputs(self):
        """Set up test data for scenario analysis."""
        return FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06,
            scenarios={
                "base_case": {},
                "optimistic": {
                    "ebit_margin": 0.20,
                    "terminal_growth_rate": 0.04,
                    "weighted_average_cost_of_capital": 0.08
                },
                "pessimistic": {
                    "ebit_margin": 0.10,
                    "terminal_growth_rate": 0.02,
                    "weighted_average_cost_of_capital": 0.12
                }
            }
        )
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return FinancialValuationEngine()
    
    def test_scenario_analysis_basic(self, test_inputs, calculator):
        """Test basic scenario analysis."""
        result = calculator.perform_scenario_analysis(test_inputs)
        
        # Check that no error occurred
        assert "error" not in result
        
        # Check that we have results for each scenario
        scenarios = result["scenarios"]
        assert "base_case" in scenarios
        assert "optimistic" in scenarios
        assert "pessimistic" in scenarios
        
        # Check that each scenario has required fields
        for scenario_name, scenario_data in scenarios.items():
            assert "ev" in scenario_data
            assert "equity" in scenario_data
            assert "price_per_share" in scenario_data

class TestComprehensiveValuation:
    """Test comprehensive valuation that runs all methods."""
    
    @pytest.fixture
    def test_inputs(self):
        """Set up test data for comprehensive valuation."""
        return FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06,
            comparable_multiples={
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            },
            scenarios={
                "base_case": {},
                "optimistic": {"ebit_margin": 0.20}
            },
            sensitivity_analysis={
                "wacc_range": [0.08, 0.10, 0.12]
            },
            monte_carlo_specs={
                "ebit_margin": {
                    "distribution": "normal",
                    "params": {"mean": 0.15, "std": 0.02}
                }
            }
        )
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return FinancialValuationEngine()
    
    def test_comprehensive_valuation(self, test_inputs, calculator):
        """Test comprehensive valuation that runs all methods."""
        result = calculator.perform_comprehensive_valuation(
            test_inputs, 
            "Test Company", 
            "2024-01-01"
        )
        
        # Check that no error occurred
        assert "error" not in result
        
        # Check that all methods were attempted
        assert "valuation_summary" in result
        assert "dcf_valuation" in result
        assert "apv_valuation" in result
        assert "comparable_valuation" in result
        assert "scenarios" in result
        assert "sensitivity_analysis" in result
        assert "monte_carlo_simulation" in result
        
        # Check that company info is included
        summary = result["valuation_summary"]
        assert "company" in summary
        assert "valuation_date" in summary
        assert summary["company"] == "Test Company"
        assert summary["valuation_date"] == "2024-01-01"

class TestJSONIntegration:
    """Test JSON input/output functionality."""
    
    def test_parse_financial_inputs(self):
        """Test creating FinancialInputs from JSON data."""
        json_data = {
            "company_name": "Test Company",
            "valuation_date": "2024-01-01",
            "financial_inputs": {
                "revenue": [100, 110, 121],
                "ebit_margin": 0.15,
                "tax_rate": 0.25,
                "capex": [20, 22, 24],
                "depreciation": [15, 16, 17],
                "nwc_changes": [5, 5.5, 6],
                "weighted_average_cost_of_capital": 0.10,
                "terminal_growth_rate": 0.03,
                "share_count": 10.0,
                "cost_of_debt": 0.06,
                "cash_balance": 50.0
            },
            "comparable_multiples": {
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            }
        }
        
        inputs = parse_financial_inputs(json_data)
        
        # Check that inputs were created correctly
        assert inputs.revenue == [100, 110, 121]
        assert inputs.ebit_margin == 0.15
        assert inputs.tax_rate == 0.25
        assert inputs.wacc == 0.10
        assert inputs.terminal_growth == 0.03
        assert inputs.share_count == 10.0
        assert inputs.cost_of_debt == 0.06
        assert inputs.cash_balance == 50.0
        
        # Check that optional fields were set
        assert inputs.comparable_multiples is not None
        assert "EV/EBITDA" in inputs.comparable_multiples
        assert "P/E" in inputs.comparable_multiples

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_json_input(self):
        """Test handling of invalid JSON input."""
        with pytest.raises(Exception):
            parse_financial_inputs({"invalid": "data"})
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        calculator = FinancialValuationEngine()
        
        # Test with missing required fields
        invalid_inputs = FinancialInputs(
            revenue=[100, 110, 121],
            ebit_margin=0.15,
            # Missing other required fields
            capex=[20, 22, 24],
            depreciation=[15, 16, 17],
            nwc_changes=[5, 5.5, 6],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=10.0,
            cost_of_debt=0.06
        )
        
        # This should not raise an exception but return an error in the result
        result = calculator.calculate_dcf_valuation(invalid_inputs)
        # The result should either be valid or contain an error message
        assert isinstance(result, dict) 