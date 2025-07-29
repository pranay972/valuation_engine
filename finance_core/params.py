"""
Valuation Parameters Module

This module defines the core data structures and validation logic for financial valuation parameters.
Provides professional-grade parameter validation and cost of capital calculations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class ValuationParameters:
    """
    Comprehensive data structure for financial valuation parameters.
    
    This class encapsulates all inputs required for professional financial valuation,
    including driver-based projections, cost of capital inputs, and scenario specifications.
    Implements robust validation and provides methods for cost of capital calculations.
    """
    
    # Revenue and Operating Metrics
    revenue_projections: List[float] = field(default_factory=list)  # Annual revenue projections (USD)
    ebit_margin: float = 0.0  # EBIT margin as decimal (e.g., 0.20 for 20%)
    
    # Capital Expenditure and Depreciation
    capital_expenditure: List[float] = field(default_factory=list)  # Annual CapEx (USD)
    depreciation_expense: List[float] = field(default_factory=list)  # Annual depreciation (USD)
    
    # Working Capital and Cash Flow Components
    net_working_capital_changes: List[float] = field(default_factory=list)  # Annual NWC changes (USD)
    amortization_expense: List[float] = field(default_factory=list)  # Annual amortization (USD)
    other_non_cash_items: List[float] = field(default_factory=list)  # Other non-cash adjustments
    other_working_capital_items: List[float] = field(default_factory=list)  # Other WC adjustments
    
    # Direct Cash Flow Override
    free_cash_flow_series: List[float] = field(default_factory=list)  # Direct FCF projections
    
    # Terminal Value and Discount Rate Assumptions
    terminal_growth_rate: float = 0.0  # Long-term growth rate (decimal)
    weighted_average_cost_of_capital: float = 0.0  # WACC (decimal)
    corporate_tax_rate: float = 0.0  # Corporate tax rate (decimal)
    use_mid_year_convention: bool = False  # Mid-year discounting convention
    
    # Capital Structure and Share Information
    shares_outstanding: float = 1.0  # Number of shares outstanding
    cost_of_debt: float = 0.0  # Pre-tax cost of debt (decimal)
    debt_schedule: Dict[int, float] = field(default_factory=dict)  # Annual debt levels
    current_equity_value: Optional[float] = None  # Current market equity value
    cash_and_equivalents: float = 0.0  # Cash and cash equivalents
    
    # Cost of Capital Inputs for Professional Calculations
    unlevered_cost_of_equity: float = 0.0  # Unlevered cost of equity (decimal)
    levered_cost_of_equity: float = 0.0  # Levered cost of equity (decimal)
    risk_free_rate: float = 0.03  # Risk-free rate (decimal)
    equity_risk_premium: float = 0.06  # Market equity risk premium (decimal)
    levered_beta: float = 1.0  # Levered equity beta
    unlevered_beta: float = 1.0  # Unlevered beta
    target_debt_to_value_ratio: float = 0.3  # Target debt-to-value ratio (decimal)
    
    # Monte Carlo Simulation Specifications
    monte_carlo_variable_specs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Comparable Company Analysis
    comparable_multiples_data: Dict[str, Any] = field(default_factory=dict)
    
    # Scenario and Sensitivity Analysis
    scenario_definitions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sensitivity_parameter_ranges: Dict[str, List[float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validate all parameters after initialization.
        
        Performs comprehensive validation of financial parameters including:
        - Non-negative values for rates and ratios
        - Reasonable ranges for growth rates and betas
        - Consistency checks for list lengths
        - Professional warnings for unusual assumptions
        """
        self._validate_basic_financial_parameters()
        self._validate_terminal_value_assumptions()
        self._validate_capital_structure_parameters()
        self._validate_list_consistency()
    
    def _validate_basic_financial_parameters(self):
        """Validate basic financial parameters for reasonableness."""
        parameters_to_validate = [
            ("ebit_margin", self.ebit_margin),
            ("weighted_average_cost_of_capital", self.weighted_average_cost_of_capital),
            ("corporate_tax_rate", self.corporate_tax_rate),
            ("cost_of_debt", self.cost_of_debt),
            ("levered_cost_of_equity", self.levered_cost_of_equity),
            ("risk_free_rate", self.risk_free_rate),
            ("equity_risk_premium", self.equity_risk_premium)
        ]
        
        for param_name, param_value in parameters_to_validate:
            if param_value < 0:
                raise ValueError(f"{param_name} cannot be negative: {param_value}")
    
    def _validate_terminal_value_assumptions(self):
        """Validate terminal value assumptions for professional reasonableness."""
        if self.terminal_growth_rate >= 1:
            raise ValueError("terminal_growth_rate must be less than 100%")
        
        if self.terminal_growth_rate >= self.weighted_average_cost_of_capital and self.weighted_average_cost_of_capital > 0:
            raise ValueError("terminal_growth_rate must be less than WACC for valid terminal value")
        
        if self.terminal_growth_rate > 0.05:
            print(f"Warning: Terminal growth rate of {self.terminal_growth_rate:.1%} is unusually high")
    
    def _validate_capital_structure_parameters(self):
        """Validate capital structure and share-related parameters."""
        if self.shares_outstanding <= 0:
            raise ValueError("shares_outstanding must be positive")
        
        if self.levered_beta <= 0:
            raise ValueError("levered_beta must be positive")
        
        if self.unlevered_beta <= 0:
            raise ValueError("unlevered_beta must be positive")
        
        if self.target_debt_to_value_ratio < 0 or self.target_debt_to_value_ratio > 1:
            raise ValueError("target_debt_to_value_ratio must be between 0 and 1")
    
    def _validate_list_consistency(self):
        """Validate that all financial input lists have consistent lengths."""
        financial_lists = [
            ("revenue_projections", self.revenue_projections),
            ("capital_expenditure", self.capital_expenditure),
            ("depreciation_expense", self.depreciation_expense),
            ("net_working_capital_changes", self.net_working_capital_changes),
            ("amortization_expense", self.amortization_expense),
            ("other_non_cash_items", self.other_non_cash_items),
            ("other_working_capital_items", self.other_working_capital_items)
        ]
        
        # Filter out empty lists
        non_empty_lists = [(name, lst) for name, lst in financial_lists if lst]
        
        if len(non_empty_lists) > 1:
            list_lengths = [len(lst) for name, lst in non_empty_lists]
            if len(set(list_lengths)) > 1:
                length_info = ", ".join([f"{name}={len(lst)}" for name, lst in non_empty_lists])
                raise ValueError(f"All financial input lists must have the same length: {length_info}")
        
        # Validate revenue values
        if self.revenue_projections and any(revenue <= 0 for revenue in self.revenue_projections):
            raise ValueError("All revenue projections must be positive")
    
    def calculate_unlevered_cost_of_equity(self) -> float:
        """
        Calculate unlevered cost of equity using available inputs.
        
        Returns:
            float: Unlevered cost of equity (decimal)
        
        Calculation priority:
        1. Use provided unlevered cost of equity if available
        2. Calculate from levered beta using Hamada equation
        3. Fall back to industry average using unlevered beta
        """
        if self.unlevered_cost_of_equity > 0:
            return self.unlevered_cost_of_equity
        
        # Calculate from levered beta if available
        if self.levered_beta > 0 and self.levered_cost_of_equity > 0:
            current_debt = self.debt_schedule.get(0, 0.0)
            current_equity = self.current_equity_value if self.current_equity_value else 1000.0
            debt_ratio = current_debt / current_equity if current_equity > 0 else 0.0
            
            unlevered_beta = self.levered_beta / (1 + (1 - self.corporate_tax_rate) * debt_ratio)
            return self.risk_free_rate + unlevered_beta * self.equity_risk_premium
        
        # Fallback to industry average
        return self.risk_free_rate + self.unlevered_beta * self.equity_risk_premium
    
    def calculate_levered_cost_of_equity(self) -> float:
        """
        Calculate levered cost of equity using available inputs.
        
        Returns:
            float: Levered cost of equity (decimal)
        
        Calculation priority:
        1. Use provided levered cost of equity if available
        2. Calculate from levered beta using CAPM
        3. Calculate from unlevered beta using Hamada equation
        """
        if self.levered_cost_of_equity > 0:
            return self.levered_cost_of_equity
        
        # If we have levered beta, use it directly with CAPM
        if self.levered_beta > 0:
            return self.risk_free_rate + self.levered_beta * self.equity_risk_premium
        
        # Calculate from unlevered beta if available
        unlevered_cost = self.calculate_unlevered_cost_of_equity()
        current_debt = self.debt_schedule.get(0, 0.0)
        current_equity = self.current_equity_value if self.current_equity_value else 1000.0
        debt_ratio = current_debt / current_equity if current_equity > 0 else 0.0
        
        levered_beta = self.unlevered_beta * (1 + (1 - self.corporate_tax_rate) * debt_ratio)
        return self.risk_free_rate + levered_beta * self.equity_risk_premium 