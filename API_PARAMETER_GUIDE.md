# API Parameter Guide

This document explains the parameter naming conventions and usage for the Financial Valuation API.

## 🔄 Parameter Mapping

The API uses two different parameter naming conventions:

1. **FinancialInputs** (API interface) - User-friendly names
2. **ValuationParameters** (Internal calculations) - Technical names

### Basic Financial Parameters

| API Parameter | Internal Parameter | Description |
|---------------|-------------------|-------------|
| `revenue` | `revenue_projections` | Annual revenue projections |
| `ebit_margin` | `ebit_margin` | EBIT margin (same) |
| `capex` | `capital_expenditure` | Capital expenditure |
| `depreciation` | `depreciation_expense` | Depreciation expense |
| `nwc_changes` | `net_working_capital_changes` | Net working capital changes |
| `tax_rate` | `corporate_tax_rate` | Corporate tax rate |
| `terminal_growth` | `terminal_growth_rate` | Terminal growth rate |
| `wacc` | `weighted_average_cost_of_capital` | Weighted average cost of capital |
| `share_count` | `shares_outstanding` | Number of shares outstanding |
| `cost_of_debt` | `cost_of_debt` | Cost of debt (same) |

### Optional Parameters

| API Parameter | Internal Parameter | Description |
|---------------|-------------------|-------------|
| `amortization` | `amortization_expense` | Amortization expense |
| `other_non_cash` | `other_non_cash_items` | Other non-cash items |
| `other_working_capital` | `other_working_capital_items` | Other working capital items |
| `cash_balance` | `cash_and_equivalents` | Cash and cash equivalents |
| `target_debt_ratio` | `target_debt_to_value_ratio` | Target debt-to-value ratio |
| `market_risk_premium` | `equity_risk_premium` | Market risk premium |

## 🎯 Scenario Analysis

**Important**: Scenario analysis uses the **Internal Parameter** names (ValuationParameters), not the API parameter names.

### Correct Scenario Example

```json
{
  "financial_inputs": {
    "revenue": [1000.0, 1100.0, 1210.0],
    "ebit_margin": 0.15,
    "terminal_growth": 0.025,
    "wacc": 0.10,
    "scenarios": {
      "optimistic": {
        "ebit_margin": 0.20,
        "terminal_growth_rate": 0.03  // ✅ Correct: uses internal name
      },
      "pessimistic": {
        "ebit_margin": 0.10,
        "terminal_growth_rate": 0.015  // ✅ Correct: uses internal name
      }
    }
  }
}
```

### Incorrect Scenario Example

```json
{
  "financial_inputs": {
    "scenarios": {
      "optimistic": {
        "ebit_margin": 0.20,
        "terminal_growth": 0.03  // ❌ Wrong: uses API name
      }
    }
  }
}
```

## 📊 Sensitivity Analysis

Sensitivity analysis also uses **Internal Parameter** names.

### Correct Sensitivity Example

```json
{
  "financial_inputs": {
    "sensitivity_analysis": {
      "weighted_average_cost_of_capital": [0.075, 0.085, 0.095, 0.105, 0.115],
      "ebit_margin": [0.14, 0.16, 0.18, 0.20, 0.22]
    }
  }
}
```

## 🎲 Monte Carlo Simulation

Monte Carlo simulation uses **Internal Parameter** names.

### Correct Monte Carlo Example

```json
{
  "financial_inputs": {
    "monte_carlo_specs": {
      "ebit_margin": {
        "distribution": "normal",
        "params": {"mean": 0.18, "std": 0.02}
      },
      "weighted_average_cost_of_capital": {
        "distribution": "normal",
        "params": {"mean": 0.095, "std": 0.01}
      }
    }
  }
}
```

## 🔍 Valid Internal Parameter Names

For scenario analysis, sensitivity analysis, and Monte Carlo simulation, use these parameter names:

