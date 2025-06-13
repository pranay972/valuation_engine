import numpy as np
import pytest
from valuation import (
    calculate_cost_of_equity,
    calculate_wacc,
    forecast_fcfs,
    calculate_terminal_value,
    discount_cash_flows,
    discount_terminal_value,
)
from montecarlo import sample_distribution

# --- Valuation.py Tests ---

def test_calculate_cost_of_equity():
    # Standard CAPM
    assert np.isclose(calculate_cost_of_equity(0.02, 1.0, 0.06), 0.08)
    assert np.isclose(calculate_cost_of_equity(0.03, 1.2, 0.05), 0.09)
    # Beta zero
    assert np.isclose(calculate_cost_of_equity(0.01, 0, 0.07), 0.01)

def test_calculate_wacc():
    # Basic WACC calculation
    coe, cod, tax = 0.1, 0.05, 0.25
    eq, debt = 800, 200
    # WACC = (0.8 * 0.1) + (0.2 * 0.05 * 0.75) = 0.08 + 0.0075 = 0.0875
    assert np.isclose(calculate_wacc(coe, cod, tax, eq, debt), 0.0875)
    # All equity
    assert np.isclose(calculate_wacc(0.1, 0.06, 0.2, 1000, 0), 0.1)
    # All debt
    assert np.isclose(calculate_wacc(0.1, 0.06, 0.2, 0, 1000), 0.048)  # 0.06 * (1-0.2)

def test_forecast_fcfs():
    # Growth rate = 10%, FCF_0 = 100, 3 years: 110, 121, 133.1
    out = forecast_fcfs(100, 0.10, 3)
    np.testing.assert_allclose(out, [110, 121, 133.1], rtol=1e-4)

def test_calculate_terminal_value():
    # FCF_n = 133.1, g_term = 2%, WACC = 7%
    tv = calculate_terminal_value(133.1, 0.02, 0.07)
    # TV = 133.1 * 1.02 / (0.07 - 0.02) = 135.762 / 0.05 = 2715.24
    assert np.isclose(tv, 2715.24, atol=0.1)

def test_discount_cash_flows():
    cf = [100, 110, 121]
    wacc = 0.05
    # Compute expected with full precision:
    expected = sum(c / (1 + wacc) ** (i + 1) for i, c in enumerate(cf))
    assert np.isclose(discount_cash_flows(cf, wacc), expected, rtol=1e-8)

def test_discount_terminal_value():
    tv = 1000
    wacc = 0.1
    n = 3
    # PV = 1000 / (1.1)^3
    expected = 751.3148
    assert np.isclose(discount_terminal_value(tv, wacc, n), expected, rtol=1e-4)

# --- montecarlo.py Tests (sampling) ---

def test_sample_distribution_normal():
    np.random.seed(42)
    cfg = {"dist": "normal", "mean": 10, "std": 2}
    vals = [sample_distribution(cfg) for _ in range(3)]
    # Check shape and that mean is close
    assert len(vals) == 3
    assert all(isinstance(v, float) for v in vals)
    assert np.isclose(np.mean(vals), 10, atol=2)

def test_sample_distribution_lognormal():
    np.random.seed(42)
    cfg = {"dist": "lognormal", "mean": 10, "std": 2}
    v = sample_distribution(cfg)
    assert v > 0

def test_sample_distribution_uniform():
    np.random.seed(42)
    cfg = {"dist": "uniform", "mean": 10, "std": 2}
    for _ in range(10):
        v = sample_distribution(cfg)
        assert 8 <= v <= 12

def test_sample_distribution_truncated_normal():
    np.random.seed(42)
    cfg = {"dist": "truncated_normal", "mean": 0.025, "std": 0.005}
    for _ in range(10):
        v = sample_distribution(cfg)
        assert 0 < v < 0.05

def test_sample_distribution_triangular():
    np.random.seed(42)
    cfg = {"dist": "triangular", "mean": 10, "std": 2}
    for _ in range(10):
        v = sample_distribution(cfg)
        assert 8 <= v <= 12

def test_sample_distribution_invalid():
    cfg = {"dist": "unsupported", "mean": 1, "std": 1}
    with pytest.raises(ValueError):
        sample_distribution(cfg)