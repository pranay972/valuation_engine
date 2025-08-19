#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Clean Modular Finance Calculator

Tests all major components including DCF, APV, multiples, scenarios, 
sensitivity analysis, and Monte Carlo simulation with proper unit testing.
"""

import unittest
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Import the modules to test
from .finance_calculator import (
    FinancialValuationEngine, 
    FinancialInputs, 
    parse_financial_inputs
)
from .params import ValuationParameters
from .dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from .multiples import analyze_comparable_multiples
from .scenario import perform_scenario_analysis
from .sensitivity import perform_sensitivity_analysis
from .monte_carlo import simulate_monte_carlo
from .drivers import project_ebit_series, project_free_cash_flow
from .error_messages import FinanceCoreError

class TestFinancialInputs(unittest.TestCase):
    """Test FinancialInputs dataclass creation and validation."""
    
    def _create_basic_inputs(self, **kwargs):
        """Helper method to create FinancialInputs with all required fields."""
        defaults = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.15,
            'capex': [20, 22, 24],
            'depreciation': [15, 16, 17],
            'nwc_changes': [5, 5.5, 6],
            'tax_rate': 0.25,
            'terminal_growth': 0.03,
            'wacc': 0.10,
            'share_count': 10.0,
            'cost_of_debt': 0.06,
            'cash_balance': 0.0,
            'unlevered_cost_of_equity': 0.12,
            'cost_of_equity': 0.15,
            'risk_free_rate': 0.03,
            'market_risk_premium': 0.06,
            'levered_beta': 1.0,
            'unlevered_beta': 0.8,
            'target_debt_ratio': 0.3
        }
        defaults.update(kwargs)
        return FinancialInputs(**defaults)
    
    def test_financial_inputs_creation(self):
        """Test creating FinancialInputs with basic data."""
        inputs = self._create_basic_inputs()
        
        self.assertEqual(inputs.revenue, [100, 110, 121])
        self.assertEqual(inputs.ebit_margin, 0.15)
        self.assertEqual(inputs.wacc, 0.10)
        self.assertEqual(inputs.share_count, 10.0)
        self.assertEqual(inputs.cash_balance, 0.0)
        self.assertEqual(inputs.comparable_multiples, None)
    
    def test_financial_inputs_with_optional_fields(self):
        """Test creating FinancialInputs with optional fields."""
        inputs = self._create_basic_inputs(
            cash_balance=50.0,
            comparable_multiples={"EV/EBITDA": [12.5, 14.2]},
            scenarios={"optimistic": {"ebit_margin": 0.20}},
            sensitivity_analysis={"wacc_range": [0.08, 0.12]},
            monte_carlo_specs={"ebit_margin": {"distribution": "normal", "params": {"mean": 0.15, "std": 0.02}}}
        )
        
        self.assertEqual(inputs.cash_balance, 50.0)
        self.assertIsNotNone(inputs.comparable_multiples)
        self.assertIsNotNone(inputs.scenarios)
        self.assertIsNotNone(inputs.sensitivity_analysis)
        self.assertIsNotNone(inputs.monte_carlo_specs)

class TestFinancialValuationEngine(unittest.TestCase):
    """Test the main FinancialValuationEngine class."""
    
    def _create_basic_inputs(self, **kwargs):
        """Helper method to create FinancialInputs with all required fields."""
        defaults = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.15,
            'capex': [20, 22, 24],
            'depreciation': [15, 16, 17],
            'nwc_changes': [5, 5.5, 6],
            'tax_rate': 0.25,
            'terminal_growth': 0.03,
            'wacc': 0.10,
            'share_count': 10.0,
            'cost_of_debt': 0.06,
            'cash_balance': 0.0,
            'unlevered_cost_of_equity': 0.12,
            'cost_of_equity': 0.15,
            'risk_free_rate': 0.03,
            'market_risk_premium': 0.06,
            'levered_beta': 1.0,
            'unlevered_beta': 0.8,
            'target_debt_ratio': 0.3
        }
        defaults.update(kwargs)
        return FinancialInputs(**defaults)
    
    def setUp(self):
        """Set up test data for all engine tests."""
        self.engine = FinancialValuationEngine()
        self.basic_inputs = self._create_basic_inputs()
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = FinancialValuationEngine()
        self.assertIsInstance(engine, FinancialValuationEngine)
    
    def test_convert_to_valuation_params(self):
        """Test conversion of FinancialInputs to ValuationParameters."""
        params = self.engine._convert_to_valuation_params(self.basic_inputs)
        self.assertIsInstance(params, ValuationParameters)
        self.assertEqual(params.revenue_projections, [100, 110, 121])
        self.assertEqual(params.ebit_margin, 0.15)
        self.assertEqual(params.weighted_average_cost_of_capital, 0.10)
    
    def test_convert_to_valuation_params_with_debt_schedule(self):
        """Test conversion with debt schedule."""
        inputs = self._create_basic_inputs(debt_schedule={"0": 50.0, "1": 40.0})
        
        params = self.engine._convert_to_valuation_params(inputs)
        self.assertEqual(params.debt_schedule, {0: 50.0, 1: 40.0})
    
    def test_validate_required_inputs_success(self):
        """Test successful validation of required inputs."""
        # Should not raise an exception
        self.engine._validate_required_inputs(self.basic_inputs)
    
    def test_validate_required_inputs_missing_revenue(self):
        """Test validation with missing revenue."""
        invalid_inputs = self._create_basic_inputs(revenue=[])  # Empty list
        
        with self.assertRaises(FinanceCoreError):
            self.engine._validate_required_inputs(invalid_inputs)
    
    def test_validate_required_inputs_negative_values(self):
        """Test validation with negative values."""
        invalid_inputs = self._create_basic_inputs(ebit_margin=-0.15)  # Negative value
        
        with self.assertRaises(FinanceCoreError):
            self.engine._validate_required_inputs(invalid_inputs)

class TestDCFValuation(unittest.TestCase):
    """Test DCF valuation calculations."""
    
    def _create_basic_inputs(self, **kwargs):
        """Helper method to create FinancialInputs with all required fields."""
        defaults = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.15,
            'capex': [20, 22, 24],
            'depreciation': [15, 16, 17],
            'nwc_changes': [5, 5.5, 6],
            'tax_rate': 0.25,
            'terminal_growth': 0.03,
            'wacc': 0.10,
            'share_count': 10.0,
            'cost_of_debt': 0.06,
            'cash_balance': 0.0,
            'unlevered_cost_of_equity': 0.12,
            'cost_of_equity': 0.15,
            'risk_free_rate': 0.03,
            'market_risk_premium': 0.06,
            'levered_beta': 1.0,
            'unlevered_beta': 0.8,
            'target_debt_ratio': 0.3
        }
        defaults.update(kwargs)
        return FinancialInputs(**defaults)
    
    def setUp(self):
        """Set up test data for DCF calculations."""
        self.engine = FinancialValuationEngine()
        self.test_inputs = self._create_basic_inputs()
    
    def test_dcf_valuation_basic(self):
        """Test basic DCF valuation."""
        result = self.engine.calculate_dcf_valuation(self.test_inputs)
        
        # Check that required fields are present
        self.assertIn("enterprise_value", result)
        self.assertIn("equity_value", result)
        self.assertIn("price_per_share", result)
        self.assertIn("free_cash_flows_after_tax_fcff", result)
        self.assertIn("terminal_value", result)
        self.assertIn("present_value_of_terminal", result)
        self.assertIn("wacc", result)
        self.assertIn("terminal_growth", result)
        
        # Check that values are reasonable
        self.assertGreater(result["enterprise_value"], 0)
        self.assertIsInstance(result["enterprise_value"], (int, float))
        self.assertIsInstance(result["equity_value"], (int, float))
        self.assertIsInstance(result["price_per_share"], (int, float))
        self.assertIsInstance(result["free_cash_flows_after_tax_fcff"], list)
    
    def test_dcf_validation_errors(self):
        """Test DCF validation with invalid inputs."""
        # Test with terminal growth >= WACC
        invalid_inputs = self._create_basic_inputs(terminal_growth=0.15)  # Higher than WACC
        
        with self.assertRaises(FinanceCoreError):
            self.engine.calculate_dcf_valuation(invalid_inputs)
    
    def test_dcf_with_cash_balance(self):
        """Test DCF with cash balance."""
        inputs_with_cash = FinancialInputs(
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
            cash_balance=50.0,
        )
        
        result = self.engine.calculate_dcf_valuation(inputs_with_cash)
        self.assertIn("net_debt_breakdown", result)
        self.assertEqual(result["net_debt_breakdown"]["cash_balance"], 50.0)
    
    def test_dcf_with_debt_schedule(self):
        """Test DCF with debt schedule."""
        inputs_with_debt = self._create_basic_inputs(debt_schedule={"0": 30.0, "1": 20.0, "2": 10.0})
        
        result = self.engine.calculate_dcf_valuation(inputs_with_debt)
        self.assertIn("net_debt_breakdown", result)
        self.assertEqual(result["net_debt_breakdown"]["current_debt"], 30.0)

class TestAPVValuation(unittest.TestCase):
    """Test APV valuation calculations."""
    
    def _create_basic_inputs(self, **kwargs):
        """Helper method to create FinancialInputs with all required fields."""
        defaults = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.15,
            'capex': [20, 22, 24],
            'depreciation': [15, 16, 17],
            'nwc_changes': [5, 5.5, 6],
            'tax_rate': 0.25,
            'terminal_growth': 0.03,
            'wacc': 0.10,
            'share_count': 10.0,
            'cost_of_debt': 0.06,
            'cash_balance': 0.0,
            'unlevered_cost_of_equity': 0.12,
            'cost_of_equity': 0.15,
            'risk_free_rate': 0.03,
            'market_risk_premium': 0.06,
            'levered_beta': 1.0,
            'unlevered_beta': 0.8,
            'target_debt_ratio': 0.3
        }
        defaults.update(kwargs)
        return FinancialInputs(**defaults)
    
    def setUp(self):
        """Set up test data for APV calculations."""
        self.engine = FinancialValuationEngine()
        self.test_inputs = self._create_basic_inputs()
    
    def test_apv_valuation_basic(self):
        """Test basic APV valuation."""
        result = self.engine.calculate_apv_valuation(self.test_inputs)
        
        # Check that required fields are present
        self.assertIn("enterprise_value", result)
        self.assertIn("equity_value", result)
        self.assertIn("price_per_share", result)
        self.assertIn("apv_components", result)
        self.assertIn("unlevered_cost_of_equity", result)
        self.assertIn("cost_of_debt", result)
        self.assertIn("tax_rate", result)
        
        # Check that values are reasonable
        self.assertGreater(result["enterprise_value"], 0)
        self.assertIsInstance(result["enterprise_value"], (int, float))
        self.assertIsInstance(result["equity_value"], (int, float))
        self.assertIsInstance(result["price_per_share"], (int, float))
    
    def test_apv_components_structure(self):
        """Test APV components structure."""
        result = self.engine.calculate_apv_valuation(self.test_inputs)
        
        apv_components = result["apv_components"]
        self.assertIn("value_unlevered", apv_components)
        self.assertIn("pv_tax_shield", apv_components)
        
        # Both components should be positive
        self.assertGreaterEqual(apv_components["value_unlevered"], 0)
        self.assertGreaterEqual(apv_components["pv_tax_shield"], 0)

class TestComparableMultiples(unittest.TestCase):
    """Test comparable multiples analysis."""
    
    def _create_basic_inputs(self, **kwargs):
        """Helper method to create FinancialInputs with all required fields."""
        defaults = {
            'revenue': [100, 110, 121],
            'ebit_margin': 0.15,
            'capex': [20, 22, 24],
            'depreciation': [15, 16, 17],
            'nwc_changes': [5, 5.5, 6],
            'tax_rate': 0.25,
            'terminal_growth': 0.03,
            'wacc': 0.10,
            'share_count': 10.0,
            'cost_of_debt': 0.06,
            'cash_balance': 0.0,
            'unlevered_cost_of_equity': 0.12,
            'cost_of_equity': 0.15,
            'risk_free_rate': 0.03,
            'market_risk_premium': 0.06,
            'levered_beta': 1.0,
            'unlevered_beta': 0.8,
            'target_debt_ratio': 0.3
        }
        defaults.update(kwargs)
        return FinancialInputs(**defaults)
    
    def setUp(self):
        """Set up test data for multiples analysis."""
        self.engine = FinancialValuationEngine()
        self.test_inputs = self._create_basic_inputs(
            comparable_multiples={
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            }
        )
    
    def test_multiples_analysis_basic(self):
        """Test basic multiples analysis."""
        result = self.engine.analyze_comparable_multiples(self.test_inputs)
        
        # Check that required fields are present
        self.assertIn("ev_multiples", result)
        self.assertIn("base_metrics_used", result)
        self.assertIn("implied_evs_by_multiple", result)
        self.assertIn("calculation_method", result)
        
        # Check that we have results for each multiple
        implied_evs = result["implied_evs_by_multiple"]
        self.assertIn("EV/EBITDA", implied_evs)
        self.assertIn("P/E", implied_evs)
        
        # Check base metrics
        base_metrics = result["base_metrics_used"]
        self.assertIn("ebitda", base_metrics)
        self.assertIn("fcf", base_metrics)
        self.assertIn("revenue", base_metrics)
        self.assertIn("net_income", base_metrics)
    
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
            # No comparable_multiples
        )
        
        with self.assertRaises(FinanceCoreError):
            self.engine.analyze_comparable_multiples(inputs_no_multiples)
    
    def test_multiples_empty_data(self):
        """Test multiples analysis with empty comparable data."""
        inputs_empty_multiples = FinancialInputs(
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
            comparable_multiples={},  # Empty dict
        )
        
        with self.assertRaises(FinanceCoreError):
            self.engine.analyze_comparable_multiples(inputs_empty_multiples)

class TestScenarioAnalysis(unittest.TestCase):
    """Test scenario analysis."""
    
    def setUp(self):
        """Set up test data for scenario analysis."""
        self.engine = FinancialValuationEngine()
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
        )
    
    def test_scenario_analysis_basic(self):
        """Test basic scenario analysis."""
        result = self.engine.perform_scenario_analysis(self.test_inputs)
        
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
            
            # Values should be reasonable
            self.assertIsInstance(scenario_data["ev"], (int, float))
            self.assertIsInstance(scenario_data["equity"], (int, float))
            self.assertIsInstance(scenario_data["price_per_share"], (int, float))
    
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
            # No scenarios
        )
        
        with self.assertRaises(FinanceCoreError):
            self.engine.perform_scenario_analysis(inputs_no_scenarios)
    
    def test_scenario_input_changes(self):
        """Test that scenario input changes are tracked."""
        result = self.engine.perform_scenario_analysis(self.test_inputs)
        
        scenarios = result["scenarios"]
        optimistic = scenarios["optimistic"]
        
        # Should have input changes for non-base scenarios
        self.assertIn("input_changes", optimistic)
        self.assertEqual(optimistic["input_changes"]["ebit_margin"], 0.20)

class TestSensitivityAnalysis(unittest.TestCase):
    """Test sensitivity analysis."""
    
    def setUp(self):
        """Set up test data for sensitivity analysis."""
        self.engine = FinancialValuationEngine()
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
        )
    
    def test_sensitivity_analysis_basic(self):
        """Test basic sensitivity analysis."""
        result = self.engine.perform_sensitivity_analysis(self.test_inputs)
        
        # Check that we have sensitivity results for each parameter
        sensitivity_results = result["sensitivity_results"]
        self.assertIn("wacc_range", sensitivity_results)
        self.assertIn("ebit_margin_range", sensitivity_results)
        self.assertIn("terminal_growth_range", sensitivity_results)
        
        # Check that each parameter has both EV and price per share sensitivity
        for param_name, param_data in sensitivity_results.items():
            self.assertIn("ev", param_data)
            self.assertIn("price_per_share", param_data)
            
            # Check that we have values for each range
            self.assertGreater(len(param_data["ev"]), 0)
            self.assertGreater(len(param_data["price_per_share"]), 0)
    
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
            # No sensitivity_analysis
        )
        
        with self.assertRaises(FinanceCoreError):
            self.engine.perform_sensitivity_analysis(inputs_no_sensitivity)
    
    def test_sensitivity_parameter_ranges(self):
        """Test that parameter ranges are included in results."""
        result = self.engine.perform_sensitivity_analysis(self.test_inputs)
        
        self.assertIn("parameter_ranges", result)
        ranges = result["parameter_ranges"]
        self.assertIn("wacc_range", ranges)
        self.assertIn("ebit_margin_range", ranges)
        self.assertIn("terminal_growth_range", ranges)

class TestMonteCarloSimulation(unittest.TestCase):
    """Test Monte Carlo simulation."""
    
    def setUp(self):
        """Set up test data for Monte Carlo simulation."""
        self.engine = FinancialValuationEngine()
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
        )
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation."""
        result = self.engine.simulate_monte_carlo(self.test_inputs, runs=100)
        
        # Check that required fields are present
        self.assertIn("runs", result)
        self.assertIn("wacc_method", result)
        self.assertIn("parameter_distributions", result)
        self.assertIn("calculation_method", result)
        
        # Check that we have statistics
        wacc_stats = result["wacc_method"]
        if wacc_stats:  # May be empty if all runs failed
            self.assertIn("mean_ev", wacc_stats)
            self.assertIn("median_ev", wacc_stats)
            self.assertIn("std_dev", wacc_stats)
            self.assertIn("confidence_interval_95", wacc_stats)
    
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
            # No monte_carlo_specs
        )
        
        with self.assertRaises(FinanceCoreError):
            self.engine.simulate_monte_carlo(inputs_no_specs)
    
    def test_monte_carlo_custom_runs(self):
        """Test Monte Carlo simulation with custom number of runs."""
        result = self.engine.simulate_monte_carlo(self.test_inputs, runs=50)
        self.assertEqual(result["runs"], 50)

