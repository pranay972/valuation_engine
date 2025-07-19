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

from params import ValuationParams
from valuation import calc_dcf_series, calc_apv

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
        
    Returns:
        Dictionary with DataFrames keyed by method:
        {
            "WACC": DataFrame(columns=["EV", "Equity", "PS"]),
            "APV": DataFrame(columns=["EV", "Equity", "PS"])
        }
        
    Raises:
        ValueError: If runs is less than 1
        ValueError: If variable_specs contains unsupported distribution types
        ValueError: If required distribution parameters are missing
    """
    # Validate inputs
    if runs < 1:
        raise ValueError(f"Number of runs ({runs}) must be at least 1")
    
    if not params.variable_specs:
        raise ValueError("No variable specifications provided for Monte Carlo simulation")
    
    # Set random seed for reproducibility
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Initialize storage
    results: Dict[str, List[Dict[str, float]]] = {"WACC": [], "APV": []}
    
    # Validate variable specifications
    for var_name, spec in params.variable_specs.items():
        if not isinstance(spec, dict):
            raise ValueError(f"Variable specification for '{var_name}' must be a dictionary")
        
        dist_type = spec.get("dist")
        if dist_type not in ["normal", "uniform"]:
            raise ValueError(f"Unsupported distribution type '{dist_type}' for variable '{var_name}'")
        
        params_dict = spec.get("params", {})
        if dist_type == "normal":
            if "loc" not in params_dict or "scale" not in params_dict:
                raise ValueError(f"Normal distribution for '{var_name}' requires 'loc' and 'scale' parameters")
            if params_dict["scale"] <= 0:
                raise ValueError(f"Scale parameter for '{var_name}' must be positive")
        elif dist_type == "uniform":
            if "low" not in params_dict or "high" not in params_dict:
                raise ValueError(f"Uniform distribution for '{var_name}' requires 'low' and 'high' parameters")
            if params_dict["low"] >= params_dict["high"]:
                raise ValueError(f"Low parameter must be less than high parameter for '{var_name}'")
    
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
                    raise ValueError(f"Variable '{name}' not found in ValuationParams")
            
            # Run WACC-based DCF
            try:
                ev_w, eq_w, ps_w = calc_dcf_series(sampled)
                results["WACC"].append({
                    "EV": ev_w, 
                    "Equity": eq_w, 
                    "PS": ps_w if ps_w is not None else np.nan
                })
            except Exception as e:
                # Log failed WACC calculation but continue
                print(f"WACC DCF failed in iteration {i}: {str(e)}")
                results["WACC"].append({"EV": np.nan, "Equity": np.nan, "PS": np.nan})
            
            # Run APV valuation
            try:
                ev_a, eq_a, ps_a = calc_apv(sampled)
                results["APV"].append({
                    "EV": ev_a, 
                    "Equity": eq_a, 
                    "PS": ps_a if ps_a is not None else np.nan
                })
            except Exception as e:
                # Log failed APV calculation but continue
                print(f"APV failed in iteration {i}: {str(e)}")
                results["APV"].append({"EV": np.nan, "Equity": np.nan, "PS": np.nan})
                
        except Exception as e:
            print(f"Monte Carlo iteration {i} failed: {str(e)}")
            # Add NaN results for failed iterations
            results["WACC"].append({"EV": np.nan, "Equity": np.nan, "PS": np.nan})
            results["APV"].append({"EV": np.nan, "Equity": np.nan, "PS": np.nan})
    
    # Convert lists of dicts to DataFrames
    return {
        method: pd.DataFrame(records) if records else pd.DataFrame(columns=pd.Index(["EV", "Equity", "PS"]))
        for method, records in results.items()
    }

def get_monte_carlo_statistics(results: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for Monte Carlo results.
    
    Args:
        results: Monte Carlo results from run_monte_carlo()
        
    Returns:
        Dictionary of statistics for each method:
        {
            "WACC": {"mean_ev": ..., "std_ev": ..., "p5_ev": ..., ...},
            "APV": {"mean_ev": ..., "std_ev": ..., "p5_ev": ..., ...}
        }
    """
    stats = {}
    
    for method, df in results.items():
        if df.empty:
            stats[method] = {}
            continue
            
        method_stats = {}
        
        # Basic statistics for each metric
        for metric in ["EV", "Equity", "PS"]:
            if metric in df.columns:
                clean_data = df[metric].dropna()
                if len(clean_data) > 0:
                    method_stats[f"mean_{metric.lower()}"] = clean_data.mean()
                    method_stats[f"std_{metric.lower()}"] = clean_data.std()
                    method_stats[f"min_{metric.lower()}"] = clean_data.min()
                    method_stats[f"max_{metric.lower()}"] = clean_data.max()
                    
                    # Percentiles
                    for p in [5, 25, 50, 75, 95]:
                        method_stats[f"p{p}_{metric.lower()}"] = clean_data.quantile(p/100)
        
        stats[method] = method_stats
    
    return stats
