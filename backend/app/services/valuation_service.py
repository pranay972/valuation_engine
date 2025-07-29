"""
Valuation service that uses the finance_core calculator directly.
"""

import sys
import os
from typing import Dict, Any, Optional
import traceback

# Import from finance_core directory
import sys
import os

# Add finance_core to path for imports
finance_core_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'finance_core')
if finance_core_path not in sys.path:
    sys.path.insert(0, finance_core_path)

from finance_calculator import CleanModularFinanceCalculator, FinancialInputs


class ValuationService:
    """Service class for handling valuation calculations."""
    
    def __init__(self):
        """Initialize the valuation service."""
        self.calculator = CleanModularFinanceCalculator()
    
    def calculate_valuation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive valuation using the finance_core calculator.
        
        Args:
            request_data: Dictionary containing valuation request data
            
        Returns:
            Dictionary with all calculation results
            
        Raises:
            ValueError: If calculation fails
        """
        try:
            # Extract financial inputs from request
            financial_inputs_data = request_data.get('financial_inputs', {})
            
            # Convert to finance_core FinancialInputs
            financial_inputs = FinancialInputs(
                revenue=financial_inputs_data.get('revenue', []),
                ebit_margin=financial_inputs_data.get('ebit_margin', 0.0),
                capex=financial_inputs_data.get('capex', []),
                depreciation=financial_inputs_data.get('depreciation', []),
                nwc_changes=financial_inputs_data.get('nwc_changes', []),
                tax_rate=financial_inputs_data.get('tax_rate', 0.0),
                terminal_growth=financial_inputs_data.get('terminal_growth', 0.0),
                wacc=financial_inputs_data.get('wacc', 0.0),
                share_count=financial_inputs_data.get('share_count', 0.0),
                cost_of_debt=financial_inputs_data.get('cost_of_debt', 0.0),
                amortization=financial_inputs_data.get('amortization', []),
                other_non_cash=financial_inputs_data.get('other_non_cash', []),
                other_working_capital=financial_inputs_data.get('other_working_capital', []),
                debt_schedule=financial_inputs_data.get('debt_schedule', {}),
                cash_balance=financial_inputs_data.get('cash_balance', 0.0),
                unlevered_cost_of_equity=financial_inputs_data.get('unlevered_cost_of_equity', 0.0),
                cost_of_equity=financial_inputs_data.get('cost_of_equity', 0.0),
                risk_free_rate=financial_inputs_data.get('risk_free_rate', 0.03),
                market_risk_premium=financial_inputs_data.get('market_risk_premium', 0.06),
                levered_beta=financial_inputs_data.get('levered_beta', 1.0),
                unlevered_beta=financial_inputs_data.get('unlevered_beta', 1.0),
                target_debt_ratio=financial_inputs_data.get('target_debt_ratio', 0.3),
                comparable_multiples=financial_inputs_data.get('comparable_multiples'),
                scenarios=financial_inputs_data.get('scenarios'),
                sensitivity_analysis=financial_inputs_data.get('sensitivity_analysis'),
                monte_carlo_specs=financial_inputs_data.get('monte_carlo_specs')
            )
            
            # Run comprehensive valuation
            results = self.calculator.run_comprehensive_valuation(
                financial_inputs, 
                request_data.get('company_name', 'Company'),
                request_data.get('valuation_date', '2024-01-01')
            )
            
            # Add request metadata to results
            results['company_name'] = request_data.get('company_name', 'Company')
            results['valuation_date'] = request_data.get('valuation_date', '2024-01-01')
            
            return results
            
        except Exception as e:
            error_msg = f"Valuation calculation failed: {str(e)}"
            details = traceback.format_exc() if os.environ.get('FLASK_DEBUG') == 'True' else None
            raise ValueError(error_msg) from e
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample valuation data for testing."""
        return {
            "company_name": "TechCorp Inc.",
            "valuation_date": "2024-01-01",
            "financial_inputs": {
                "revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
                "ebit_margin": 0.18,
                "tax_rate": 0.25,
                "capex": [187.5, 206.3, 226.9, 249.6, 274.5],
                "depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
                "nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
                "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
                "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
                "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
                "terminal_growth": 0.025,
                "wacc": 0.095,
                "share_count": 45.2,
                "cost_of_debt": 0.065,
                "cash_balance": 50.0,
                "risk_free_rate": 0.03,
                "market_risk_premium": 0.06,
                "levered_beta": 1.2,
                "unlevered_beta": 1.0,
                "target_debt_ratio": 0.3,
                "debt_schedule": {
                    "0": 150.0,
                    "1": 135.0,
                    "2": 120.0,
                    "3": 105.0,
                    "4": 90.0
                },
                "scenarios": {
                    "optimistic": {
                        "ebit_margin": 0.22,
                        "terminal_growth_rate": 0.03
                    },
                    "pessimistic": {
                        "ebit_margin": 0.14,
                        "terminal_growth_rate": 0.015
                    }
                }
            }
        } 