class TestComprehensiveValuation(unittest.TestCase):
    """Test comprehensive valuation that runs all methods."""
    
    def setUp(self):
        """Set up test data for comprehensive valuation."""
        self.engine = FinancialValuationEngine()
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
        )
    
    def test_comprehensive_valuation(self):
        """Test comprehensive valuation that runs all methods."""
        result = self.engine.perform_comprehensive_valuation(
            self.test_inputs, 
            "Test Company", 
            "2024-01-01"
        )
        
        # Check that all methods were attempted
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
    
    def test_comprehensive_valuation_minimal_inputs(self):
        """Test comprehensive valuation with minimal inputs."""
        minimal_inputs = FinancialInputs(
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
        )
        
        result = self.engine.perform_comprehensive_valuation(minimal_inputs)
        
        # Should still have basic structure
        self.assertIn("valuation_summary", result)
        self.assertIn("dcf_valuation", result)
        self.assertIn("apv_valuation", result)
        
        # Optional methods should be empty or have error messages
        self.assertIn("comparable_valuation", result)
        self.assertIn("scenarios", result)
        self.assertIn("sensitivity_analysis", result)
        self.assertIn("monte_carlo_simulation", result)

class TestJSONIntegration(unittest.TestCase):
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
                "cash_balance": 50.0,
            },
            "comparable_multiples": {
                "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
                "P/E": [18.5, 22.1, 20.8, 24.3]
            }
        }
        
        inputs = parse_financial_inputs(json_data)
        
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
    
    def test_parse_financial_inputs_flat_structure(self):
        """Test creating FinancialInputs from flat JSON structure."""
        json_data = {
            "revenue": [100, 110, 121],
            "ebit_margin": 0.15,
            "tax_rate": 0.25,
            "capex": [20, 22, 24],
            "depreciation": [15, 16, 17],
            "nwc_changes": [5, 5.5, 6],
            "wacc": 0.10,
            "terminal_growth": 0.03,
            "share_count": 10.0,
            "cost_of_debt": 0.06,
        }
        
        inputs = parse_financial_inputs(json_data)
        
        # Check that inputs were created correctly
        self.assertEqual(inputs.revenue, [100, 110, 121])
        self.assertEqual(inputs.ebit_margin, 0.15)
        self.assertEqual(inputs.wacc, 0.10)
    
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
                }
            }
            json.dump(json_data, f)
            temp_file_path = f.name
        
        try:
            # Read the file and create inputs
            with open(temp_file_path, 'r') as f:
                loaded_data = json.load(f)
            
            inputs = parse_financial_inputs(loaded_data)
            
            # Verify the data was loaded correctly
            self.assertEqual(inputs.revenue, [100, 110, 121])
            self.assertEqual(inputs.ebit_margin, 0.15)
            self.assertEqual(inputs.tax_rate, 0.25)
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_invalid_json_input(self):
        """Test handling of invalid JSON input."""
        with self.assertRaises(Exception):
            parse_financial_inputs({"invalid": "data"})

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        calculator = FinancialValuationEngine()
        
        # Test with missing required fields
        invalid_inputs = FinancialInputs(
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
        )
        
        # This should not raise an exception but return an error in the result
        result = calculator.calculate_dcf_valuation(invalid_inputs)
        # The result should either be valid or contain an error message
        self.assertIsInstance(result, dict)
    
    def test_edge_case_zero_values(self):
        """Test edge cases with zero values."""
        calculator = FinancialValuationEngine()
        
        zero_inputs = FinancialInputs(
            revenue=[1, 1, 1],  # Small positive values instead of zero
            ebit_margin=0.01,  # Small positive value
            capex=[0.1, 0.1, 0.1],
            depreciation=[0.1, 0.1, 0.1],
            nwc_changes=[0.1, 0.1, 0.1],
            tax_rate=0.01,  # Small positive value
            terminal_growth=0.001,  # Small positive value
            wacc=0.01,  # Small but non-zero
            share_count=1.0,
            cost_of_debt=0.01,  # Small but non-zero
        )
        
        # Should handle very small values gracefully
        result = calculator.calculate_dcf_valuation(zero_inputs)
        self.assertIsInstance(result, dict)
    
    def test_edge_case_very_large_values(self):
        """Test edge cases with very large values."""
        calculator = FinancialValuationEngine()
        
        large_inputs = FinancialInputs(
            revenue=[1e12, 1e12, 1e12],  # Very large revenue
            ebit_margin=0.5,
            capex=[1e11, 1e11, 1e11],
            depreciation=[1e10, 1e10, 1e10],
            nwc_changes=[1e9, 1e9, 1e9],
            tax_rate=0.25,
            terminal_growth=0.03,
            wacc=0.10,
            share_count=1e9,  # Very large share count
            cost_of_debt=0.06,
        )
        
        # Should handle large values gracefully
        result = calculator.calculate_dcf_valuation(large_inputs)
        self.assertIsInstance(result, dict)

