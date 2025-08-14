import sys
import os
import json
from typing import Dict, Any, Optional
import numpy as np

# Add finance core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'finance_core'))

try:
    from finance_calculator import CleanModularFinanceCalculator, FinancialInputs
except ImportError as e:
    print(f"Warning: Could not import finance_calculator: {e}")
    CleanModularFinanceCalculator = None
    FinancialInputs = None

class FinanceCoreService:
    """Service for integrating with the finance core calculator"""
    
    def __init__(self):
        self.calculator = None
        if CleanModularFinanceCalculator:
            self.calculator = CleanModularFinanceCalculator()
    
    def validate_inputs(self, analysis_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs for specific analysis type"""
        errors = []
        warnings = []
        
        financial_inputs = inputs.get('financial_inputs', {})
        
        # Basic validation
        required_fields = [
            'revenue', 'ebit_margin', 'tax_rate', 'capex', 'depreciation',
            'nwc_changes', 'share_count'
        ]
        
        for field in required_fields:
            if field not in financial_inputs:
                errors.append(f'Missing required field: {field}')
        
        # Analysis-specific validation
        if analysis_type == 'dcf_wacc':
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                errors.append('Missing required field: weighted_average_cost_of_capital')
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
        
        elif analysis_type == 'apv':
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
            
            # FIXED: Check both direct and nested cost_of_capital structure
            cost_of_capital = financial_inputs.get('cost_of_capital', {})
            if ('unlevered_cost_of_equity' not in financial_inputs and 
                'unlevered_cost_of_equity' not in cost_of_capital):
                errors.append('Missing required field: unlevered_cost_of_equity (in financial_inputs or cost_of_capital)')
        
        elif analysis_type == 'multiples':
            if 'comparable_multiples' not in inputs:
                errors.append('Missing required field: comparable_multiples')
        
        elif analysis_type == 'scenario':
            if 'scenarios' not in inputs:
                errors.append('Missing required field: scenarios')
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                errors.append('Missing required field: weighted_average_cost_of_capital')
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
        
        elif analysis_type == 'sensitivity':
            if 'sensitivity_analysis' not in inputs:
                errors.append('Missing required field: sensitivity_analysis')
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                errors.append('Missing required field: weighted_average_cost_of_capital')
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
        
        elif analysis_type == 'monte_carlo':
            if 'monte_carlo_specs' not in inputs:
                errors.append('Missing required field: monte_carlo_specs')
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                errors.append('Missing required field: weighted_average_cost_of_capital')
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
            
            # FIXED: Check for runs parameter in Monte Carlo specs
            monte_carlo_specs = inputs.get('monte_carlo_specs', {})
            if 'runs' not in monte_carlo_specs:
                errors.append('Missing required field: runs in monte_carlo_specs')
            else:
                runs = monte_carlo_specs.get('runs')
                if not isinstance(runs, int) or runs <= 0:
                    errors.append('runs must be a positive integer')
                elif runs > 10000:
                    warnings.append('runs value is very high (>10,000) which may cause performance issues')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def create_financial_inputs(self, inputs: Dict[str, Any]) -> Optional[FinancialInputs]:
        """Create FinancialInputs object from dictionary"""
        if not FinancialInputs:
            return None
        
        try:
            financial_inputs = inputs.get('financial_inputs', {})
            
            # Extract required fields
            revenue = financial_inputs.get('revenue', [])
            ebit_margin = financial_inputs.get('ebit_margin', 0.0)
            tax_rate = financial_inputs.get('tax_rate', 0.0)
            capex = financial_inputs.get('capex', [])
            depreciation = financial_inputs.get('depreciation', [])
            nwc_changes = financial_inputs.get('nwc_changes', [])
            share_count = financial_inputs.get('share_count', 0.0)
            
            # Create FinancialInputs object with all required fields
            fi = FinancialInputs(
                revenue=revenue,
                ebit_margin=ebit_margin,
                tax_rate=tax_rate,
                capex=capex,
                depreciation=depreciation,
                nwc_changes=nwc_changes,
                share_count=share_count,
                terminal_growth=financial_inputs.get('terminal_growth_rate', 0.0),
                wacc=financial_inputs.get('weighted_average_cost_of_capital', 0.0),
                cost_of_debt=financial_inputs.get('cost_of_debt', 0.0)
            )
            
            # Add optional fields
            if 'cash_balance' in financial_inputs:
                fi.cash_balance = financial_inputs['cash_balance']
            
            if 'amortization' in financial_inputs:
                fi.amortization = financial_inputs['amortization']
            
            if 'other_non_cash' in financial_inputs:
                fi.other_non_cash = financial_inputs['other_non_cash']
            
            if 'other_working_capital' in financial_inputs:
                fi.other_working_capital = financial_inputs['other_working_capital']
            
            # FIXED: Add cost of capital fields from nested structure
            if 'cost_of_capital' in financial_inputs:
                cost_of_capital = financial_inputs['cost_of_capital']
                fi.risk_free_rate = cost_of_capital.get('risk_free_rate', 0.03)
                fi.market_risk_premium = cost_of_capital.get('market_risk_premium', 0.06)
                fi.levered_beta = cost_of_capital.get('levered_beta', 1.0)
                fi.unlevered_beta = cost_of_capital.get('unlevered_beta', 1.0)
                fi.target_debt_ratio = cost_of_capital.get('target_debt_to_value_ratio', 0.3)
                fi.unlevered_cost_of_equity = cost_of_capital.get('unlevered_cost_of_equity', 0.0)
            
            # FIXED: Add debt schedule mapping
            if 'debt_schedule' in financial_inputs:
                fi.debt_schedule = financial_inputs['debt_schedule']
            
            # Add analysis-specific fields
            if 'comparable_multiples' in inputs:
                fi.comparable_multiples = inputs['comparable_multiples']
            
            if 'scenarios' in inputs:
                fi.scenarios = inputs['scenarios']
            
            if 'sensitivity_analysis' in inputs:
                fi.sensitivity_analysis = inputs['sensitivity_analysis']
            
            if 'monte_carlo_specs' in inputs:
                fi.monte_carlo_specs = inputs['monte_carlo_specs']
            
            return fi
            
        except Exception as e:
            print(f"Error creating FinancialInputs: {e}")
            return None
    
    def run_analysis(self, analysis_type: str, inputs: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """Run analysis using finance core calculator"""
        if not self.calculator:
            return {
                'success': False,
                'error': 'Finance calculator not available'
            }
        
        try:
            # Validate inputs
            validation = self.validate_inputs(analysis_type, inputs)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid inputs',
                    'validation_errors': validation['errors']
                }
            
            # Create FinancialInputs object
            fi = self.create_financial_inputs(inputs)
            if not fi:
                return {
                    'success': False,
                    'error': 'Failed to create financial inputs'
                }
            
            # Run analysis based on type
            if analysis_type == 'dcf_wacc':
                results = self.calculator.run_dcf_valuation(fi)
                return {
                    'success': True,
                    'results': {
                        'dcf_wacc': results
                    },
                    'enterprise_value': results.get('enterprise_value'),
                    'equity_value': results.get('equity_value'),
                    'price_per_share': results.get('price_per_share')
                }
            
            elif analysis_type == 'apv':
                results = self.calculator.run_apv_valuation(fi)
                return {
                    'success': True,
                    'results': {
                        'apv': results
                    },
                    'enterprise_value': results.get('apv_enterprise_value'),
                    'equity_value': results.get('equity_value'),
                    'price_per_share': results.get('price_per_share')
                }
            
            elif analysis_type == 'multiples':
                results = self.calculator.run_comparable_multiples(fi)
                return {
                    'success': True,
                    'results': {
                        'comparable_multiples': results
                    },
                    'enterprise_value': results.get('mean_enterprise_value'),
                    'equity_value': results.get('mean_equity_value'),
                    'price_per_share': results.get('mean_price_per_share')
                }
            
            elif analysis_type == 'scenario':
                results = self.calculator.run_scenario_analysis(fi)
                return {
                    'success': True,
                    'results': {
                        'scenarios': results
                    },
                    'enterprise_value': results.get('base_case', {}).get('enterprise_value'),
                    'equity_value': results.get('base_case', {}).get('equity_value'),
                    'price_per_share': results.get('base_case', {}).get('price_per_share')
                }
            
            elif analysis_type == 'sensitivity':
                results = self.calculator.run_sensitivity_analysis(fi)
                return {
                    'success': True,
                    'results': {
                        'sensitivity_analysis': results
                    },
                    'enterprise_value': None,  # Multiple values in sensitivity
                    'equity_value': None,
                    'price_per_share': None
                }
            
            elif analysis_type == 'monte_carlo':
                # FIXED: Extract runs parameter from Monte Carlo specs
                monte_carlo_specs = inputs.get('monte_carlo_specs', {})
                runs = monte_carlo_specs.get('runs', 1000)  # Default to 1000 if not specified
                
                # FIXED: Remove runs from specs before passing to calculator to avoid it being treated as a variable
                monte_carlo_specs_for_calc = {k: v for k, v in monte_carlo_specs.items() if k != 'runs'}
                fi.monte_carlo_specs = monte_carlo_specs_for_calc
                
                results = self.calculator.run_monte_carlo_simulation(fi, runs=runs)
                return {
                    'success': True,
                    'results': {
                        'monte_carlo': results
                    },
                    'enterprise_value': results.get('enterprise_value', {}).get('mean'),
                    'equity_value': results.get('equity_value', {}).get('mean'),
                    'price_per_share': results.get('price_per_share', {}).get('mean')
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported analysis type: {analysis_type}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def get_sample_inputs(self, analysis_type: str) -> Dict[str, Any]:
        """Get sample inputs for analysis type"""
        sample_inputs = {
            'financial_inputs': {
                'revenue': [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
                'ebit_margin': 0.18,
                'tax_rate': 0.25,
                'capex': [187.5, 206.3, 226.9, 249.6, 274.5],
                'depreciation': [125.0, 137.5, 151.3, 166.4, 183.0],
                'nwc_changes': [62.5, 68.8, 75.6, 83.2, 91.5],
                'weighted_average_cost_of_capital': 0.095,
                'terminal_growth_rate': 0.025,
                'share_count': 45.2,
                'cost_of_debt': 0.065,
                'cash_balance': 50.0,
                
                # FIXED: Add missing cost of capital structure
                'cost_of_capital': {
                    'risk_free_rate': 0.03,
                    'market_risk_premium': 0.06,
                    'levered_beta': 1.2,
                    'unlevered_beta': 1.0,
                    'target_debt_to_value_ratio': 0.3,
                    'unlevered_cost_of_equity': 0.11
                },
                
                # FIXED: Add debt schedule
                'debt_schedule': {
                    '0': 150.0,
                    '1': 135.0,
                    '2': 120.0,
                    '3': 105.0,
                    '4': 90.0
                }
            }
        }
        
        # Add analysis-specific sample inputs
        if analysis_type == 'multiples':
            sample_inputs['comparable_multiples'] = {
                'EV/EBITDA': [12.5, 14.2, 13.8, 15.1],
                'P/E': [18.5, 22.1, 20.8, 24.3],
                'EV/FCF': [15.2, 17.8, 16.5, 18.9],
                'EV/Revenue': [2.8, 3.2, 3.0, 3.5]
            }
        
        elif analysis_type == 'scenario':
            sample_inputs['scenarios'] = {
                'base_case': {},
                'optimistic': {
                    'ebit_margin': 0.22,
                    'terminal_growth_rate': 0.03,
                    'weighted_average_cost_of_capital': 0.085
                },
                'pessimistic': {
                    'ebit_margin': 0.14,
                    'terminal_growth_rate': 0.015,
                    'weighted_average_cost_of_capital': 0.105
                }
            }
        
        elif analysis_type == 'sensitivity':
            sample_inputs['sensitivity_analysis'] = {
                'wacc_range': [0.075, 0.085, 0.095, 0.105, 0.115],
                'ebit_margin_range': [0.14, 0.16, 0.18, 0.20, 0.22],
                'terminal_growth_range': [0.015, 0.020, 0.025, 0.030, 0.035]
            }
        
        elif analysis_type == 'monte_carlo':
            sample_inputs['monte_carlo_specs'] = {
                # FIXED: Add runs parameter to allow users to specify number of simulations
                'runs': 1000,
                'ebit_margin': {
                    'distribution': 'normal',
                    'params': {'mean': 0.18, 'std': 0.02}
                },
                'weighted_average_cost_of_capital': {
                    'distribution': 'normal',
                    'params': {'mean': 0.095, 'std': 0.01}
                },
                'terminal_growth_rate': {
                    'distribution': 'normal',
                    'params': {'mean': 0.025, 'std': 0.005}
                },
                'levered_beta': {
                    'distribution': 'normal',
                    'params': {'mean': 1.2, 'std': 0.1}
                }
            }
        
        return sample_inputs
