import sys
import os
import json
import logging
from typing import Dict, Any, Optional
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store original sys.path to restore it later
_original_sys_path = sys.path.copy()

def _import_finance_core():
    """Import finance core modules with proper path management and error handling"""
    try:
        # Try importing from the current finance_core directory first
        from finance_core.finance_calculator import FinancialValuationEngine, FinancialInputs
        logger.info("Successfully imported finance_calculator from current finance_core")
        return FinancialValuationEngine, FinancialInputs
    except ImportError as e:
        logger.warning(f"Could not import from current finance_core: {e}")
        try:
            # Try importing from the backend finance_core directory
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'finance_core'))
            from finance_calculator import FinancialValuationEngine, FinancialInputs
            logger.info("Successfully imported finance_calculator from backend finance_core")
            return FinancialValuationEngine, FinancialInputs
        except ImportError as e2:
            logger.warning(f"Could not import from backend finance_core: {e2}")
            try:
                # Try importing from the parent directory
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                from finance_core.finance_calculator import FinancialValuationEngine, FinancialInputs
                logger.info("Successfully imported finance_calculator from parent directory")
                return FinancialValuationEngine, FinancialInputs
            except ImportError as e3:
                logger.error(f"Failed to import finance_calculator from all paths: {e3}")
                return None, None
        finally:
            # Restore original sys.path to prevent corruption
            sys.path = _original_sys_path.copy()

# Import finance core modules
FinancialValuationEngine, FinancialInputs = _import_finance_core()

