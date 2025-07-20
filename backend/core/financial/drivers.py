"""
Financial Projection Drivers Module

This module contains helper functions to project core financial series:
- project_revenue: Builds revenue forecast from base values and growth rates
- project_ebit: Computes EBIT from revenues and margin
- project_fcf: Computes Free Cash Flow from projected inputs

All functions include comprehensive validation and error handling.
"""

from typing import List
import numpy as np

def project_revenue(base_revenue: List[float], growth_rates: List[float]) -> List[float]:
    """
    Apply year-over-year growth rates to base revenue.
    
    Two projection modes:
    1. If len(growth_rates) == len(base_revenue):
       revenue[i] = base_revenue[i] * (1 + growth_rates[i])
    2. If len(growth_rates) == len(base_revenue) - 1:
       revenue[0] = base_revenue[0]
       revenue[i] = revenue[i-1] * (1 + growth_rates[i-1]) for i = 1..n
    
    Args:
        base_revenue: List of base revenue values
        growth_rates: List of growth rates (as decimals, e.g., 0.10 for 10%)
        
    Returns:
        List of projected revenue values
        
    Raises:
        ValueError: If growth_rates length is neither equal nor one less than base_revenue
        ValueError: If any growth rate is less than -1 (which would make revenue negative)
        ValueError: If base_revenue is empty
    """
    if not base_revenue:
        raise ValueError("base_revenue cannot be empty")
    
    if not growth_rates:
        raise ValueError("growth_rates cannot be empty")
    
    # Validate growth rates
    for i, rate in enumerate(growth_rates):
        if rate < -1:
            raise ValueError(f"Growth rate at index {i} ({rate:.1%}) cannot be less than -100%")
    
    if len(growth_rates) == len(base_revenue):
        # Mode 1: Apply growth rate to each base revenue
        return [r * (1 + g) for r, g in zip(base_revenue, growth_rates)]
    elif len(growth_rates) == len(base_revenue) - 1:
        # Mode 2: Compound growth from first base revenue
        rev_forecast = [base_revenue[0]]
        for g in growth_rates:
            rev_forecast.append(rev_forecast[-1] * (1 + g))
        return rev_forecast
    else:
        raise ValueError(
            f"growth_rates length ({len(growth_rates)}) must be same as base_revenue length "
            f"({len(base_revenue)}) or one shorter ({len(base_revenue) - 1})"
        )

def project_ebit(revenue: List[float], margin: float) -> List[float]:
    """
    Compute EBIT = revenue × ebit_margin for each year.
    
    Args:
        revenue: List of revenue values
        margin: EBIT margin as a decimal (e.g., 0.20 for 20%)
        
    Returns:
        List of EBIT values
        
    Raises:
        ValueError: If margin is negative or greater than 1
        ValueError: If revenue list is empty
    """
    if not revenue:
        raise ValueError("revenue list cannot be empty")
    
    if margin < 0 or margin > 1:
        raise ValueError(f"EBIT margin ({margin:.1%}) must be between 0% and 100%")
    
    return [r * margin for r in revenue]

def project_fcf(
    revenue: List[float],
    ebit: List[float],
    capex: List[float],
    depreciation: List[float],
    nwc_changes: List[float],
    tax_rate: float
) -> List[float]:
    """
    Compute Free Cash Flow per year using the formula:
    FCF = NOPAT + Depreciation - CapEx - ΔNWC
    where NOPAT = EBIT × (1 - tax_rate)
    
    Args:
        revenue: List of revenue values (for validation)
        ebit: List of EBIT values
        capex: List of capital expenditure values
        depreciation: List of depreciation values
        nwc_changes: List of net working capital changes
        tax_rate: Tax rate as a decimal (e.g., 0.21 for 21%)
        
    Returns:
        List of Free Cash Flow values
        
    Raises:
        ValueError: If any input list has different lengths
        ValueError: If tax_rate is negative or greater than 1
        ValueError: If any input list is empty
    """
    # Validate inputs
    if not all([ebit, capex, depreciation, nwc_changes]):
        raise ValueError("All input lists must be non-empty")
    
    if tax_rate < 0 or tax_rate > 1:
        raise ValueError(f"Tax rate ({tax_rate:.1%}) must be between 0% and 100%")
    
    # Check that all lists have the same length
    lengths = [len(ebit), len(capex), len(depreciation), len(nwc_changes)]
    if len(set(lengths)) > 1:
        raise ValueError(
            f"All input lists must have the same length. "
            f"Lengths: EBIT={len(ebit)}, CapEx={len(capex)}, "
            f"Depreciation={len(depreciation)}, NWC Changes={len(nwc_changes)}"
        )
    
    fcf = []
    for e, c, d, delta_nwc in zip(ebit, capex, depreciation, nwc_changes):
        nopat = e * (1 - tax_rate)
        fcf.append(nopat + d - c - delta_nwc)
    
    return fcf 