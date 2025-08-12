"""
Clean Sensitivity Analysis Module

Barebones sensitivity analysis without extra dependencies.
"""

import pandas as pd
from copy import deepcopy
from typing import Dict, List, Any

from params import ValuationParameters
from dcf import calculate_dcf_valuation_wacc

def create_parameter_copy(params: ValuationParameters) -> ValuationParameters:
    """Create a copy of parameters for sensitivity analysis."""
    return deepcopy(params)

def perform_sensitivity_analysis(params: ValuationParameters) -> pd.DataFrame:
    """
    Run sensitivity analysis by varying parameters and calculating DCF values.
    
    Returns:
        DataFrame with sensitivity results
    """
    if not params.sensitivity_parameter_ranges:
        raise ValueError("No sensitivity ranges provided")
    
    # Pre-allocate data structure for efficiency
    max_length = max(len(test_values) for test_values in params.sensitivity_parameter_ranges.values())
    data = {}
    for param_name in params.sensitivity_parameter_ranges.keys():
        data[f"{param_name}_ev"] = [float('nan')] * max_length
        data[f"{param_name}_price_per_share"] = [float('nan')] * max_length
    
    # Run sensitivity analysis for each parameter
    for param_name, test_values in params.sensitivity_parameter_ranges.items():
        # Map range parameter names to actual parameter names
        param_mapping = {
            "weighted_average_cost_of_capital": "weighted_average_cost_of_capital",
            "ebit_margin": "ebit_margin", 
            "terminal_growth_rate": "terminal_growth_rate",
            "target_debt_to_value_ratio": "target_debt_to_value_ratio"
        }
        actual_param_name = param_mapping.get(param_name, param_name)
        
        for i, test_value in enumerate(test_values):
            try:
                # Create parameter copy with test value
                p = create_parameter_copy(params)
                setattr(p, actual_param_name, test_value)
                
                # For target debt ratio changes, recalculate WACC
                if actual_param_name == "target_debt_to_value_ratio":
                    cost_of_equity = p.calculate_levered_cost_of_equity()
                    p.weighted_average_cost_of_capital = (1 - test_value) * cost_of_equity + test_value * p.cost_of_debt * (1 - p.corporate_tax_rate)
                
                # For WACC changes, ensure it's used directly (not overridden by target structure)
                if actual_param_name == "weighted_average_cost_of_capital":
                    # Temporarily set target_debt_to_value_ratio to None to avoid override
                    # This will be handled by the WACC calculation logic
                    p.target_debt_to_value_ratio = None
                
                # Run DCF calculation
                ev, equity, price_per_share, _, _, _ = calculate_dcf_valuation_wacc(p)
                
                # Store both EV and price per share
                data[f"{param_name}_ev"][i] = ev
                data[f"{param_name}_price_per_share"][i] = price_per_share if price_per_share else float('nan')
                
            except Exception as e:
                data[param_name][i] = float('nan')
    
    # Convert to DataFrame
    return pd.DataFrame(data) 