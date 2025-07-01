# scenario.py

"""
Scenario analysis:
  – run_scenarios: for each named scenario, override params fields,
    run DCF, and collect results.
"""

import pandas as pd
from copy import deepcopy
from typing import Dict, Any

from params import ValuationParams
from valuation import calc_dcf_series


def run_scenarios(params: ValuationParams) -> pd.DataFrame:
    """
    Iterate over each scenario defined in params.scenarios:
      1) Deep‐copy the base params
      2) Apply the overrides for this scenario
      3) Run calc_dcf_series on the adjusted params
      4) Record EV, Equity value, and Price/Share

    Returns:
      DataFrame indexed by scenario name, with columns:
        – EV
        – Equity
        – PS
    """
    rows: list[Dict[str, Any]] = []
    for scen_name, overrides in params.scenarios.items():
        # 1 & 2: copy and apply
        p = deepcopy(params)
        for field, val in overrides.items():
            setattr(p, field, val)

        # 3: run DCF
        ev, equity, ps = calc_dcf_series(p)

        # 4: record
        rows.append({
            "Scenario": scen_name,
            "EV": ev,
            "Equity": equity,
            "PS": ps
        })

    # Build DataFrame
    df = pd.DataFrame(rows).set_index("Scenario")
    return df
