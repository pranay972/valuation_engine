"""
Discounted Cash Flow (DCF) Valuation Module

This module provides professional-grade DCF valuation functions using industry-standard
methodologies. Includes both WACC-based DCF and Adjusted Present Value (APV) approaches
with comprehensive validation and professional best practices.

Key Functions:
- calculate_dcf_valuation_wacc: Standard DCF using WACC methodology
- calculate_adjusted_present_value: APV method separating unlevered value and tax shields
- calculate_net_debt_for_valuation: Calculate net debt for valuation purposes
- validate_terminal_value_assumptions: Professional validation of terminal value inputs
- calculate_present_value_of_tax_shields: Calculate PV of interest tax shields for APV
"""

from typing import Tuple, Optional, Dict, List
import numpy as np

from drivers import project_ebit_series, project_free_cash_flow
from params import ValuationParameters
from wacc import calculate_unlevered_cost_of_equity, calculate_iterative_wacc

def calculate_net_debt_for_valuation(valuation_parameters: ValuationParameters) -> float:
    """
    Calculate net debt for valuation purposes using current market values.
    
    Net debt is calculated as current debt minus cash and cash equivalents,
    which represents the true debt burden for valuation purposes.
    
    Args:
        valuation_parameters: ValuationParameters object containing debt and cash information
        
    Returns:
        float: Net debt value (USD)
    """
    current_debt = valuation_parameters.debt_schedule.get(0, 0.0)
    net_debt = current_debt - valuation_parameters.cash_and_equivalents
    return net_debt

def validate_terminal_value_assumptions(valuation_parameters: ValuationParameters):
    """
    Validate terminal value assumptions for professional standards.
    
    This function performs comprehensive validation of terminal value inputs
    to ensure they meet professional valuation standards and are economically reasonable.
    
    Args:
        valuation_parameters: ValuationParameters object containing terminal value inputs
        
    Raises:
        ValueError: If terminal value assumptions are unreasonable
        Warning: If terminal ROIC appears unrealistically high
    """
    # Validate terminal growth rate reasonableness
    if valuation_parameters.terminal_growth_rate > 0.05:
        raise ValueError(
            f"Terminal growth rate ({valuation_parameters.terminal_growth_rate:.1%}) "
            f"should typically not exceed 5% for sustainable long-term growth"
        )
    
    # Validate terminal growth vs WACC constraint
    if valuation_parameters.terminal_growth_rate >= valuation_parameters.weighted_average_cost_of_capital:
        raise ValueError(
            f"Terminal growth rate ({valuation_parameters.terminal_growth_rate:.1%}) "
            f"must be less than WACC ({valuation_parameters.weighted_average_cost_of_capital:.1%}) "
            f"for valid terminal value calculation"
        )
    
    # Optional check for terminal ROIC reasonableness
    if (valuation_parameters.terminal_growth_rate > 0 and 
        valuation_parameters.weighted_average_cost_of_capital > valuation_parameters.terminal_growth_rate):
        
        terminal_return_on_invested_capital = (
            valuation_parameters.terminal_growth_rate / 
            (1 - valuation_parameters.terminal_growth_rate / valuation_parameters.weighted_average_cost_of_capital)
        )
        
        if terminal_return_on_invested_capital > 0.25:  # 25% ROIC is very high
            print(
                f"Warning: Terminal ROIC of {terminal_return_on_invested_capital:.1%} "
                f"appears unrealistically high for sustainable long-term performance"
            )

