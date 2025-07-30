"""
Clean Monte Carlo Simulation Module

Barebones Monte Carlo simulation without extra dependencies.
"""

import warnings
import copy
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

# Suppress pandas FutureWarning about DataFrame concatenation
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')

from params import ValuationParameters
from dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value

def create_parameter_copy(params: ValuationParameters) -> ValuationParameters:
    """Create a copy of parameters for Monte Carlo."""
    return copy.deepcopy(params)

def generate_random_samples(params: ValuationParameters, runs: int) -> Dict[str, np.ndarray]:
    """Pre-generate all random samples for efficiency."""
    samples = {}
    for name, spec in params.monte_carlo_variable_specs.items():
        dist = spec.get("distribution")
        p = spec.get("params", {})
        
        if dist == "normal":
            samples[name] = np.random.normal(
                loc=p.get("mean"), 
                scale=p.get("std"),
                size=runs
            )
        elif dist == "uniform":
            samples[name] = np.random.uniform(
                low=p.get("min"), 
                high=p.get("max"),
                size=runs
            )
        elif dist == "lognormal":
            samples[name] = np.random.lognormal(
                mean=p.get("mean", 0),
                sigma=p.get("std", 1),
                size=runs
            )
        elif dist == "triangular":
            samples[name] = np.random.triangular(
                left=p.get("min"),
                mode=p.get("mode", (p.get("min") + p.get("max")) / 2),
                right=p.get("max"),
                size=runs
            )
        else:
            raise ValueError(f"Unsupported distribution type: {dist}")
    
    return samples

def run_single_iteration(params: ValuationParameters, sample_values: Dict[str, float], 
                        method: str) -> Optional[Dict[str, float]]:
    """Run a single Monte Carlo iteration."""
    try:
        # Create parameter copy
        p = create_parameter_copy(params)
        
        # Apply random values
        for name, value in sample_values.items():
            if hasattr(p, name):
                setattr(p, name, value)
        
        # Run valuation
        if method == "WACC":
            ev, equity, ps, _, _, _ = calculate_dcf_valuation_wacc(p)
        elif method == "APV":
            ev, equity, ps, _ = calculate_adjusted_present_value(p)
        else:
            return None
        
        return {
            "EV": ev,
            "Equity": equity,
            "PS": ps if ps is not None else float('nan')
        }
        
    except Exception as e:
        return None

def run_monte_carlo(params: ValuationParameters, runs: int = 1000, 
                   random_seed: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """
    Run Monte Carlo simulation for valuation uncertainty analysis.
    
    Returns:
        Dictionary with results for each valuation method
    """
    if not params.monte_carlo_variable_specs:
        raise ValueError("No variable specifications provided for Monte Carlo simulation")
    
    # Validate variable specifications
    for name in params.monte_carlo_variable_specs.keys():
        if not hasattr(params, name):
            raise ValueError(f"Variable '{name}' in monte_carlo_variable_specs does not exist in ValuationParameters.")
    
    # Set random seed for reproducibility
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Determine which valuation methods to use
    methods = []
    if params.weighted_average_cost_of_capital > 0:
        methods.append("WACC")
    if params.unlevered_cost_of_equity > 0:
        methods.append("APV")
    
    if not methods:
        raise ValueError("No valid valuation methods available (need weighted_average_cost_of_capital for WACC or unlevered_cost_of_equity for APV)")
    
    # Generate random samples
    samples = generate_random_samples(params, runs)
    
    # Initialize results storage
    result_dfs = {}
    for method in methods:
        result_dfs[method] = pd.DataFrame(columns=["EV", "Equity", "PS"])
    
    # Run simulations
    valid_records = 0
    for i in range(runs):
        # Extract sample values for this iteration
        sample_values = {name: samples[name][i] for name in samples.keys()}
        
        # Run each method
        for method in methods:
            result = run_single_iteration(params, sample_values, method)
            if result is not None:
                result_dfs[method] = pd.concat([
                    result_dfs[method], 
                    pd.DataFrame([result])
                ], ignore_index=True)
                valid_records += 1
    
    return result_dfs 