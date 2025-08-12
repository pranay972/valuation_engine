"""
Clean Comparable Multiples Analysis Module

Barebones comparable company multiples analysis without extra dependencies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union

from .drivers import project_ebit_series, project_free_cash_flow
from .params import ValuationParameters

def calculate_net_income(ebit: float, debt: float, cost_of_debt: float, tax_rate: float) -> float:
    """Calculate Net Income for P/E ratio."""
    interest_expense = debt * cost_of_debt
    ebt = ebit - interest_expense  # Earnings before tax
    net_income = ebt * (1 - tax_rate)
    return net_income

def calculate_ebitda(ebit: float, depreciation: float) -> float:
    """Calculate EBITDA = EBIT + Depreciation"""
    return ebit + depreciation

def analyze_comparable_multiples(params: ValuationParameters, comps: pd.DataFrame) -> pd.DataFrame:
    """
    Perform comparable multiples analysis using peer company data.
    
    Returns:
        DataFrame with implied enterprise values by multiple type
    """
    if comps.empty:
        raise ValueError("Comparable companies DataFrame is empty")
    
    if not params.revenue_projections:
        raise ValueError("Revenue projections required for multiples analysis")
    
    # 1) Compute our company's last-year metrics
    revenues = params.revenue_projections
    ebits = project_ebit_series(revenues, params.ebit_margin)
    fcfs = project_free_cash_flow(
        revenues,
        ebits,
        params.capital_expenditure,
        params.depreciation_expense,
        params.net_working_capital_changes,
        params.corporate_tax_rate
    )
    
    # Get terminal debt for Net Income calculation
    terminal_debt = None
    if params.debt_schedule and params.revenue_projections:
        terminal_year = len(params.revenue_projections) - 1
        terminal_debt = params.debt_schedule.get(terminal_year, None)
    
    # Calculate key financial metrics
    metric_map = {
        "EBITDA": calculate_ebitda(
            ebits[-1], 
            params.depreciation_expense[-1] if params.depreciation_expense else 0.0
        ),
        "Earnings": calculate_net_income(
            ebits[-1], 
            terminal_debt if terminal_debt is not None else 0.0, 
            params.cost_of_debt, 
            params.corporate_tax_rate
        ),
        "E": calculate_net_income(
            ebits[-1], 
            terminal_debt if terminal_debt is not None else 0.0, 
            params.cost_of_debt, 
            params.corporate_tax_rate
        ),
        "FCF": fcfs[-1],
        "Revenue": revenues[-1]
    }
    
    # 2) Apply peer multiples to our metrics
    results = []
    
    for col in comps.columns:
        try:
            # Parse multiple type (e.g., "EV/EBITDA" -> numerator="EV", denominator="EBITDA")
            if "/" not in col:
                continue
                
            num, den = [s.strip() for s in col.split("/", 1)]
            if den not in metric_map:
                continue  # Skip unknown denominators
            
            our_metric = metric_map[den]
            if our_metric <= 0:
                continue  # Skip if our metric is non-positive
            
            # Clean and convert peer multiples to float
            peer_vals = comps[col].dropna()
            if peer_vals.empty:
                continue
                
            # Convert to numeric, handling any non-numeric values
            peer_vals_numeric = pd.to_numeric(peer_vals, errors='coerce').dropna()
            if peer_vals_numeric.empty:
                continue
            
            # Filter out extreme outliers (beyond 3 standard deviations)
            mean_mult = peer_vals_numeric.mean()
            std_mult = peer_vals_numeric.std()
            if std_mult > 0:
                peer_vals_filtered = peer_vals_numeric[
                    (peer_vals_numeric >= mean_mult - 3 * std_mult) & 
                    (peer_vals_numeric <= mean_mult + 3 * std_mult)
                ]
            else:
                peer_vals_filtered = peer_vals_numeric
            
            if peer_vals_filtered.empty:
                continue
            
            # Calculate implied enterprise values
            implied_evs = peer_vals_filtered * our_metric
            
            # Calculate summary statistics
            result = {
                "Multiple": col,
                "Mean Implied EV": implied_evs.mean(),
                "Median Implied EV": implied_evs.median(),
                "Std Dev Implied EV": implied_evs.std(),
                "Min Implied EV": implied_evs.min(),
                "Max Implied EV": implied_evs.max(),
                "Peer Count": len(peer_vals_filtered),
                "Our Metric": our_metric,
                "Mean Multiple": peer_vals_filtered.mean()
            }
            
            # Store implied EVs separately to avoid DataFrame issues
            result["_implied_evs"] = implied_evs.tolist()
            
            results.append(result)
            
        except Exception as e:
            # Log error but continue with other multiples
            continue
    
    if not results:
        raise ValueError(
            "No valid multiples found. Please check that the comparable companies "
            "DataFrame contains columns with format 'EV/Metric' or 'P/Metric'"
        )
    
    # 3) Return as DataFrame indexed by multiple name
    result_df = pd.DataFrame(results).set_index("Multiple")
    return result_df 