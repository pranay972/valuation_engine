"""Professional-grade financial valuation calculator with industry-standard methodologies."""

import warnings
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

# Suppress all warnings for silent operation
warnings.filterwarnings('ignore')

from .params import ValuationParameters
from .drivers import project_ebit_series, project_free_cash_flow
from .wacc import calculate_weighted_average_cost_of_capital, calculate_unlevered_cost_of_equity
from .dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from .multiples import analyze_comparable_multiples
from .scenario import perform_scenario_analysis
from .monte_carlo import simulate_monte_carlo
from .sensitivity import perform_sensitivity_analysis
from .error_messages import create_error, validate_required_field, validate_non_negative, validate_list_consistency, FinanceCoreError

@dataclass
class FinancialInputs:
    """Comprehensive input data structure for financial valuation calculations."""
    # Basic financial data (required)
    revenue: List[float]
    ebit_margin: float
    capex: List[float]
    depreciation: List[float]
    nwc_changes: List[float]
    tax_rate: float
    terminal_growth: float
    wacc: float
    share_count: float
    cost_of_debt: float
    
    # Capital structure (optional with sensible defaults)
    cash_balance: float = 0.0
    unlevered_cost_of_equity: float = 0.0
    cost_of_equity: float = 0.0
    risk_free_rate: float = 0.03
    market_risk_premium: float = 0.06
    levered_beta: float = 1.0
    unlevered_beta: float = 1.0
    target_debt_ratio: float = 0.3
    
    # Optional fields with defaults
    debt_schedule: Dict[int, float] = field(default_factory=dict)
    
    # Additional inputs for APV (optional)
    equity_value: Optional[float] = None
    
    # Comparable multiples data (optional)
    comparable_multiples: Optional[Dict[str, List[float]]] = None
    
    # Scenario analysis (optional)
    scenarios: Optional[Dict[str, Dict[str, Any]]] = None
    
    # Sensitivity analysis (optional)
    sensitivity_analysis: Optional[Dict[str, List[float]]] = None
    
    # Monte Carlo specifications (optional)
    monte_carlo_specs: Optional[Dict[str, Dict[str, Any]]] = None
    
    # Configuration toggles (optional)
    use_input_wacc: bool = True
    use_debt_schedule: bool = False

