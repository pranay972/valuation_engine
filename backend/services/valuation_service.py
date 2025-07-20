"""
Service layer for the Financial Valuation Engine

This module provides business logic services that separate core functionality
from UI components and API endpoints.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

from ..core.models.params import ValuationParams
from ..core.valuation.dcf import calc_dcf_series, calc_apv
from ..core.valuation.monte_carlo import run_monte_carlo
from ..core.valuation.multiples import run_multiples_analysis
from ..core.valuation.scenario import run_scenarios, detect_circular_references
from ..core.valuation.sensitivity import run_sensitivity_analysis
from ..utils.exceptions import CalculationError, InvalidInputError, DataValidationError
from ..utils.validation import validate_financial_data, validate_valuation_params
from ..config.logging import get_logger
from ..utils.cache import get_cache_stats

logger = get_logger(__name__)

class ValuationService:
    """
    Service class for handling valuation calculations and business logic.
    
    This class encapsulates all the business logic for valuation calculations,
    providing a clean interface for UI components and API endpoints.
    """
    
    def __init__(self):
        """Initialize the valuation service."""
        self.logger = logger
    
    def validate_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean input data.
        
        Args:
            input_data: Raw input data from user
            
        Returns:
            Cleaned and validated input data
            
        Raises:
            InvalidInputError: If validation fails
        """
        try:
            # Extract and validate financial series
            validated_data = {}
            
            # Validate revenue series if provided
            if 'revenue' in input_data and input_data['revenue']:
                revenue = self._parse_series_input(input_data['revenue'], 'revenue')
                validate_financial_data(revenue, 'revenue')
                validated_data['revenue'] = revenue
            
            # Validate FCF series if provided
            if 'fcf_series' in input_data and input_data['fcf_series']:
                fcf_series = self._parse_series_input(input_data['fcf_series'], 'fcf_series')
                validate_financial_data(fcf_series, 'fcf_series')
                validated_data['fcf_series'] = fcf_series
            
            # Validate other financial series
            for series_name in ['capex', 'depreciation', 'nwc_changes']:
                if series_name in input_data and input_data[series_name]:
                    series_data = self._parse_series_input(input_data[series_name], series_name)
                    validate_financial_data(series_data, series_name)
                    validated_data[series_name] = series_data
            
            # Validate scalar parameters
            scalar_params = ['ebit_margin', 'wacc', 'terminal_growth', 'tax_rate', 'share_count', 'cost_of_debt']
            for param in scalar_params:
                if param in input_data:
                    value = float(input_data[param])
                    validated_data[param] = value
            
            # Validate boolean parameters
            if 'mid_year_convention' in input_data:
                validated_data['mid_year_convention'] = bool(input_data['mid_year_convention'])
            
            # Validate debt schedule
            if 'debt_schedule' in input_data and input_data['debt_schedule']:
                debt_schedule = {}
                for year_str, amount in input_data['debt_schedule'].items():
                    try:
                        year = int(year_str)
                        debt_schedule[year] = float(amount)
                    except (ValueError, TypeError):
                        raise InvalidInputError(
                            f"Invalid debt schedule entry: year={year_str}, amount={amount}",
                            field='debt_schedule'
                        )
                validated_data['debt_schedule'] = debt_schedule
            
            # Validate Monte Carlo specifications
            if 'variable_specs' in input_data and input_data['variable_specs']:
                validated_data['variable_specs'] = input_data['variable_specs']
            
            # Validate scenarios
            if 'scenarios' in input_data and input_data['scenarios']:
                validated_data['scenarios'] = input_data['scenarios']
            
            # Validate sensitivity ranges
            if 'sensitivity_ranges' in input_data and input_data['sensitivity_ranges']:
                validated_data['sensitivity_ranges'] = input_data['sensitivity_ranges']
            
            return validated_data
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            raise
    
    def _parse_series_input(self, input_text: Union[str, List[float]], name: str) -> List[float]:
        """
        Parse input into list of floats. Handles both strings and lists.
        
        Args:
            input_text: Comma-separated string of numbers or list of numbers
            name: Name of the series for error messages
            
        Returns:
            List of parsed float values
            
        Raises:
            InvalidInputError: If parsing fails
        """
        try:
            # If input is already a list, validate and return
            if isinstance(input_text, list):
                values = [float(x) for x in input_text]
                if not values:
                    raise InvalidInputError(f"Empty {name} series", field=name)
                return values
            
            # If input is a string, parse comma-separated values
            elif isinstance(input_text, str):
                values = [float(x.strip()) for x in input_text.split(",") if x.strip()]
                if not values:
                    raise InvalidInputError(f"Empty {name} series", field=name)
                return values
            
            else:
                raise InvalidInputError(
                    f"Invalid {name} format. Expected string or list, got {type(input_text)}",
                    field=name,
                    value=str(input_text)
                )
                
        except ValueError as e:
            raise InvalidInputError(
                f"Invalid numbers in {name}. Please use valid numeric values.",
                field=name,
                value=str(input_text)
            )
    
    def create_valuation_params(self, validated_data: Dict[str, Any]) -> ValuationParams:
        """
        Create ValuationParams object from validated data.
        
        Args:
            validated_data: Validated input data
            
        Returns:
            ValuationParams object
            
        Raises:
            InvalidInputError: If required parameters are missing
        """
        try:
            # Set defaults for missing parameters
            defaults = {
                'revenue': [],
                'ebit_margin': 0.20,
                'capex': [],
                'depreciation': [],
                'nwc_changes': [],
                'fcf_series': [],
                'terminal_growth': 0.02,
                'wacc': 0.10,
                'tax_rate': 0.21,
                'mid_year_convention': False,
                'share_count': 100000000.0,
                'cost_of_debt': 0.05,
                'debt_schedule': {},
                'variable_specs': {},
                'scenarios': {},
                'sensitivity_ranges': {}
            }
            
            # Merge validated data with defaults
            params_dict = {**defaults, **validated_data}
            
            return ValuationParams(**params_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to create ValuationParams: {str(e)}")
            raise InvalidInputError(f"Failed to create valuation parameters: {str(e)}")
    
    def run_valuation_analyses(
        self, 
        params: ValuationParams, 
        analyses: List[str], 
        comps_data: Optional[List[Dict[str, Any]]] = None,
        mc_runs: int = 2000
    ) -> Dict[str, Any]:
        """
        Run specified valuation analyses.
        
        Args:
            params: ValuationParams object
            analyses: List of analysis types to run
            comps_data: Comparable companies data for multiples analysis
            mc_runs: Number of Monte Carlo runs
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            CalculationError: If any analysis fails
        """
        results = {}
        
        try:
            # Run WACC DCF
            if "WACC DCF" in analyses:
                self.logger.info("Running WACC DCF analysis")
                ev, equity, ps = calc_dcf_series(params)
                results["wacc_dcf"] = {
                    "enterprise_value": float(ev),
                    "equity_value": float(equity),
                    "price_per_share": float(ps) if ps is not None else None
                }
            
            # Run APV
            if "APV" in analyses:
                self.logger.info("Running APV analysis")
                ev, equity, ps = calc_apv(params)
                results["apv"] = {
                    "enterprise_value": float(ev),
                    "equity_value": float(equity),
                    "price_per_share": float(ps) if ps is not None else None
                }
            
            # Run Monte Carlo
            if "Monte Carlo" in analyses:
                self.logger.info("Running Monte Carlo analysis")
                mc_results = run_monte_carlo(params, runs=mc_runs)
                results["monte_carlo"] = mc_results
            
            # Run Multiples
            if "Multiples" in analyses and comps_data:
                self.logger.info("Running Multiples analysis")
                multiples_results = run_multiples_analysis(params, comps_data)
                results["multiples"] = multiples_results
            
            # Run Scenarios
            if "Scenarios" in analyses and params.scenarios:
                self.logger.info("Running Scenarios analysis")
                scenario_results = run_scenarios(params)
                results["scenarios"] = scenario_results
            
            # Run Sensitivity
            if "Sensitivity" in analyses and params.sensitivity_ranges:
                self.logger.info("Running Sensitivity analysis")
                sensitivity_results = run_sensitivity_analysis(params)
                results["sensitivity"] = sensitivity_results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Valuation analysis failed: {str(e)}")
            raise CalculationError(f"Valuation analysis failed: {str(e)}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics including cache performance.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            cache_stats = get_cache_stats()
            
            return {
                "cache": cache_stats,
                "version": "2.0.0",
                "status": "operational"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {str(e)}")
            return {
                "cache": {},
                "version": "2.0.0",
                "status": "error",
                "error": str(e)
            }

# Global service instance
valuation_service = ValuationService() 