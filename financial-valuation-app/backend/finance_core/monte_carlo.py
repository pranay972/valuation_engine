"""
Monte Carlo Simulation Module for Financial Valuation

This module provides Monte Carlo simulation capabilities for financial valuation,
including proper error handling and validation of simulation parameters.
"""

import numpy as np
import pandas as pd
import copy
from typing import Dict, List, Any, Tuple, Optional
from params import ValuationParameters
from dcf import calculate_dcf_valuation_wacc
from error_messages import create_error

def validate_monte_carlo_parameters(params: ValuationParameters, 
                                  monte_carlo_specs: Dict[str, Any]) -> None:
    """
    Validate Monte Carlo simulation parameters and raise clear errors for invalid inputs.
    
    Args:
        params: ValuationParameters object
        monte_carlo_specs: Dictionary containing Monte Carlo specifications
        
    Raises:
        ValueError: If parameters are invalid or would cause simulation failures
    """
    # Check for required fields
    required_fields = ['ebit_margin', 'terminal_growth_rate', 'weighted_average_cost_of_capital']
    for field in required_fields:
        if field not in monte_carlo_specs:
            raise ValueError(f"Missing required Monte Carlo field: {field}")
    
    # Validate distribution parameters
    for field, spec in monte_carlo_specs.items():
        if 'distribution' not in spec:
            raise ValueError(f"Missing distribution type for {field}")
        
        if spec['distribution'] == 'normal':
            if 'params' not in spec or 'mean' not in spec['params'] or 'std' not in spec['params']:
                raise ValueError(f"Invalid normal distribution parameters for {field}")
            
            mean = spec['params']['mean']
            std = spec['params']['std']
            
            # Check for reasonable bounds
            if field == 'ebit_margin' and (mean <= 0 or mean > 1):
                raise ValueError(f"EBIT margin must be between 0 and 1, got {mean}")
            if field == 'terminal_growth_rate' and (mean < -0.1 or mean > 0.2):
                raise ValueError(f"Terminal growth rate should be between -10% and 20%, got {mean}")
            if field == 'weighted_average_cost_of_capital' and (mean <= 0 or mean > 0.5):
                raise ValueError(f"WACC must be positive and reasonable, got {mean}")
            
            if std <= 0:
                raise ValueError(f"Standard deviation must be positive for {field}")
            if std > abs(mean) * 2:
                raise ValueError(f"Standard deviation too large for {field} (would cause negative values)")
                
        else:
            raise ValueError(f"Unsupported distribution type: {spec['distribution']}")

