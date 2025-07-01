# montecarlo.py

"""
Monte Carlo engine for valuation:

  – For each method in ["WACC", "APV"]:
      • Draw 'runs' samples of user-specified variables
      • Override params for each sample
      • Compute EV, Equity value, and Price/Share
  – Returns a dict of DataFrames keyed by method
"""

import copy
from typing import Dict
import numpy as np
import pandas as pd

from params import ValuationParams
from valuation import calc_dcf_series, calc_apv

def run_monte_carlo(
    params: ValuationParams,
    runs: int = 2000
) -> Dict[str, pd.DataFrame]:
    """
    Args:
      params: ValuationParams object with base inputs and variable_specs
      runs: Number of Monte Carlo iterations

    Returns:
      {
        "WACC": DataFrame(columns=["EV","Equity","PS"]),
        "APV" : DataFrame(columns=["EV","Equity","PS"])
      }
    """
    # Initialize storage
    results: Dict[str, list] = {"WACC": [], "APV": []}

    # Simulation loop
    for _ in range(runs):
        # Copy base params for sampling
        sampled = copy.deepcopy(params)

        # Sample each variable per spec
        for name, spec in params.variable_specs.items():
            dist = spec.get("dist")
            p = spec.get("params", {})
            if dist == "normal":
                sampled_val = np.random.normal(loc=p.get("loc"), scale=p.get("scale"))
            elif dist == "uniform":
                sampled_val = np.random.uniform(low=p.get("low"), high=p.get("high"))
            else:
                raise ValueError(f"Unsupported distribution type '{dist}' for variable '{name}'")
            setattr(sampled, name, sampled_val)

        # WACC-based DCF
        ev_w, eq_w, ps_w = calc_dcf_series(sampled)
        results["WACC"].append({"EV": ev_w, "Equity": eq_w, "PS": ps_w})

        # APV valuation
        ev_a, eq_a, ps_a = calc_apv(sampled)
        results["APV"].append({"EV": ev_a, "Equity": eq_a, "PS": ps_a})

    # Convert lists of dicts to DataFrames
    return {
        method: pd.DataFrame(records)
        for method, records in results.items()
    }
