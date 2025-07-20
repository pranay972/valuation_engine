"""
Sensitivity Analysis Module

This module provides sensitivity analysis capabilities for valuation:
- run_sensitivity_analysis: Vary one input at a time and record effect on EV
- Support for multiple parameters and value ranges
- Comprehensive error handling and validation

Sensitivity analysis helps identify which parameters have the greatest
impact on valuation results.
"""

import pandas as pd
import numpy as np
from copy import deepcopy
from typing import Dict, List, Any

from params import ValuationParams
from valuation import calc_dcf_series

def run_sensitivity_analysis(params: ValuationParams) -> pd.DataFrame:
    """
    Run sensitivity analysis by varying one parameter at a time.
    
    For each parameter in params.sensitivity_ranges:
    1. Loop through its list of test values
    2. Deep-copy params and override that parameter with the test value
    3. Run calc_dcf_series on the adjusted params to get EV
    4. Collect EVs in a column named after the parameter
    
    Args:
        params: ValuationParams object with base inputs and sensitivity_ranges
        
    Returns:
        DataFrame where each column is a parameter name, and each row
        corresponds (by position) to the test value in that parameter's list.
        Missing values (if lists differ in length) are filled with NaN.
        
    Raises:
        ValueError: If no sensitivity ranges are defined
        ValueError: If sensitivity ranges contain invalid parameters
        ValueError: If any parameter range is empty
    """
    print(f"Sensitivity ranges received: {params.sensitivity_ranges}")
    
    if not params.sensitivity_ranges:
        raise ValueError("No sensitivity ranges defined in params.sensitivity_ranges")
    
    # Validate sensitivity ranges
    valid_attrs = set(ValuationParams.__dataclass_fields__.keys())
    for param_name, test_values in params.sensitivity_ranges.items():
        if param_name not in valid_attrs:
            raise ValueError(
                f"Invalid parameter '{param_name}' in sensitivity ranges. "
                f"Valid parameters: {', '.join(sorted(valid_attrs))}"
            )
        
        if not isinstance(test_values, list):
            raise ValueError(f"Sensitivity range for '{param_name}' must be a list")
        
        if not test_values:
            raise ValueError(f"Sensitivity range for '{param_name}' is empty")
        
        # Validate test values based on parameter type
        for i, value in enumerate(test_values):
            if param_name in ["ebit_margin", "wacc", "tax_rate", "terminal_growth", "cost_of_debt"]:
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Test value {i} for '{param_name}' must be numeric")
                
                # More flexible validation based on parameter type
                if param_name in ["ebit_margin", "tax_rate"]:
                    if value < 0 or value > 1:
                        raise ValueError(f"Test value {i} for '{param_name}' must be between 0 and 1")
                elif param_name in ["wacc", "cost_of_debt"]:
                    if value < 0:
                        raise ValueError(f"Test value {i} for '{param_name}' must be non-negative")
                    # Allow values > 1 for hyperinflationary scenarios
                elif param_name == "terminal_growth":
                    # Allow negative growth for deflationary scenarios
                    if value >= 1:
                        raise ValueError(f"Test value {i} for '{param_name}' must be less than 100%")
            
            elif param_name == "share_count":
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Test value {i} for '{param_name}' must be numeric")
                if value <= 0:
                    raise ValueError(f"Test value {i} for '{param_name}' must be positive")
    
    data: Dict[str, List[float]] = {}
    
    for param_name, test_values in params.sensitivity_ranges.items():
        ev_list: List[float] = []
        
        for i, test_value in enumerate(test_values):
            try:
                # Copy and override parameter
                p = deepcopy(params)
                setattr(p, param_name, test_value)
                
                # Run DCF
                ev, _, _ = calc_dcf_series(p)
                ev_list.append(ev)
                
            except Exception as e:
                # Log error but continue with other test values
                print(f"Sensitivity test failed for '{param_name}' value {i} ({test_value}): {str(e)}")
                ev_list.append(float('nan'))
        
        data[param_name] = ev_list
    
    # Convert to DataFrame; rows align by list index
    # Pad shorter lists with NaN to ensure all columns have the same length
    max_length = max(len(ev_list) for ev_list in data.values())
    
    for param_name in data:
        while len(data[param_name]) < max_length:
            data[param_name].append(float('nan'))
    
    return pd.DataFrame(data)

