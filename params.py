# params.py

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class ValuationParams:
    # ---- Driver-based inputs ----
    revenue: List[float] = field(default_factory=list)  # Revenue (dollars)
    ebit_margin: float = 0.0  # As decimal (e.g., 0.20 for 20%)
    capex: List[float] = field(default_factory=list)  # CapEx (dollars)
    depreciation: List[float] = field(default_factory=list)  # Depreciation (dollars)
    nwc_changes: List[float] = field(default_factory=list)  # NWC changes (dollars)

    # ---- Direct FCF override ----
    fcf_series: List[float] = field(default_factory=list)  # FCF (dollars)

    # ---- Terminal & discount assumptions ----
    terminal_growth: float = 0.0  # As decimal (e.g., 0.02 for 2%)
    wacc: float = 0.0  # As decimal (e.g., 0.10 for 10%)
    tax_rate: float = 0.0  # As decimal (e.g., 0.21 for 21%)
    mid_year_convention: bool = False  # True for mid-year, False for year-end

    # ---- Capital structure & shares ----
    share_count: float = 1.0  # Number of shares
    cost_of_debt: float = 0.0  # As decimal (e.g., 0.05 for 5%)
    debt_schedule: Dict[int, float] = field(default_factory=dict)  # Year -> Debt (dollars)

    # ---- Monte Carlo specs ----
    variable_specs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ---- Peer multiples metadata ----
    multiples_input: Dict[str, Any] = field(default_factory=dict)

    # ---- Scenarios & Sensitivity ranges ----
    scenarios: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sensitivity_ranges: Dict[str, List[float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        # Validate percentages
        for field_name, value in [
            ("ebit_margin", self.ebit_margin),
            ("wacc", self.wacc),
            ("tax_rate", self.tax_rate),
            ("cost_of_debt", self.cost_of_debt)
        ]:
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")
        
        # Validate terminal growth (can be negative for deflation)
        if self.terminal_growth >= 1:
            raise ValueError("terminal_growth must be less than 100%")
        
        # Validate share count
        if self.share_count <= 0:
            raise ValueError("share_count must be positive")
        
        # Validate series consistency
        if self.revenue and any(r <= 0 for r in self.revenue):
            raise ValueError("All revenue values must be positive")
