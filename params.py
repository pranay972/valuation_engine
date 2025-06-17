from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ValuationParams:
    # Core inputs
    risk_free_rate: float = 0.02
    market_risk_premium: float = 0.06
    cost_of_debt: float = 0.04
    tax_rate: float = 0.21
    total_debt: float = 100e9
    cash_and_equivalents: float = 50e9
    shares_outstanding: float = 5e9

    # Forecast settings
    n: int = 5
    target_debt_ratio: float = 0.25
    mid_year_discount: bool = True

    # FCF inputs
    fcf_input_mode: str = 'AUTO'               # 'AUTO' or 'LIST'
    FCF_0: float = 10e9
    g_exp: float = 0.08
    g_term: float = 0.02
    fcf_list: List[float] = field(default_factory=lambda: [
        10e9, 10e9 * 1.08, 10e9 * 1.08**2, 10e9 * 1.08**3, 10e9 * 1.08**4
    ])

    # Peer multiples
    multiples_input: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'MSFT':  {'EV/EBITDA': 20.0, 'EV/Revenue': 8.0,  'P/E': 25.0},
        'GOOGL': {'EV/EBITDA': 18.0, 'EV/Revenue': 7.0,  'P/E': 23.0},
        'AMZN':  {'EV/EBITDA': 50.0, 'EV/Revenue': 3.0,  'P/E': 60.0},
    })
    LTM_EBITDA: float = 60e9
    LTM_Revenue: float = 300e9
    LTM_EPS: float = 6.0