"""
Financial Projection Drivers Module

This module provides professional-grade financial projection functions for valuation analysis.
Contains comprehensive functions to project revenue, EBIT, and Free Cash Flow using
industry-standard methodologies and validation.

Key Functions:
- project_revenue_series: Builds revenue forecast from base values and growth rates
- project_ebit_series: Computes EBIT from revenues and margin
- project_free_cash_flow: Computes comprehensive Free Cash Flow with all components
"""

from typing import List, Optional
import numpy as np

def project_revenue_series(
    base_revenue_values: List[float], 
    annual_growth_rates: List[float]
) -> List[float]:
    """
    Project revenue series using year-over-year growth rates.
    
    This function supports two projection methodologies:
    
    1. Direct Growth Application:
       If len(annual_growth_rates) == len(base_revenue_values):
       projected_revenue[i] = base_revenue_values[i] * (1 + annual_growth_rates[i])
    
    2. Compound Growth Application:
       If len(annual_growth_rates) == len(base_revenue_values) - 1:
       projected_revenue[0] = base_revenue_values[0]
       projected_revenue[i] = projected_revenue[i-1] * (1 + annual_growth_rates[i-1]) for i = 1..n
    
    Args:
        base_revenue_values: List of base revenue values (USD)
        annual_growth_rates: List of annual growth rates (as decimals, e.g., 0.10 for 10%)
        
    Returns:
        List[float]: Projected revenue values (USD)
        
    Raises:
        ValueError: If growth_rates length is neither equal nor one less than base_revenue
        ValueError: If any growth rate is less than -1 (which would make revenue negative)
        ValueError: If base_revenue is empty or growth_rates is empty
    """
    if not base_revenue_values:
        raise ValueError("base_revenue_values cannot be empty")
    
    if not annual_growth_rates:
        raise ValueError("annual_growth_rates cannot be empty")
    
    # Validate growth rates for reasonableness
    for index, growth_rate in enumerate(annual_growth_rates):
        if growth_rate < -1:
            raise ValueError(
                f"Growth rate at index {index} ({growth_rate:.1%}) cannot be less than -100%"
            )
    
    if len(annual_growth_rates) == len(base_revenue_values):
        # Mode 1: Apply growth rate directly to each base revenue value
        projected_revenue = [
            base_revenue * (1 + growth_rate) 
            for base_revenue, growth_rate in zip(base_revenue_values, annual_growth_rates)
        ]
        return projected_revenue
        
    elif len(annual_growth_rates) == len(base_revenue_values) - 1:
        # Mode 2: Apply compound growth from first base revenue value
        projected_revenue = [base_revenue_values[0]]
        for growth_rate in annual_growth_rates:
            next_revenue = projected_revenue[-1] * (1 + growth_rate)
            projected_revenue.append(next_revenue)
        return projected_revenue
        
    else:
        raise ValueError(
            f"annual_growth_rates length ({len(annual_growth_rates)}) must be equal to "
            f"base_revenue_values length ({len(base_revenue_values)}) or one shorter "
            f"({len(base_revenue_values) - 1})"
        )

def project_ebit_series(
    revenue_series: List[float], 
    ebit_margin: float
) -> List[float]:
    """
    Compute EBIT series from revenue projections and margin.
    
    Calculates EBIT for each period using the formula:
    EBIT = Revenue × EBIT Margin
    
    Args:
        revenue_series: List of projected revenue values (USD)
        ebit_margin: EBIT margin as a decimal (e.g., 0.20 for 20%)
        
    Returns:
        List[float]: Projected EBIT values (USD)
        
    Raises:
        ValueError: If margin is negative or greater than 1
        ValueError: If revenue_series is empty
    """
    if not revenue_series:
        raise ValueError("revenue_series cannot be empty")
    
    if ebit_margin < 0 or ebit_margin > 1:
        raise ValueError(
            f"EBIT margin ({ebit_margin:.1%}) must be between 0% and 100%"
        )
    
    ebit_series = [revenue * ebit_margin for revenue in revenue_series]
    return ebit_series

