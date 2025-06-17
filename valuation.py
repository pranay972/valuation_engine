import numpy as np
from typing import List, Optional
from params import ValuationParams

# -- Forecasting --
def forecast_fcfs(FCF0: float, growth: float, periods: int) -> List[float]:
    return [FCF0 * (1 + growth)**t for t in range(1, periods+1)]

def prepare_fcfs(params: ValuationParams, g_exp: float) -> List[float]:
    if params.fcf_input_mode == 'AUTO':
        return forecast_fcfs(params.FCF_0, g_exp, params.n)
    if len(params.fcf_list) != params.n:
        raise ValueError(f"Expected {params.n} FCF items, got {len(params.fcf_list)}")
    return params.fcf_list

# -- Discounting & Terminal Value --
def discount_cash_flows(cfs: List[float], rate: float, mid_year: bool) -> float:
    return sum(cf / (1+rate)**((i+1)-(0.5 if mid_year else 0))
               for i, cf in enumerate(cfs))

def calculate_terminal_value(last_cf: float, growth: float, rate: float) -> float:
    return last_cf * (1+growth) / (rate - growth)

def discount_terminal_value(tv: float, rate: float, periods: int, mid_year: bool) -> float:
    return tv / (1+rate)**(periods - (0.5 if mid_year else 0))

# -- Core Models --
def calculate_wacc(ce: float, cd: float, tr: float, dv: float) -> float:
    return ce*(1-dv) + cd*(1-tr)*dv

def calculate_apv(params: ValuationParams,
                  ce: float, cd: float,
                  fcf: List[float], g_term: float) -> float:
    pv_unlev = discount_cash_flows(fcf, ce, params.mid_year_discount)
    tv_unlev = calculate_terminal_value(fcf[-1], g_term, ce)
    pv_tv_unlev = discount_terminal_value(tv_unlev, ce, params.n, params.mid_year_discount)

    annual_shield = params.total_debt * cd * params.tax_rate
    pv_shields = sum(
        annual_shield/(1+cd)**((t+1)-(0.5 if params.mid_year_discount else 0))
        for t in range(params.n)
    )
    return pv_unlev + pv_tv_unlev + pv_shields

def single_ev(params: ValuationParams,
              method: str,
              beta_override: Optional[float]=None,
              cd_override: Optional[float]=None,
              g_exp_override: Optional[float]=None,
              g_term_override: Optional[float]=None,
              dv_override: Optional[float]=None,
              re_override: Optional[float]=None) -> float:
    beta = beta_override or 1.1
    cd = cd_override or params.cost_of_debt
    g_exp = g_exp_override or params.g_exp
    g_term = g_term_override or params.g_term
    dv = dv_override or params.target_debt_ratio
    ce = re_override if re_override is not None else (
        params.risk_free_rate + beta*params.market_risk_premium
    )

    fcf = prepare_fcfs(params, g_exp)
    if method.upper()=='WACC':
        wacc = calculate_wacc(ce, cd, params.tax_rate, dv)
        pv_fcf = discount_cash_flows(fcf, wacc, params.mid_year_discount)
        tv = calculate_terminal_value(fcf[-1], g_term, wacc)
        pv_tv = discount_terminal_value(tv, wacc, params.n, params.mid_year_discount)
        return pv_fcf + pv_tv
    return calculate_apv(params, ce, cd, fcf, g_term)

# -- Batch Valuation --
def run_single_valuations(params: ValuationParams, methods: List[str]):
    net_debt = params.total_debt - params.cash_and_equivalents
    import pandas as pd
    rows=[]
    for m in methods:
        ev = single_ev(params, m)
        eq = ev - net_debt
        rows.append({'Method': m,
                     'EV ($B)':ev/1e9,
                     'Equity ($B)':eq/1e9,
                     'Share Price':eq/params.shares_outstanding})
    return pd.DataFrame(rows)