def calculate_dcf_valuation_wacc(valuation_parameters: ValuationParameters) -> Tuple[float, float, Optional[float], List[float], float, float]:
    """
    Calculate DCF valuation using the WACC (Weighted Average Cost of Capital) method.
    
    This function implements the standard DCF methodology used in professional valuation:
    1. Project free cash flows
    2. Calculate WACC using target capital structure or iterative approach
    3. Discount FCFs to present value
    4. Calculate terminal value using Gordon Growth Model
    5. Sum PV of FCFs and PV of terminal value to get enterprise value
    
    Args:
        valuation_parameters: ValuationParameters object with all required inputs
        
    Returns:
        Tuple containing:
        - float: Enterprise value (USD)
        - float: Equity value (USD)
        - Optional[float]: Price per share (USD)
        - List[float]: Free cash flow series (USD)
        - float: Terminal value (USD)
        - float: Present value of terminal value (USD)
        
    Raises:
        ValueError: If terminal value assumptions are invalid
        ValueError: If insufficient data for FCF projection
    """
    # Validate terminal value assumptions
    validate_terminal_value_assumptions(valuation_parameters)
    
    # Step 1: Determine free cash flow series
    if valuation_parameters.free_cash_flow_series:
        free_cash_flow_series = valuation_parameters.free_cash_flow_series
    else:
        # Validate that we have all required inputs for driver-based projection
        required_inputs = [
            valuation_parameters.revenue_projections,
            valuation_parameters.capital_expenditure,
            valuation_parameters.depreciation_expense,
            valuation_parameters.net_working_capital_changes
        ]
        
        if not all(required_inputs):
            raise ValueError(
                "No FCF series available for valuation. Please provide either "
                "free_cash_flow_series or all driver-based inputs."
            )
        
        # Project revenue → EBIT → FCF using professional methodology
        ebit_series = project_ebit_series(
            valuation_parameters.revenue_projections, 
            valuation_parameters.ebit_margin
        )
        
        free_cash_flow_series = project_free_cash_flow(
            valuation_parameters.revenue_projections,
            ebit_series,
            valuation_parameters.capital_expenditure,
            valuation_parameters.depreciation_expense,
            valuation_parameters.net_working_capital_changes,
            valuation_parameters.corporate_tax_rate,
            valuation_parameters.amortization_expense,
            valuation_parameters.other_non_cash_items,
            valuation_parameters.other_working_capital_items
        )
    
    if not free_cash_flow_series:
        raise ValueError("No free cash flow series available for valuation")
    
    # Step 2: Calculate WACC using target capital structure or iterative approach
    weighted_average_cost_of_capital = calculate_iterative_wacc(valuation_parameters)
    
    # Step 3: Discount each FCF to present value
    if valuation_parameters.use_mid_year_convention:
        # Mid-year convention: cash flows occur at middle of year
        discount_factors = [
            (1 + weighted_average_cost_of_capital) ** (period + 0.5) 
            for period in range(len(free_cash_flow_series))
        ]
    else:
        # Year-end convention: cash flows occur at end of year
        discount_factors = [
            (1 + weighted_average_cost_of_capital) ** (period + 1) 
            for period in range(len(free_cash_flow_series))
        ]
    
    present_value_of_fcfs = [
        fcf / discount_factor 
        for fcf, discount_factor in zip(free_cash_flow_series, discount_factors)
    ]

    # Step 4: Calculate terminal value using Gordon Growth Model
    terminal_fcf = free_cash_flow_series[-1]
    terminal_value = (
        terminal_fcf * (1 + valuation_parameters.terminal_growth_rate) / 
        (weighted_average_cost_of_capital - valuation_parameters.terminal_growth_rate)
    )
    
    if valuation_parameters.use_mid_year_convention:
        # Terminal value starts at middle of year after last forecast
        present_value_of_terminal = terminal_value / (
            (1 + weighted_average_cost_of_capital) ** (len(free_cash_flow_series) + 0.5)
        )
    else:
        # Terminal value starts at end of year after last forecast
        present_value_of_terminal = terminal_value / (
            (1 + weighted_average_cost_of_capital) ** (len(free_cash_flow_series) + 1)
        )

    # Step 5: Calculate enterprise value
    enterprise_value = sum(present_value_of_fcfs) + present_value_of_terminal

    # Step 6: Calculate equity value and price per share
    net_debt = calculate_net_debt_for_valuation(valuation_parameters)
    equity_value = enterprise_value - net_debt
    
    price_per_share = (
        equity_value / valuation_parameters.shares_outstanding 
        if valuation_parameters.shares_outstanding and valuation_parameters.shares_outstanding > 0 
        else None
    )

    return (
        enterprise_value, 
        equity_value, 
        price_per_share, 
        free_cash_flow_series, 
        terminal_value, 
        present_value_of_terminal
    )

def calculate_present_value_of_tax_shields(
    debt_schedule: Dict[int, float], 
    cost_of_debt: float, 
    corporate_tax_rate: float, 
    unlevered_cost_of_equity: float,
    use_mid_year_convention: bool = False
) -> float:
    """
    Calculate present value of interest tax shields for APV valuation.
    
    This function calculates the present value of interest tax shields that arise
    from debt financing. Tax shields are discounted at the unlevered cost of equity,
    which is the appropriate discount rate for tax shield valuation in APV methodology.
    
    Formula: PV(Tax Shields) = Σ[Interest Expense × Tax Rate / (1 + Unlevered Cost of Equity)^t]
    
    Args:
        debt_schedule: Dictionary mapping year to debt level (USD)
        cost_of_debt: Cost of debt as decimal
        corporate_tax_rate: Corporate tax rate as decimal
        unlevered_cost_of_equity: Unlevered cost of equity as decimal
        use_mid_year_convention: Whether to use mid-year discounting convention
        
    Returns:
        float: Present value of tax shields (USD)
    """
    present_value_of_tax_shields = 0.0
    
    for year, debt_level in debt_schedule.items():
        if debt_level > 0:
            interest_expense = debt_level * cost_of_debt
            tax_shield = interest_expense * corporate_tax_rate
            
            # Discount at unlevered cost of equity (not cost of debt)
            if use_mid_year_convention:
                discount_factor = (1 + unlevered_cost_of_equity) ** (year + 0.5)
            else:
                discount_factor = (1 + unlevered_cost_of_equity) ** (year + 1)
            
            present_value_of_tax_shields += tax_shield / discount_factor
    
    return present_value_of_tax_shields

