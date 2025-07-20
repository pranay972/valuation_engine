"""
Comparable Multiples Analysis Module

This module provides functionality for comparable company multiples analysis:
- run_multiples_analysis: Apply peer ratios to forecast metrics
- Support for common multiples (EV/EBITDA, P/E, EV/FCF, EV/Revenue)
- Comprehensive error handling and validation

The analysis calculates implied enterprise values based on peer company multiples
and provides summary statistics for valuation comparison.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union
from ...core.financial.drivers import project_ebit, project_fcf
from ...core.models.params import ValuationParams

def calculate_net_income(ebit: float, debt: float, cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculate Net Income for P/E ratio.
    Net Income = EBIT - Interest Expense - Taxes
    """
    interest_expense = debt * cost_of_debt
    ebt = ebit - interest_expense  # Earnings before tax
    net_income = ebt * (1 - tax_rate)
    return net_income

def calculate_ebitda(ebit: float, depreciation: float, amortization: float = 0.0) -> float:
    """
    Calculate EBITDA = EBIT + Depreciation + Amortization
    """
    return ebit + depreciation + amortization

def run_multiples_analysis(
    params: ValuationParams,
    comps: pd.DataFrame
) -> pd.DataFrame:  # type: ignore
    """
    Perform comparable multiples analysis using peer company data.
    
    Given a company's projected financials and peer company multiples,
    calculate implied enterprise values for each multiple type.
    
    Args:
        params: ValuationParams object with company projections
        comps: DataFrame of peer company multiples with columns like 
               "EV/EBITDA", "P/E", "EV/FCF", "EV/Revenue", etc.
        
    Returns:
        DataFrame with implied enterprise values by multiple type:
        - Mean Implied EV
        - Median Implied EV
        - Standard Deviation
        - Min/Max values
        
    Raises:
        ValueError: If comps DataFrame is empty
        ValueError: If no valid multiples are found in comps
        ValueError: If required financial projections are missing
    """
    # Validate inputs
    if comps.empty:
        raise ValueError("Comparable companies DataFrame is empty")
    
    if not params.revenue:
        raise ValueError("Revenue projections required for multiples analysis")
    
    # 1) Compute our company's last-year metrics
    revenues = params.revenue
    ebits = project_ebit(revenues, params.ebit_margin)
    fcfs = project_fcf(
        revenues,
        ebits,
        params.capex,
        params.depreciation,
        params.nwc_changes,
        params.tax_rate
    )
    
    # Get terminal debt for Net Income calculation
    terminal_debt = 0.0
    if params.debt_schedule and params.revenue:
        terminal_year = len(params.revenue) - 1
        terminal_debt = params.debt_schedule.get(terminal_year, 0.0)
    
    # Calculate key financial metrics
    metric_map: Dict[str, float] = {
        # EBITDA = EBIT + Depreciation + Amortization (assuming no amortization for simplicity)
        "EBITDA": calculate_ebitda(
            ebits[-1], 
            params.depreciation[-1] if params.depreciation else 0.0,
            0.0  # No amortization in current model
        ),
        
        # FIXED: For P/E ratio, calculate proper Net Income
        # Support both "Earnings" and "E" for P/E ratio compatibility
        "Earnings": calculate_net_income(
            ebits[-1], 
            terminal_debt, 
            params.cost_of_debt, 
            params.tax_rate
        ),
        "E": calculate_net_income(
            ebits[-1], 
            terminal_debt, 
            params.cost_of_debt, 
            params.tax_rate
        ),
        
        # FCF = last-year free cash flow
        "FCF": fcfs[-1] if fcfs else 0.0,
        
        # Revenue = last-year revenue
        "Revenue": revenues[-1]
    }
    
    print(f"Calculated metrics: {metric_map}")
    print(f"Last year EBIT: {ebits[-1]}")
    print(f"Last year FCF: {fcfs[-1] if fcfs else 'No FCF'}")
    print(f"Last year Revenue: {revenues[-1]}")
    print(f"Terminal debt used for Net Income: {terminal_debt}")
    
    # Validate that we have meaningful metrics
    if all(value <= 0 for value in metric_map.values()):
        raise ValueError("All calculated financial metrics are non-positive")
    
    results = []
    
    # 2) Identify and apply each multiple in comps
    for col in comps.columns:
        if "/" not in col:
            continue  # Skip non-multiple columns
            
        try:
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
            
            results.append(result)
            
        except Exception as e:
            # Log error but continue with other multiples
            print(f"Error processing multiple '{col}': {str(e)}")
            continue
    
    if not results:
        raise ValueError(
            "No valid multiples found. Please check that the comparable companies "
            "DataFrame contains columns with format 'EV/Metric' or 'P/Metric'"
        )
    
    # 3) Return as DataFrame indexed by multiple name
    result_df = pd.DataFrame(results).set_index("Multiple")
    return result_df

def get_implied_valuation_summary(multiples_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate summary statistics for implied valuations from multiples analysis.
    
    Args:
        multiples_df: Results from run_multiples_analysis()
        
    Returns:
        Dictionary with summary statistics
    """
    if multiples_df.empty:
        return {}
    
    # Get all implied EV columns
    ev_columns = [col for col in multiples_df.columns if "Implied EV" in col]
    if not ev_columns:
        return {}
    
    # Calculate summary across all multiples
    all_evs = []
    for col in ev_columns:
        all_evs.extend(multiples_df[col].dropna().tolist())
    
    if not all_evs:
        return {}
    
    return {
        "mean_implied_ev": float(np.mean(all_evs)),
        "median_implied_ev": float(np.median(all_evs)),
        "std_implied_ev": float(np.std(all_evs)),
        "min_implied_ev": float(np.min(all_evs)),
        "max_implied_ev": float(np.max(all_evs)),
        "ev_range": float(np.max(all_evs) - np.min(all_evs)),
        "ev_cv": float(np.std(all_evs) / np.mean(all_evs)) if np.mean(all_evs) != 0 else 0.0
    } 