"""
Valuation Module

This module contains the core valuation functions for DCF analysis:
- calc_dcf_series: Standard DCF using WACC method
- calc_apv: Adjusted Present Value method

Both functions support either direct FCF series input or driver-based projections.
"""

from typing import Tuple, Optional
import numpy as np

from drivers import project_ebit, project_fcf
from params import ValuationParams

def calc_dcf_series(params: ValuationParams) -> Tuple[float, float, Optional[float]]:
    """
    Calculate DCF valuation using the WACC method.
    
    Supports two input modes:
    1. Direct FCF series (if params.fcf_series is provided)
    2. Driver-based projection (using revenue, margins, capex, etc.)
    
    Args:
        params: ValuationParams object containing all valuation inputs
        
    Returns:
        Tuple of (Enterprise Value, Equity Value, Price per Share)
        Price per Share will be None if share_count is not provided
        
    Raises:
        ValueError: If terminal growth >= WACC (Gordon growth model constraint)
        ValueError: If no FCF series can be calculated
    """
    # Validate terminal growth constraint
    if params.terminal_growth >= params.wacc:
        raise ValueError(
            f"Terminal growth rate ({params.terminal_growth:.1%}) must be less than WACC ({params.wacc:.1%}) "
            "for Gordon growth model to be valid"
        )
    
    # Additional terminal value sanity checks (warnings will be handled in app.py)
    if params.terminal_growth > 0.05:  # 5% growth
        pass  # Warning will be shown in UI
    if params.terminal_growth < -0.02:  # -2% growth
        pass  # Warning will be shown in UI
    
    # 1) Determine FCF series
    if params.fcf_series:
        fcfs = params.fcf_series
    else:
        # Validate that we have all required inputs for driver-based projection
        if not params.revenue or not params.capex or not params.depreciation or not params.nwc_changes:
            raise ValueError("No FCF series available for valuation")
        
        # Project revenue → EBIT → FCF
        ebits = project_ebit(params.revenue, params.ebit_margin)
        fcfs = project_fcf(
            params.revenue,
            ebits,
            params.capex,
            params.depreciation,
            params.nwc_changes,
            params.tax_rate
        )
    
    if not fcfs:
        raise ValueError("No FCF series available for valuation")
    
    # 2) Discount each FCF
    if params.mid_year_convention:
        # Mid-year convention: cash flows occur at middle of year
        discount_factors = [(1 + params.wacc) ** (i + 0.5) for i in range(len(fcfs))]
    else:
        # Year-end convention: cash flows occur at end of year
        discount_factors = [(1 + params.wacc) ** (i + 1) for i in range(len(fcfs))]
    
    pv_fcfs = [f / df for f, df in zip(fcfs, discount_factors)]

    # 3) Terminal value via Gordon growth model
    last_fcf = fcfs[-1]
    tv = last_fcf * (1 + params.terminal_growth) / (params.wacc - params.terminal_growth)
    
    if params.mid_year_convention:
        # Terminal value starts at middle of year after last forecast
        pv_tv = tv / ((1 + params.wacc) ** (len(fcfs) + 0.5))
    else:
        # Terminal value starts at end of year after last forecast
        pv_tv = tv / ((1 + params.wacc) ** (len(fcfs) + 1))

    # 4) Enterprise value = PV of FCFs + PV of terminal value
    ev = sum(pv_fcfs) + pv_tv

    # 5) Equity value = Enterprise value - Net debt
    net_debt = params.debt_schedule.get(0, 0.0)
    equity = ev - net_debt

    # 6) Price per share = Equity value / Number of shares
    ps = equity / params.share_count if params.share_count and params.share_count > 0 else None

    return ev, equity, ps


def calc_apv(params: ValuationParams) -> Tuple[float, float, Optional[float]]:
    """
    Calculate DCF valuation using the Adjusted Present Value (APV) method.
    
    APV method:
    1. Calculate unlevered enterprise value (all-equity DCF)
    2. Add present value of interest tax shields
    3. Subtract net debt to get equity value
    
    Args:
        params: ValuationParams object containing all valuation inputs
        
    Returns:
        Tuple of (Enterprise Value, Equity Value, Price per Share)
        Price per Share will be None if share_count is not provided
        
    Raises:
        ValueError: If cost of debt is not provided and cannot be inferred
    """
    # 1) Base all-equity DCF (zero out debt schedule)
    params_dict = vars(params).copy()
    params_dict['debt_schedule'] = {}
    base_params = ValuationParams(**params_dict)
    ev_unlevered, _, _ = calc_dcf_series(base_params)

    # 2) PV of interest tax shields
    # Use cost of debt if provided, otherwise use WACC as approximation
    cod = params.cost_of_debt if params.cost_of_debt > 0 else params.wacc
    
    shields_pv = 0.0
    for year, debt in params.debt_schedule.items():
        if debt > 0:  # Only calculate shields for positive debt
            interest = debt * cod
            shield = interest * params.tax_rate
            # Tax shields should be discounted at cost of debt, not WACC
            # +1 for year-end convention
            shields_pv += shield / ((1 + cod) ** (year + 1))

    # 3) Levered enterprise value = Unlevered EV + PV of tax shields
    ev_apv = ev_unlevered + shields_pv

    # 4) Equity value = Levered EV - Net debt
    net_debt = params.debt_schedule.get(0, 0.0)
    equity_apv = ev_apv - net_debt
    
    # 5) Price per share
    ps_apv = equity_apv / params.share_count if params.share_count and params.share_count > 0 else None

    return ev_apv, equity_apv, ps_apv