def calculate_adjusted_present_value(valuation_parameters: ValuationParameters) -> Tuple[float, float, Optional[float], Dict[str, float]]:
    """
    Calculate DCF valuation using the Adjusted Present Value (APV) method.
    
    APV separates the valuation into two components:
    1. Unlevered enterprise value (value assuming all-equity financing)
    2. Present value of interest tax shields
    
    This approach is particularly useful when capital structure is expected to change
    significantly over time or when tax shield valuation is complex.
    
    Args:
        valuation_parameters: ValuationParameters object with all required inputs
        
    Returns:
        Tuple containing:
        - float: Enterprise value (USD)
        - float: Equity value (USD)
        - Optional[float]: Price per share (USD)
        - Dict[str, float]: APV components breakdown
        
    Raises:
        ValueError: If insufficient data for valuation
    """
    # Step 1: Calculate unlevered cost of equity using proper Hamada equation
    unlevered_cost_of_equity = valuation_parameters.calculate_unlevered_cost_of_equity()
    
    # Step 2: Calculate unlevered FCF (same as WACC method)
    if valuation_parameters.free_cash_flow_series:
        unlevered_fcf_series = valuation_parameters.free_cash_flow_series
    else:
        # Validate that we have all required inputs for driver-based projection
        required_inputs = [
            valuation_parameters.revenue_projections,
            valuation_parameters.capital_expenditure,
            valuation_parameters.depreciation_expense,
            valuation_parameters.net_working_capital_changes
        ]
        
        if not all(required_inputs):
            raise ValueError(
                "No FCF series available for APV valuation. Please provide either "
                "free_cash_flow_series or all driver-based inputs."
            )
        
        # Project revenue → EBIT → FCF
        ebit_series = project_ebit_series(
            valuation_parameters.revenue_projections, 
            valuation_parameters.ebit_margin
        )
        
        unlevered_fcf_series = project_free_cash_flow(
            valuation_parameters.revenue_projections,
            ebit_series,
            valuation_parameters.capital_expenditure,
            valuation_parameters.depreciation_expense,
            valuation_parameters.net_working_capital_changes,
            valuation_parameters.corporate_tax_rate,
            valuation_parameters.amortization_expense,
            valuation_parameters.other_non_cash_items,
            valuation_parameters.other_working_capital_items
        )
    
    if not unlevered_fcf_series:
        raise ValueError("No FCF series available for APV valuation")
    
    # Step 3: Discount unlevered FCFs using unlevered cost of equity
    if valuation_parameters.use_mid_year_convention:
        discount_factors = [
            (1 + unlevered_cost_of_equity) ** (period + 0.5) 
            for period in range(len(unlevered_fcf_series))
        ]
    else:
        discount_factors = [
            (1 + unlevered_cost_of_equity) ** (period + 1) 
            for period in range(len(unlevered_fcf_series))
        ]
    
    present_value_of_unlevered_fcfs = [
        fcf / discount_factor 
        for fcf, discount_factor in zip(unlevered_fcf_series, discount_factors)
    ]
    
    # Step 4: Calculate terminal value using unlevered cost of equity
    terminal_unlevered_fcf = unlevered_fcf_series[-1]
    terminal_value = (
        terminal_unlevered_fcf * (1 + valuation_parameters.terminal_growth_rate) / 
        (unlevered_cost_of_equity - valuation_parameters.terminal_growth_rate)
    )
    
    if valuation_parameters.use_mid_year_convention:
        present_value_of_terminal = terminal_value / (
            (1 + unlevered_cost_of_equity) ** (len(unlevered_fcf_series) + 0.5)
        )
    else:
        present_value_of_terminal = terminal_value / (
            (1 + unlevered_cost_of_equity) ** (len(unlevered_fcf_series) + 1)
        )
    
    # Step 5: Calculate unlevered enterprise value
    unlevered_enterprise_value = sum(present_value_of_unlevered_fcfs) + present_value_of_terminal
    
    # Step 6: Calculate present value of interest tax shields
    present_value_of_tax_shields = calculate_present_value_of_tax_shields(
        valuation_parameters.debt_schedule, 
        valuation_parameters.cost_of_debt, 
        valuation_parameters.corporate_tax_rate, 
        unlevered_cost_of_equity,
        valuation_parameters.use_mid_year_convention
    )
    
    # Step 7: Calculate total enterprise value
    enterprise_value = unlevered_enterprise_value + present_value_of_tax_shields
    
    # Step 8: Calculate equity value and price per share
    net_debt = calculate_net_debt_for_valuation(valuation_parameters)
    equity_value = enterprise_value - net_debt
    
    price_per_share = (
        equity_value / valuation_parameters.shares_outstanding 
        if valuation_parameters.shares_outstanding and valuation_parameters.shares_outstanding > 0 
        else None
    )
    
    # Step 9: Prepare APV components for return
    apv_components = {
        "value_unlevered": unlevered_enterprise_value,
        "pv_tax_shield": present_value_of_tax_shields,
        "unlevered_cost_of_equity": unlevered_cost_of_equity,
        "unlevered_fcfs": unlevered_fcf_series
    }
    
    return enterprise_value, equity_value, price_per_share, apv_components 