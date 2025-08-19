"""
Weighted Average Cost of Capital (WACC) Calculator Module

This module provides professional-grade WACC calculation functions using industry-standard
methodologies. Includes functions for resolving circular dependency issues and implementing
the Hamada equation for unlevered/levered beta calculations.

Key Functions:
- calculate_cost_of_equity_capm: Calculate cost of equity using CAPM
- calculate_weighted_average_cost_of_capital: Calculate WACC from components
- calculate_wacc_target_capital_structure: Calculate WACC using target capital structure
- calculate_unlevered_cost_of_equity: Calculate unlevered cost of equity using Hamada equation
- calculate_levered_cost_of_equity: Calculate levered cost of equity using Hamada equation
- calculate_iterative_wacc: Resolve circular dependency in WACC calculation
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from params import ValuationParameters

def calculate_cost_of_equity_capm(
    risk_free_rate: float, 
    equity_beta: float, 
    equity_risk_premium: float
) -> float:
    """
    Calculate cost of equity using the Capital Asset Pricing Model (CAPM).
    
    Formula: Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium
    
    This is the industry-standard approach for calculating cost of equity
    in corporate finance and valuation analysis.
    
    Args:
        risk_free_rate: Risk-free rate as decimal (e.g., 0.03 for 3%)
        equity_beta: Equity beta (systematic risk measure)
        equity_risk_premium: Market equity risk premium as decimal (e.g., 0.06 for 6%)
        
    Returns:
        float: Cost of equity as decimal
        
    Raises:
        ValueError: If any input is negative
    """
    if risk_free_rate < 0 or equity_beta < 0 or equity_risk_premium < 0:
        raise ValueError("All CAPM inputs must be non-negative")
    
    cost_of_equity = risk_free_rate + equity_beta * equity_risk_premium
    return cost_of_equity

def calculate_weighted_average_cost_of_capital(
    market_value_of_equity: float, 
    market_value_of_debt: float, 
    cost_of_equity: float, 
    cost_of_debt: float, 
    corporate_tax_rate: float
) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC) from market values.
    
    Formula: WACC = (E/V × Re) + (D/V × Rd × (1-T))
    where:
    - E = Market value of equity
    - D = Market value of debt
    - V = Total enterprise value (E + D)
    - Re = Cost of equity
    - Rd = Cost of debt
    - T = Corporate tax rate
    
    Args:
        market_value_of_equity: Market value of equity (USD)
        market_value_of_debt: Market value of debt (USD)
        cost_of_equity: Cost of equity as decimal
        cost_of_debt: Cost of debt as decimal
        corporate_tax_rate: Corporate tax rate as decimal
        
    Returns:
        float: WACC as decimal
        
    Raises:
        ValueError: If total enterprise value is zero
    """
    total_enterprise_value = market_value_of_equity + market_value_of_debt
    
    if total_enterprise_value == 0:
        raise ValueError("Total enterprise value cannot be zero")
    
    equity_weight = market_value_of_equity / total_enterprise_value
    debt_weight = market_value_of_debt / total_enterprise_value
    
    weighted_average_cost_of_capital = (
        equity_weight * cost_of_equity + 
        debt_weight * cost_of_debt * (1 - corporate_tax_rate)
    )
    
    return weighted_average_cost_of_capital

def calculate_wacc_target_capital_structure(
    target_debt_to_value_ratio: float, 
    cost_of_equity: float, 
    cost_of_debt: float, 
    corporate_tax_rate: float
) -> float:
    """
    Calculate WACC using target capital structure (avoids circular dependency).
    
    This approach uses target capital structure ratios rather than current market values,
    which is the preferred method in professional valuation practice as it avoids
    the circular dependency problem where WACC depends on market values that are
    themselves outputs of the DCF valuation.
    
    Formula: WACC = (1 - D/V) × Re + (D/V) × Rd × (1-T)
    where D/V is the target debt-to-value ratio.
    
    Args:
        target_debt_to_value_ratio: Target debt-to-value ratio as decimal (e.g., 0.30 for 30%)
        cost_of_equity: Cost of equity as decimal
        cost_of_debt: Cost of debt as decimal
        corporate_tax_rate: Corporate tax rate as decimal
        
    Returns:
        float: WACC as decimal
        
    Raises:
        ValueError: If target debt ratio is outside valid range [0, 1]
    """
    if target_debt_to_value_ratio < 0 or target_debt_to_value_ratio > 1:
        raise ValueError("Target debt-to-value ratio must be between 0 and 1")
    
    equity_weight = 1 - target_debt_to_value_ratio
    debt_weight = target_debt_to_value_ratio
    
    weighted_average_cost_of_capital = (
        equity_weight * cost_of_equity + 
        debt_weight * cost_of_debt * (1 - corporate_tax_rate)
    )
    
    return weighted_average_cost_of_capital

