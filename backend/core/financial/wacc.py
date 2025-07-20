"""
WACC Calculator Module

This module provides functions to calculate WACC and related cost of capital metrics:
- calculate_wacc: Calculate WACC from components
- calculate_cost_of_equity: Calculate cost of equity using CAPM
- calculate_unlevered_cost_of_equity: Calculate unlevered cost of equity using Hamada equation
"""

def calculate_cost_of_equity(risk_free_rate: float, beta: float, market_risk_premium: float) -> float:
    """
    Calculate cost of equity using CAPM.
    
    Args:
        risk_free_rate: Risk-free rate (e.g., 0.03 for 3%)
        beta: Equity beta
        market_risk_premium: Market risk premium (e.g., 0.06 for 6%)
        
    Returns:
        Cost of equity as decimal
    """
    return risk_free_rate + beta * market_risk_premium

def calculate_wacc(equity_value: float, debt_value: float, cost_of_equity: float, 
                  cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculate WACC = (E/V × Re) + (D/V × Rd × (1-T))
    
    Args:
        equity_value: Market value of equity
        debt_value: Market value of debt
        cost_of_equity: Cost of equity (decimal)
        cost_of_debt: Cost of debt (decimal)
        tax_rate: Corporate tax rate (decimal)
        
    Returns:
        WACC as decimal
    """
    total_value = equity_value + debt_value
    if total_value == 0:
        return cost_of_equity  # All equity firm
    
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    
    wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)
    return wacc

def calculate_unlevered_cost_of_equity(cost_of_equity: float, debt_ratio: float, 
                                     cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculate unlevered cost of equity using Hamada equation.
    
    Args:
        cost_of_equity: Levered cost of equity
        debt_ratio: Debt to total capital ratio
        cost_of_debt: Cost of debt
        tax_rate: Corporate tax rate
        
    Returns:
        Unlevered cost of equity as decimal
    """
    unlevered_cost = cost_of_equity - (debt_ratio * cost_of_debt * (1 - tax_rate))
    return unlevered_cost

def calculate_levered_cost_of_equity(unlevered_cost: float, debt_ratio: float,
                                   cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculate levered cost of equity using Hamada equation.
    
    Args:
        unlevered_cost: Unlevered cost of equity
        debt_ratio: Debt to total capital ratio
        cost_of_debt: Cost of debt
        tax_rate: Corporate tax rate
        
    Returns:
        Levered cost of equity as decimal
    """
    levered_cost = unlevered_cost + (debt_ratio * cost_of_debt * (1 - tax_rate))
    return levered_cost 