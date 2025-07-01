# sensitivity.py

"""
Sensitivity analysis:
  – run_sensitivity_analysis: vary one input at a time according to
    params.sensitivity_ranges and record the effect on EV.
"""

import pandas as pd
from copy import deepcopy
from params import ValuationParams
from valuation import calc_dcf_series


def run_sensitivity_analysis(params: ValuationParams) -> pd.DataFrame:
    """
    For each parameter in params.sensitivity_ranges:
      1) Loop its list of test values
      2) Deep‐copy params and override that parameter with the test value
      3) Run calc_dcf_series on the adjusted params to get EV
      4) Collect EVs in a column named after the parameter

    Returns:
      DataFrame where each column is a parameter name, and each row
      corresponds (by position) to the test value in that parameter’s list.
      Missing values (if lists differ in length) are filled with NaN.
    """
    data: dict[str, list[float]] = {}

    for param_name, test_values in params.sensitivity_ranges.items():
        ev_list: list[float] = []
        for v in test_values:
            # Copy and override
            p = deepcopy(params)
            setattr(p, param_name, v)
            # Run DCF
            ev, _, _ = calc_dcf_series(p)
            ev_list.append(ev)
        data[param_name] = ev_list

    # Convert to DataFrame; rows align by list index
    return pd.DataFrame(data)