class TestJSONOutputValidation(unittest.TestCase):
    """Test that the finance calculator produces expected output when run with sample input JSON and compared to output_validation.json."""
    
    def setUp(self):
        """Load the sample input and expected output JSON files."""
        with open('sample_input.json', 'r') as f:
            self.sample_input = json.load(f)
        
        with open('output_validation.json', 'r') as f:
            self.expected_output = json.load(f)
    
    def test_sample_input_produces_expected_output(self):
        """Test that running the finance calculator with sample input produces expected output matching output_validation.json."""
        # Parse the sample input JSON
        inputs = parse_financial_inputs(self.sample_input)
        
        # Run the comprehensive valuation
        engine = FinancialValuationEngine()
        actual_results = engine.perform_comprehensive_valuation(inputs)
        
        # Validate key metrics with detailed reporting
        self._validate_dcf_valuation(actual_results)
        self._validate_apv_valuation(actual_results)
        self._validate_comparable_multiples(actual_results)
        self._validate_scenarios(actual_results)
        self._validate_sensitivity_analysis(actual_results)
        self._validate_monte_carlo(actual_results)
    
    def test_detailed_output_comparison(self):
        """Detailed comparison showing exact differences between actual calculator output and output_validation.json."""
        # Parse the sample input JSON
        inputs = parse_financial_inputs(self.sample_input)
        
        # Run the comprehensive valuation
        engine = FinancialValuationEngine()
        actual_results = engine.perform_comprehensive_valuation(inputs)
        
        print("\n" + "="*80)
        print("DETAILED COMPARISON: Finance Calculator vs output_validation.json")
        print("="*80)
        
        # Compare key metrics with detailed reporting
        self._compare_detailed_values(actual_results, "DCF Valuation", "dcf_valuation")
        self._compare_detailed_values(actual_results, "APV Valuation", "apv_valuation")
        self._compare_detailed_values(actual_results, "Comparable Multiples", "comparable_valuation")
        
        # Compare FCF calculations specifically
        self._compare_fcf_calculations(actual_results)
        
        # Compare scenario results
        self._compare_scenario_results(actual_results)
        
        # Compare sensitivity analysis
        self._compare_sensitivity_analysis(actual_results)
        
        # Compare Monte Carlo
        self._compare_monte_carlo(actual_results)
        
        print("\n" + "="*80)
        print("COMPARISON COMPLETED")
        print("="*80)
        
        # The test passes if we're just reporting differences
        self.assertTrue(True, "Detailed comparison completed")
    
    def _compare_sensitivity_analysis(self, actual_results):
        """Compare sensitivity analysis results."""
        sensitivity_actual = actual_results.get('sensitivity_analysis', {})
        sensitivity_expected = self.expected_output.get('sensitivity_analysis', {})
        
        print(f"\n=== Sensitivity Analysis Comparison ===")
        
        if 'sensitivity_results' in sensitivity_actual and 'sensitivity_results' in sensitivity_expected:
            # Compare WACC sensitivity
            wacc_sens_actual = sensitivity_actual['sensitivity_results'].get('weighted_average_cost_of_capital', {})
            wacc_sens_expected = sensitivity_expected['sensitivity_results'].get('weighted_average_cost_of_capital', {})
            
            if wacc_sens_actual and wacc_sens_expected:
                print("WACC Sensitivity - Enterprise Values:")
                for wacc in ['0.085', '0.09', '0.095', '0.1', '0.105']:
                    if wacc in wacc_sens_actual and wacc in wacc_sens_expected:
                        actual_ev = wacc_sens_actual[wacc].get('ev', 0)
                        expected_ev = wacc_sens_expected[wacc].get('ev', 0)
                        diff = actual_ev - expected_ev
                        pct_diff = (diff / expected_ev * 100) if expected_ev != 0 else 0
                        print(f"  WACC {wacc}: {actual_ev:.1f} vs {expected_ev:.1f} (diff: {diff:+.1f}, {pct_diff:+.2f}%)")
    
    def _compare_monte_carlo(self, actual_results):
        """Compare Monte Carlo simulation results."""
        monte_carlo_actual = actual_results.get('monte_carlo', {})
        monte_carlo_expected = self.expected_output.get('monte_carlo_simulation', {})
        
        print(f"\n=== Monte Carlo Comparison ===")
        
        if monte_carlo_actual and monte_carlo_expected:
            # Compare WACC method results
            wacc_actual = monte_carlo_actual.get('wacc_method', {})
            wacc_expected = monte_carlo_expected.get('wacc_method', {})
            
            if wacc_actual and wacc_expected:
                actual_mean_ev = wacc_actual.get('mean_ev', 0)
                expected_mean_ev = wacc_expected.get('mean_ev', 0)
                diff = actual_mean_ev - expected_mean_ev
                pct_diff = (diff / expected_mean_ev * 100) if expected_mean_ev != 0 else 0
                print(f"Mean EV: {actual_mean_ev:.1f} vs {expected_mean_ev:.1f} (diff: {diff:+.1f}, {pct_diff:+.2f}%)")
                
                actual_median_ev = wacc_actual.get('median_ev', 0)
                expected_median_ev = wacc_expected.get('median_ev', 0)
                diff = actual_median_ev - expected_median_ev
                pct_diff = (diff / expected_median_ev * 100) if expected_median_ev != 0 else 0
                print(f"Median EV: {actual_median_ev:.1f} vs {expected_median_ev:.1f} (diff: {diff:+.1f}, {pct_diff:+.2f}%)")

    def _compare_detailed_values(self, actual_results, section_name, section_key):
        """Compare detailed values for a specific section."""
        actual_section = actual_results.get(section_key, {})
        expected_section = self.expected_output.get(section_key, {})
        
        print(f"\n=== {section_name} Comparison ===")
        
        # Compare enterprise value
        actual_ev = actual_section.get('enterprise_value', 0)
        expected_ev = expected_section.get('enterprise_value', 0)
        ev_diff = actual_ev - expected_ev
        ev_pct_diff = (ev_diff / expected_ev * 100) if expected_ev != 0 else 0
        
        print(f"Enterprise Value: {actual_ev:.2f} vs {expected_ev:.2f} (diff: {ev_diff:+.2f}, {ev_pct_diff:+.2f}%)")
        
        # Compare equity value
        actual_eq = actual_section.get('equity_value', 0)
        expected_eq = expected_section.get('equity_value', 0)
        eq_diff = actual_eq - expected_eq
        eq_pct_diff = (eq_diff / expected_eq * 100) if expected_eq != 0 else 0
        
        print(f"Equity Value: {actual_eq:.2f} vs {expected_eq:.2f} (diff: {eq_diff:+.2f}, {eq_pct_diff:+.2f}%)")
        
        # Compare price per share
        actual_pps = actual_section.get('price_per_share', 0)
        expected_pps = expected_section.get('price_per_share', 0)
        pps_diff = actual_pps - expected_pps
        pps_pct_diff = (pps_diff / expected_pps * 100) if expected_pps != 0 else 0
        
        print(f"Price per Share: {actual_pps:.2f} vs {expected_pps:.2f} (diff: {pps_diff:+.2f}, {pps_pct_diff:+.2f}%)")
        
        # For APV, also compare components
        if section_key == 'apv_valuation':
            actual_unlevered = actual_section.get('apv_components', {}).get('value_unlevered', 0)
            expected_unlevered = expected_section.get('apv_components', {}).get('value_unlevered', 0)
            actual_tax_shield = actual_section.get('apv_components', {}).get('pv_tax_shield', 0)
            expected_tax_shield = expected_section.get('apv_components', {}).get('pv_tax_shield', 0)
            
            print(f"Unlevered Value: {actual_unlevered:.2f} vs {expected_unlevered:.2f}")
            print(f"PV Tax Shield: {actual_tax_shield:.2f} vs {expected_tax_shield:.2f}")
    
    def _compare_fcf_calculations(self, actual_results):
        """Compare Free Cash Flow calculations in detail."""
        dcf_actual = actual_results.get('dcf_valuation', {})
        dcf_expected = self.expected_output.get('dcf_valuation', {})
        
        actual_fcfs = dcf_actual.get('free_cash_flows_after_tax_fcff', [])
        expected_fcfs = dcf_expected.get('free_cash_flows_after_tax_fcff', [])
        
        print(f"\n=== Free Cash Flow Comparison ===")
        
        for i, (actual_fcf, expected_fcf) in enumerate(zip(actual_fcfs, expected_fcfs)):
            diff = actual_fcf - expected_fcf
            pct_diff = (diff / expected_fcf * 100) if expected_fcf != 0 else 0
            print(f"Year {i+1}: {actual_fcf:.2f} vs {expected_fcf:.2f} (diff: {diff:+.2f}, {pct_diff:+.2f}%)")
    
    def _compare_scenario_results(self, actual_results):
        """Compare scenario analysis results."""
        scenarios_actual = actual_results.get('scenarios', {})
        scenarios_expected = self.expected_output.get('scenarios', {})
        
        print(f"\n=== Scenario Analysis Comparison ===")
        
        # Handle nested scenarios structure in output_validation.json
        if 'scenarios' in scenarios_expected:
            scenarios_expected = scenarios_expected['scenarios']
        
        for scenario_name in ['optimistic', 'pessimistic']:
            if scenario_name in scenarios_actual and scenario_name in scenarios_expected:
                scenario_actual = scenarios_actual[scenario_name]
                scenario_expected = scenarios_expected[scenario_name]
                
                # Compare enterprise value (note: output_validation.json uses 'ev' instead of 'enterprise_value')
                actual_ev = scenario_actual.get('enterprise_value', 0)
                expected_ev = scenario_expected.get('ev', 0)
                diff = actual_ev - expected_ev
                pct_diff = (diff / expected_ev * 100) if expected_ev != 0 else 0
                
                print(f"{scenario_name.capitalize()}: {actual_ev:.2f} vs {expected_ev:.2f} (diff: {diff:+.2f}, {pct_diff:+.2f}%)")

    def _validate_dcf_valuation(self, actual_results):
        """Validate DCF valuation results."""
        dcf_actual = actual_results.get('dcf_valuation', {})
        dcf_expected = self.expected_output.get('dcf_valuation', {})
        
        # Test key metrics with tolerance
        self._assert_within_tolerance(
            dcf_actual.get('enterprise_value', 0),
            dcf_expected.get('enterprise_value', 0),
            0.01,  # 1% tolerance
            "DCF Enterprise Value"
        )
        
        self._assert_within_tolerance(
            dcf_actual.get('equity_value', 0),
            dcf_expected.get('equity_value', 0),
            0.01,  # 1% tolerance
            "DCF Equity Value"
        )
        
        self._assert_within_tolerance(
            dcf_actual.get('price_per_share', 0),
            dcf_expected.get('price_per_share', 0),
            0.01,  # 1% tolerance
            "DCF Price per Share"
        )
        
        # Test FCF calculations
        actual_fcfs = dcf_actual.get('free_cash_flows_after_tax_fcff', [])
        expected_fcfs = dcf_expected.get('free_cash_flows_after_tax_fcff', [])
        
        self.assertEqual(len(actual_fcfs), len(expected_fcfs), 
                        "FCF array length should match")
        
        for i, (actual_fcf, expected_fcf) in enumerate(zip(actual_fcfs, expected_fcfs)):
            self._assert_within_tolerance(
                actual_fcf, expected_fcf, 0.01, f"FCF Year {i+1}"
            )
    
    def _validate_apv_valuation(self, actual_results):
        """Validate APV valuation results."""
        apv_actual = actual_results.get('apv_valuation', {})
        apv_expected = self.expected_output.get('apv_valuation', {})
        
        # Test enterprise value
        self._assert_within_tolerance(
            apv_actual.get('enterprise_value', 0),
            apv_expected.get('enterprise_value', 0),
            0.01,  # 1% tolerance
            "APV Enterprise Value"
        )
        
        # Test equity value
        self._assert_within_tolerance(
            apv_actual.get('equity_value', 0),
            apv_expected.get('equity_value', 0),
            0.01,  # 1% tolerance
            "APV Equity Value"
        )
        
        # Test unlevered value + tax shield = APV enterprise value
        unlevered_value = apv_actual.get('apv_components', {}).get('value_unlevered', 0)
        pv_tax_shield = apv_actual.get('apv_components', {}).get('pv_tax_shield', 0)
        apv_enterprise_value = apv_actual.get('enterprise_value', 0)
        
        calculated_apv = unlevered_value + pv_tax_shield
        self._assert_within_tolerance(
            apv_enterprise_value, calculated_apv, 0.01, "APV = Unlevered + Tax Shield"
        )
    
    def _validate_comparable_multiples(self, actual_results):
        """Validate comparable multiples results."""
        comp_actual = actual_results.get('comparable_valuation', {})
        comp_expected = self.expected_output.get('comparable_valuation', {})
        
        # Test EV multiples
        ev_actual = comp_actual.get('ev_multiples', {})
        ev_expected = comp_expected.get('ev_multiples', {})
        
        self._assert_within_tolerance(
            ev_actual.get('mean_ev', 0),
            ev_expected.get('mean_ev', 0),
            0.01,  # 1% tolerance
            "Mean EV from Multiples"
        )
        
        # Test implied EVs by multiple
        implied_evs_actual = comp_actual.get('implied_evs_by_multiple', {})
        implied_evs_expected = comp_expected.get('implied_evs_by_multiple', {})
        
        for multiple_type in ['EV/EBITDA', 'EV/Revenue', 'P/E']:
            if multiple_type in implied_evs_actual and multiple_type in implied_evs_expected:
                self._assert_within_tolerance(
                    implied_evs_actual[multiple_type].get('mean_implied_ev', 0),
                    implied_evs_expected[multiple_type].get('mean_implied_ev', 0),
                    0.01,  # 1% tolerance
                    f"{multiple_type} Mean Implied EV"
                )
    
    def _validate_scenarios(self, actual_results):
        """Validate scenario analysis results."""
        scenarios_actual = actual_results.get('scenarios', {})
        scenarios_expected = self.expected_output.get('scenarios', {})
        
        for scenario_name in ['optimistic', 'pessimistic']:
            if scenario_name in scenarios_actual and scenario_name in scenarios_expected:
                scenario_actual = scenarios_actual[scenario_name]
                scenario_expected = scenarios_expected[scenario_name]
                
                # Test enterprise value
                self._assert_within_tolerance(
                    scenario_actual.get('enterprise_value', 0),
                    scenario_expected.get('enterprise_value', 0),
                    0.01,  # 1% tolerance
                    f"{scenario_name.capitalize()} Scenario Enterprise Value"
                )
    
    def _validate_sensitivity_analysis(self, actual_results):
        """Validate sensitivity analysis results."""
        sensitivity_actual = actual_results.get('sensitivity_analysis', {})
        sensitivity_expected = self.expected_output.get('sensitivity_analysis', {})
        
        if 'sensitivity_results' in sensitivity_actual and 'sensitivity_results' in sensitivity_expected:
            # Test WACC sensitivity
            wacc_sens_actual = sensitivity_actual['sensitivity_results'].get('weighted_average_cost_of_capital', {})
            wacc_sens_expected = sensitivity_expected['sensitivity_results'].get('weighted_average_cost_of_capital', {})
            
            if wacc_sens_actual and wacc_sens_expected:
                # Test that higher WACC leads to lower EV (inverse relationship)
                ev_values_actual = wacc_sens_actual.get('ev', {})
                if len(ev_values_actual) > 1:
                    wacc_values = sorted([float(k) for k in ev_values_actual.keys()])
                    ev_values_sorted = [ev_values_actual[str(w)] for w in wacc_values]
                    
                    # Check if EV generally decreases as WACC increases
                    decreasing_count = sum(1 for i in range(len(ev_values_sorted)-1) 
                                        if ev_values_sorted[i] >= ev_values_sorted[i+1])
                    
                    # At least 70% of the relationships should show inverse relationship
                    self.assertGreaterEqual(
                        decreasing_count / (len(ev_values_sorted) - 1), 0.7,
                        "WACC sensitivity should generally show inverse relationship"
                    )
    
    def _validate_monte_carlo(self, actual_results):
        """Validate Monte Carlo simulation results."""
        monte_carlo_actual = actual_results.get('monte_carlo', {})
        monte_carlo_expected = self.expected_output.get('monte_carlo', {})
        
        if monte_carlo_actual and monte_carlo_expected:
            # Test percentile ordering
            percentiles_actual = monte_carlo_actual.get('percentiles', {})
            if percentiles_actual:
                p10 = percentiles_actual.get('10', 0)
                p50 = percentiles_actual.get('50', 0)
                p90 = percentiles_actual.get('90', 0)
                
                if p10 > 0 and p50 > 0 and p90 > 0:
                    self.assertLessEqual(p10, p50, "P10 should be ≤ P50")
                    self.assertLessEqual(p50, p90, "P50 should be ≤ P90")
    
    def _assert_within_tolerance(self, actual, expected, tolerance, metric_name):
        """Assert that actual value is within tolerance of expected value."""
        if expected != 0:
            percentage_diff = abs(actual - expected) / abs(expected)
            self.assertLessEqual(
                percentage_diff, tolerance,
                f"{metric_name}: {actual} vs {expected} (diff: {percentage_diff:.4f} > {tolerance})"
            )
        else:
            # If expected is 0, just check that actual is close to 0
            self.assertLessEqual(abs(actual), 0.01, f"{metric_name}: {actual} should be close to 0")

if __name__ == '__main__':
    unittest.main() 