def run_monte_carlo_simulation(params: ValuationParameters, 
                              monte_carlo_specs: Dict[str, Any], 
                              num_simulations: int = 1000,
                              seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for financial valuation with proper error handling.
    
    Args:
        params: Base ValuationParameters object
        monte_carlo_specs: Dictionary containing Monte Carlo specifications
        num_simulations: Number of simulation runs
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary containing simulation results and statistics
        
    Raises:
        ValueError: If simulation parameters are invalid
        RuntimeError: If simulation fails to produce valid results
    """
    try:
        # Validate parameters first
        validate_monte_carlo_parameters(params, monte_carlo_specs)
        
        # Set random seed for reproducibility
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize results storage
        enterprise_values = []
        equity_values = []
        price_per_shares = []
        failed_simulations = 0
        max_failures = num_simulations // 10  # Allow max 10% failure rate
        
        for i in range(num_simulations):
            try:
                # Create copy of parameters for this simulation
                sim_params = copy.deepcopy(params)
                
                # Generate random values for each parameter
                for field, spec in monte_carlo_specs.items():
                    if spec['distribution'] == 'normal':
                        mean = spec['params']['mean']
                        std = spec['params']['std']
                        
                        # Generate value with bounds checking
                        if field == 'ebit_margin':
                            # EBIT margin must be positive and reasonable
                            value = np.random.normal(mean, std)
                            value = max(0.01, min(0.8, value))  # Bound between 1% and 80%
                        elif field == 'terminal_growth_rate':
                            # Growth rate must be reasonable
                            value = np.random.normal(mean, std)
                            value = max(-0.05, min(0.15, value))  # Bound between -5% and 15%
                        elif field == 'weighted_average_cost_of_capital':
                            # WACC must be positive and reasonable
                            value = np.random.normal(mean, std)
                            value = max(0.02, min(0.25, value))  # Bound between 2% and 25%
                        else:
                            value = np.random.normal(mean, std)
                        
                        # Set the parameter
                        setattr(sim_params, field, value)
                
                # Validate that WACC > terminal growth rate (critical for terminal value)
                if sim_params.weighted_average_cost_of_capital <= sim_params.terminal_growth_rate:
                    # Resample WACC to ensure it's greater than growth rate
                    min_wacc = sim_params.terminal_growth_rate + 0.01
                    sim_params.weighted_average_cost_of_capital = max(
                        min_wacc, 
                        sim_params.weighted_average_cost_of_capital
                    )
                
                # Run DCF valuation
                result = calculate_dcf_valuation_wacc(sim_params)
                
                # Extract values from tuple: (enterprise_value, equity_value, price_per_share, fcf_series, terminal_value, pv_terminal)
                ev = result[0] if len(result) > 0 else 0
                equity = result[1] if len(result) > 1 else 0
                pps = result[2] if len(result) > 2 else 0
                
                # Only accept reasonable results
                if (ev > 0 and ev < 1e12 and  # Reasonable EV bounds
                    equity > -1e10 and equity < 1e12 and  # Allow some negative equity
                    pps > -1000 and pps < 10000):  # Reasonable price bounds
                    
                    enterprise_values.append(ev)
                    equity_values.append(equity)
                    price_per_shares.append(pps)
                else:
                    failed_simulations += 1
                    
            except Exception as e:
                failed_simulations += 1
                if failed_simulations > max_failures:
                    raise RuntimeError(
                        f"Too many simulation failures ({failed_simulations}/{num_simulations}). "
                        f"Check your parameters. Last error: {str(e)}"
                    )
                continue
        
        # Check if we have enough successful simulations
        if len(enterprise_values) < num_simulations // 2:
            raise RuntimeError(
                f"Simulation failed: only {len(enterprise_values)} successful runs out of {num_simulations}. "
                f"Check your parameter distributions."
            )
        
        # Calculate statistics
        results = {
            'enterprise_value': {
                'mean': float(np.mean(enterprise_values)),
                'median': float(np.median(enterprise_values)),
                'std_dev': float(np.std(enterprise_values)),
                'min': float(np.min(enterprise_values)),
                'max': float(np.max(enterprise_values)),
                'percentiles': {
                    '10th': float(np.percentile(enterprise_values, 10)),
                    '25th': float(np.percentile(enterprise_values, 25)),
                    '75th': float(np.percentile(enterprise_values, 75)),
                    '90th': float(np.percentile(enterprise_values, 90))
                }
            },
            'equity_value': {
                'mean': float(np.mean(equity_values)),
                'median': float(np.median(equity_values)),
                'std_dev': float(np.std(equity_values)),
                'min': float(np.min(equity_values)),
                'max': float(np.max(equity_values)),
                'percentiles': {
                    '10th': float(np.percentile(equity_values, 10)),
                    '25th': float(np.percentile(equity_values, 25)),
                    '75th': float(np.percentile(equity_values, 75)),
                    '90th': float(np.percentile(equity_values, 90))
                }
            },
            'price_per_share': {
                'mean': float(np.mean(price_per_shares)),
                'median': float(np.median(price_per_shares)),
                'std_dev': float(np.std(price_per_shares)),
                'min': float(np.min(price_per_shares)),
                'max': float(np.max(price_per_shares)),
                'percentiles': {
                    '10th': float(np.percentile(price_per_shares, 10)),
                    '25th': float(np.percentile(price_per_shares, 25)),
                    '75th': float(np.percentile(price_per_shares, 75)),
                    '90th': float(np.percentile(price_per_shares, 90))
                }
            },
            'simulation_metadata': {
                'total_simulations': num_simulations,
                'successful_simulations': len(enterprise_values),
                'failed_simulations': failed_simulations,
                'success_rate': len(enterprise_values) / num_simulations,
                'random_seed': seed
            }
        }
        
        return results
        
    except Exception as e:
        # Provide clear error message
        error_msg = f"Monte Carlo simulation failed: {str(e)}"
        if "WACC" in str(e) and "growth rate" in str(e):
            error_msg += "\n\nSOLUTION: Ensure WACC is greater than terminal growth rate."
        elif "EBIT margin" in str(e):
            error_msg += "\n\nSOLUTION: Check that EBIT margin parameters are reasonable (0-100%)."
        elif "standard deviation" in str(e):
            error_msg += "\n\nSOLUTION: Reduce standard deviation values to prevent extreme outliers."
        
        raise RuntimeError(error_msg) 