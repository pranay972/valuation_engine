"""
Valuation Module

This module contains the core valuation functions for DCF analysis:
- calc_dcf_series: Standard DCF using WACC method
- calc_apv: Adjusted Present Value method

Both functions support either direct FCF series input or driver-based projections.
"""

from typing import Tuple, Optional
import numpy as np

from ...core.financial.drivers import project_ebit, project_fcf
from ...core.models.params import ValuationParams
from ...utils.exceptions import CalculationError, InvalidInputError, DataValidationError
from ...utils.validation import validate_financial_data, validate_valuation_params
from ...config.logging import get_logger
from ...utils.cache import cached
from ...core.financial.wacc import calculate_unlevered_cost_of_equity as calc_unlevered_cost

logger = get_logger(__name__)

def calculate_unlevered_cost_of_equity(params: ValuationParams) -> float:
    """
    Calculate unlevered cost of equity for APV method.
    Uses Hamada equation if sufficient data is available, otherwise approximates with WACC.
    """
    # If unlevered cost of equity is explicitly provided, use it
    if params.unlevered_cost_of_equity > 0:
        return params.unlevered_cost_of_equity
    
    # Calculate debt ratio for Hamada equation
    if params.debt_schedule and params.revenue:
        terminal_year = len(params.revenue) - 1
        terminal_debt = params.debt_schedule.get(terminal_year, 0.0)
        
        # Estimate equity value (this is a rough approximation)
        # In practice, you'd need the actual market value of equity
        estimated_equity_value = params.share_count * 10  # Rough estimate
        total_value = estimated_equity_value + terminal_debt
        
        if total_value > 0:
            debt_ratio = terminal_debt / total_value
            
            # Use Hamada equation: unlevered_cost = cost_of_equity - (debt_ratio * cost_of_debt * (1-tax_rate))
            # For now, assume cost_of_equity ≈ WACC (this is an approximation)
            unlevered_cost = calc_unlevered_cost(
                params.wacc,  # Approximate cost of equity
                debt_ratio,
                params.cost_of_debt,
                params.tax_rate
            )
            return unlevered_cost
    
    # Fallback: use WACC as approximation (not ideal but maintains functionality)
    return params.wacc

def calculate_net_debt_for_valuation(params: ValuationParams) -> float:
    """
    Calculate appropriate net debt for valuation.
    Uses terminal debt level if available, otherwise current debt.
    """
    if not params.debt_schedule:
        return 0.0
    
    # Use terminal debt level (most common approach)
    if params.revenue:
        terminal_year = len(params.revenue) - 1
        terminal_debt = params.debt_schedule.get(terminal_year, 0.0)
        if terminal_debt > 0:
            return terminal_debt
    
    # Fallback to current debt (year 0)
    return params.debt_schedule.get(0, 0.0)

