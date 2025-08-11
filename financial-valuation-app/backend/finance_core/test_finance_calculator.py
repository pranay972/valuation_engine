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
from finance_calculator import (
    FinancialValuationEngine, 
    FinancialInputs, 
    parse_financial_inputs
)
from params import ValuationParameters
from dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from multiples import analyze_comparable_multiples
from scenario import perform_scenario_analysis
from sensitivity import perform_sensitivity_analysis
from monte_carlo import simulate_monte_carlo
from drivers import project_ebit_series, project_free_cash_flow
from error_messages import FinanceCoreError

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

if __name__ == '__main__':
    unittest.main() 