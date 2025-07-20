"""
Configuration management for the Financial Valuation Engine

This module provides centralized configuration management for all
application settings, environment variables, and defaults.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Application settings
    app_name: str = "Financial Valuation Engine"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache settings
    cache_max_size: int = 128
    cache_ttl_seconds: Optional[int] = None
    dcf_cache_ttl: int = 3600  # 1 hour
    monte_carlo_cache_ttl: int = 1800  # 30 minutes
    sensitivity_cache_ttl: int = 7200  # 2 hours
    
    # Performance settings
    monte_carlo_default_runs: int = 2000
    max_monte_carlo_runs: int = 10000
    default_random_seed: int = 42
    
    # Validation settings
    max_series_length: int = 20
    min_wacc: float = 0.01  # 1%
    max_wacc: float = 0.50  # 50%
    min_terminal_growth: float = -0.10  # -10%
    max_terminal_growth: float = 0.10  # 10%
    
    # File settings
    max_file_size_mb: int = 10
    allowed_file_types: list = field(default_factory=lambda: ['.csv', '.xlsx', '.xls'])
    upload_dir: str = "uploads"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list = field(default_factory=lambda: ["*"])
    api_rate_limit: int = 100  # requests per minute
    
    # Security settings
    enable_rate_limiting: bool = True
    enable_input_validation: bool = True
    enable_logging: bool = True
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE'),
            cache_max_size=int(os.getenv('CACHE_MAX_SIZE', '128')),
            cache_ttl_seconds=int(os.getenv('CACHE_TTL_SECONDS', '0')) or None,
            monte_carlo_default_runs=int(os.getenv('MC_DEFAULT_RUNS', '2000')),
            max_monte_carlo_runs=int(os.getenv('MC_MAX_RUNS', '10000')),
            api_host=os.getenv('API_HOST', '0.0.0.0'),
            api_port=int(os.getenv('API_PORT', '8000')),
            enable_rate_limiting=os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            enable_input_validation=os.getenv('ENABLE_INPUT_VALIDATION', 'true').lower() == 'true',
            enable_logging=os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
        )
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.cache_max_size <= 0:
            raise ValueError("cache_max_size must be positive")
        
        if self.monte_carlo_default_runs <= 0:
            raise ValueError("monte_carlo_default_runs must be positive")
        
        if self.max_monte_carlo_runs < self.monte_carlo_default_runs:
            raise ValueError("max_monte_carlo_runs must be >= monte_carlo_default_runs")
        
        if self.min_wacc >= self.max_wacc:
            raise ValueError("min_wacc must be less than max_wacc")
        
        if self.min_terminal_growth >= self.max_terminal_growth:
            raise ValueError("min_terminal_growth must be less than max_terminal_growth")
        
        if self.api_port <= 0 or self.api_port > 65535:
            raise ValueError("api_port must be between 1 and 65535")
    
    def get_cache_config(self, cache_type: str) -> Dict[str, Any]:
        """
        Get cache configuration for a specific type.
        
        Args:
            cache_type: Type of cache ('dcf', 'monte_carlo', 'sensitivity')
            
        Returns:
            Cache configuration dictionary
        """
        ttl_map = {
            'dcf': self.dcf_cache_ttl,
            'monte_carlo': self.monte_carlo_cache_ttl,
            'sensitivity': self.sensitivity_cache_ttl
        }
        
        return {
            'max_size': self.cache_max_size // 2,  # Smaller size for specialized caches
            'ttl_seconds': ttl_map.get(cache_type, self.cache_ttl_seconds)
        }
    
    def get_validation_constraints(self) -> Dict[str, Any]:
        """
        Get validation constraints for input parameters.
        
        Returns:
            Dictionary of validation constraints
        """
        return {
            'max_series_length': self.max_series_length,
            'wacc_range': (self.min_wacc, self.max_wacc),
            'terminal_growth_range': (self.min_terminal_growth, self.max_terminal_growth),
            'max_monte_carlo_runs': self.max_monte_carlo_runs
        }

# Global configuration instance
config = AppConfig.from_env()

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config

def update_config(**kwargs) -> None:
    """
    Update configuration settings.
    
    Args:
        **kwargs: Configuration settings to update
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    # Validate updated configuration
    config.validate()

def create_upload_directory() -> Path:
    """
    Create upload directory if it doesn't exist.
    
    Returns:
        Path to upload directory
    """
    upload_path = Path(config.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path

def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration.
    
    Returns:
        Logging configuration dictionary
    """
    return {
        'level': config.log_level,
        'file': config.log_file,
        'format': config.log_format
    } 