def calculate_unlevered_cost_of_equity(
    levered_beta: float, 
    risk_free_rate: float, 
    equity_risk_premium: float, 
    debt_to_equity_ratio: float, 
    cost_of_debt: float, 
    corporate_tax_rate: float
) -> float:
    """
    Calculate unlevered cost of equity using the Hamada equation.
    
    This function unlevers the equity beta to remove the effect of financial leverage,
    then calculates the unlevered cost of equity using CAPM.
    
    Formula: 
    1. Unlevered Beta = Levered Beta / [1 + (1-T) × (D/E)]
    2. Unlevered Cost of Equity = Risk-Free Rate + Unlevered Beta × Equity Risk Premium
    
    Args:
        levered_beta: Levered equity beta
        risk_free_rate: Risk-free rate as decimal
        equity_risk_premium: Market equity risk premium as decimal
        debt_to_equity_ratio: Debt-to-equity ratio (D/E)
        cost_of_debt: Cost of debt as decimal
        corporate_tax_rate: Corporate tax rate as decimal
        
    Returns:
        float: Unlevered cost of equity as decimal
    """
    # Calculate unlevered beta using Hamada equation
    unlevered_beta = levered_beta / (1 + (1 - corporate_tax_rate) * debt_to_equity_ratio)
    
    # Calculate unlevered cost of equity using CAPM
    unlevered_cost_of_equity = risk_free_rate + unlevered_beta * equity_risk_premium
    return unlevered_cost_of_equity

def calculate_levered_cost_of_equity(
    unlevered_beta: float, 
    risk_free_rate: float,
    equity_risk_premium: float, 
    debt_to_equity_ratio: float,
    cost_of_debt: float, 
    corporate_tax_rate: float
) -> float:
    """
    Calculate levered cost of equity using the Hamada equation.
    
    This function relevers the unlevered beta to incorporate the effect of financial leverage,
    then calculates the levered cost of equity using CAPM.
    
    Formula:
    1. Levered Beta = Unlevered Beta × [1 + (1-T) × (D/E)]
    2. Levered Cost of Equity = Risk-Free Rate + Levered Beta × Equity Risk Premium
    
    Args:
        unlevered_beta: Unlevered beta
        risk_free_rate: Risk-free rate as decimal
        equity_risk_premium: Market equity risk premium as decimal
        debt_to_equity_ratio: Debt-to-equity ratio (D/E)
        cost_of_debt: Cost of debt as decimal
        corporate_tax_rate: Corporate tax rate as decimal
        
    Returns:
        float: Levered cost of equity as decimal
    """
    # Calculate levered beta using Hamada equation
    levered_beta = unlevered_beta * (1 + (1 - corporate_tax_rate) * debt_to_equity_ratio)
    
    # Calculate levered cost of equity using CAPM
    levered_cost_of_equity = risk_free_rate + levered_beta * equity_risk_premium
    return levered_cost_of_equity

def calculate_iterative_wacc(valuation_parameters: "ValuationParameters", max_iterations: int = 3) -> float:
    """
    Calculate WACC iteratively to resolve circular dependency issues.
    
    This function implements a professional approach to WACC calculation that prioritizes
    target capital structure methodology over iterative market value approaches.
    
    Calculation Priority:
    1. Use target capital structure approach if target_debt_to_value_ratio is provided
    2. Use provided WACC if available
    3. Fall back to simple calculation using estimated market values
    
    Args:
        valuation_parameters: ValuationParameters object with all required inputs
        max_iterations: Maximum number of iterations for convergence (default: 3)
        
    Returns:
        float: Calculated WACC as decimal
        
    Note:
        The iterative approach is simplified to prioritize target capital structure
        methodology, which is more common in professional practice.
    """
    # Priority 1: Use target capital structure approach
    if valuation_parameters.target_debt_to_value_ratio > 0:
        cost_of_equity = valuation_parameters.calculate_levered_cost_of_equity()
        return calculate_wacc_target_capital_structure(
            valuation_parameters.target_debt_to_value_ratio,
            cost_of_equity,
            valuation_parameters.cost_of_debt,
            valuation_parameters.corporate_tax_rate
        )
    
    # Priority 2: Use provided WACC if available
    if valuation_parameters.weighted_average_cost_of_capital > 0:
        return valuation_parameters.weighted_average_cost_of_capital
    
    # Priority 3: Fallback to simple calculation using estimated market values
    estimated_equity_value = (
        valuation_parameters.revenue_projections[0] * 2.0 
        if valuation_parameters.revenue_projections else 1000.0
    )
    estimated_debt_value = valuation_parameters.debt_schedule.get(0, 0.0)
    cost_of_equity = valuation_parameters.calculate_levered_cost_of_equity()
    
    return calculate_weighted_average_cost_of_capital(
        estimated_equity_value, 
        estimated_debt_value, 
        cost_of_equity, 
        valuation_parameters.cost_of_debt, 
        valuation_parameters.corporate_tax_rate
    )

 