def create_sensitivity_template() -> Dict[str, List[float]]:
    """
    Create a template for sensitivity analysis ranges.
    
    Returns:
        Dictionary with example sensitivity ranges that can be used as a starting point
    """
    return {
        "wacc": [0.08, 0.09, 0.10, 0.11, 0.12],
        "terminal_growth": [0.01, 0.015, 0.02, 0.025, 0.03],
        "ebit_margin": [0.15, 0.17, 0.20, 0.23, 0.25],
        "tax_rate": [0.18, 0.20, 0.21, 0.22, 0.25]
    }

def validate_sensitivity_ranges(ranges: Dict[str, List[float]]) -> List[str]:
    """
    Validate sensitivity analysis parameter ranges.
    
    Args:
        ranges: Dictionary of parameter ranges
        
    Returns:
        List of validation messages (empty if valid)
    """
    messages = []
    valid_attrs = set(ValuationParams.__dataclass_fields__.keys())
    
    for param_name, test_values in ranges.items():
        if param_name not in valid_attrs:
            messages.append(f"Invalid parameter: '{param_name}'")
            continue
        
        if not isinstance(test_values, list):
            messages.append(f"'{param_name}' range must be a list")
            continue
        
        if not test_values:
            messages.append(f"'{param_name}' range is empty")
            continue
        
        # Type-specific validation
        for i, value in enumerate(test_values):
            if param_name in ["ebit_margin", "wacc", "tax_rate", "terminal_growth", "cost_of_debt"]:
                if not isinstance(value, (int, float)):
                    messages.append(f"'{param_name}' value {i} must be numeric")
                elif value < 0 or value > 1:
                    messages.append(f"'{param_name}' value {i} must be between 0 and 1")
            
            elif param_name == "share_count":
                if not isinstance(value, (int, float)):
                    messages.append(f"'{param_name}' value {i} must be numeric")
                elif value <= 0:
                    messages.append(f"'{param_name}' value {i} must be positive")
    
    return messages

def get_sensitivity_summary(sensitivity_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for sensitivity analysis results.
    
    Args:
        sensitivity_df: Results from run_sensitivity_analysis()
        
    Returns:
        Dictionary with summary statistics for each parameter:
        {
            "wacc": {
                "min_ev": ..., "max_ev": ..., "ev_range": ..., "ev_cv": ...
            },
            ...
        }
    """
    summary = {}
    
    for param_name in sensitivity_df.columns:
        ev_series = sensitivity_df[param_name].dropna()
        if ev_series.empty:
            continue
        
        param_summary = {
            "min_ev": ev_series.min(),
            "max_ev": ev_series.max(),
            "ev_range": ev_series.max() - ev_series.min(),
            "ev_cv": ev_series.std() / ev_series.mean() if ev_series.mean() > 0 else 0,
            "mean_ev": ev_series.mean(),
            "std_ev": ev_series.std()
        }
        
        summary[param_name] = param_summary
    
    return summary

def find_most_sensitive_parameter(sensitivity_df: pd.DataFrame) -> str:
    """
    Find the parameter with the highest coefficient of variation in EV.
    
    Args:
        sensitivity_df: Results from run_sensitivity_analysis()
        
    Returns:
        Name of the most sensitive parameter
    """
    if sensitivity_df.empty:
        return ""
    
    max_cv = 0
    most_sensitive = ""
    
    for param_name in sensitivity_df.columns:
        ev_series = sensitivity_df[param_name].dropna()
        if ev_series.empty:
            continue
        
        cv = ev_series.std() / ev_series.mean() if ev_series.mean() > 0 else 0
        if cv > max_cv:
            max_cv = cv
            most_sensitive = param_name
    
    return most_sensitive
