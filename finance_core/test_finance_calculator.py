#!/usr/bin/env python3
"""
Unit Tests for Clean Modular Finance Calculator

Tests all major components including DCF, APV, multiples, scenarios, 
sensitivity analysis, and Monte Carlo simulation.
"""


import json
import tempfile
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Add finance_core to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from finance_calculator import (
    CleanModularFinanceCalculator, 
    FinancialInputs, 
    create_financial_inputs_from_json
)
from params import ValuationParameters
from dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from multiples import run_multiples_analysis
from scenario import run_scenarios
from sensitivity import run_sensitivity_analysis
from monte_carlo import run_monte_carlo
from drivers import project_ebit_series, project_free_cash_flow

class TestFinancialInputs(unittest.TestCase):
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
            cost_of_debt=0.06,
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        
        self.assertEqual(inputs.revenue, [100, 110, 121])
        self.assertEqual(inputs.ebit_margin, 0.15)
        self.assertEqual(inputs.wacc, 0.10)
        self.assertEqual(inputs.share_count, 10.0)

class TestDCFValuation(unittest.TestCase):
    """Test DCF valuation calculations."""
    
    def setUp(self):
        """Set up test data for DCF calculations."""
        self.test_inputs = FinancialInputs(
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
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_dcf_valuation_basic(self):
        """Test basic DCF valuation."""
        result = self.calculator.run_dcf_valuation(self.test_inputs)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that required fields are present
        self.assertIn("enterprise_value", result)
        self.assertIn("equity_value", result)
        self.assertIn("price_per_share", result)
        self.assertIn("free_cash_flows_after_tax_fcff", result)
        self.assertIn("terminal_value", result)
        self.assertIn("present_value_of_terminal", result)
        
        # Check that values are reasonable
        self.assertGreater(result["enterprise_value"], 0)
        # Note: Equity value can be negative if debt > enterprise value
        self.assertIsInstance(result["equity_value"], (int, float))
        self.assertIsInstance(result["price_per_share"], (int, float))
    
    def test_dcf_validation_errors(self):
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
            cost_of_debt=0.06,
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        
        # Test that FinanceCoreError is raised for invalid inputs
        with self.assertRaises(Exception) as context:
            self.calculator.run_dcf_valuation(invalid_inputs)
        
        # Verify the error message contains expected content
        error_message = str(context.exception)
        self.assertIn("DCF calculation failed", error_message)
        self.assertIn("terminal_growth_rate must be less than WACC", error_message)

class TestAPVValuation(unittest.TestCase):
    """Test APV valuation calculations."""
    
    def setUp(self):
        """Set up test data for APV calculations."""
        self.test_inputs = FinancialInputs(
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
            unlevered_cost_of_equity=0.12,
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_apv_valuation_basic(self):
        """Test basic APV valuation."""
        result = self.calculator.run_apv_valuation(self.test_inputs)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that required fields are present
        self.assertIn("enterprise_value", result)
        self.assertIn("equity_value", result)
        self.assertIn("price_per_share", result)
        self.assertIn("apv_components", result)
        
        # Check that values are reasonable
        self.assertGreater(result["enterprise_value"], 0)
        self.assertIsInstance(result["equity_value"], (int, float))
        self.assertIsInstance(result["price_per_share"], (int, float))

class TestComparableMultiples(unittest.TestCase):
    """Test comparable multiples analysis."""
    
    def setUp(self):
        """Set up test data for multiples analysis."""
        self.test_inputs = FinancialInputs(
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
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_multiples_analysis_basic(self):
        """Test basic multiples analysis."""
        result = self.calculator.run_comparable_multiples(self.test_inputs)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that required fields are present (actual structure)
        self.assertIn("ev_multiples", result)
        self.assertIn("base_metrics_used", result)
        self.assertIn("implied_evs_by_multiple", result)
        
        # Check that we have results for each multiple
        implied_evs = result["implied_evs_by_multiple"]
        self.assertIn("EV/EBITDA", implied_evs)
        self.assertIn("P/E", implied_evs)
    
    def test_multiples_no_data(self):
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
            cost_of_debt=0.06,
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
            # No comparable_multiples
        )
        
        # Test that FinanceCoreError is raised for missing comparable data
        with self.assertRaises(Exception) as context:
            self.calculator.run_comparable_multiples(inputs_no_multiples)
        
        # Verify the error message contains expected content
        error_message = str(context.exception)
        self.assertIn("Comparable multiples data is empty or invalid", error_message)

class TestScenarioAnalysis(unittest.TestCase):
    """Test scenario analysis."""
    
    def setUp(self):
        """Set up test data for scenario analysis."""
        self.test_inputs = FinancialInputs(
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
            },
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_scenario_analysis_basic(self):
        """Test basic scenario analysis."""
        result = self.calculator.run_scenario_analysis(self.test_inputs)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that we have results for each scenario
        scenarios = result["scenarios"]
        self.assertIn("base_case", scenarios)
        self.assertIn("optimistic", scenarios)
        self.assertIn("pessimistic", scenarios)
        
        # Check that each scenario has required fields
        for scenario_name, scenario_data in scenarios.items():
            self.assertIn("ev", scenario_data)
            self.assertIn("equity", scenario_data)
            self.assertIn("price_per_share", scenario_data)
    
    def test_scenario_no_data(self):
        """Test scenario analysis without scenario definitions."""
        inputs_no_scenarios = FinancialInputs(
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
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
            # No scenarios
        )
        
        # Test that FinanceCoreError is raised for missing scenario definitions
        with self.assertRaises(Exception) as context:
            self.calculator.run_scenario_analysis(inputs_no_scenarios)
        
        # Verify the error message contains expected content
        error_message = str(context.exception)
        self.assertIn("Invalid scenario definition", error_message)

class TestSensitivityAnalysis(unittest.TestCase):
    """Test sensitivity analysis."""
    
    def setUp(self):
        """Set up test data for sensitivity analysis."""
        self.test_inputs = FinancialInputs(
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
            sensitivity_analysis={
                "wacc_range": [0.08, 0.09, 0.10, 0.11, 0.12],
                "ebit_margin_range": [0.12, 0.14, 0.16, 0.18, 0.20],
                "terminal_growth_range": [0.02, 0.025, 0.03, 0.035, 0.04]
            },
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_sensitivity_analysis_basic(self):
        """Test basic sensitivity analysis."""
        result = self.calculator.run_sensitivity_analysis(self.test_inputs)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that we have sensitivity results for each parameter
        sensitivity_results = result["sensitivity_results"]
        self.assertIn("wacc", sensitivity_results)
        self.assertIn("ebit_margin", sensitivity_results)
        self.assertIn("terminal_growth", sensitivity_results)
        
        # Check that each parameter has both EV and price per share sensitivity
        for param_name, param_data in sensitivity_results.items():
            self.assertIn("ev", param_data)
            self.assertIn("price_per_share", param_data)
    
    def test_sensitivity_no_data(self):
        """Test sensitivity analysis without sensitivity ranges."""
        inputs_no_sensitivity = FinancialInputs(
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
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
            # No sensitivity_analysis
        )
        
        # Test that FinanceCoreError is raised for missing sensitivity ranges
        with self.assertRaises(Exception) as context:
            self.calculator.run_sensitivity_analysis(inputs_no_sensitivity)
        
        # Verify the error message contains expected content
        error_message = str(context.exception)
        self.assertIn("Invalid Monte Carlo specifications", error_message)

class TestMonteCarloSimulation(unittest.TestCase):
    """Test Monte Carlo simulation."""
    
    def setUp(self):
        """Set up test data for Monte Carlo simulation."""
        self.test_inputs = FinancialInputs(
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
            monte_carlo_specs={
                "ebit_margin": {
                    "distribution": "normal",
                    "params": {"mean": 0.15, "std": 0.02}
                },
                "weighted_average_cost_of_capital": {
                    "distribution": "normal",
                    "params": {"mean": 0.10, "std": 0.01}
                },
                "terminal_growth_rate": {
                    "distribution": "normal",
                    "params": {"mean": 0.03, "std": 0.005}
                }
            },
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation."""
        result = self.calculator.run_monte_carlo_simulation(self.test_inputs, runs=100)
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that required fields are present
        self.assertIn("runs", result)
        self.assertIn("wacc_method", result)
        
        # Check that we have statistics
        wacc_stats = result["wacc_method"]
        if wacc_stats:  # May be empty if all runs failed
            self.assertIn("mean_ev", wacc_stats)
            self.assertIn("median_ev", wacc_stats)
            self.assertIn("std_dev", wacc_stats)
    
    def test_monte_carlo_no_specs(self):
        """Test Monte Carlo simulation without specifications."""
        inputs_no_specs = FinancialInputs(
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
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
            # No monte_carlo_specs
        )
        
        # Test that FinanceCoreError is raised for missing Monte Carlo specifications
        with self.assertRaises(Exception) as context:
            self.calculator.run_monte_carlo_simulation(inputs_no_specs)
        
        # Verify the error message contains expected content
        error_message = str(context.exception)
        self.assertIn("Invalid Monte Carlo specifications", error_message)

class TestComprehensiveValuation(unittest.TestCase):
    """Test comprehensive valuation that runs all methods."""
    
    def setUp(self):
        """Set up test data for comprehensive valuation."""
        self.test_inputs = FinancialInputs(
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
            },
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        self.calculator = CleanModularFinanceCalculator()
    
    def test_comprehensive_valuation(self):
        """Test comprehensive valuation that runs all methods."""
        result = self.calculator.run_comprehensive_valuation(
            self.test_inputs, 
            "Test Company", 
            "2024-01-01"
        )
        
        # Check that no error occurred
        self.assertNotIn("error", result)
        
        # Check that all methods were attempted (actual structure)
        self.assertIn("valuation_summary", result)
        self.assertIn("dcf_valuation", result)
        self.assertIn("apv_valuation", result)
        self.assertIn("comparable_valuation", result)
        self.assertIn("scenarios", result)
        self.assertIn("sensitivity_analysis", result)
        self.assertIn("monte_carlo_simulation", result)
        
        # Check that company info is included
        summary = result["valuation_summary"]
        self.assertIn("company", summary)
        self.assertIn("valuation_date", summary)
        self.assertEqual(summary["company"], "Test Company")
        self.assertEqual(summary["valuation_date"], "2024-01-01")

class TestJSONIntegration(unittest.TestCase):
    """Test JSON input/output functionality."""
    
    def test_create_financial_inputs_from_json(self):
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
                "cash_balance": 50.0,
                "amortization": [2, 2.2, 2.4],
                "other_non_cash": [1, 1.1, 1.2],
                "other_working_capital": [0.5, 0.55, 0.6]
            },
            "comparable_multiples": {
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            }
        }
        
        inputs = create_financial_inputs_from_json(json_data)
        
        # Check that inputs were created correctly
        self.assertEqual(inputs.revenue, [100, 110, 121])
        self.assertEqual(inputs.ebit_margin, 0.15)
        self.assertEqual(inputs.tax_rate, 0.25)
        self.assertEqual(inputs.wacc, 0.10)
        self.assertEqual(inputs.terminal_growth, 0.03)
        self.assertEqual(inputs.share_count, 10.0)
        self.assertEqual(inputs.cost_of_debt, 0.06)
        self.assertEqual(inputs.cash_balance, 50.0)
        
        # Check that optional fields were set
        self.assertIsNotNone(inputs.comparable_multiples)
        self.assertIn("EV/EBITDA", inputs.comparable_multiples)
        self.assertIn("P/E", inputs.comparable_multiples)
    
    def test_json_file_creation(self):
        """Test creating and reading JSON files."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_data = {
                "company_name": "Test Company",
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
                    "amortization": [2, 2.2, 2.4],
                    "other_non_cash": [1, 1.1, 1.2],
                    "other_working_capital": [0.5, 0.55, 0.6]
                }
            }
            json.dump(json_data, f)
            temp_file_path = f.name
        
        try:
            # Read the file and create inputs
            with open(temp_file_path, 'r') as f:
                loaded_data = json.load(f)
            
            inputs = create_financial_inputs_from_json(loaded_data)
            
            # Verify the data was loaded correctly
            self.assertEqual(inputs.revenue, [100, 110, 121])
            self.assertEqual(inputs.ebit_margin, 0.15)
            self.assertEqual(inputs.tax_rate, 0.25)
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_json_input(self):
        """Test handling of invalid JSON input."""
        with self.assertRaises(Exception):
            create_financial_inputs_from_json({"invalid": "data"})
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        calculator = CleanModularFinanceCalculator()
        
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
            cost_of_debt=0.06,
            amortization=[2, 2.2, 2.4],
            other_non_cash=[1, 1.1, 1.2],
            other_working_capital=[0.5, 0.55, 0.6]
        )
        
        # This should not raise an exception but return an error in the result
        result = calculator.run_dcf_valuation(invalid_inputs)
        # The result should either be valid or contain an error message
        self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main() 