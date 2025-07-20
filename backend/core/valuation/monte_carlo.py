"""
Monte Carlo Simulation Module

This module provides Monte Carlo simulation capabilities for valuation uncertainty analysis.
It supports multiple valuation methods and various probability distributions for input variables.

Key Features:
- WACC DCF and APV valuation methods
- Normal and uniform distributions for input variables
- Configurable number of simulation runs
- Comprehensive error handling and validation
"""

import copy
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from ...core.models.params import ValuationParams
from .dcf import calc_dcf_series, calc_apv
from ...utils.exceptions import MonteCarloError, InvalidInputError
from ...utils.validation import validate_monte_carlo_specs
from ...config.logging import get_logger
from ...utils.cache import cached_with_params

logger = get_logger(__name__)

@cached_with_params(max_size=32, ttl_seconds=1800)
def run_monte_carlo(
    params: ValuationParams,
    runs: int = 2000,
    random_seed: Optional[int] = None
) -> Dict[str, pd.DataFrame]:
    """
    Run Monte Carlo simulation for valuation uncertainty analysis.
    
    For each method in ["WACC", "APV"]:
    1. Draw 'runs' samples of user-specified variables
    2. Override params for each sample
    3. Compute EV, Equity value, and Price/Share
    4. Return distribution statistics
    
    Args:
        params: ValuationParams object with base inputs and variable_specs
        runs: Number of Monte Carlo iterations (default: 2000)
        random_seed: Random seed for reproducibility
        
    Returns:
        Dictionary with DataFrames keyed by method:
        {
            "WACC": DataFrame(columns=["EV", "Equity", "PS"]),
            "APV": DataFrame(columns=["EV", "Equity", "PS"])
        }
        
    Raises:
        MonteCarloError: If runs is less than 1
        InvalidInputError: If variable_specs contains unsupported distribution types
        InvalidInputError: If required distribution parameters are missing
    """
    logger.debug(f"Starting Monte Carlo simulation with {runs} runs")
    
    # Validate inputs
    if runs < 1:
        raise MonteCarloError(f"Number of runs ({runs}) must be at least 1")
    
    if not params.variable_specs:
        raise InvalidInputError("No variable specifications provided for Monte Carlo simulation")
    
    # Validate variable specifications
    try:
        validate_monte_carlo_specs(params.variable_specs)
    except InvalidInputError as e:
        logger.error(f"Invalid Monte Carlo specifications: {str(e)}")
        raise
    
    # Set random seed for reproducibility
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Initialize storage
    results: Dict[str, List[Dict[str, Optional[float]]]] = {"WACC": [], "APV": []}
    
    # Set random seed for reproducibility
    
    # Pre-generate all random samples for efficiency
    samples = {}
    for name, spec in params.variable_specs.items():
        dist = spec.get("dist")
        p = spec.get("params", {})
        
        if dist == "normal":
            samples[name] = np.random.normal(
                loc=p.get("loc"), 
                scale=p.get("scale"),
                size=runs
            )
        elif dist == "uniform":
            samples[name] = np.random.uniform(
                low=p.get("low"), 
                high=p.get("high"),
                size=runs
            )
    
    # Simulation loop
    successful_runs = {"WACC": 0, "APV": 0}
    
    for i in range(runs):
        try:
            # Create shallow copy and only override sampled variables
            sampled = copy.copy(params)
            # Deep copy only the lists that might be modified
            sampled.revenue = copy.deepcopy(params.revenue)
            sampled.capex = copy.deepcopy(params.capex)
            sampled.depreciation = copy.deepcopy(params.depreciation)
            sampled.nwc_changes = copy.deepcopy(params.nwc_changes)
            sampled.fcf_series = copy.deepcopy(params.fcf_series)
            sampled.debt_schedule = copy.deepcopy(params.debt_schedule)
            
            # Set sampled values from pre-generated arrays
            for name in params.variable_specs.keys():
                if hasattr(sampled, name):
                    setattr(sampled, name, samples[name][i])
                else:
                    raise MonteCarloError(
                        f"Variable '{name}' not found in ValuationParams",
                        iteration=i,
                        variable=name
                    )
            
            # Run WACC-based DCF
            try:
                ev_w, eq_w, ps_w = calc_dcf_series(sampled)
                # Validate results to prevent infinite values
                if not (np.isfinite(ev_w) and np.isfinite(eq_w)):
                    raise MonteCarloError(
                        "Invalid valuation results (infinite or NaN values)",
                        iteration=i
                    )
                
                results["WACC"].append({
                    "EV": float(ev_w), 
                    "Equity": float(eq_w), 
                    "PS": float(ps_w) if ps_w is not None and np.isfinite(ps_w) else None
                })
                successful_runs["WACC"] += 1
            except Exception as e:
                # Log failed WACC calculation but continue
                logger.warning(f"WACC DCF failed in iteration {i}: {str(e)}")
                results["WACC"].append({"EV": None, "Equity": None, "PS": None})
            
            # Run APV valuation
            try:
                ev_a, eq_a, ps_a = calc_apv(sampled)
                # Validate results to prevent infinite values
                if not (np.isfinite(ev_a) and np.isfinite(eq_a)):
                    raise MonteCarloError(
                        "Invalid valuation results (infinite or NaN values)",
                        iteration=i
                    )
                
                results["APV"].append({
                    "EV": float(ev_a), 
                    "Equity": float(eq_a), 
                    "PS": float(ps_a) if ps_a is not None and np.isfinite(ps_a) else None
                })
                successful_runs["APV"] += 1
            except Exception as e:
                # Log failed APV calculation but continue
                logger.warning(f"APV failed in iteration {i}: {str(e)}")
                results["APV"].append({"EV": None, "Equity": None, "PS": None})
                
        except Exception as e:
            logger.error(f"Monte Carlo iteration {i} failed: {str(e)}")
            # Add None results for failed iterations
            results["WACC"].append({"EV": None, "Equity": None, "PS": None})
            results["APV"].append({"EV": None, "Equity": None, "PS": None})
    
    # Log simulation results
    logger.info(f"Monte Carlo simulation completed. Successful runs - WACC: {successful_runs['WACC']}/{runs}, APV: {successful_runs['APV']}/{runs}")
    
    # Convert lists of dicts to DataFrames, handling None values
    result_dfs = {}
    for method, records in results.items():
        if records:
            # Filter out None values and create DataFrame
            valid_records = [r for r in records if r["EV"] is not None and r["Equity"] is not None]
            if valid_records:
                result_dfs[method] = pd.DataFrame(valid_records)
            else:
                # If no valid records, create empty DataFrame with proper structure
                result_dfs[method] = pd.DataFrame(columns=pd.Index(["EV", "Equity", "PS"]))
        else:
            result_dfs[method] = pd.DataFrame(columns=pd.Index(["EV", "Equity", "PS"]))
    
    return result_dfs

def get_monte_carlo_statistics(results: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for Monte Carlo results.
    
    Args:
        results: Dictionary of DataFrames from run_monte_carlo
        
    Returns:
        Dictionary with statistics for each method and metric
    """
    stats = {}
    
    for method, df in results.items():
        if df.empty:
            stats[method] = {}
            continue
            
        method_stats = {}
        for column in ["EV", "Equity", "PS"]:
            if column in df.columns:
                values = df[column].dropna()
                if len(values) > 0:
                    method_stats[column] = {
                        "mean": float(values.mean()),
                        "std": float(values.std()),
                        "min": float(values.min()),
                        "max": float(values.max()),
                        "median": float(values.median()),
                        "count": int(len(values))
                    }
                else:
                    method_stats[column] = {
                        "mean": None, "std": None, "min": None, 
                        "max": None, "median": None, "count": 0
                    }
        
        stats[method] = method_stats
    
    return stats 