def project_free_cash_flow(
    revenue_series: List[float],
    ebit_series: List[float],
    capital_expenditure: List[float],
    depreciation_expense: List[float],
    net_working_capital_changes: List[float],
    corporate_tax_rate: float,
    amortization_expense: Optional[List[float]] = None,
    other_non_cash_items: Optional[List[float]] = None,
    other_working_capital_items: Optional[List[float]] = None
) -> List[float]:
    """
    Compute comprehensive Free Cash Flow series using professional methodology.
    
    Uses the comprehensive FCF formula:
    FCF = NOPAT + Depreciation + Amortization + Other Non-Cash Items - CapEx - ΔNWC - Other WC
    where NOPAT = EBIT × (1 - corporate_tax_rate)
    
    This implementation follows industry best practices for FCF calculation,
    including all relevant cash flow components for accurate valuation.
    
    Args:
        revenue_series: List of revenue values (for validation purposes)
        ebit_series: List of EBIT values (USD)
        capital_expenditure: List of capital expenditure values (USD)
        depreciation_expense: List of depreciation values (USD)
        net_working_capital_changes: List of NWC changes (USD)
        corporate_tax_rate: Corporate tax rate as decimal (e.g., 0.21 for 21%)
        amortization_expense: List of amortization values (USD, optional, defaults to zeros)
        other_non_cash_items: List of other non-cash items (USD, optional, defaults to zeros)
        other_working_capital_items: List of other WC items (USD, optional, defaults to zeros)
        
    Returns:
        List[float]: Projected Free Cash Flow values (USD)
        
    Raises:
        ValueError: If any input list has different lengths
        ValueError: If corporate_tax_rate is negative or greater than 1
        ValueError: If any required input list is empty
    """
    # Validate required inputs
    required_inputs = [ebit_series, capital_expenditure, depreciation_expense, net_working_capital_changes]
    if not all(required_inputs):
        raise ValueError("All required input lists must be non-empty")
    
    if corporate_tax_rate < 0 or corporate_tax_rate > 1:
        raise ValueError(
            f"Corporate tax rate ({corporate_tax_rate:.1%}) must be between 0% and 100%"
        )
    
    # Set default values for optional parameters
    if amortization_expense is None:
        amortization_expense = [0.0] * len(ebit_series)
    if other_non_cash_items is None:
        other_non_cash_items = [0.0] * len(ebit_series)
    if other_working_capital_items is None:
        other_working_capital_items = [0.0] * len(ebit_series)
    
    # Validate that all input lists have consistent lengths
    input_lengths = [
        len(ebit_series), 
        len(capital_expenditure), 
        len(depreciation_expense), 
        len(net_working_capital_changes),
        len(amortization_expense), 
        len(other_non_cash_items), 
        len(other_working_capital_items)
    ]
    
    if len(set(input_lengths)) > 1:
        raise ValueError(
            f"All input lists must have the same length. "
            f"Lengths: EBIT={len(ebit_series)}, CapEx={len(capital_expenditure)}, "
            f"Depreciation={len(depreciation_expense)}, NWC Changes={len(net_working_capital_changes)}, "
            f"Amortization={len(amortization_expense)}, Other Non-Cash={len(other_non_cash_items)}, "
            f"Other Working Capital={len(other_working_capital_items)}"
        )
    
    # Calculate FCF for each period
    free_cash_flow_series = []
    for (ebit, capex, depreciation, nwc_change, amortization, 
         other_non_cash, other_wc) in zip(ebit_series, capital_expenditure, 
                                         depreciation_expense, net_working_capital_changes,
                                         amortization_expense, other_non_cash_items, 
                                         other_working_capital_items):
        
        # Calculate NOPAT (Net Operating Profit After Tax)
        net_operating_profit_after_tax = ebit * (1 - corporate_tax_rate)
        
        # Calculate comprehensive FCF
        free_cash_flow = (net_operating_profit_after_tax + depreciation + amortization + 
                         other_non_cash - capex - nwc_change - other_wc)
        
        free_cash_flow_series.append(free_cash_flow)
    
    return free_cash_flow_series

 