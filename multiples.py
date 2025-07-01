# multiples.py

"""
Implied multiples analysis:
  – run_multiples_analysis: apply peer ratios to your forecast metrics
"""

import pandas as pd
from typing import Dict, Any
from drivers import project_ebit, project_fcf
from params import ValuationParams

def run_multiples_analysis(
    params: ValuationParams,
    comps: pd.DataFrame
) -> pd.DataFrame:
    """
    Given:
      – params: ValuationParams with your company projections
      – comps: DataFrame of peer multiples, columns named like "EV/EBITDA", "P/E", etc.
    Returns a DataFrame of implied enterprise values by multiple, plus summary stats:
      – Mean Implied EV
      – Median Implied EV
    """
    # 1) Compute our company’s last‐year metrics
    revenues = params.revenue
    ebits = project_ebit(revenues, params.ebit_margin)
    fcfs = project_fcf(
        revenues,
        ebits,
        params.capex,
        params.depreciation,
        params.nwc_changes,
        params.tax_rate
    )

    metric_map: Dict[str, float] = {
        # EBITDA = EBIT + Depreciation
        "EBITDA": ebits[-1] + params.depreciation[-1],
        # Earnings = NOPAT = EBIT × (1 – tax_rate)
        "Earnings": ebits[-1] * (1 - params.tax_rate),
        # FCF = last‐year free cash flow
        "FCF": fcfs[-1],
        # Revenue = last‐year revenue
        "Revenue": revenues[-1]
    }

    results = []
    # 2) Identify and apply each multiple in comps
    for col in comps.columns:
        if "/" not in col:
            continue
        num, den = [s.strip() for s in col.split("/", 1)]
        if den not in metric_map:
            # skip unknown denominators
            continue

        our_metric = metric_map[den]
        # drop NaNs before multiplication
        peer_vals = comps[col].dropna().astype(float)
        implied_evs = peer_vals * our_metric

        results.append({
            "Multiple": col,
            "Mean Implied EV": implied_evs.mean(),
            "Median Implied EV": implied_evs.median()
        })

    # 3) Return as DataFrame indexed by multiple name
    result_df = pd.DataFrame(results).set_index("Multiple")
    return result_df
