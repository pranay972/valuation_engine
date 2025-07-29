# Finance Core - Analysis Methods & Required Input Fields

This document outlines all 6 analysis methods available in the Finance Core system and specifies which input fields are required (marked with *) for each analysis.

## 📊 Analysis Methods Overview

1. **DCF Valuation (WACC)** - Discounted Cash Flow using Weighted Average Cost of Capital
2. **APV Valuation** - Adjusted Present Value method
3. **Comparable Multiples** - Relative valuation using peer company ratios
4. **Scenario Analysis** - Multiple scenarios with different parameter combinations
5. **Sensitivity Analysis** - Parameter impact analysis on key valuation drivers
6. **Monte Carlo Simulation** - Risk analysis with probability distributions

---

## 1. DCF Valuation (WACC) Analysis

**Purpose**: Standard discounted cash flow valuation using weighted average cost of capital

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*weighted_average_cost_of_capital": 0.095,
    "*terminal_growth_rate": 0.025,
    "*share_count": 45.2,
    "*cost_of_debt": 0.065
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    },
    "cost_of_capital": {
      "risk_free_rate": 0.03,
      "market_risk_premium": 0.06,
      "levered_beta": 1.2,
      "unlevered_beta": 1.0,
      "target_debt_to_value_ratio": 0.3,
      "unlevered_cost_of_equity": 0.11
    }
  }
}
```

### Output
- Enterprise Value
- Equity Value
- Share Price
- Free Cash Flows
- Terminal Value
- WACC Components

---

## 2. APV Valuation Analysis

**Purpose**: Adjusted Present Value method that separates unlevered value from financing effects

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*terminal_growth_rate": 0.025,
    "*share_count": 45.2,
    "*cost_of_debt": 0.065
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    },
    "cost_of_capital": {
      "risk_free_rate": 0.03,
      "market_risk_premium": 0.06,
      "levered_beta": 1.2,
      "unlevered_beta": 1.0,
      "target_debt_to_value_ratio": 0.3,
      "*unlevered_cost_of_equity": 0.11
    }
  }
}
```

### Output
- Unlevered Enterprise Value
- Present Value of Tax Shields
- APV Enterprise Value
- Equity Value
- Share Price

---

## 3. Comparable Multiples Analysis

**Purpose**: Relative valuation using peer company ratios

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*share_count": 45.2
  },
  "*comparable_multiples": {
    "EV/EBITDA": [12.5, 14.2, 13.8, 15.1, 12.9, 13.5, 14.8, 13.2],
    "P/E": [18.5, 22.1, 20.8, 24.3, 19.7, 21.5, 23.2, 20.1],
    "EV/FCF": [15.2, 17.8, 16.5, 18.9, 15.8, 17.2, 18.5, 16.1],
    "EV/Revenue": [2.8, 3.2, 3.0, 3.5, 2.9, 3.1, 3.4, 3.0]
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    }
  }
}
```

### Output
- Implied Enterprise Values for each multiple
- Mean and Median values
- Standard deviation
- Min/Max values

---

## 4. Scenario Analysis

**Purpose**: Multiple scenarios with different parameter combinations

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*weighted_average_cost_of_capital": 0.095,
    "*terminal_growth_rate": 0.025,
    "*share_count": 45.2,
    "*cost_of_debt": 0.065
  },
  "*scenarios": {
    "base_case": {},
    "optimistic": {
      "ebit_margin": 0.22,
      "terminal_growth_rate": 0.03,
      "weighted_average_cost_of_capital": 0.085
    },
    "pessimistic": {
      "ebit_margin": 0.14,
      "terminal_growth_rate": 0.015,
      "weighted_average_cost_of_capital": 0.105
    },
    "high_growth": {
      "revenue_projections": [1250.0, 1437.5, 1653.1, 1901.1, 2186.2],
      "ebit_margin": 0.20,
      "terminal_growth_rate": 0.035
    },
    "low_growth": {
      "revenue_projections": [1250.0, 1312.5, 1378.1, 1447.0, 1519.4],
      "ebit_margin": 0.16,
      "terminal_growth_rate": 0.015
    }
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    }
  }
}
```

### Output
- Enterprise Value for each scenario
- Equity Value for each scenario
- Share Price for each scenario
- Input changes for each scenario

---

## 5. Sensitivity Analysis