### Financial Metrics
- `revenue_projections`
- `ebit_margin`
- `capital_expenditure`
- `depreciation_expense`
- `net_working_capital_changes`
- `amortization_expense`
- `other_non_cash_items`
- `other_working_capital_items`
- `free_cash_flow_series`

### Terminal Value & Discount Rates
- `terminal_growth_rate`
- `weighted_average_cost_of_capital`
- `corporate_tax_rate`
- `use_mid_year_convention`

### Capital Structure
- `shares_outstanding`
- `cost_of_debt`
- `debt_schedule`
- `current_equity_value`
- `cash_and_equivalents`

### Cost of Capital
- `unlevered_cost_of_equity`
- `levered_cost_of_equity`
- `risk_free_rate`
- `equity_risk_premium`
- `levered_beta`
- `unlevered_beta`
- `target_debt_to_value_ratio`

### Analysis Specifications
- `monte_carlo_variable_specs`
- `comparable_multiples_data`
- `scenario_definitions`
- `sensitivity_parameter_ranges`

## 🚨 Common Errors

### Error: Invalid parameter 'terminal_growth'
```
Invalid parameter 'terminal_growth' in scenario 'optimistic'. 
Valid parameters: terminal_growth_rate, ebit_margin, ...
```

**Solution**: Use `terminal_growth_rate` instead of `terminal_growth` in scenarios.

### Error: Invalid parameter 'wacc'
```
Invalid parameter 'wacc' in sensitivity analysis.
Valid parameters: weighted_average_cost_of_capital, ebit_margin, ...
```

**Solution**: Use `weighted_average_cost_of_capital` instead of `wacc` in sensitivity analysis.

## 📝 Best Practices

1. **Basic Inputs**: Use API parameter names (e.g., `terminal_growth`, `wacc`)
2. **Analysis Parameters**: Use internal parameter names (e.g., `terminal_growth_rate`, `weighted_average_cost_of_capital`)
3. **Test Your Requests**: Use the Swagger UI to test parameter combinations
4. **Check Error Messages**: Error messages list all valid parameter names
5. **Use Sample Data**: The `/api/valuation/sample` endpoint provides correct examples

## 🔧 Testing

### Test with Swagger UI
1. Visit `http://localhost:5001/api/docs`
2. Try the `/api/valuation/calculate` endpoint
3. Use the "Try it out" feature to test different parameters

### Test with Sample Data
```bash
curl http://localhost:5001/api/valuation/sample
```

### Test with Custom Data
```bash
curl -X POST http://localhost:5001/api/valuation/calculate \
  -H "Content-Type: application/json" \
  -d @your_data.json
```

## 📚 Examples

### Complete Example with All Analysis Types

```json
{
  "company_name": "Example Corp",
  "valuation_date": "2024-01-01",
  "financial_inputs": {
    "revenue": [1000.0, 1100.0, 1210.0],
    "ebit_margin": 0.15,
    "tax_rate": 0.25,
    "capex": [150.0, 165.0, 181.5],
    "depreciation": [100.0, 110.0, 121.0],
    "nwc_changes": [50.0, 55.0, 60.5],
    "terminal_growth": 0.025,
    "wacc": 0.10,
    "share_count": 10.0,
    "cost_of_debt": 0.06,
    "scenarios": {
      "optimistic": {
        "ebit_margin": 0.20,
        "terminal_growth_rate": 0.03
      },
      "pessimistic": {
        "ebit_margin": 0.10,
        "terminal_growth_rate": 0.015
      }
    },
    "sensitivity_analysis": {
      "weighted_average_cost_of_capital": [0.08, 0.09, 0.10, 0.11, 0.12],
      "ebit_margin": [0.12, 0.14, 0.16, 0.18, 0.20]
    },
    "monte_carlo_specs": {
      "ebit_margin": {
        "distribution": "normal",
        "params": {"mean": 0.15, "std": 0.02}
      },
      "weighted_average_cost_of_capital": {
        "distribution": "normal",
        "params": {"mean": 0.10, "std": 0.01}
      }
    }
  }
}
```

This guide should help you avoid parameter naming issues and use the API effectively! 