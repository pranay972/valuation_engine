import sys
import os
import json
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _import_finance_core():
    """Import finance core modules from backend finance_core directory"""
    try:
        from finance_core.finance_calculator import FinancialValuationEngine, FinancialInputs
        logger.info("Successfully imported finance_calculator from backend finance_core")
        return FinancialValuationEngine, FinancialInputs
    except ImportError as e:
        logger.error(f"Failed to import finance_calculator from backend finance_core: {e}")
        return None, None

# Import finance core modules
FinancialValuationEngine, FinancialInputs = _import_finance_core()

class FinanceCoreService:
    """Service for integrating with the finance core calculator"""
    
    def __init__(self):
        """Initialize the service"""
        self.calculator = None
        if FinancialValuationEngine:
            try:
                self.calculator = FinancialValuationEngine()
                logger.info("Finance calculator initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing calculator: {e}")
        else:
            logger.error("Finance calculator could not be imported")
    
    def create_financial_inputs(self, inputs: Dict[str, Any]) -> Optional[FinancialInputs]:
        """Create FinancialInputs object from dictionary"""
        if not FinancialInputs:
            logger.error("FinancialInputs class not available")
            return None
        
        try:
            financial_inputs = inputs.get('financial_inputs', {})
            
            # Create FinancialInputs object with required fields
            fi = FinancialInputs(
                revenue=financial_inputs['revenue'],
                ebit_margin=financial_inputs['ebit_margin'],
                tax_rate=financial_inputs['tax_rate'],
                capex=financial_inputs['capex'],
                depreciation=financial_inputs['depreciation'],
                nwc_changes=financial_inputs['nwc_changes'],
                share_count=financial_inputs['share_count'],
                terminal_growth=financial_inputs['terminal_growth_rate'],
                wacc=financial_inputs['weighted_average_cost_of_capital'],
                cost_of_debt=financial_inputs['cost_of_debt']
            )
            
            # Add optional fields if present
            optional_fields = [
                'cash_balance', 'amortization', 'other_non_cash', 
                'other_working_capital', 'debt_schedule', 'comparable_multiples', 
                'scenarios', 'sensitivity_analysis', 'monte_carlo_specs',
                'unlevered_cost_of_equity'
            ]
            
            for field in optional_fields:
                if field in financial_inputs:
                    if field == 'debt_schedule' and financial_inputs[field]:
                        # Convert debt schedule keys from strings to integers if needed
                        debt_schedule = financial_inputs[field]
                        if debt_schedule and isinstance(debt_schedule, dict) and len(debt_schedule) > 0:
                            # Check if keys are strings and convert to integers
                            first_key = next(iter(debt_schedule.keys()))
                            if isinstance(first_key, str):
                                debt_schedule = {int(k): v for k, v in debt_schedule.items()}
                        setattr(fi, field, debt_schedule)
                    else:
                        setattr(fi, field, financial_inputs[field])
                elif field in inputs:
                    setattr(fi, field, inputs[field])
            
            logger.info("Successfully created FinancialInputs object")
            return fi
            
        except Exception as e:
            logger.error(f"Error creating FinancialInputs: {e}", exc_info=True)
            return None
    
    def validate_inputs(self, analysis_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs for specific analysis type"""
        logger.info(f"Validating inputs for analysis type: {analysis_type}")
        
        errors = []
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
        if analysis_type in ['dcf_wacc', 'apv', 'scenario', 'sensitivity', 'monte_carlo']:
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                errors.append('Missing required field: weighted_average_cost_of_capital')
            if 'terminal_growth_rate' not in financial_inputs:
                errors.append('Missing required field: terminal_growth_rate')
            if 'cost_of_debt' not in financial_inputs:
                errors.append('Missing required field: cost_of_debt')
        
        if analysis_type == 'apv':
            if 'unlevered_cost_of_equity' not in financial_inputs:
                errors.append('Missing required field: unlevered_cost_of_equity')
        
        elif analysis_type == 'multiples':
            if 'comparable_multiples' not in inputs:
                errors.append('Missing required field: comparable_multiples')
        
        elif analysis_type == 'scenario':
            if 'scenarios' not in inputs:
                errors.append('Missing required field: scenarios')
        
        elif analysis_type == 'sensitivity':
            if 'sensitivity_analysis' not in inputs:
                errors.append('Missing required field: sensitivity_analysis')
        
        elif analysis_type == 'monte_carlo':
            if 'monte_carlo_specs' not in inputs:
                errors.append('Missing required field: monte_carlo_specs')
        
        valid = len(errors) == 0
        
        if valid:
            logger.info("Input validation passed successfully")
        else:
            logger.error(f"Input validation failed with {len(errors)} errors: {errors}")
        
        return {
            'valid': valid,
            'errors': errors
        }
    
    def run_analysis(self, analysis_type: str, inputs: Dict[str, Any], company_name: str = "Company") -> Dict[str, Any]:
        """Run analysis using finance core calculator"""
        logger.info(f"Starting analysis for {company_name} with type: {analysis_type}")
        
        if not self.calculator:
            return {
                'success': False,
                'error': 'Finance calculator not available',
                'analysis_type': analysis_type,
                'company_name': company_name
            }
        
        try:
            # Validate inputs
            validation = self.validate_inputs(analysis_type, inputs)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid inputs',
                    'validation_errors': validation['errors'],
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            # Create FinancialInputs object
            fi = self.create_financial_inputs(inputs)
            if not fi:
                return {
                    'success': False,
                    'error': 'Failed to create financial inputs',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            # Run analysis based on type
            logger.info(f"Running {analysis_type} analysis...")
            
            if analysis_type == 'dcf_wacc':
                results = self.calculator.calculate_dcf_valuation(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            elif analysis_type == 'apv':
                results = self.calculator.calculate_apv_valuation(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            elif analysis_type == 'multiples':
                results = self.calculator.analyze_comparable_multiples(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            elif analysis_type == 'scenario':
                results = self.calculator.perform_scenario_analysis(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            elif analysis_type == 'sensitivity':
                results = self.calculator.perform_sensitivity_analysis(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            elif analysis_type == 'monte_carlo':
                results = self.calculator.simulate_monte_carlo(fi)
                return {
                    'success': True,
                    'results': results,
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported analysis type: {analysis_type}',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }
        
        except Exception as e:
            logger.error(f'Analysis failed: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'analysis_type': analysis_type,
                'company_name': company_name
            } 