class FinanceCoreService:
    """Service for integrating with the finance core calculator"""
    
    def __init__(self):
        """Initialize the service with proper error handling"""
        self.calculator = None
        self._import_status = "unknown"
        
        if FinancialValuationEngine:
            try:
                self.calculator = FinancialValuationEngine()
                self._import_status = "success"
                logger.info("Finance calculator initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing calculator: {e}")
                self._import_status = f"initialization_failed: {str(e)}"
        else:
            self._import_status = "import_failed"
            logger.error("Finance calculator could not be imported")
    
    def create_financial_inputs(self, inputs: Dict[str, Any]) -> Optional[FinancialInputs]:
        """Create FinancialInputs object from dictionary with enhanced error handling"""
        if not FinancialInputs:
            error_msg = f"FinancialInputs class not available. Import status: {self._import_status}"
            logger.error(error_msg)
            return None
        
        try:
            financial_inputs = inputs.get('financial_inputs', {})
            
            # Log input structure for debugging
            logger.info(f"Creating FinancialInputs with {len(financial_inputs)} fields")
            logger.debug(f"Financial inputs keys: {list(financial_inputs.keys())}")
            
            # Extract required fields with validation
            required_fields = {
                'revenue': financial_inputs.get('revenue', []),
                'ebit_margin': financial_inputs.get('ebit_margin', 0.0),
                'tax_rate': financial_inputs.get('tax_rate', 0.0),
                'capex': financial_inputs.get('capex', []),
                'depreciation': financial_inputs.get('depreciation', []),
                'nwc_changes': financial_inputs.get('nwc_changes', []),
                'share_count': financial_inputs.get('share_count', 0.0),
                'terminal_growth': financial_inputs.get('terminal_growth_rate', 0.0),
                'wacc': financial_inputs.get('weighted_average_cost_of_capital', 0.0),
                'cost_of_debt': financial_inputs.get('cost_of_debt', 0.0)
            }
            
            # Validate required fields
            for field_name, field_value in required_fields.items():
                if field_value is None:
                    error_msg = f"Required field '{field_name}' is None"
                    logger.error(error_msg)
                    return None
            
            # Create FinancialInputs object with all required arguments
            fi = FinancialInputs(
                revenue=required_fields['revenue'],
                ebit_margin=required_fields['ebit_margin'],
                tax_rate=required_fields['tax_rate'],
                capex=required_fields['capex'],
                depreciation=required_fields['depreciation'],
                nwc_changes=required_fields['nwc_changes'],
                share_count=required_fields['share_count'],
                terminal_growth=required_fields['terminal_growth'],
                wacc=required_fields['wacc'],
                cost_of_debt=required_fields['cost_of_debt']
            )
            
            # Add APV-specific fields
            if 'unlevered_cost_of_equity' in financial_inputs:
                fi.unlevered_cost_of_equity = financial_inputs['unlevered_cost_of_equity']
            
            # Add other optional fields
            optional_fields = [
                'cash_balance', 'amortization', 'other_non_cash', 
                'other_working_capital', 'comparable_multiples', 
                'scenarios', 'sensitivity_analysis', 'monte_carlo_specs'
            ]
            
            for field in optional_fields:
                if field in financial_inputs:
                    setattr(fi, field, financial_inputs[field])
                elif field in inputs:
                    setattr(fi, field, inputs[field])
            
            logger.info(f"Successfully created FinancialInputs object")
            return fi
            
        except Exception as e:
            error_msg = f"Error creating FinancialInputs: {e}"
            logger.error(error_msg, exc_info=True)
            return None
    
    def validate_inputs(self, analysis_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs for specific analysis type"""
        logger.info(f"Validating inputs for analysis type: {analysis_type}")
        
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
                error_msg = f'Missing required field: {field}'
                errors.append(error_msg)
                logger.error(error_msg)
        
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
            if 'unlevered_cost_of_equity' not in financial_inputs:
                errors.append('Missing required field: unlevered_cost_of_equity')
        
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
        
        valid = len(errors) == 0
        
        if valid:
            logger.info("Input validation passed successfully")
        else:
            logger.error(f"Input validation failed with {len(errors)} errors: {errors}")
        
        return {
            'valid': valid,
            'errors': errors,
            'warnings': warnings
        }
    
    def run_analysis(self, analysis_type: str, inputs: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """Run analysis using finance core calculator"""
        logger.info(f"Starting analysis for {company_name} with type: {analysis_type}")
        if not self.calculator:
            error_msg = 'Finance calculator not available'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'calculator_unavailable',
                'analysis_type': analysis_type,
                'company_name': company_name
            }
        
        try:
            # Validate inputs
            logger.info("Validating inputs...")
            validation = self.validate_inputs(analysis_type, inputs)
            if not validation['valid']:
                error_msg = 'Invalid inputs'
                logger.error(f"{error_msg}: {validation['errors']}")
                return {
                    'success': False,
                    'error': error_msg,
                    'validation_errors': validation['errors'],
                    'error_type': 'validation_failed',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            # Create FinancialInputs object
            fi = self.create_financial_inputs(inputs)
            if not fi:
                error_msg = 'Failed to create financial inputs'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'financial_inputs_creation_failed',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            # Run analysis based on type
            logger.info(f"Running {analysis_type} analysis...")
            
            if analysis_type == 'dcf_wacc':
                results = self.calculator.calculate_dcf_valuation(fi)
                logger.info("DCF WACC analysis completed successfully")
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
                results = self.calculator.calculate_apv_valuation(fi)
                logger.info("APV analysis completed successfully")
                return {
                    'success': True,
                    'results': {
                        'apv': results
                    },
                    'enterprise_value': results.get('enterprise_value'),
                    'equity_value': results.get('equity_value'),
                    'price_per_share': results.get('price_per_share')
                }
            
            elif analysis_type == 'multiples':
                results = self.calculator.analyze_comparable_multiples(fi)
                logger.info("Multiples analysis completed successfully")
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
                results = self.calculator.perform_scenario_analysis(fi)
                logger.info("Scenario analysis completed successfully")
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
                results = self.calculator.perform_sensitivity_analysis(fi)
                logger.info("Sensitivity analysis completed successfully")
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
                results = self.calculator.simulate_monte_carlo(fi)
                logger.info("Monte Carlo simulation completed successfully")
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
                error_msg = f'Unsupported analysis type: {analysis_type}'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'unsupported_analysis_type',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
        
        except Exception as e:
            import traceback
            error_msg = f'Analysis failed: {str(e)}'
            logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'calculation_exception',
                'analysis_type': analysis_type,
                'company_name': company_name,
                'exception_details': str(e),
                'traceback': traceback.format_exc()
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
                'cash_balance': 50.0
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
                }
            }
        
        return sample_inputs 