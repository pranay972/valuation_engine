"""
Scenario Analysis Module

This module provides scenario analysis capabilities for valuation:
- run_scenarios: Run DCF analysis under different parameter scenarios
- Support for multiple scenarios with parameter overrides
- Comprehensive error handling and validation

Scenarios allow users to test "what-if" situations by overriding
specific parameters while keeping others constant.
"""

import pandas as pd
from copy import deepcopy
from typing import Dict, Any, List

from params import ValuationParams
from valuation import calc_dcf_series

def run_scenarios(params: ValuationParams) -> pd.DataFrame:
    """
    Run scenario analysis by applying parameter overrides to base case.
    
    Iterate over each scenario defined in params.scenarios:
    1. Deep-copy the base params
    2. Apply the overrides for this scenario
    3. Run calc_dcf_series on the adjusted params
    4. Record EV, Equity value, and Price/Share
    
    Args:
        params: ValuationParams object with base inputs and scenarios
        
    Returns:
        DataFrame indexed by scenario name with columns:
        - EV: Enterprise Value
        - Equity: Equity Value  
        - PS: Price per Share
        
    Raises:
        ValueError: If no scenarios are defined
        ValueError: If scenario overrides contain invalid parameters
    """
    if not params.scenarios:
        raise ValueError("No scenarios defined in params.scenarios")
    
    # Validate scenario structure
    for scen_name, overrides in params.scenarios.items():
        if not isinstance(overrides, dict):
            raise ValueError(f"Scenario '{scen_name}' overrides must be a dictionary")
        
        # Check that all override parameters are valid ValuationParams attributes
        valid_attrs = set(ValuationParams.__dataclass_fields__.keys())
        for param_name in overrides.keys():
            if param_name not in valid_attrs:
                raise ValueError(
                    f"Invalid parameter '{param_name}' in scenario '{scen_name}'. "
                    f"Valid parameters: {', '.join(sorted(valid_attrs))}"
                )
    
    rows: List[Dict[str, Any]] = []
    
    for scen_name, overrides in params.scenarios.items():
        try:
            # 1 & 2: Copy and apply overrides
            p = deepcopy(params)
            for field, val in overrides.items():
                setattr(p, field, val)
            
            # 3: Run DCF
            ev, equity, ps = calc_dcf_series(p)
            
            # 4: Record results
            rows.append({
                "Scenario": scen_name,
                "EV": ev,
                "Equity": equity,
                "PS": ps if ps is not None else float('nan')
            })
            
        except Exception as e:
            # Log error but continue with other scenarios
            print(f"Scenario '{scen_name}' failed: {str(e)}")
            rows.append({
                "Scenario": scen_name,
                "EV": float('nan'),
                "Equity": float('nan'),
                "PS": float('nan')
            })
    
    if not rows:
        raise ValueError("No scenarios were successfully executed")
    
    # Build DataFrame
    df = pd.DataFrame(rows).set_index("Scenario")
    return df

def create_scenario_template() -> Dict[str, Dict[str, Any]]:
    """
    Create a template for scenario definitions.
    
    Returns:
        Dictionary with example scenarios that can be used as a starting point
    """
    return {
        "Base": {},
        "Optimistic": {
            "ebit_margin": 0.25,
            "terminal_growth": 0.03,
            "wacc": 0.09
        },
        "Pessimistic": {
            "ebit_margin": 0.15,
            "terminal_growth": 0.01,
            "wacc": 0.12
        },
        "High Growth": {
            "terminal_growth": 0.04,
            "ebit_margin": 0.22
        },
        "Low Cost of Capital": {
            "wacc": 0.08,
            "cost_of_debt": 0.04
        }
    }

def validate_scenario_overrides(overrides: Dict[str, Any]) -> List[str]:
    """
    Validate scenario parameter overrides.
    
    Args:
        overrides: Dictionary of parameter overrides
        
    Returns:
        List of validation messages (empty if valid)
    """
    messages = []
    valid_attrs = set(ValuationParams.__dataclass_fields__.keys())
    
    for param_name, value in overrides.items():
        if param_name not in valid_attrs:
            messages.append(f"Invalid parameter: '{param_name}'")
            continue
        
        # Type-specific validation
        if param_name in ["ebit_margin", "wacc", "tax_rate", "terminal_growth", "cost_of_debt"]:
            if not isinstance(value, (int, float)):
                messages.append(f"'{param_name}' must be numeric")
            elif param_name in ["ebit_margin", "tax_rate"]:
                if value < 0 or value > 1:
                    messages.append(f"'{param_name}' must be between 0 and 1")
            elif param_name in ["wacc", "cost_of_debt"]:
                if value < 0:
                    messages.append(f"'{param_name}' must be non-negative")
            elif param_name == "terminal_growth":
                if value >= 1:
                    messages.append(f"'{param_name}' must be less than 100%")
        
        elif param_name == "share_count":
            if not isinstance(value, (int, float)):
                messages.append(f"'{param_name}' must be numeric")
            elif value <= 0:
                messages.append(f"'{param_name}' must be positive")
        
        elif param_name in ["revenue", "capex", "depreciation", "nwc_changes", "fcf_series"]:
            if not isinstance(value, list):
                messages.append(f"'{param_name}' must be a list")
            elif not all(isinstance(x, (int, float)) for x in value):
                messages.append(f"All values in '{param_name}' must be numeric")
    
    return messages

def detect_circular_references(scenarios: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Detect potential circular references in scenario definitions.
    
    Args:
        scenarios: Dictionary of scenario definitions
        
    Returns:
        List of circular reference warnings
    """
    warnings = []
    
    # Check for scenarios that reference each other (simplified check)
    scenario_names = set(scenarios.keys())
    for scen_name, overrides in scenarios.items():
        for param_name, value in overrides.items():
            if isinstance(value, str) and value in scenario_names:
                warnings.append(f"Scenario '{scen_name}' references scenario '{value}' - potential circular reference")
    
    return warnings

def get_scenario_summary(scenarios_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate summary statistics across all scenarios.
    
    Args:
        scenarios_df: Results from run_scenarios()
        
    Returns:
        Dictionary with summary statistics:
        - mean_ev: Average EV across scenarios
        - ev_range: Range of EVs
        - ev_cv: Coefficient of variation
        - best_scenario: Scenario with highest EV
        - worst_scenario: Scenario with lowest EV
    """
    if scenarios_df.empty:
        return {}
    
    ev_series = scenarios_df["EV"].dropna()
    if ev_series.empty:
        return {}
    
    summary = {
        "mean_ev": ev_series.mean(),
        "ev_range": ev_series.max() - ev_series.min(),
        "ev_cv": ev_series.std() / ev_series.mean() if ev_series.mean() > 0 else 0,
        "best_scenario": ev_series.idxmax(),
        "worst_scenario": ev_series.idxmin()
    }
    
    return summary
