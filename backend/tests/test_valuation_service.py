"""
Tests for the valuation service.
"""

import pytest
import sys
import os

# Add the root directory to the path to import finance_core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.valuation_service import ValuationService


class TestValuationService:
    """Test cases for ValuationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ValuationService()
    
    def test_get_sample_data(self):
        """Test that sample data is returned correctly."""
        sample_data = self.service.get_sample_data()
        
        assert 'company_name' in sample_data
        assert 'valuation_date' in sample_data
        assert 'financial_inputs' in sample_data
        
        financial_inputs = sample_data['financial_inputs']
        assert 'revenue' in financial_inputs
        assert 'ebit_margin' in financial_inputs
        assert 'tax_rate' in financial_inputs
    
    def test_calculate_valuation_basic(self):
        """Test basic valuation calculation."""
        sample_data = self.service.get_sample_data()
        
        # Calculate valuation
        result = self.service.calculate_valuation(sample_data)
        
        # Check that results are returned
        assert 'company_name' in result
        assert 'valuation_date' in result
        assert 'dcf_valuation' in result
        
        # Check DCF results
        dcf_results = result['dcf_valuation']
        assert 'enterprise_value' in dcf_results
        assert 'equity_value' in dcf_results
        assert 'price_per_share' in dcf_results
        
        # Check that values are reasonable
        assert dcf_results['enterprise_value'] > 0
        assert isinstance(dcf_results['equity_value'], (int, float))
        assert isinstance(dcf_results['price_per_share'], (int, float))
    
    def test_calculate_valuation_invalid_input(self):
        """Test that invalid input raises appropriate error."""
        invalid_data = {
            "company_name": "Test Company",
            "financial_inputs": {
                "revenue": [],  # Empty revenue list
                "ebit_margin": 0.18,
                "tax_rate": 0.25,
                "capex": [],
                "depreciation": [],
                "nwc_changes": [],
                "terminal_growth": 0.025,
                "wacc": 0.095,
                "share_count": 45.2,
                "cost_of_debt": 0.065
            }
        }
        
        with pytest.raises(ValueError):
            self.service.calculate_valuation(invalid_data) 