# drivers.py

"""
Helper functions to project core financial series:
  – project_revenue: builds a revenue forecast from base values and growth rates
  – project_ebit: computes EBIT from revenues and margin
  – project_fcf: computes Free Cash Flow from projected inputs
"""

from typing import List

def project_revenue(base_revenue: List[float], growth_rates: List[float]) -> List[float]:
    """
    Apply year-over-year growth rates to base revenue.

    Two modes:
      1) If len(growth_rates) == len(base_revenue):
           revenue[i] = base_revenue[i] * (1 + growth_rates[i])
      2) If len(growth_rates) == len(base_revenue) - 1:
           revenue[0] = base_revenue[0]
           revenue[i] = revenue[i-1] * (1 + growth_rates[i-1])  for i = 1..n
    Raises:
      ValueError if growth_rates length is neither equal nor one less than base_revenue.
    """
    if len(growth_rates) == len(base_revenue):
        return [r * (1 + g) for r, g in zip(base_revenue, growth_rates)]
    elif len(growth_rates) == len(base_revenue) - 1:
        rev_forecast = [base_revenue[0]]
        for g in growth_rates:
            rev_forecast.append(rev_forecast[-1] * (1 + g))
        return rev_forecast
    else:
        raise ValueError(
            "growth_rates must be same length as base_revenue or one shorter."
        )

def project_ebit(revenue: List[float], margin: float) -> List[float]:
    """
    Compute EBIT = revenue × ebit_margin for each year.
    """
    return [r * margin for r in revenue]

def project_fcf(
    revenue: List[float],
    ebit: List[float],
    capex: List[float],
    depreciation: List[float],
    nwc_changes: List[float],
    tax_rate: float
) -> List[float]:
    """
    Compute Free Cash Flow per year:
      FCF = NOPAT + Depreciation – CapEx – ΔNWC
    where:
      NOPAT = EBIT × (1 – tax_rate)
    """
    fcf = []
    for r, e, c, d, delta_nwc in zip(revenue, ebit, capex, depreciation, nwc_changes):
        nopat = e * (1 - tax_rate)
        fcf.append(nopat + d - c - delta_nwc)
    return fcf
