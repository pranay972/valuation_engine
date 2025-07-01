# params.py

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class ValuationParams:
    # ---- Driver-based inputs ----
    revenue: List[float] = field(default_factory=list)
    ebit_margin: float = 0.0
    capex: List[float] = field(default_factory=list)
    depreciation: List[float] = field(default_factory=list)
    nwc_changes: List[float] = field(default_factory=list)

    # ---- Direct FCF override ----
    fcf_series: List[float] = field(default_factory=list)

    # ---- Terminal & discount assumptions ----
    terminal_growth: float = 0.0
    wacc: float = 0.0
    tax_rate: float = 0.0

    # ---- Capital structure & shares ----
    share_count: float = 1.0
    cost_of_debt: float = 0.0
    debt_schedule: Dict[int, float] = field(default_factory=dict)

    # ---- Monte Carlo specs ----
    variable_specs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ---- Peer multiples metadata ----
    multiples_input: Dict[str, Any] = field(default_factory=dict)

    # ---- Scenarios & Sensitivity ranges ----
    scenarios: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sensitivity_ranges: Dict[str, List[float]] = field(default_factory=dict)