class FinancialValuationEngine:
    """
    Professional-grade financial valuation engine with comprehensive analysis capabilities.
    
    This engine implements industry-standard financial valuation methodologies
    including DCF (WACC), APV, comparable multiples, scenario analysis, sensitivity
    analysis, and Monte Carlo simulation. It provides a professional interface
    for performing comprehensive financial analysis with robust error handling and
    validation.
    
    Key Features:
        - DCF Valuation: Standard discounted cash flow using WACC methodology
        - APV Valuation: Adjusted Present Value method with tax shield analysis
        - Comparable Multiples: Relative valuation using peer company ratios
        - Scenario Analysis: Multiple scenarios with different parameter combinations
        - Sensitivity Analysis: Parameter impact analysis on key valuation drivers
        - Monte Carlo Simulation: Risk analysis with probability distributions
        - Comprehensive Validation: Multi-layer input validation and error handling
        - Professional Standards: Industry-standard methodologies and best practices
    
    Usage:
        engine = FinancialValuationEngine()
        results = engine.run_comprehensive_valuation(inputs, "Company Name")
    """
    
    def __init__(self):
        """
        Initialize the finance calculator with default settings.
        
        The calculator is ready to use immediately after initialization.
        No additional configuration is required for basic functionality.
        """
        pass
    
    def _convert_to_valuation_params(self, inputs: FinancialInputs) -> ValuationParameters:
        """
        Convert FinancialInputs to ValuationParameters for the modular system.
        
        This method performs the conversion between the user-friendly FinancialInputs
        dataclass and the internal ValuationParameters structure used by the core
        calculation modules. It handles data type conversions and ensures all
        required fields are properly mapped.
        
        Args:
            inputs: FinancialInputs object containing all valuation inputs
            
        Returns:
            ValuationParameters: Internal parameter structure for calculations
            
        Raises:
            FinanceCoreError: If required fields are missing or invalid
        """
        try:
            # Handle legacy input structure
            if hasattr(inputs, 'financial_inputs'):
                financial_data = inputs.financial_inputs
            else:
                financial_data = inputs
            
            # Validate required fields
            self._validate_required_inputs(inputs)
            
            # Convert debt schedule keys to integers if needed
            debt_schedule = inputs.debt_schedule
            if debt_schedule and isinstance(next(iter(debt_schedule.keys())), str):
                debt_schedule = {int(k): v for k, v in debt_schedule.items()}
            
            # Create ValuationParameters object
            params = ValuationParameters(
                revenue_projections=inputs.revenue,
                ebit_margin=inputs.ebit_margin,
                capital_expenditure=inputs.capex,
                depreciation_expense=inputs.depreciation,
                net_working_capital_changes=inputs.nwc_changes,
                corporate_tax_rate=inputs.tax_rate,
                terminal_growth_rate=inputs.terminal_growth,
                weighted_average_cost_of_capital=inputs.wacc,
                shares_outstanding=inputs.share_count,
                cost_of_debt=inputs.cost_of_debt,
                debt_schedule=debt_schedule,
                cash_and_equivalents=inputs.cash_balance,
                unlevered_cost_of_equity=inputs.unlevered_cost_of_equity,
                levered_cost_of_equity=inputs.cost_of_equity,
                risk_free_rate=inputs.risk_free_rate,
                equity_risk_premium=inputs.market_risk_premium,
                levered_beta=inputs.levered_beta,
                unlevered_beta=inputs.unlevered_beta,
                target_debt_to_value_ratio=inputs.target_debt_ratio,
                current_equity_value=inputs.equity_value,
                use_input_wacc=inputs.use_input_wacc,
                use_debt_schedule=inputs.use_debt_schedule
            )
            
            # Add optional analysis data
            if inputs.comparable_multiples:
                params.comparable_multiples_data = inputs.comparable_multiples
            
            if inputs.scenarios:
                params.scenario_definitions = inputs.scenarios
            
            if inputs.sensitivity_analysis:
                params.sensitivity_parameter_ranges = inputs.sensitivity_analysis
            
            if inputs.monte_carlo_specs:
                params.monte_carlo_variable_specs = inputs.monte_carlo_specs
            
            return params
            
        except Exception as e:
            # Re-raise as standardized error
            raise create_error("DCF_CALCULATION_FAILED", reason=f"Parameter conversion failed: {str(e)}")
    
    def _validate_required_inputs(self, inputs: FinancialInputs) -> None:
        """
        Validate that all required input fields are present and valid.
        
        Args:
            inputs: FinancialInputs object to validate
            
        Raises:
            FinanceCoreError: If any required fields are missing or invalid
        """
        # Validate required fields exist and are not empty
        required_fields = {
            'revenue': inputs.revenue,
            'capex': inputs.capex,
            'depreciation': inputs.depreciation,
            'nwc_changes': inputs.nwc_changes
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                raise create_error("MISSING_REQUIRED_FIELD", field_name=field_name)
        
        # Validate numeric fields are non-negative
        numeric_fields = {
            'ebit_margin': inputs.ebit_margin,
            'tax_rate': inputs.tax_rate,
            'terminal_growth': inputs.terminal_growth,
            'wacc': inputs.wacc,
            'share_count': inputs.share_count,
            'cost_of_debt': inputs.cost_of_debt,
            'cash_balance': inputs.cash_balance,
            'unlevered_cost_of_equity': inputs.unlevered_cost_of_equity,
            'cost_of_equity': inputs.cost_of_equity,
            'risk_free_rate': inputs.risk_free_rate,
            'market_risk_premium': inputs.market_risk_premium,
            'levered_beta': inputs.levered_beta,
            'unlevered_beta': inputs.unlevered_beta,
            'target_debt_ratio': inputs.target_debt_ratio
        }
        
        for field_name, field_value in numeric_fields.items():
            validate_non_negative(field_value, field_name)
        
        # Validate list consistency
        list_fields = {
            'revenue': inputs.revenue,
            'capex': inputs.capex,
            'depreciation': inputs.depreciation,
            'nwc_changes': inputs.nwc_changes
        }
        
        validate_list_consistency(list_fields)
    
    def calculate_dcf_valuation(self, inputs: FinancialInputs) -> Dict[str, Any]:
        """
        Perform DCF (Discounted Cash Flow) valuation using WACC methodology.
        
        This method implements the standard DCF valuation approach used in professional
        financial analysis. It projects free cash flows, calculates the weighted average
        cost of capital (WACC), discounts the cash flows to present value, and determines
        the terminal value using the Gordon Growth Model.
        
        The calculation follows these steps:
        1. Project EBIT based on revenue and margin assumptions
        2. Calculate NOPAT (Net Operating Profit After Tax)
        3. Project free cash flows using comprehensive FCF formula
        4. Calculate terminal value using Gordon Growth Model
        5. Discount all cash flows using WACC
        6. Calculate enterprise value and equity value
        7. Determine price per share
        
        Args:
            inputs: FinancialInputs object containing all required valuation inputs
            
        Returns:
            Dict containing:
                - enterprise_value: Total enterprise value (USD millions)
                - equity_value: Equity value after subtracting net debt (USD millions)
                - price_per_share: Implied share price (USD)
                - free_cash_flows_after_tax_fcff: Projected FCF series
                - terminal_value: Terminal value at end of projection period
                - present_value_of_terminal: PV of terminal value
                - present_value_of_fcfs: PV of projected FCFs
                - net_debt: Net debt (debt minus cash)
                - wacc_components: Breakdown of WACC calculation
                
        Raises:
            FinanceCoreError: If calculation fails due to invalid inputs or parameters
        """
        try:
            # Convert inputs to internal parameter structure
            params = self._convert_to_valuation_params(inputs)
            
            # Perform DCF calculation using WACC method
            ev, equity, price_per_share, fcf_series, terminal_value, pv_terminal = calculate_dcf_valuation_wacc(params)
            
            # Calculate present value of projected FCFs (excluding terminal value)
            pv_fcfs = ev - pv_terminal
            
            # Calculate net debt for equity value determination
            net_debt = params.debt_schedule.get(0, 0.0) - params.cash_and_equivalents
            current_debt = params.debt_schedule.get(0, 0.0)
            
            # Get WACC details - use the same WACC that was used in the DCF calculation
            if params.use_input_wacc:
                wacc_used = params.weighted_average_cost_of_capital
            else:
                # If not using input WACC, calculate the iterative WACC that was actually used
                from wacc import calculate_iterative_wacc
                wacc_used = calculate_iterative_wacc(params)
            
            return {
                "wacc": wacc_used,
                "terminal_growth": inputs.terminal_growth,
                "enterprise_value": round(ev, 1),
                "equity_value": round(equity, 1),
                "price_per_share": round(price_per_share, 2) if price_per_share else 0.0,
                "free_cash_flows_after_tax_fcff": [round(fcf, 1) for fcf in fcf_series],
                "terminal_value": round(terminal_value, 1),
                "present_value_of_terminal": round(pv_terminal, 1),
                "present_value_of_fcfs": round(pv_fcfs, 1),
                "net_debt_breakdown": {
                    "current_debt": round(current_debt, 1),
                    "cash_balance": round(params.cash_and_equivalents, 1),
                    "net_debt": round(net_debt, 1)
                },
                "wacc_components": {
                    "target_debt_ratio": getattr(params, 'target_debt_to_value_ratio', 0.0),
                    "cost_of_equity": params.calculate_levered_cost_of_equity(),
                    "cost_of_debt": params.cost_of_debt,
                    "tax_rate": params.corporate_tax_rate
                }
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=str(e))
    
    def calculate_apv_valuation(self, inputs: FinancialInputs) -> Dict[str, Any]:
        """
        Perform APV (Adjusted Present Value) valuation analysis.
        
        This method implements the APV valuation approach, which separates the value
        of the unlevered business from the value of financing effects (tax shields).
        This approach is particularly useful when the capital structure is expected
        to change significantly over time or when analyzing leveraged buyouts.
        
        The calculation follows these steps:
        1. Project unlevered free cash flows (same as DCF but without financing effects)
        2. Calculate unlevered cost of equity using Hamada equation
        3. Discount unlevered FCFs to present value
        4. Calculate present value of interest tax shields
        5. Add unlevered value and tax shield value to get APV
        6. Subtract net debt to get equity value
        
        Args:
            inputs: FinancialInputs object containing all required valuation inputs
            
        Returns:
            Dict containing:
                - unlevered_cost_of_equity: Cost of equity for unlevered business
                - cost_of_debt: Pre-tax cost of debt
                - tax_rate: Corporate tax rate
                - enterprise_value: Total APV enterprise value
                - apv_components: Breakdown of APV calculation
                - unlevered_fcfs_used: Projected unlevered FCF series
                - equity_value: Equity value after subtracting net debt
                - price_per_share: Implied share price
                - net_debt_breakdown: Detailed net debt analysis
                
        Raises:
            FinanceCoreError: If calculation fails due to invalid inputs or parameters
        """
        try:
            params = self._convert_to_valuation_params(inputs)
            ev, equity, price_per_share, apv_components = calculate_adjusted_present_value(params)
            
            # Get net debt breakdown
            net_debt = params.debt_schedule.get(0, 0.0) - params.cash_and_equivalents
            current_debt = params.debt_schedule.get(0, 0.0)
            
            # Get unlevered cost of equity
            unlevered_cost_of_equity = apv_components.get("unlevered_cost_of_equity", inputs.unlevered_cost_of_equity)
            
            return {
                "unlevered_cost_of_equity": unlevered_cost_of_equity,
                "cost_of_debt": inputs.cost_of_debt,
                "tax_rate": inputs.tax_rate,
                "enterprise_value": round(ev, 1),
                "apv_components": {
                    "value_unlevered": round(apv_components.get("value_unlevered", 0), 1),
                    "pv_tax_shield": round(apv_components.get("pv_tax_shield", 0), 1)
                },
                "unlevered_fcfs_used": apv_components.get("unlevered_fcfs", []),
                "equity_value": round(equity, 1),
                "price_per_share": round(price_per_share, 2) if price_per_share else 0.0,
                "net_debt_breakdown": {
                    "current_debt": round(current_debt, 1),
                    "cash_balance": round(params.cash_and_equivalents, 1),
                    "net_debt": round(net_debt, 1)
                }
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=f"APV calculation failed: {str(e)}")
    
    def analyze_comparable_multiples(self, inputs: FinancialInputs) -> Dict[str, Any]:
        """
        Perform comparable multiples analysis for relative valuation.
        
        This method implements relative valuation using peer company multiples to
        estimate the value of the target company. It calculates implied enterprise
        values based on various multiples (EV/EBITDA, P/E, EV/FCF, EV/Revenue) and
        provides statistical summaries of the valuation range.
        
        The analysis follows these steps:
        1. Calculate the company's key financial metrics (EBITDA, FCF, Revenue, Net Income)
        2. Apply peer company multiples to these metrics
        3. Calculate implied enterprise values for each multiple
        4. Provide statistical summaries (mean, median, standard deviation, range)
        5. Break down results by multiple type
        
        Args:
            inputs: FinancialInputs object containing financial data and comparable multiples
            
        Returns:
            Dict containing:
                - summary: Statistical summary of all implied values
                - base_metrics: Company's financial metrics used in analysis
                - implied_evs_by_multiple: Detailed breakdown by multiple type
                - calculation_method: "Comparable Multiples"
                
        Raises:
            FinanceCoreError: If comparable multiples data is missing or calculation fails
        """
        try:
            # Validate that comparable multiples data is provided
            if not inputs.comparable_multiples:
                raise create_error("EMPTY_COMPARABLE_DATA")
            
            params = self._convert_to_valuation_params(inputs)
            
            # Convert comparable multiples to DataFrame format
            comps_data = []
            for multiple_type, values in inputs.comparable_multiples.items():
                for value in values:
                    comps_data.append({multiple_type: value})
            
            comps_df = pd.DataFrame(comps_data)
            
            # Run multiples analysis
            results_df = analyze_comparable_multiples(params, comps_df)
            
            # Calculate summary statistics
            ev_values = []
            for multiple_name, row in results_df.iterrows():
                if '_implied_evs' in row:
                    ev_values.extend(row['_implied_evs'])
            
            if ev_values:
                summary = {
                    "mean_ev": round(np.mean(ev_values), 1),
                    "median_ev": round(np.median(ev_values), 1),
                    "std_dev": round(np.std(ev_values), 1),
                    "range": [round(min(ev_values), 1), round(max(ev_values), 1)]
                }
            else:
                summary = {
                    "mean_ev": 0.0,
                    "median_ev": 0.0,
                    "std_dev": 0.0,
                    "range": [0.0, 0.0]
                }
            
            # Get base metrics used
            base_metrics = {
                "ebitda": round(params.revenue_projections[-1] * params.ebit_margin + params.depreciation_expense[-1], 1),
                "fcf": round(params.revenue_projections[-1] * params.ebit_margin * (1 - params.corporate_tax_rate) + 
                           params.depreciation_expense[-1] - params.capital_expenditure[-1] - params.net_working_capital_changes[-1], 1),
                "revenue": round(params.revenue_projections[-1], 1),
                "net_income": round(params.revenue_projections[-1] * params.ebit_margin * (1 - params.corporate_tax_rate), 1)
            }
            
            # Calculate implied EVs by multiple type
            implied_evs_by_multiple = {}
            for multiple_name, row in results_df.iterrows():
                implied_evs_by_multiple[multiple_name] = {
                    "mean_implied_ev": round(row['Mean Implied EV'], 1),
                    "median_implied_ev": round(row['Median Implied EV'], 1),
                    "our_metric": round(row['Our Metric'], 1),
                    "mean_multiple": round(row['Mean Multiple'], 2),
                    "peer_count": row['Peer Count']
                }
            
            return {
                "ev_multiples": summary,
                "base_metrics_used": base_metrics,
                "implied_evs_by_multiple": implied_evs_by_multiple,
                "calculation_method": "Comparable Multiples"
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=f"Comparable multiples analysis failed: {str(e)}")
    
    def perform_scenario_analysis(self, inputs: FinancialInputs) -> Dict[str, Any]:
        """
        Perform scenario analysis to evaluate valuation under different assumptions.
        
        This method runs multiple valuation scenarios with different parameter combinations
        to understand how changes in key assumptions affect the valuation outcome. It's
        particularly useful for sensitivity analysis and risk assessment.
        
        The analysis follows these steps:
        1. Start with base case scenario using provided inputs
        2. Apply scenario-specific parameter changes
        3. Run DCF valuation for each scenario
        4. Compare results across scenarios
        5. Provide detailed breakdown of changes and outcomes
        
        Args:
            inputs: FinancialInputs object containing base case data and scenario definitions
            
        Returns:
            Dict containing:
                - scenarios: Results for each scenario (EV, equity, price per share)
                - base_case: Base case scenario results
                - scenario_comparison: Summary comparison across scenarios
                - calculation_method: "Scenario Analysis"
                
        Raises:
            FinanceCoreError: If scenario definitions are missing or calculation fails
        """
        try:
            # Validate that scenario definitions are provided
            if not inputs.scenarios:
                raise create_error("INVALID_SCENARIO_DEFINITION", reason="No scenario definitions provided")
            
            params = self._convert_to_valuation_params(inputs)
            scenarios_df = perform_scenario_analysis(params)
            
            scenarios = {}
            for scenario_name, row in scenarios_df.iterrows():
                scenarios[scenario_name] = {
                    "ev": round(row["EV"], 1) if not pd.isna(row["EV"]) else 0.0,
                    "equity": round(row["Equity"], 1) if not pd.isna(row["Equity"]) else 0.0,
                    "price_per_share": round(row["PS"], 2) if not pd.isna(row["PS"]) else 0.0
                }
                
                # Add notes for negative equity values
                if scenarios[scenario_name]["equity"] <= 0:
                    scenarios[scenario_name]["note"] = "Equity value negative, capped at zero"
                
                # Add scenario input changes for traceability
                if scenario_name in inputs.scenarios:
                    scenario_inputs = inputs.scenarios[scenario_name]
                    if scenario_inputs:
                        scenarios[scenario_name]["input_changes"] = scenario_inputs
            
            return {
                "scenarios": scenarios,
                "calculation_method": "Scenario Analysis"
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=f"Scenario analysis failed: {str(e)}")
    
    def perform_sensitivity_analysis(self, inputs: FinancialInputs) -> Dict[str, Any]:
        """
        Perform sensitivity analysis to understand parameter impact on valuation.
        
        This method analyzes how changes in key valuation parameters affect the
        enterprise value and share price. It systematically varies one parameter
        at a time while holding others constant, providing insights into which
        assumptions have the greatest impact on valuation outcomes.
        
        The analysis follows these steps:
        1. Start with base case parameters
        2. Systematically vary each parameter across specified ranges
        3. Run DCF valuation for each parameter value
        4. Calculate enterprise value and share price for each combination
        5. Organize results by parameter and value
        
        Args:
            inputs: FinancialInputs object containing base case data and sensitivity ranges
            
        Returns:
            Dict containing:
                - sensitivity_results: Results organized by parameter and value
                - parameter_ranges: The ranges tested for each parameter
                - calculation_method: "Sensitivity Analysis"
                
        Raises:
            FinanceCoreError: If sensitivity ranges are missing or calculation fails
        """
        try:
            # Validate that sensitivity analysis ranges are provided
            if not inputs.sensitivity_analysis:
                raise create_error("INVALID_MONTE_CARLO_SPECS", reason="No sensitivity analysis ranges provided")
            
            params = self._convert_to_valuation_params(inputs)
            sensitivity_df = perform_sensitivity_analysis(params)
            
            sensitivity = {}
            for col in sensitivity_df.columns:
                if col.endswith("_ev"):
                    param_name = col.replace("_ev", "")
                    if param_name not in sensitivity:
                        sensitivity[param_name] = {"ev": {}, "price_per_share": {}}
                    
                    for i, value in enumerate(sensitivity_df[col]):
                        if not pd.isna(value):
                            # Get the corresponding range value
                            if param_name in inputs.sensitivity_analysis:
                                range_values = inputs.sensitivity_analysis[param_name]
                                if i < len(range_values):
                                    sensitivity[param_name]["ev"][str(range_values[i])] = round(value, 1)
                
                elif col.endswith("_price_per_share"):
                    param_name = col.replace("_price_per_share", "")
                    if param_name not in sensitivity:
                        sensitivity[param_name] = {"ev": {}, "price_per_share": {}}
                    
                    for i, value in enumerate(sensitivity_df[col]):
                        if not pd.isna(value):
                            # Get the corresponding range value
                            if param_name in inputs.sensitivity_analysis:
                                range_values = inputs.sensitivity_analysis[param_name]
                                if i < len(range_values):
                                    sensitivity[param_name]["price_per_share"][str(range_values[i])] = round(value, 2)
            
            return {
                "sensitivity_results": sensitivity,
                "parameter_ranges": inputs.sensitivity_analysis,
                "calculation_method": "Sensitivity Analysis"
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=f"Sensitivity analysis failed: {str(e)}")
    
    def simulate_monte_carlo(self, inputs: FinancialInputs, runs: int = 1000) -> Dict[str, Any]:
        """
        Perform Monte Carlo simulation for risk analysis and uncertainty quantification.
        
        This method uses Monte Carlo simulation to analyze the uncertainty in valuation
        outcomes by randomly sampling from probability distributions of key parameters.
        It provides statistical insights into the range of possible valuation outcomes
        and helps quantify the risk associated with different assumptions.
        
        The simulation follows these steps:
        1. Define probability distributions for key parameters
        2. Generate random samples from these distributions
        3. Run DCF valuation for each set of sampled parameters
        4. Collect and analyze the distribution of results
        5. Calculate statistical measures (mean, median, standard deviation, confidence intervals)
        
        Args:
            inputs: FinancialInputs object containing base case data and Monte Carlo specifications
            runs: Number of simulation runs (default: 1000)
            
        Returns:
            Dict containing:
                - runs: Number of simulation runs performed
                - wacc_method: Statistical summary of WACC method results
                - apv_method: Statistical summary of APV method results (if applicable)
                - parameter_distributions: Summary of parameter distributions used
                - calculation_method: "Monte Carlo Simulation"
                
        Raises:
            FinanceCoreError: If Monte Carlo specifications are missing or calculation fails
        """
        try:
            # Validate that Monte Carlo specifications are provided
            if not inputs.monte_carlo_specs:
                raise create_error("INVALID_MONTE_CARLO_SPECS", reason="No Monte Carlo specifications provided")
            
            params = self._convert_to_valuation_params(inputs)
            results = simulate_monte_carlo(params, runs=runs)
            
            # Process WACC method results
            wacc_stats = {}
            if "WACC" in results and not results["WACC"].empty:
                ev_values = results["WACC"]["EV"].dropna()
                if not ev_values.empty:
                    wacc_stats = {
                        "mean_ev": round(ev_values.mean(), 1),
                        "median_ev": round(ev_values.median(), 1),
                        "std_dev": round(ev_values.std(), 1),
                        "confidence_interval_95": [
                            round(ev_values.quantile(0.025), 1),
                            round(ev_values.quantile(0.975), 1)
                        ]
                    }
            
            return {
                "runs": runs,
                "wacc_method": wacc_stats,
                "parameter_distributions": inputs.monte_carlo_specs,
                "calculation_method": "Monte Carlo Simulation"
            }
        except Exception as e:
            # Convert any exception to standardized error format
            if isinstance(e, FinanceCoreError):
                raise e
            else:
                raise create_error("DCF_CALCULATION_FAILED", reason=f"Monte Carlo simulation failed: {str(e)}")
    
    def perform_comprehensive_valuation(self, inputs: FinancialInputs, 
                                      company_name: str = "Company",
                                      valuation_date: str = "2024-01-01") -> Dict[str, Any]:
        """
        Perform comprehensive financial valuation using all available methods.
        
        This method orchestrates a complete financial analysis by running all applicable
        valuation methods based on the provided inputs. It provides a comprehensive view
        of the company's value from multiple perspectives and methodologies.
        
        The comprehensive analysis includes:
        1. DCF Valuation (WACC): Standard discounted cash flow analysis
        2. APV Valuation: Adjusted Present Value method
        3. Comparable Multiples: Relative valuation using peer companies
        4. Scenario Analysis: Multiple scenarios with different assumptions
        5. Sensitivity Analysis: Parameter impact analysis
        6. Monte Carlo Simulation: Risk and uncertainty analysis
        
        Args:
            inputs: FinancialInputs object containing all valuation inputs
            company_name: Name of the company being valued (default: "Company")
            valuation_date: Date of the valuation (default: "2024-01-01")
            
        Returns:
            Dict containing comprehensive valuation results with the following structure:
                - valuation_summary: Basic information about the valuation
                - dcf_valuation: DCF (WACC) method results
                - apv_valuation: APV method results
                - comparable_valuation: Comparable multiples results (if applicable)
                - scenarios: Scenario analysis results (if applicable)
                - sensitivity_analysis: Sensitivity analysis results (if applicable)
                - monte_carlo_simulation: Monte Carlo simulation results (if applicable)
                
        Raises:
            FinanceCoreError: If any calculation fails due to invalid inputs or parameters
        """
        
        # Initialize results structure
        results = {
            "valuation_summary": {
                "valuation_date": valuation_date,
                "company": company_name,
                "share_count": inputs.share_count
            },
            "dcf_valuation": {},
            "apv_valuation": {},
            "comparable_valuation": {},
            "scenarios": {},
            "sensitivity_analysis": {},
            "monte_carlo_simulation": {}
        }
        
        # Run DCF
        dcf_result = self.calculate_dcf_valuation(inputs)
        if "error" not in dcf_result:
            results["dcf_valuation"] = dcf_result
        else:
            results["dcf_valuation"] = {"error": dcf_result.get("error", "Unknown error")}
        
        # Run APV
        apv_result = self.calculate_apv_valuation(inputs)
        if "error" not in apv_result:
            results["apv_valuation"] = apv_result
        else:
            results["apv_valuation"] = {"error": apv_result.get("error", "Unknown error")}
        
        # Run Comparable Multiples
        if inputs.comparable_multiples:
            multiples_result = self.analyze_comparable_multiples(inputs)
            if "error" not in multiples_result:
                results["comparable_valuation"] = multiples_result
            else:
                results["comparable_valuation"] = {"error": multiples_result.get("error", "Unknown error")}
        
        # Run Scenario Analysis
        if inputs.scenarios:
            scenario_result = self.perform_scenario_analysis(inputs)
            if not isinstance(scenario_result, dict) or "error" not in scenario_result:
                results["scenarios"] = scenario_result
            else:
                results["scenarios"] = {"error": scenario_result.get("error", "Unknown error")}
        
        # Run Sensitivity Analysis
        if inputs.sensitivity_analysis:
            sensitivity_result = self.perform_sensitivity_analysis(inputs)
            if not isinstance(sensitivity_result, dict) or "error" not in sensitivity_result:
                results["sensitivity_analysis"] = sensitivity_result
            else:
                results["sensitivity_analysis"] = {"error": sensitivity_result.get("error", "Unknown error")}
        
        # Run Monte Carlo
        if inputs.monte_carlo_specs:
            # Get runs from monte_carlo_specs or use default
            runs = inputs.monte_carlo_specs.get("runs", 1000)
            monte_carlo_result = self.simulate_monte_carlo(inputs, runs=runs)
            if "error" not in monte_carlo_result:
                results["monte_carlo_simulation"] = monte_carlo_result
            else:
                results["monte_carlo_simulation"] = {"error": monte_carlo_result.get("error", "Unknown error")}
        
        return results

def parse_financial_inputs(data: Dict[str, Any]) -> FinancialInputs:
    """
    Create FinancialInputs object from JSON data with comprehensive validation.
    
    This function converts JSON data into a FinancialInputs object, handling various
    input formats and providing robust error handling. It supports both flat and nested
    JSON structures and performs validation to ensure data integrity.
    
    The function handles:
    - Nested structures with financial inputs under "financial_inputs" key
    - Multiple field name variations (e.g., "wacc" vs "weighted_average_cost_of_capital")
    - Debt schedule conversion from string keys to integer keys
    - Cost of capital parameter extraction
    - Default value assignment for optional fields
    
    Args:
        data: Dictionary containing financial valuation inputs in JSON format
        
    Returns:
        FinancialInputs: Validated FinancialInputs object ready for valuation calculations
        
    Raises:
        FinanceCoreError: If required fields are missing or data is invalid
        
    Example:
        >>> json_data = {
        ...     "financial_inputs": {
        ...         "revenue": [1000, 1100, 1200],
        ...         "ebit_margin": 0.18,
        ...         "wacc": 0.095
        ...     }
        ... }
        >>> inputs = create_financial_inputs_from_json(json_data)
    """
    # Handle nested structure where financial inputs are under "financial_inputs" key
    if "financial_inputs" in data:
        financial_data = data["financial_inputs"]
    else:
        financial_data = data
    
    # Convert debt_schedule from string keys to integer keys if needed
    debt_schedule = financial_data.get("debt_schedule", {})
    if debt_schedule and isinstance(next(iter(debt_schedule.keys())), str):
        debt_schedule = {int(k): v for k, v in debt_schedule.items()}
    
    # Extract cost of capital parameters
    cost_of_capital = financial_data.get("cost_of_capital", {})
    
    return FinancialInputs(
        revenue=financial_data.get("revenue", financial_data.get("revenue_projections", [])),
        ebit_margin=financial_data["ebit_margin"],
        capex=financial_data.get("capex", financial_data.get("capital_expenditure", [])),
        depreciation=financial_data.get("depreciation", financial_data.get("depreciation_expense", [])),
        nwc_changes=financial_data.get("nwc_changes", financial_data.get("net_working_capital_changes", [])),
        tax_rate=financial_data.get("tax_rate", financial_data.get("corporate_tax_rate")),
        terminal_growth=financial_data.get("terminal_growth", financial_data.get("terminal_growth_rate")),
        wacc=financial_data.get("wacc", financial_data.get("weighted_average_cost_of_capital")),
        share_count=financial_data.get("share_count", financial_data.get("shares_outstanding")),
        cost_of_debt=financial_data["cost_of_debt"],

        debt_schedule=debt_schedule,
        cash_balance=financial_data.get("cash_balance"),
        
        # Cost of capital parameters
        unlevered_cost_of_equity=financial_data.get("unlevered_cost_of_equity", 
                                                   cost_of_capital.get("unlevered_cost_of_equity")),
        cost_of_equity=financial_data.get("cost_of_equity", cost_of_capital.get("cost_of_equity")),
        risk_free_rate=cost_of_capital.get("risk_free_rate"),
        market_risk_premium=cost_of_capital.get("market_risk_premium"),
        levered_beta=cost_of_capital.get("levered_beta"),
        unlevered_beta=cost_of_capital.get("unlevered_beta"),
        target_debt_ratio=cost_of_capital.get("target_debt_ratio", cost_of_capital.get("target_debt_to_value_ratio")),
        
        equity_value=financial_data.get("equity_value"),
        comparable_multiples=data.get("comparable_multiples"),
        scenarios=data.get("scenarios"),
        sensitivity_analysis=data.get("sensitivity_analysis"),
        monte_carlo_specs=data.get("monte_carlo_specs"),
        use_input_wacc=financial_data.get("use_input_wacc", True),
        use_debt_schedule=financial_data.get("use_debt_schedule", False)
    )

def main():
    """Command-line interface for the finance calculator."""
    import sys
    import os
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else None
    
    try:
        # Load input data
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        # Create engine and inputs
        engine = FinancialValuationEngine()
        inputs = parse_financial_inputs(input_data)
        
        # Run comprehensive valuation
        results = engine.perform_comprehensive_valuation(
            inputs=inputs,
            company_name=input_data.get("company_name", "Company"),
            valuation_date=input_data.get("valuation_date", "2024-01-01")
        )
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_valuation_results.json"
        
        # Save results to JSON file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Valuation completed silently
        
    except FileNotFoundError:
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.exit(1)
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main() 