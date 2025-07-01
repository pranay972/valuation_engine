# valuation.py

from typing import Tuple, Optional
import numpy as np

from drivers import project_ebit, project_fcf
from params import ValuationParams

def calc_dcf_series(params: ValuationParams) -> Tuple[float, float, Optional[float]]:
    """
    DCF that supports either:
      • Direct FCF series (if params.fcf_series non-empty)
      • Driver-based projection otherwise
    Returns (EV, EquityValue, PricePerShare or None).
    """
    # 1) Determine FCF series
    if params.fcf_series:
        fcfs = params.fcf_series
    else:
        # project revenue → ebit → fcf
        # assume params.revenue is full revenue forecast
        ebits = project_ebit(params.revenue, params.ebit_margin)
        fcfs = project_fcf(
            params.revenue,
            ebits,
            params.capex,
            params.depreciation,
            params.nwc_changes,
            params.tax_rate
        )

    # 2) Discount each FCF (year-end)
    discount_factors = [(1 + params.wacc) ** (i + 1) for i in range(len(fcfs))]
    pv_fcfs = [f / df for f, df in zip(fcfs, discount_factors)]

    # 3) Terminal value via Gordon growth
    last_fcf = fcfs[-1]
    tv = last_fcf * (1 + params.terminal_growth) / (params.wacc - params.terminal_growth)
    pv_tv = tv / ((1 + params.wacc) ** len(fcfs))

    # 4) Enterprise value
    ev = sum(pv_fcfs) + pv_tv

    # 5) Subtract net debt at t=0
    net_debt = params.debt_schedule.get(0, 0.0)
    equity = ev - net_debt

    # 6) Price per share
    ps = equity / params.share_count if params.share_count else None

    return ev, equity, ps


def calc_apv(params: ValuationParams) -> Tuple[float, float, Optional[float]]:
    """
    APV:
      1) All-equity DCF (zero out debt)
      2) PV of interest tax shields on the debt schedule
      3) Sum → levered EV; subtract net debt → equity; divide by shares
    """
    # 1) Base all-equity DCF
    zero_debt = params.debt_schedule.copy()
    base_params = ValuationParams(**vars(params), debt_schedule={})
    ev_unlevered, _, _ = calc_dcf_series(base_params)

    # 2) PV of tax shields
    cod = params.cost_of_debt or params.wacc
    shields_pv = 0.0
    for year, debt in params.debt_schedule.items():
        interest = debt * cod
        shield = interest * params.tax_rate
        shields_pv += shield / ((1 + params.wacc) ** year)

    ev_apv = ev_unlevered + shields_pv

    # 3) Equity & PS
    net_debt = params.debt_schedule.get(0, 0.0)
    equity_apv = ev_apv - net_debt
    ps_apv = equity_apv / params.share_count if params.share_count else None

    return ev_apv, equity_apv, ps_apv
