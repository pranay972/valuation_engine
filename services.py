"""
Service layer for the Financial Valuation Engine

This module provides business logic services that separate core functionality
from UI components and API endpoints.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

from params import ValuationParams
from valuation import calc_dcf_series, calc_apv
from montecarlo import run_monte_carlo
from multiples import run_multiples_analysis
from scenario import run_scenarios, detect_circular_references
from sensitivity import run_sensitivity_analysis
from exceptions import CalculationError, InvalidInputError, DataValidationError
from validation import validate_financial_data, validate_valuation_params
from logging_config import get_logger
from cache import get_cache_stats

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
        comps_file: Optional[str] = None,
        comps_data: Optional[List[Dict[str, Any]]] = None,
        mc_runs: int = 2000
    ) -> Dict[str, Any]:
        """
        Run all selected valuation analyses.
        
        Args:
            params: ValuationParams object
            analyses: List of analysis types to run
            comps_file: Optional path to comparable companies file
            mc_runs: Number of Monte Carlo runs
            
        Returns:
            Dictionary containing results for each analysis
            
        Raises:
            CalculationError: If any analysis fails
        """
        results = {}
        
        try:
            # DCF Analysis
            if "WACC DCF" in analyses:
                try:
                    ev, equity, ps = calc_dcf_series(params)
                    results["wacc_dcf"] = {
                        "enterprise_value": float(ev),
                        "equity_value": float(equity),
                        "price_per_share": float(ps) if ps else None
                    }
                    self.logger.info(f"WACC DCF completed - EV: ${ev:,.0f}")
                except Exception as e:
                    self.logger.error(f"WACC DCF calculation failed: {str(e)}")
                    results["wacc_dcf"] = {"error": str(e)}
            
            if "APV DCF" in analyses:
                try:
                    ev, equity, ps = calc_apv(params)
                    results["apv_dcf"] = {
                        "enterprise_value": float(ev),
                        "equity_value": float(equity),
                        "price_per_share": float(ps) if ps else None
                    }
                    self.logger.info(f"APV DCF completed - EV: ${ev:,.0f}")
                except Exception as e:
                    self.logger.error(f"APV calculation failed: {str(e)}")
                    results["apv_dcf"] = {"error": str(e)}
            
            # Monte Carlo - FIXED VERSION
            if "Monte Carlo" in analyses:
                try:
                    mc_results = run_monte_carlo(params, runs=mc_runs, random_seed=42)
                    # Convert DataFrames to serializable format
                    mc_dict = {}
                    for method, df in mc_results.items():
                        if df.empty:
                            mc_dict[method] = {
                                "data": [],
                                "statistics": {},
                                "error": "No successful Monte Carlo runs"
                            }
                        else:
                            # Handle DataFrame conversion safely
                            try:
                                # Convert DataFrame to records, handling any NaN values
                                df_clean = df.fillna(0)  # Replace NaN with 0
                                records = []
                                for _, row in df_clean.iterrows():
                                    record = {}
                                    for col in df_clean.columns:
                                        value = row[col]
                                        if pd.isna(value) or np.isinf(value):
                                            record[col] = 0
                                        else:
                                            record[col] = float(value)
                                    records.append(record)
                                
                                mc_dict[method] = {
                                    "data": records,
                                    "statistics": {
                                        "count": len(df),
                                        "EV": {
                                            "mean": float(df["EV"].mean()) if "EV" in df.columns and len(df) > 0 else 0,
                                            "std": float(df["EV"].std()) if "EV" in df.columns and len(df) > 0 else 0,
                                            "min": float(df["EV"].min()) if "EV" in df.columns and len(df) > 0 else 0,
                                            "max": float(df["EV"].max()) if "EV" in df.columns and len(df) > 0 else 0,
                                            "5%": float(df["EV"].quantile(0.05)) if "EV" in df.columns and len(df) > 0 else 0,
                                            "25%": float(df["EV"].quantile(0.25)) if "EV" in df.columns and len(df) > 0 else 0,
                                            "50%": float(df["EV"].quantile(0.50)) if "EV" in df.columns and len(df) > 0 else 0,
                                            "75%": float(df["EV"].quantile(0.75)) if "EV" in df.columns and len(df) > 0 else 0,
                                            "95%": float(df["EV"].quantile(0.95)) if "EV" in df.columns and len(df) > 0 else 0
                                        }
                                    }
                                }
                            except Exception as e:
                                self.logger.error(f"Error processing Monte Carlo DataFrame for {method}: {str(e)}")
                                mc_dict[method] = {
                                    "data": [],
                                    "statistics": {},
                                    "error": f"Data processing error: {str(e)}"
                                }
                    results["monte_carlo"] = mc_dict
                    self.logger.info("Monte Carlo simulation completed")
                    
                    # Check if any methods had successful runs
                    successful_methods = [method for method, data in mc_dict.items() if data.get("statistics", {}).get("count", 0) > 0]
                    if not successful_methods:
                        results["monte_carlo"] = {"error": "No successful Monte Carlo runs. This may be due to terminal growth >= WACC in some iterations. Try adjusting the variable specifications."}
                except Exception as e:
                    self.logger.error(f"Monte Carlo simulation failed: {str(e)}")
                    results["monte_carlo"] = {"error": str(e)}
            
            # Multiples Analysis
            if "Multiples" in analyses and (comps_file or comps_data):
                try:
                    if comps_data:
                        self.logger.info(f"Processing multiples analysis with {len(comps_data)} comparable companies")
                        comps_df = pd.DataFrame(comps_data)
                        self.logger.debug(f"Comps DataFrame columns: {list(comps_df.columns)}")
                        self.logger.debug(f"Comps DataFrame shape: {comps_df.shape}")
                        self.logger.debug(f"Sample of comps data: {comps_df.head().to_dict()}")
                    elif comps_file:
                        self.logger.info(f"Processing multiples analysis with file: {comps_file}")
                        comps_df = pd.read_csv(comps_file)
                    else:
                        raise ValueError("No comparable companies data provided")
                    
                    if comps_df.empty:
                        raise ValueError("Comparable companies DataFrame is empty")
                    
                    mult_results = run_multiples_analysis(params, comps_df)
                    results["multiples"] = mult_results.to_dict('records')
                    self.logger.info(f"Multiples analysis completed with {len(mult_results)} valid multiples")
                except Exception as e:
                    self.logger.error(f"Multiples analysis failed: {str(e)}")
                    results["multiples"] = {"error": str(e)}
            elif "Multiples" in analyses:
                self.logger.warning("Multiples analysis selected but no comparable companies data provided")
                results["multiples"] = {"error": "No comparable companies data provided. Please upload a CSV file in the Advanced Analysis section."}
            
            # Scenarios
            if "Scenarios" in analyses:
                try:
                    scen_results = run_scenarios(params)
                    results["scenarios"] = scen_results.to_dict('records')
                    self.logger.info("Scenario analysis completed")
                except Exception as e:
                    self.logger.error(f"Scenario analysis failed: {str(e)}")
                    results["scenarios"] = {"error": str(e)}
            
            # Sensitivity
            if "Sensitivity" in analyses:
                try:
                    if not params.sensitivity_ranges:
                        raise ValueError("No sensitivity ranges configured. Please configure sensitivity parameters in the Advanced Analysis section.")
                    
                    sens_df = run_sensitivity_analysis(params)
                    # Convert DataFrame to frontend-friendly format
                    sens_records = []
                    for param_name in sens_df.columns:
                        param_series = sens_df[param_name].dropna()
                        for i, ev_value in enumerate(param_series):
                            if not pd.isna(ev_value) and not np.isinf(ev_value):
                                # Get the original parameter value that was tested
                                param_value = params.sensitivity_ranges[param_name][i] if i < len(params.sensitivity_ranges[param_name]) else 0
                                sens_records.append({
                                    "parameter": param_name,
                                    "value": param_value,
                                    "EV": float(ev_value)
                                })
                    
                    if not sens_records:
                        results["sensitivity"] = {"error": "No valid sensitivity results generated. Check parameter ranges."}
                    else:
                        results["sensitivity"] = sens_records
                        self.logger.info(f"Sensitivity analysis completed with {len(sens_records)} valid results")
                except Exception as e:
                    self.logger.error(f"Sensitivity analysis failed: {str(e)}")
                    results["sensitivity"] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            self.logger.error(f"Valuation analyses failed: {str(e)}")
            raise CalculationError(f"Valuation analyses failed: {str(e)}")
    
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
                "service_status": "healthy",
                "timestamp": pd.Timestamp.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {str(e)}")
            return {
                "error": str(e),
                "service_status": "error",
                "timestamp": pd.Timestamp.now().isoformat()
            }

# Global service instance
valuation_service = ValuationService() 