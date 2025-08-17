"""
Clean Comparable Multiples Analysis Module

Barebones comparable company multiples analysis without extra dependencies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple

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

def analyze_comparable_multiples(params: ValuationParameters, comps: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Perform comparable multiples analysis using peer company data.
    
    Returns:
        Dict containing:
            - ev_based: DataFrame with implied enterprise values by EV-based multiple type
            - equity_based: DataFrame with implied equity values by equity-based multiple type
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
    
    # 2) Separate EV-based and equity-based multiples
    ev_based_multiples = ["EV/EBITDA", "EV/Revenue", "EV/FCF", "EV/Earnings"]
    equity_based_multiples = ["P/E", "P/B", "P/S"]
    
    ev_results = []
    equity_results = []
    
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
            
            # Calculate implied values based on multiple type
            if col in ev_based_multiples:
                # EV-based multiple: produces enterprise value
                implied_values = peer_vals_filtered * our_metric
                result = {
                    "Multiple": col,
                    "Mean Implied EV": implied_values.mean(),
                    "Median Implied EV": implied_values.median(),
                    "Std Dev Implied EV": implied_values.std(),
                    "Min Implied EV": implied_values.min(),
                    "Max Implied EV": implied_values.max(),
                    "Peer Count": len(peer_vals_filtered),
                    "Our Metric": our_metric,
                    "Mean Multiple": peer_vals_filtered.mean()
                }
                result["_implied_values"] = implied_values.tolist()
                ev_results.append(result)
                
            elif col in equity_based_multiples:
                # Equity-based multiple: produces equity value
                implied_values = peer_vals_filtered * our_metric
                result = {
                    "Multiple": col,
                    "Mean Implied Equity": implied_values.mean(),
                    "Median Implied Equity": implied_values.median(),
                    "Std Dev Implied Equity": implied_values.std(),
                    "Min Implied Equity": implied_values.min(),
                    "Max Implied Equity": implied_values.max(),
                    "Peer Count": len(peer_vals_filtered),
                    "Our Metric": our_metric,
                    "Mean Multiple": peer_vals_filtered.mean()
                }
                result["_implied_values"] = implied_values.tolist()
                equity_results.append(result)
            
        except Exception as e:
            # Log error but continue with other multiples
            continue
    
    # 3) Return as separate DataFrames
    ev_df = pd.DataFrame(ev_results).set_index("Multiple") if ev_results else pd.DataFrame()
    equity_df = pd.DataFrame(equity_results).set_index("Multiple") if equity_results else pd.DataFrame()
    
    return {
        "ev_based": ev_df,
        "equity_based": equity_df
    } 