@cached
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
        CalculationError: If terminal growth >= WACC (Gordon growth model constraint)
        CalculationError: If no FCF series can be calculated
        InvalidInputError: If input parameters are invalid
    """
    logger.debug(f"Starting DCF calculation with WACC: {params.wacc:.1%}, terminal growth: {params.terminal_growth:.1%}")
    
    try:
        # Validate input parameters
        validate_valuation_params({
            "wacc": params.wacc,
            "terminal_growth": params.terminal_growth,
            "tax_rate": params.tax_rate
        })
        
        # Validate terminal growth constraint
        if params.terminal_growth >= params.wacc:
            raise CalculationError(
                f"Terminal growth rate ({params.terminal_growth:.1%}) must be less than WACC ({params.wacc:.1%}) "
                "for Gordon growth model to be valid",
                calculation_type="DCF",
                params={"wacc": params.wacc, "terminal_growth": params.terminal_growth}
            )
    
        # Additional terminal value sanity checks (warnings will be handled in app.py)
        if params.terminal_growth > 0.05:  # 5% growth
            logger.warning(f"High terminal growth rate: {params.terminal_growth:.1%}")
        if params.terminal_growth < -0.02:  # -2% growth
            logger.warning(f"Low terminal growth rate: {params.terminal_growth:.1%}")
        
        # 1) Determine FCF series
        if params.fcf_series:
            validate_financial_data(params.fcf_series, "fcf_series")
            fcfs = params.fcf_series
        else:
            # Validate that we have all required inputs for driver-based projection
            if not params.revenue or not params.capex or not params.depreciation or not params.nwc_changes:
                raise CalculationError(
                    "No FCF series available for valuation. Please provide either fcf_series or all driver-based inputs.",
                    calculation_type="DCF"
                )
            
            # Validate financial data
            validate_financial_data(params.revenue, "revenue")
            validate_financial_data(params.capex, "capex")
            validate_financial_data(params.depreciation, "depreciation")
            validate_financial_data(params.nwc_changes, "nwc_changes")
            
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
            raise CalculationError(
                "No FCF series available for valuation",
                calculation_type="DCF"
            )
    
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

        # 5) Equity value = Enterprise value - Net debt (using improved debt calculation)
        net_debt = calculate_net_debt_for_valuation(params)
        equity = ev - net_debt

        # 6) Price per share = Equity value / Number of shares
        ps = equity / params.share_count if params.share_count and params.share_count > 0 else None

        logger.debug(f"DCF calculation completed - EV: ${ev:,.0f}, Equity: ${equity:,.0f}")
        return ev, equity, ps
        
    except Exception as e:
        logger.error(f"DCF calculation failed: {str(e)}")
        raise


def calc_apv(params: ValuationParams) -> Tuple[float, float, Optional[float]]:
    """
    Calculate DCF valuation using the Adjusted Present Value (APV) method.
    
    APV method:
    1. Calculate unlevered enterprise value (all-equity DCF using unlevered cost of equity)
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
    # 1) Calculate unlevered cost of equity
    unlevered_cost_of_equity = calculate_unlevered_cost_of_equity(params)
    
    # 2) Calculate unlevered FCF (same as WACC method)
    if params.fcf_series:
        validate_financial_data(params.fcf_series, "fcf_series")
        unlevered_fcfs = params.fcf_series
    else:
        # Validate that we have all required inputs for driver-based projection
        if not params.revenue or not params.capex or not params.depreciation or not params.nwc_changes:
            raise CalculationError(
                "No FCF series available for APV valuation. Please provide either fcf_series or all driver-based inputs.",
                calculation_type="APV"
            )
        
        # Validate financial data
        validate_financial_data(params.revenue, "revenue")
        validate_financial_data(params.capex, "capex")
        validate_financial_data(params.depreciation, "depreciation")
        validate_financial_data(params.nwc_changes, "nwc_changes")
        
        # Project revenue → EBIT → FCF
        ebits = project_ebit(params.revenue, params.ebit_margin)
        unlevered_fcfs = project_fcf(
            params.revenue,
            ebits,
            params.capex,
            params.depreciation,
            params.nwc_changes,
            params.tax_rate
        )
    
    if not unlevered_fcfs:
        raise CalculationError(
            "No unlevered FCF series available for APV valuation",
            calculation_type="APV"
        )

    # 3) Discount unlevered FCFs at unlevered cost of equity
    if params.mid_year_convention:
        discount_factors = [(1 + unlevered_cost_of_equity) ** (i + 0.5) for i in range(len(unlevered_fcfs))]
    else:
        discount_factors = [(1 + unlevered_cost_of_equity) ** (i + 1) for i in range(len(unlevered_fcfs))]
    
    pv_unlevered_fcfs = [f / df for f, df in zip(unlevered_fcfs, discount_factors)]

    # 4) Terminal value for unlevered FCFs
    last_unlevered_fcf = unlevered_fcfs[-1]
    unlevered_tv = last_unlevered_fcf * (1 + params.terminal_growth) / (unlevered_cost_of_equity - params.terminal_growth)
    
    if params.mid_year_convention:
        pv_unlevered_tv = unlevered_tv / ((1 + unlevered_cost_of_equity) ** (len(unlevered_fcfs) + 0.5))
    else:
        pv_unlevered_tv = unlevered_tv / ((1 + unlevered_cost_of_equity) ** (len(unlevered_fcfs) + 1))

    # 5) Unlevered enterprise value
    unlevered_ev = sum(pv_unlevered_fcfs) + pv_unlevered_tv

    # 6) Calculate tax shields (if debt schedule is provided)
    pv_tax_shields = 0.0
    if params.debt_schedule and params.cost_of_debt > 0:
        for year, debt in params.debt_schedule.items():
            if debt > 0:
                interest = debt * params.cost_of_debt
                tax_shield = interest * params.tax_rate
                
                # Discount tax shield at cost of debt (risk-free rate)
                if params.mid_year_convention:
                    pv_tax_shield = tax_shield / ((1 + params.cost_of_debt) ** (year + 0.5))
                else:
                    pv_tax_shield = tax_shield / ((1 + params.cost_of_debt) ** (year + 1))
                
                pv_tax_shields += pv_tax_shield

    # 7) APV Enterprise Value = Unlevered EV + PV of tax shields
    apv_ev = unlevered_ev + pv_tax_shields

    # 8) Equity value = APV Enterprise Value - Net debt
    net_debt = calculate_net_debt_for_valuation(params)
    equity = apv_ev - net_debt

    # 9) Price per share = Equity value / Number of shares
    ps = equity / params.share_count if params.share_count and params.share_count > 0 else None

    return apv_ev, equity, ps 