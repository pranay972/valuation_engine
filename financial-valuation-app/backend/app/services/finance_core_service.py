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
        from finance_core.finance_calculator import (
            FinancialValuationEngine,
            FinancialInputs,
            parse_financial_inputs,
        )
        logger.info("Successfully imported finance_calculator from backend finance_core")
        return FinancialValuationEngine, FinancialInputs, parse_financial_inputs
    except ImportError as e:
        logger.error(f"Failed to import finance_calculator from backend finance_core: {e}")
        return None, None, None

# Import finance core modules
FinancialValuationEngine, FinancialInputs, parse_financial_inputs_fn = _import_finance_core()

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
            if parse_financial_inputs_fn:
                fi = parse_financial_inputs_fn(inputs)
                logger.info("Successfully created FinancialInputs via parse_financial_inputs (direct parity)")
                return fi
            logger.error("parse_financial_inputs function not available")
            return None
            
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
        
        # For APV, do not require unlevered_cost_of_equity explicitly; local calculator can derive it
        # if analysis_type == 'apv':
        #     pass
        
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
            
            # Run comprehensive valuation once to ensure identical logic/paths as local
            logger.info("Running comprehensive valuation for exact parity...")
            valuation_date = inputs.get('valuation_date', '2024-01-01')
            all_results = self.calculator.perform_comprehensive_valuation(
                inputs=fi,
                company_name=company_name,
                valuation_date=valuation_date
            )

            # Map analysis_type to section key
            type_to_key = {
                'dcf_wacc': 'dcf_valuation',
                'apv': 'apv_valuation',
                'multiples': 'comparable_valuation',
                'scenario': 'scenarios',
                'sensitivity': 'sensitivity_analysis',
                'monte_carlo': 'monte_carlo_simulation',
            }
            section_key = type_to_key.get(analysis_type)
            if not section_key:
                return {
                    'success': False,
                    'error': f'Unsupported analysis type: {analysis_type}',
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }

            section = all_results.get(section_key, {})
            # Include both normalized and legacy keys for compatibility
            legacy_map = {
                'dcf_valuation': 'dcf_wacc',
                'apv_valuation': 'apv',
                'comparable_valuation': 'comparable_multiples',
                'scenarios': 'scenario',
                'sensitivity_analysis': 'sensitivity',
                'monte_carlo_simulation': 'monte_carlo',
            }
            legacy_key = legacy_map.get(section_key)
            results_payload = {section_key: section}
            if legacy_key:
                results_payload[legacy_key] = section

            return {
                'success': True,
                'results': results_payload,
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