"""
Validation utilities for the Financial Valuation Engine

This module provides validation decorators and utility functions for
input validation and data integrity checks.
"""

from functools import wraps
from typing import Any, Dict, List, Optional, Union, Callable
import numpy as np

from .exceptions import InvalidInputError, DataValidationError

def validate_numeric_range(min_val: float, max_val: float, field_name: str = "value"):
    """
    Decorator to validate numeric parameters are within a specified range.
    
    Args:
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Name of the field being validated (for error messages)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find the parameter to validate (assuming it's the first parameter after self)
            if len(args) > 1:
                value = args[1]  # Skip self
            elif field_name in kwargs:
                value = kwargs[field_name]
            else:
                # If we can't find the parameter, just call the function
                return func(*args, **kwargs)
            
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                raise InvalidInputError(
                    f"{field_name} must be between {min_val} and {max_val}, got {value}",
                    field=field_name,
                    value=value
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_positive_numeric(field_name: str = "value"):
    """
    Decorator to validate numeric parameters are positive.
    
    Args:
        field_name: Name of the field being validated (for error messages)
    """
    return validate_numeric_range(0, float('inf'), field_name)

def validate_percentage_range(field_name: str = "percentage"):
    """
    Decorator to validate percentage values are between 0 and 1.
    
    Args:
        field_name: Name of the field being validated (for error messages)
    """
    return validate_numeric_range(0, 1, field_name)

def validate_list_length(expected_length: int, field_name: str = "list"):
    """
    Decorator to validate list parameters have the expected length.
    
    Args:
        expected_length: Expected length of the list
        field_name: Name of the field being validated (for error messages)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find the list parameter to validate
            if len(args) > 1:
                value = args[1]  # Skip self
            elif field_name in kwargs:
                value = kwargs[field_name]
            else:
                return func(*args, **kwargs)
            
            if not isinstance(value, list) or len(value) != expected_length:
                raise InvalidInputError(
                    f"{field_name} must be a list with {expected_length} elements, got {len(value) if isinstance(value, list) else type(value)}",
                    field=field_name,
                    value=value
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_non_empty_list(field_name: str = "list"):
    """
    Decorator to validate list parameters are not empty.
    
    Args:
        field_name: Name of the field being validated (for error messages)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find the list parameter to validate
            if len(args) > 1:
                value = args[1]  # Skip self
            elif field_name in kwargs:
                value = kwargs[field_name]
            else:
                return func(*args, **kwargs)
            
            if not isinstance(value, list) or len(value) == 0:
                raise InvalidInputError(
                    f"{field_name} must be a non-empty list",
                    field=field_name,
                    value=value
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_series_consistency(*series_names: str):
    """
    Decorator to validate that multiple series have the same length.
    
    Args:
        *series_names: Names of the series to validate
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract series from args or kwargs
            series = {}
            for name in series_names:
                if name in kwargs:
                    series[name] = kwargs[name]
                else:
                    # Try to find in positional args (assuming they're in order)
                    pass  # This is simplified - would need more complex logic
            
            if len(series) >= 2:
                lengths = [len(s) for s in series.values() if isinstance(s, list)]
                if len(set(lengths)) > 1:
                    raise DataValidationError(
                        f"All series must have the same length. Lengths: {dict(zip(series.keys(), lengths))}",
                        data_type="series",
                        constraints={"required_length": lengths[0] if lengths else 0}
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_financial_data(data: List[float], data_type: str) -> None:
    """
    Validate financial data series.
    
    Args:
        data: List of financial values
        data_type: Type of financial data (e.g., "revenue", "ebit", "fcf")
        
    Raises:
        DataValidationError: If validation fails
    """
    if not isinstance(data, list):
        raise DataValidationError(
            f"{data_type} must be a list",
            data_type=data_type
        )
    
    if len(data) == 0:
        raise DataValidationError(
            f"{data_type} cannot be empty",
            data_type=data_type
        )
    
    # Check for non-numeric values
    for i, value in enumerate(data):
        if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
            raise DataValidationError(
                f"{data_type} contains invalid value at index {i}: {value}",
                data_type=data_type,
                constraints={"index": i, "value": value}
            )
    
    # Check for negative values where inappropriate
    if data_type in ["revenue", "ebit", "fcf"]:
        for i, value in enumerate(data):
            if value < 0:
                raise DataValidationError(
                    f"{data_type} contains negative value at index {i}: {value}",
                    data_type=data_type,
                    constraints={"index": i, "value": value}
                )

def validate_terminal_growth_assumptions(terminal_growth: float, wacc: float) -> List[str]:
    """
    Validate terminal growth assumptions.
    
    Args:
        terminal_growth: Terminal growth rate
        wacc: Weighted average cost of capital
        
    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings = []
    
    # Check if terminal growth >= WACC (Gordon growth model constraint)
    if terminal_growth >= wacc:
        warnings.append(
            f"Terminal growth rate ({terminal_growth:.1%}) should be less than WACC ({wacc:.1%}) "
            "for Gordon growth model to be valid"
        )
    
    # Check for unusually high growth rates
    if terminal_growth > 0.05:  # 5% growth
        warnings.append(
            f"High terminal growth rate: {terminal_growth:.1%}. "
            "Consider if this is sustainable in perpetuity."
        )
    
    # Check for negative growth rates
    if terminal_growth < -0.02:  # -2% growth
        warnings.append(
            f"Low terminal growth rate: {terminal_growth:.1%}. "
            "Consider if this reflects long-term deflation expectations."
        )
    
    return warnings

def validate_debt_schedule(debt_schedule: Dict[int, float], revenue_length: int) -> List[str]:
    """
    Validate debt schedule assumptions.
    
    Args:
        debt_schedule: Dictionary mapping years to debt amounts
        revenue_length: Length of revenue forecast
        
    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings = []
    
    if not debt_schedule:
        return warnings
    
    # Check for debt in years beyond revenue forecast
    max_revenue_year = revenue_length - 1
    for year in debt_schedule:
        if year > max_revenue_year:
            warnings.append(
                f"Debt schedule includes year {year} beyond revenue forecast (max year: {max_revenue_year})"
            )
    
    # Check for negative debt values
    for year, debt in debt_schedule.items():
        if debt < 0:
            warnings.append(f"Negative debt value in year {year}: ${debt:,.0f}")
    
    return warnings

def validate_valuation_params(params: Dict[str, Any]) -> None:
    """
    Validate core valuation parameters.
    
    Args:
        params: Dictionary of valuation parameters
        
    Raises:
        InvalidInputError: If validation fails
    """
    # Validate WACC
    wacc = params.get("wacc", 0)
    if wacc <= 0 or wacc >= 1:
        raise InvalidInputError(
            f"WACC must be between 0 and 1, got {wacc}",
            field="wacc",
            value=wacc
        )
    
    # Validate tax rate
    tax_rate = params.get("tax_rate", 0)
    if tax_rate < 0 or tax_rate >= 1:
        raise InvalidInputError(
            f"Tax rate must be between 0 and 1, got {tax_rate}",
            field="tax_rate",
            value=tax_rate
        )
    
    # Validate terminal growth
    terminal_growth = params.get("terminal_growth", 0)
    if terminal_growth >= 1:
        raise InvalidInputError(
            f"Terminal growth must be less than 1, got {terminal_growth}",
            field="terminal_growth",
            value=terminal_growth
        )
    
    # Validate terminal growth vs WACC
    if terminal_growth >= wacc:
        raise InvalidInputError(
            f"Terminal growth ({terminal_growth:.1%}) must be less than WACC ({wacc:.1%}) "
            "for Gordon growth model to be valid",
            field="terminal_growth",
            value=terminal_growth
        )

def validate_monte_carlo_specs(specs: Dict[str, Dict[str, Any]]) -> None:
    """
    Validate Monte Carlo variable specifications.
    
    Args:
        specs: Dictionary of variable specifications
        
    Raises:
        InvalidInputError: If validation fails
    """
    for var_name, var_spec in specs.items():
        # Check required fields
        required_fields = ["distribution", "params"]
        for field in required_fields:
            if field not in var_spec:
                raise InvalidInputError(
                    f"Monte Carlo variable '{var_name}' missing required field '{field}'",
                    field=f"variable_specs.{var_name}.{field}"
                )
        
        # Validate distribution type
        distribution = var_spec["distribution"]
        valid_distributions = ["normal", "uniform", "lognormal", "triangular"]
        if distribution not in valid_distributions:
            raise InvalidInputError(
                f"Invalid distribution '{distribution}' for variable '{var_name}'. "
                f"Valid distributions: {valid_distributions}",
                field=f"variable_specs.{var_name}.distribution",
                value=distribution
            )
        
        # Validate parameters based on distribution
        params = var_spec["params"]
        if distribution == "normal":
            if "mean" not in params or "std" not in params:
                raise InvalidInputError(
                    f"Normal distribution for '{var_name}' requires 'mean' and 'std' parameters",
                    field=f"variable_specs.{var_name}.params"
                )
            if params["std"] <= 0:
                raise InvalidInputError(
                    f"Standard deviation for '{var_name}' must be positive",
                    field=f"variable_specs.{var_name}.params.std",
                    value=params["std"]
                )
        
        elif distribution == "uniform":
            if "min" not in params or "max" not in params:
                raise InvalidInputError(
                    f"Uniform distribution for '{var_name}' requires 'min' and 'max' parameters",
                    field=f"variable_specs.{var_name}.params"
                )
            if params["min"] >= params["max"]:
                raise InvalidInputError(
                    f"Uniform distribution for '{var_name}' requires min < max",
                    field=f"variable_specs.{var_name}.params"
                )
        
        elif distribution == "lognormal":
            if "mean" not in params or "std" not in params:
                raise InvalidInputError(
                    f"Lognormal distribution for '{var_name}' requires 'mean' and 'std' parameters",
                    field=f"variable_specs.{var_name}.params"
                )
            if params["std"] <= 0:
                raise InvalidInputError(
                    f"Standard deviation for '{var_name}' must be positive",
                    field=f"variable_specs.{var_name}.params.std",
                    value=params["std"]
                )
        
        elif distribution == "triangular":
            if "min" not in params or "max" not in params or "mode" not in params:
                raise InvalidInputError(
                    f"Triangular distribution for '{var_name}' requires 'min', 'max', and 'mode' parameters",
                    field=f"variable_specs.{var_name}.params"
                )
            if not (params["min"] <= params["mode"] <= params["max"]):
                raise InvalidInputError(
                    f"Triangular distribution for '{var_name}' requires min <= mode <= max",
                    field=f"variable_specs.{var_name}.params"
                ) 