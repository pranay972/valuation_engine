"""
Clean Scenario Analysis Module

Barebones scenario analysis without extra dependencies.
"""

import pandas as pd
from copy import deepcopy
from typing import Dict, Any, List

from .params import ValuationParameters
from .dcf import calculate_dcf_valuation_wacc

def run_scenarios(params: ValuationParameters) -> pd.DataFrame:
    """
    Run scenario analysis by applying parameter overrides to base case.
    
    Returns:
        DataFrame indexed by scenario name with columns: EV, Equity, PS
    """
    if not params.scenario_definitions:
        raise ValueError("No scenarios defined in params.scenario_definitions")
    
    # Validate scenario structure
    for scen_name, overrides in params.scenario_definitions.items():
        if not isinstance(overrides, dict):
            raise ValueError(f"Scenario '{scen_name}' overrides must be a dictionary")
        
        # Check that all override parameters are valid ValuationParameters attributes
        valid_attrs = set(ValuationParameters.__dataclass_fields__.keys())
        for param_name in overrides.keys():
            if param_name not in valid_attrs:
                raise ValueError(
                    f"Invalid parameter '{param_name}' in scenario '{scen_name}'. "
                    f"Valid parameters: {', '.join(sorted(valid_attrs))}"
                )
    
    rows = []
    
    for scen_name, overrides in params.scenario_definitions.items():
        try:
            # 1 & 2: Copy and apply overrides
            p = deepcopy(params)
            for field, val in overrides.items():
                setattr(p, field, val)
            
            # 3: Run DCF
            ev, equity, ps, _, _, _ = calculate_dcf_valuation_wacc(p)
            
            # 4: Record results
            rows.append({
                "Scenario": scen_name,
                "EV": ev,
                "Equity": equity,
                "PS": ps if ps is not None else float('nan')
            })
            
        except Exception as e:
            # Log error but continue with other scenarios
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