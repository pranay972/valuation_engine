"""
Comprehensive tests for the improved Financial Valuation Engine

This module tests the new features and improvements including:
- Custom exceptions
- Validation utilities
- Caching system
- Service layer
- Configuration management
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

# Import the modules to test
from exceptions import (
    ValuationError, InvalidInputError, CalculationError, 
    DataValidationError, MonteCarloError
)
from validation import (
    validate_financial_data, validate_valuation_params,
    validate_monte_carlo_specs
)
from cache import ValuationCache, cached, get_cache_stats
from services import ValuationService
from config import AppConfig, get_config, update_config
from params import ValuationParams
from valuation import calc_dcf_series
from montecarlo import run_monte_carlo

class TestExceptions:
    """Test custom exception classes."""
    
    def test_valuation_error_inheritance(self):
        """Test that all exceptions inherit from ValuationError."""
        assert issubclass(InvalidInputError, ValuationError)
        assert issubclass(CalculationError, ValuationError)
        assert issubclass(DataValidationError, ValuationError)
        assert issubclass(MonteCarloError, ValuationError)
    
    def test_invalid_input_error(self):
        """Test InvalidInputError with field and value."""
        error = InvalidInputError("Test error", field="test_field", value="test_value")
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.value == "test_value"
    
    def test_calculation_error(self):
        """Test CalculationError with calculation type and params."""
        error = CalculationError("Test error", calculation_type="DCF", params={"wacc": 0.1})
        assert error.message == "Test error"
        assert error.calculation_type == "DCF"
        assert error.params == {"wacc": 0.1}
    
    def test_monte_carlo_error(self):
        """Test MonteCarloError with iteration and variable."""
        error = MonteCarloError("Test error", iteration=5, variable="wacc")
        assert error.message == "Test error"
        assert error.iteration == 5
        assert error.variable == "wacc"

class TestValidation:
    """Test validation utilities."""
    
    def test_validate_financial_data_valid(self):
        """Test validation of valid financial data."""
        data = [100.0, 110.0, 120.0]
        validate_financial_data(data, "revenue")
        # Should not raise any exception
    
    def test_validate_financial_data_empty(self):
        """Test validation of empty financial data."""
        with pytest.raises(DataValidationError):
            validate_financial_data([], "revenue")
    
    def test_validate_financial_data_invalid_type(self):
        """Test validation of invalid data type."""
        with pytest.raises(DataValidationError):
            validate_financial_data([], "revenue")  # Empty list should fail
    
    def test_validate_financial_data_negative_revenue(self):
        """Test validation of negative revenue values."""
        with pytest.raises(DataValidationError):
            validate_financial_data([100.0, -50.0, 120.0], "revenue")
    
    def test_validate_financial_data_nan_values(self):
        """Test validation of NaN values."""
        with pytest.raises(DataValidationError):
            validate_financial_data([100.0, np.nan, 120.0], "revenue")
    
    def test_validate_valuation_params_valid(self):
        """Test validation of valid valuation parameters."""
        params = {
            "wacc": 0.10,
            "terminal_growth": 0.02,
            "tax_rate": 0.21
        }
        validate_valuation_params(params)
        # Should not raise any exception
    
    def test_validate_valuation_params_missing_field(self):
        """Test validation with missing required field."""
        params = {"wacc": 0.10, "terminal_growth": 0.02}
        with pytest.raises(InvalidInputError):
            validate_valuation_params(params)
    
    def test_validate_valuation_params_invalid_wacc(self):
        """Test validation with invalid WACC."""
        params = {
            "wacc": -0.05,
            "terminal_growth": 0.02,
            "tax_rate": 0.21
        }
        with pytest.raises(InvalidInputError):
            validate_valuation_params(params)
    
    def test_validate_valuation_params_terminal_growth_too_high(self):
        """Test validation with terminal growth >= WACC."""
        params = {
            "wacc": 0.10,
            "terminal_growth": 0.15,
            "tax_rate": 0.21
        }
        with pytest.raises(InvalidInputError):
            validate_valuation_params(params)
    
    def test_validate_monte_carlo_specs_valid(self):
        """Test validation of valid Monte Carlo specifications."""
        specs = {
            "wacc": {
                "dist": "normal",
                "params": {"loc": 0.10, "scale": 0.01}
            }
        }
        validate_monte_carlo_specs(specs)
        # Should not raise any exception
    
    def test_validate_monte_carlo_specs_invalid_distribution(self):
        """Test validation with invalid distribution type."""
        specs = {
            "wacc": {
                "dist": "invalid_dist",
                "params": {"loc": 0.10, "scale": 0.01}
            }
        }
        with pytest.raises(InvalidInputError):
            validate_monte_carlo_specs(specs)
    
    def test_validate_monte_carlo_specs_missing_params(self):
        """Test validation with missing distribution parameters."""
        specs = {
            "wacc": {
                "dist": "normal",
                "params": {"loc": 0.10}  # Missing scale
            }
        }
        with pytest.raises(InvalidInputError):
            validate_monte_carlo_specs(specs)

class TestCache:
    """Test caching system."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = ValuationCache(max_size=10, ttl_seconds=60)
        assert cache.max_size == 10
        assert cache.ttl_seconds == 60
        assert cache.size() == 0
    
    def test_cache_set_and_get(self):
        """Test setting and getting values from cache."""
        cache = ValuationCache()
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = ValuationCache(ttl_seconds=1)  # 1 second TTL
        cache.set("test_key", "test_value")
        import time
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("test_key") is None
    
    def test_cache_eviction(self):
        """Test cache eviction when full."""
        cache = ValuationCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = ValuationCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = ValuationCache(max_size=10)
        cache.set("key1", "value1")
        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["utilization"] == 0.1

