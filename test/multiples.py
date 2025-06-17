import numpy as np
import pandas as pd
from params import ValuationParams


def run_multiples_analysis(params: ValuationParams) -> pd.DataFrame:
    net_debt = params.total_debt - params.cash_and_equivalents
    peer_prices = {'P/E':[], 'EV/EBITDA':[], 'EV/Revenue':[]}

    for comp, mult in params.multiples_input.items():
        peer_prices['P/E'].append(mult['P/E'] * params.LTM_EPS)
        peer_prices['EV/EBITDA'].append((mult['EV/EBITDA']*params.LTM_EBITDA - net_debt)/params.shares_outstanding)
        peer_prices['EV/Revenue'].append((mult['EV/Revenue']*params.LTM_Revenue - net_debt)/params.shares_outstanding)

    rows=[]
    for fam, prices in peer_prices.items():
        rows.append({
            'Multiple': fam,
            'Mean Price': np.mean(prices),
            'Median Price': np.median(prices)
        })
    df=pd.DataFrame(rows)
    print(f"Blended median: ${df['Median Price'].mean():.2f}")
    return df