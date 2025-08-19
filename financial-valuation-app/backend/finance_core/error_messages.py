"""
Standardized Error Messages for Finance Core

This module provides centralized error message definitions and formatting
functions to ensure consistent error reporting across the finance_core system.
"""

from typing import Dict, Any, Optional
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels for consistent error reporting."""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class ErrorCategory(Enum):
    """Error categories for organized error reporting."""
    VALIDATION = "VALIDATION"
    CALCULATION = "CALCULATION"
    INPUT = "INPUT"
    CONFIGURATION = "CONFIGURATION"
    SYSTEM = "SYSTEM"

class FinanceCoreError(Exception):
    """Base exception class for finance_core with standardized error formatting."""
    
    def __init__(self, 
                 message: str, 
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[Dict[str, Any]] = None,
                 suggestion: Optional[str] = None):
        """
        Initialize a standardized finance_core error.
        
        Args:
            message: Primary error message
            category: Error category for classification
            severity: Error severity level
            context: Additional context information
            suggestion: Suggested fix or action
        """
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.suggestion = suggestion
        
        # Format the full error message
        full_message = self._format_error_message()
        super().__init__(full_message)
    
    def _format_error_message(self) -> str:
        """Format the complete error message with all components."""
        parts = [f"[{self.severity.value}] {self.message}"]
        
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            parts.append(f"Context: {context_str}")
        
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        
        return " | ".join(parts)

# Standardized error message templates
ERROR_MESSAGES = {
    # Validation Errors
    "MISSING_REQUIRED_FIELD": {
        "message": "Required field '{field_name}' is missing",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Please provide the required field '{field_name}' in your input data"
    },
    
    "INVALID_DATA_TYPE": {
        "message": "Field '{field_name}' has invalid data type. Expected {expected_type}, got {actual_type}",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Ensure '{field_name}' is of type {expected_type}"
    },
    
    "NEGATIVE_VALUE": {
        "message": "Field '{field_name}' cannot be negative. Value: {value}",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Provide a non-negative value for '{field_name}'"
    },
    
    "INCONSISTENT_LIST_LENGTHS": {
        "message": "Financial projection lists have inconsistent lengths: {lengths}",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Ensure all financial projection arrays have the same length"
    },
    
    # Financial Validation Errors
    "TERMINAL_GROWTH_TOO_HIGH": {
        "message": "Terminal growth rate ({growth_rate:.1%}) exceeds maximum recommended value of 5%",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.WARNING,
        "suggestion": "Consider using a terminal growth rate of 5% or less for sustainable long-term growth"
    },
    
    "TERMINAL_GROWTH_EXCEEDS_WACC": {
        "message": "Terminal growth rate ({growth_rate:.1%}) must be less than WACC ({wacc:.1%})",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Reduce terminal growth rate or increase WACC to ensure valid terminal value calculation"
    },
    
    "UNREALISTIC_ROIC": {
        "message": "Terminal ROIC of {roic:.1%} appears unrealistically high",
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.WARNING,
        "suggestion": "Consider reviewing terminal growth rate and WACC assumptions"
    },
    
    # Calculation Errors
    "DCF_CALCULATION_FAILED": {
        "message": "DCF calculation failed: {reason}",
        "category": ErrorCategory.CALCULATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Check input parameters and ensure all required fields are provided"
    },
    
    "WACC_CALCULATION_FAILED": {
        "message": "WACC calculation failed: {reason}",
        "category": ErrorCategory.CALCULATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Verify cost of capital inputs and capital structure assumptions"
    },
    
    "ZERO_ENTERPRISE_VALUE": {
        "message": "Total enterprise value cannot be zero for WACC calculation",
        "category": ErrorCategory.CALCULATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Check market values of equity and debt"
    },
    
    # Input Errors
    "INVALID_JSON_STRUCTURE": {
        "message": "Invalid JSON structure: {reason}",
        "category": ErrorCategory.INPUT,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Ensure JSON follows the required structure defined in the documentation"
    },
    
    "EMPTY_COMPARABLE_DATA": {
        "message": "Comparable multiples data is empty or invalid",
        "category": ErrorCategory.INPUT,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Provide valid comparable company multiples data"
    },
    
    "INVALID_MONTE_CARLO_SPECS": {
        "message": "Invalid Monte Carlo specifications: {reason}",
        "category": ErrorCategory.INPUT,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Check distribution parameters and ensure all required fields are provided"
    },
    
    # Configuration Errors
    "UNSUPPORTED_DISTRIBUTION": {
        "message": "Unsupported distribution type: {distribution}",
        "category": ErrorCategory.CONFIGURATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Use supported distributions: normal, uniform, lognormal, triangular"
    },
    
    "INVALID_SCENARIO_DEFINITION": {
        "message": "Invalid scenario definition: {reason}",
        "category": ErrorCategory.CONFIGURATION,
        "severity": ErrorSeverity.ERROR,
        "suggestion": "Check scenario parameter names and values"
    }
}

def create_error(error_key: str, **kwargs) -> FinanceCoreError:
    """
    Create a standardized error using predefined templates.
    
    Args:
        error_key: Key from ERROR_MESSAGES dictionary
        **kwargs: Parameters to format the error message
        
    Returns:
        FinanceCoreError: Formatted error with all components
        
    Raises:
        KeyError: If error_key is not found in ERROR_MESSAGES
    """
    if error_key not in ERROR_MESSAGES:
        raise KeyError(f"Unknown error key: {error_key}")
    
    template = ERROR_MESSAGES[error_key]
    
    # Format the message with provided parameters
    message = template["message"].format(**kwargs)
    
    return FinanceCoreError(
        message=message,
        category=template["category"],
        severity=template["severity"],
        context=kwargs,
        suggestion=template["suggestion"].format(**kwargs) if "suggestion" in template else None
    )

def validate_required_field(data: Dict[str, Any], field_name: str, field_type: type = None) -> None:
    """
    Validate that a required field exists and has the correct type.
    
    Args:
        data: Dictionary containing the data to validate
        field_name: Name of the required field
        field_type: Expected type of the field (optional)
        
    Raises:
        FinanceCoreError: If field is missing or has wrong type
    """
    if field_name not in data:
        raise create_error("MISSING_REQUIRED_FIELD", field_name=field_name)
    
    if field_type is not None and not isinstance(data[field_name], field_type):
        raise create_error(
            "INVALID_DATA_TYPE", 
            field_name=field_name,
            expected_type=field_type.__name__,
            actual_type=type(data[field_name]).__name__
        )

def validate_non_negative(value: float, field_name: str) -> None:
    """
    Validate that a numeric field is non-negative.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error reporting
        
    Raises:
        FinanceCoreError: If value is negative
    """
    if value < 0:
        raise create_error("NEGATIVE_VALUE", field_name=field_name, value=value)

def validate_list_consistency(lists: Dict[str, list]) -> None:
    """
    Validate that all lists have the same length.
    
    Args:
        lists: Dictionary of list_name -> list pairs
        
    Raises:
        FinanceCoreError: If lists have inconsistent lengths
    """
    non_empty_lists = {name: lst for name, lst in lists.items() if lst}
    
    if len(non_empty_lists) > 1:
        lengths = {name: len(lst) for name, lst in non_empty_lists.items()}
        if len(set(lengths.values())) > 1:
            length_str = ", ".join([f"{name}={length}" for name, length in lengths.items()])
            raise create_error("INCONSISTENT_LIST_LENGTHS", lengths=length_str) 