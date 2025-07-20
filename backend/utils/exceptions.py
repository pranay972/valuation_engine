"""
Custom exception classes for the Financial Valuation Engine

This module defines domain-specific exceptions that provide better error handling
and more informative error messages than generic exceptions.
"""

from typing import Optional, Dict, Any

class ValuationError(Exception):
    """Base exception for all valuation-related errors"""
    pass


class InvalidInputError(ValuationError):
    """Raised when input parameters are invalid or missing"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class CalculationError(ValuationError):
    """Raised when valuation calculations fail"""
    
    def __init__(self, message: str, calculation_type: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        self.message = message
        self.calculation_type = calculation_type
        self.params = params or {}
        super().__init__(self.message)


class DataValidationError(ValuationError):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, data_type: Optional[str] = None, constraints: Optional[Dict[str, Any]] = None):
        self.message = message
        self.data_type = data_type
        self.constraints = constraints or {}
        super().__init__(self.message)


class ConfigurationError(ValuationError):
    """Raised when application configuration is invalid"""
    pass


class FileProcessingError(ValuationError):
    """Raised when file processing operations fail"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        self.message = message
        self.file_path = file_path
        self.operation = operation
        super().__init__(self.message)


class MonteCarloError(ValuationError):
    """Raised when Monte Carlo simulation fails"""
    
    def __init__(self, message: str, iteration: Optional[int] = None, variable: Optional[str] = None):
        self.message = message
        self.iteration = iteration
        self.variable = variable
        super().__init__(self.message) 