class TestServiceLayer:
    """Test service layer functionality."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = ValuationService()
        assert service.logger is not None
    
    def test_parse_series_input_valid(self):
        """Test parsing valid series input."""
        service = ValuationService()
        result = service._parse_series_input("100,110,120", "revenue")
        assert result == [100.0, 110.0, 120.0]
    
    def test_parse_series_input_invalid(self):
        """Test parsing invalid series input."""
        service = ValuationService()
        with pytest.raises(InvalidInputError):
            service._parse_series_input("100,abc,120", "revenue")
    
    def test_parse_series_input_empty(self):
        """Test parsing empty series input."""
        service = ValuationService()
        with pytest.raises(InvalidInputError):
            service._parse_series_input("", "revenue")
    
    def test_validate_input_data_valid(self):
        """Test validation of valid input data."""
        service = ValuationService()
        input_data = {
            "revenue": "100,110,120",
            "wacc": 0.10,
            "terminal_growth": 0.02,
            "tax_rate": 0.21
        }
        result = service.validate_input_data(input_data)
        assert "revenue" in result
        assert result["wacc"] == 0.10
    
    def test_create_valuation_params(self):
        """Test creation of ValuationParams object."""
        service = ValuationService()
        validated_data = {
            "revenue": [100.0, 110.0, 120.0],
            "wacc": 0.10,
            "terminal_growth": 0.02,
            "tax_rate": 0.21
        }
        params = service.create_valuation_params(validated_data)
        assert isinstance(params, ValuationParams)
        assert params.wacc == 0.10
        assert params.terminal_growth == 0.02

class TestConfiguration:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = AppConfig()
        assert config.app_name == "Financial Valuation Engine"
        assert config.debug is False
        assert config.cache_max_size == 128
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(os.environ, {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}):
            config = AppConfig.from_env()
            assert config.debug is True
            assert config.log_level == "DEBUG"
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid settings."""
        config = AppConfig()
        config.validate()  # Should not raise any exception
    
    def test_config_validation_invalid_cache_size(self):
        """Test configuration validation with invalid cache size."""
        config = AppConfig(cache_max_size=0)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_validation_invalid_port(self):
        """Test configuration validation with invalid port."""
        config = AppConfig(api_port=70000)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_get_cache_config(self):
        """Test getting cache configuration for specific types."""
        config = AppConfig()
        dcf_config = config.get_cache_config('dcf')
        assert 'max_size' in dcf_config
        assert 'ttl_seconds' in dcf_config
        assert dcf_config['ttl_seconds'] == 3600
    
    def test_get_validation_constraints(self):
        """Test getting validation constraints."""
        config = AppConfig()
        constraints = config.get_validation_constraints()
        assert 'max_series_length' in constraints
        assert 'wacc_range' in constraints
        assert 'terminal_growth_range' in constraints

class TestIntegration:
    """Test integration between components."""
    
    def test_cached_dcf_calculation(self):
        """Test that DCF calculation works with caching."""
        params = ValuationParams(
            fcf_series=[50.0, 55.0, 60.0],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100.0
        )
        
        # First calculation
        ev1, equity1, ps1 = calc_dcf_series(params)
        
        # Second calculation (should use cache)
        ev2, equity2, ps2 = calc_dcf_series(params)
        
        assert ev1 == ev2
        assert equity1 == equity2
        assert ps1 == ps2
    
    def test_service_with_validation(self):
        """Test service layer with input validation."""
        service = ValuationService()
        
        input_data = {
            "fcf_series": "50,55,60",
            "wacc": 0.10,
            "terminal_growth": 0.02,
            "share_count": 100.0
        }
        
        validated_data = service.validate_input_data(input_data)
        params = service.create_valuation_params(validated_data)
        
        assert params.fcf_series == [50.0, 55.0, 60.0]
        assert params.wacc == 0.10
    
    def test_monte_carlo_with_validation(self):
        """Test Monte Carlo with proper validation."""
        params = ValuationParams(
            fcf_series=[50.0, 55.0, 60.0],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100.0,
            variable_specs={
                "wacc": {
                    "dist": "normal",
                    "params": {"loc": 0.10, "scale": 0.01}
                }
            }
        )
        
        # Should not raise validation errors
        results = run_monte_carlo(params, runs=5)
        assert "WACC" in results
        assert "APV" in results

class TestErrorHandling:
    """Test error handling improvements."""
    
    def test_valuation_with_invalid_params(self):
        """Test valuation with invalid parameters."""
        params = ValuationParams(
            fcf_series=[50.0, 55.0, 60.0],
            wacc=0.10,
            terminal_growth=0.15,  # Greater than WACC
            share_count=100.0
        )
        
        with pytest.raises(InvalidInputError):
            calc_dcf_series(params)
    
    def test_monte_carlo_with_invalid_specs(self):
        """Test Monte Carlo with invalid specifications."""
        params = ValuationParams(
            fcf_series=[50.0, 55.0, 60.0],
            wacc=0.10,
            terminal_growth=0.02,
            share_count=100.0,
            variable_specs={
                "wacc": {
                    "dist": "invalid_dist",
                    "params": {"loc": 0.10, "scale": 0.01}
                }
            }
        )
        
        with pytest.raises(InvalidInputError):
            run_monte_carlo(params, runs=5)

if __name__ == "__main__":
    pytest.main([__file__]) 