**Purpose**: Parameter impact analysis on key valuation drivers

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*weighted_average_cost_of_capital": 0.095,
    "*terminal_growth_rate": 0.025,
    "*share_count": 45.2,
    "*cost_of_debt": 0.065
  },
  "*sensitivity_analysis": {
    "wacc_range": [0.075, 0.085, 0.095, 0.105, 0.115],
    "ebit_margin_range": [0.14, 0.16, 0.18, 0.20, 0.22],
    "terminal_growth_range": [0.015, 0.020, 0.025, 0.030, 0.035],
    "target_debt_ratio_range": [0.1, 0.2, 0.3, 0.4, 0.5]
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    }
  }
}
```

### Output
- Enterprise Value sensitivity for each parameter
- Share Price sensitivity for each parameter
- Range of values tested

---

## 6. Monte Carlo Simulation

**Purpose**: Risk analysis with probability distributions

### Required Input Fields (*)

```json
{
  "financial_inputs": {
    "*revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "*ebit_margin": 0.18,
    "*tax_rate": 0.25,
    "*capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "*depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "*nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "*weighted_average_cost_of_capital": 0.095,
    "*terminal_growth_rate": 0.025,
    "*share_count": 45.2,
    "*cost_of_debt": 0.065
  },
  "*monte_carlo_specs": {
    "ebit_margin": {
      "distribution": "normal",
      "params": { "mean": 0.18, "std": 0.02 }
    },
    "weighted_average_cost_of_capital": {
      "distribution": "normal",
      "params": { "mean": 0.095, "std": 0.01 }
    },
    "terminal_growth_rate": {
      "distribution": "normal",
      "params": { "mean": 0.025, "std": 0.005 }
    },
    "levered_beta": {
      "distribution": "normal",
      "params": { "mean": 1.2, "std": 0.1 }
    }
  }
}
```

### Optional Input Fields

```json
{
  "financial_inputs": {
    "amortization": [25.0, 27.5, 30.3, 33.3, 36.6],
    "other_non_cash": [10.0, 11.0, 12.1, 13.3, 14.6],
    "other_working_capital": [5.0, 5.5, 6.1, 6.7, 7.3],
    "cash_balance": 50.0,
    "debt_schedule": {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    },
    "cost_of_capital": {
      "risk_free_rate": 0.03,
      "market_risk_premium": 0.06,
      "levered_beta": 1.2,
      "unlevered_beta": 1.0,
      "target_debt_to_value_ratio": 0.3,
      "unlevered_cost_of_equity": 0.11
    }
  }
}
```

### Output
- Mean Enterprise Value
- Median Enterprise Value
- Standard Deviation
- 95% Confidence Interval
- Distribution statistics

---

## 📋 Summary of Required Fields by Analysis

| Analysis Method | Core Financial Fields | Analysis-Specific Fields |
|----------------|----------------------|-------------------------|
| **DCF (WACC)** | revenue*, ebit_margin*, tax_rate*, capex*, depreciation*, nwc_changes*, wacc*, terminal_growth*, share_count*, cost_of_debt* | None |
| **APV** | revenue*, ebit_margin*, tax_rate*, capex*, depreciation*, nwc_changes*, terminal_growth*, share_count*, cost_of_debt* | unlevered_cost_of_equity* |
| **Comparable Multiples** | revenue*, ebit_margin*, tax_rate*, capex*, depreciation*, nwc_changes*, share_count* | comparable_multiples* |
| **Scenario Analysis** | All DCF fields* | scenarios* |
| **Sensitivity Analysis** | All DCF fields* | sensitivity_analysis* |
| **Monte Carlo** | All DCF fields* | monte_carlo_specs* |

## 🎯 Key Notes

- **Core Financial Fields**: These are the basic financial inputs required for most analyses
- **Analysis-Specific Fields**: These are additional fields required only for specific analysis types
- **Optional Fields**: These enhance accuracy but have default values if not provided
- **Arrays**: Revenue, capex, depreciation, nwc_changes, amortization, other_non_cash, and other_working_capital should be arrays with values for each forecast year
- **Percentages**: All percentage values (margins, rates, growth) should be expressed as decimals (e.g., 0.18 for 18%)
- **Monetary Values**: All monetary values are in millions of dollars
- **Debt Schedule**: Maps year indices (0, 1, 2, etc.) to debt amounts

## 🔧 Usage Example

```python
from finance_calculator import CleanModularFinanceCalculator, FinancialInputs

# Create inputs with required fields for DCF analysis
inputs = FinancialInputs(
    revenue=[1000, 1100, 1200, 1300, 1400],  # Required*
    ebit_margin=0.20,                        # Required*
    capex=[150, 165, 180, 195, 210],         # Required*
    depreciation=[100, 110, 120, 130, 140],  # Required*
    nwc_changes=[50, 55, 60, 65, 70],        # Required*
    tax_rate=0.25,                           # Required*
    terminal_growth=0.025,                   # Required*
    wacc=0.10,                               # Required*
    share_count=45.2,                        # Required*
    cost_of_debt=0.065                       # Required*
)

calculator = CleanModularFinanceCalculator()
results = calculator.run_dcf_valuation(inputs)
``` 