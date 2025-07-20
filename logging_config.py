"""
Logging configuration for the Financial Valuation Engine

This module provides centralized logging configuration and utility functions
for consistent logging across the application.
"""

import logging
import sys
from typing import Optional, Any
from pathlib import Path

# Configure logging levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
        log_format: Optional custom format string
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If invalid logging level is provided
    """
    if level.upper() not in LOG_LEVELS:
        raise ValueError(f"Invalid logging level: {level}. Must be one of {list(LOG_LEVELS.keys())}")
    
    # Default format if none provided
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVELS[level.upper()])
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVELS[level.upper()])
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(LOG_LEVELS[level.upper()])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log function calls with parameters for debugging.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger.debug(f"Calling {func_name} with parameters: {kwargs}")

def log_function_result(logger: logging.Logger, func_name: str, result: Any):
    """
    Log function results for debugging.
    
    Args:
        logger: Logger instance
        func_name: Name of the function that was called
        result: Function result to log
    """
    logger.debug(f"{func_name} returned: {result}")

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log errors with context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    error_msg = f"Error in {context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)

# Initialize default logging
default_logger = setup_logging() 