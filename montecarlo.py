import numpy as np
from typing import List, Dict
from params import ValuationParams
from valuation import single_ev

def run_monte_carlo(params: ValuationParams,
                    methods: List[str],
                    runs: int=2000,
                    seed: int=42) -> tuple[object, Dict[str, np.ndarray]]:
    np.random.seed(seed)
    betas   = np.maximum(0, np.random.normal(1.1,1.1*0.1,runs))
    cds     = np.maximum(0, np.random.normal(params.cost_of_debt, params.cost_of_debt*0.1, runs))
    g_exps  = np.maximum(0, np.random.normal(params.g_exp, params.g_exp*0.1, runs))
    g_terms = np.maximum(0, np.random.normal(params.g_term, params.g_term*0.1, runs))
    dvs     = np.clip(np.random.normal(params.target_debt_ratio, params.target_debt_ratio*0.1, runs),0,1)

    import pandas as pd
    summary=[]
    ev_store={}
    net_debt=params.total_debt-params.cash_and_equivalents

    for m in methods:
        evs = np.array([
            single_ev(params,m,
                      beta_override=betas[i],
                      cd_override=cds[i],
                      g_exp_override=g_exps[i],
                      g_term_override=g_terms[i],
                      dv_override=dvs[i])
            for i in range(runs)
        ])
        prices=(evs-net_debt)/params.shares_outstanding
        ev_store[m]=evs
        summary.append({
            'Method':m,
            'EV Mean ($B)':evs.mean()/1e9,
            'Price Mean ($)':prices.mean(),
            'Price P5':np.percentile(prices,5),
            'Price P95':np.percentile(prices,95)
        })
    return pd.DataFrame(summary), ev_store