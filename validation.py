"""
Validation utilities for the Financial Valuation Engine

This module provides validation decorators and utility functions for
input validation and data integrity checks.
"""

from functools import wraps
from typing import Any, Dict, List, Optional, Union, Callable
import numpy as np

from exceptions import InvalidInputError, DataValidationError

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

def validate_valuation_params(params: Dict[str, Any]) -> None:
    """
    Validate valuation parameters.
    
    Args:
        params: Dictionary of valuation parameters
        
    Raises:
        InvalidInputError: If validation fails
    """
    required_fields = ["wacc", "terminal_growth", "tax_rate"]
    
    for field in required_fields:
        if field not in params:
            raise InvalidInputError(
                f"Missing required field: {field}",
                field=field
            )
        
        value = params[field]
        if not isinstance(value, (int, float)):
            raise InvalidInputError(
                f"{field} must be numeric, got {type(value)}",
                field=field,
                value=value
            )
    
    # Validate specific constraints
    if params["wacc"] <= 0:
        raise InvalidInputError(
            "WACC must be positive",
            field="wacc",
            value=params["wacc"]
        )
    
    if params["terminal_growth"] >= params["wacc"]:
        raise InvalidInputError(
            "Terminal growth must be less than WACC",
            field="terminal_growth",
            value=params["terminal_growth"]
        )
    
    if not (0 <= params["tax_rate"] <= 1):
        raise InvalidInputError(
            "Tax rate must be between 0 and 1",
            field="tax_rate",
            value=params["tax_rate"]
        )

def validate_monte_carlo_specs(specs: Dict[str, Dict[str, Any]]) -> None:
    """
    Validate Monte Carlo variable specifications.
    
    Args:
        specs: Dictionary of variable specifications
        
    Raises:
        InvalidInputError: If validation fails
    """
    if not isinstance(specs, dict):
        raise InvalidInputError(
            "Variable specifications must be a dictionary",
            field="variable_specs",
            value=specs
        )
    
    for var_name, spec in specs.items():
        if not isinstance(spec, dict):
            raise InvalidInputError(
                f"Specification for '{var_name}' must be a dictionary",
                field=var_name,
                value=spec
            )
        
        if "dist" not in spec:
            raise InvalidInputError(
                f"Missing 'dist' key for variable '{var_name}'",
                field=var_name
            )
        
        dist_type = spec["dist"]
        if dist_type not in ["normal", "uniform"]:
            raise InvalidInputError(
                f"Unsupported distribution type '{dist_type}' for variable '{var_name}'",
                field=var_name,
                value=dist_type
            )
        
        if "params" not in spec:
            raise InvalidInputError(
                f"Missing 'params' key for variable '{var_name}'",
                field=var_name
            )
        
        params = spec["params"]
        if dist_type == "normal":
            if "loc" not in params or "scale" not in params:
                raise InvalidInputError(
                    f"Normal distribution for '{var_name}' requires 'loc' and 'scale' parameters",
                    field=var_name
                )
            if params["scale"] <= 0:
                raise InvalidInputError(
                    f"Scale parameter for '{var_name}' must be positive",
                    field=var_name,
                    value=params["scale"]
                )
        elif dist_type == "uniform":
            if "low" not in params or "high" not in params:
                raise InvalidInputError(
                    f"Uniform distribution for '{var_name}' requires 'low' and 'high' parameters",
                    field=var_name
                )
            if params["low"] >= params["high"]:
                raise InvalidInputError(
                    f"Low parameter must be less than high parameter for '{var_name}'",
                    field=var_name,
                    value={"low": params["low"], "high": params["high"]}
                ) 