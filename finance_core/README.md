# Finance Core - Professional Financial Valuation System

A comprehensive, modular financial valuation system built with clean architecture principles. This system provides professional-grade financial calculations for DCF (WACC), APV, Comparable Multiples, Scenario Analysis, Sensitivity Analysis, and Monte Carlo Simulation.

## 🎯 Key Features

### Core Valuation Methods
- **DCF Valuation (WACC)**: Standard discounted cash flow using weighted average cost of capital
- **Adjusted Present Value (APV)**: Separates unlevered value from financing effects
- **Comparable Multiples**: Relative valuation using peer company ratios
- **Scenario Analysis**: Multiple scenarios with different parameter combinations
- **Sensitivity Analysis**: Parameter impact analysis on key valuation drivers
- **Monte Carlo Simulation**: Risk analysis with probability distributions

### Professional Standards
- **WACC Circular Dependency**: Resolved using target capital structure approach
- **Hamada Equation**: Proper unlevered/levered beta calculations with CAPM
- **Comprehensive FCF**: Complete cash flow components (amortization, other non-cash items)
- **Net Debt**: Current debt minus cash balance for accurate valuation
- **Terminal Value Validation**: Professional checks for growth rates and ROIC
- **APV Tax Shields**: Proper discounting at unlevered cost of equity

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd finance_core

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```python
from finance_calculator import CleanModularFinanceCalculator, FinancialInputs

# Create financial inputs
inputs = FinancialInputs(
    revenue=[1000, 1100, 1200, 1300, 1400],  # 5 years of revenue
    ebit_margin=0.20,  # 20% EBIT margin
    capex=[150, 165, 180, 195, 210],
    depreciation=[100, 110, 120, 130, 140],
    nwc_changes=[50, 55, 60, 65, 70],
    tax_rate=0.25,     # 25% tax rate
    terminal_growth=0.025,  # 2.5% terminal growth
    wacc=0.10,         # 10% WACC
    share_count=45.2,  # 45.2 million shares
    cost_of_debt=0.065
)

# Create calculator and run valuation
calculator = CleanModularFinanceCalculator()
results = calculator.run_comprehensive_valuation(inputs, "TechCorp Inc.")

print(f"Enterprise Value: ${results['dcf_wacc']['enterprise_value']:,.0f}")
print(f"Equity Value: ${results['dcf_wacc']['equity_value']:,.0f}")
print(f"Share Price: ${results['dcf_wacc']['price_per_share']:.2f}")
```

## 📁 Project Structure

```
finance_core/
├── finance_calculator.py      # Main calculator class and orchestration
├── dcf.py                     # DCF valuation methods (WACC & APV)
├── wacc.py                    # WACC and cost of capital calculations
├── multiples.py               # Comparable multiples analysis
├── scenario.py                # Scenario analysis
├── sensitivity.py             # Sensitivity analysis
├── monte_carlo.py             # Monte Carlo simulation
├── drivers.py                 # Financial drivers and projections
├── params.py                  # Valuation parameters and data structures
├── test_finance_calculator.py # Comprehensive test suite
├── sample_input.json          # Sample input data
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## 📊 Input Data Format

### Required Fields
```json
{
  "company_name": "TechCorp Inc.",
  "valuation_date": "2024-01-01",
  "financial_inputs": {
    "revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "ebit_margin": 0.18,
    "tax_rate": 0.25,
    "capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "weighted_average_cost_of_capital": 0.095,
    "terminal_growth_rate": 0.025,
    "share_count": 45.2,
    "cost_of_debt": 0.065,
    "cash_balance": 50.0
  }
}
```

### Optional Advanced Fields
```json
{
  "comparable_multiples": {
    "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
    "P/E": [18.5, 22.1, 20.8, 24.3],
    "EV/FCF": [15.2, 17.8, 16.5, 18.9],
    "EV/Revenue": [2.8, 3.2, 3.0, 3.5]
  },
  "scenarios": {
    "optimistic": {
      "ebit_margin": 0.22,
      "terminal_growth_rate": 0.03,
      "weighted_average_cost_of_capital": 0.085
    },
    "pessimistic": {
      "ebit_margin": 0.14,
      "terminal_growth_rate": 0.015,
      "weighted_average_cost_of_capital": 0.105
    }
  },
  "monte_carlo_specs": {
    "ebit_margin": {
      "distribution": "normal",
      "params": { "mean": 0.18, "std": 0.02 }
    },
    "weighted_average_cost_of_capital": {
      "distribution": "normal",
      "params": { "mean": 0.095, "std": 0.01 }
    }
  },
  "sensitivity_analysis": {
    "wacc_range": [0.075, 0.085, 0.095, 0.105, 0.115],
    "ebit_margin_range": [0.14, 0.16, 0.18, 0.20, 0.22],
    "terminal_growth_range": [0.015, 0.020, 0.025, 0.030, 0.035]
  }
}
```

## 🔧 Usage Examples

### 1. DCF Valuation Only
```python
from finance_calculator import CleanModularFinanceCalculator, FinancialInputs

inputs = FinancialInputs(
    revenue=[1000, 1100, 1200, 1300, 1400],
    ebit_margin=0.20,
    capex=[150, 165, 180, 195, 210],
    depreciation=[100, 110, 120, 130, 140],
    nwc_changes=[50, 55, 60, 65, 70],
    tax_rate=0.25,
    terminal_growth=0.025,
    wacc=0.10,
    share_count=45.2,
    cost_of_debt=0.065
)

calculator = CleanModularFinanceCalculator()
dcf_results = calculator.run_dcf_valuation(inputs)

print(f"Enterprise Value: ${dcf_results['enterprise_value']:,.0f}")
print(f"Equity Value: ${dcf_results['equity_value']:,.0f}")
print(f"Share Price: ${dcf_results['price_per_share']:.2f}")
```

### 2. APV Valuation
```python
apv_results = calculator.run_apv_valuation(inputs)

print(f"Unlevered Enterprise Value: ${apv_results['unlevered_enterprise_value']:,.0f}")
print(f"Present Value of Tax Shields: ${apv_results['pv_tax_shields']:,.0f}")
print(f"APV Enterprise Value: ${apv_results['apv_enterprise_value']:,.0f}")
```

### 3. Comparable Multiples Analysis
```python
# Add comparable multiples data to inputs
inputs.comparable_multiples = {
    "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
    "P/E": [18.5, 22.1, 20.8, 24.3]
}

multiples_results = calculator.run_comparable_multiples(inputs)

for multiple, data in multiples_results['implied_values'].items():
    print(f"{multiple}: ${data['mean']:,.0f} (${data['median']:,.0f})")
```

### 4. Scenario Analysis
```python
# Add scenario data to inputs
inputs.scenarios = {
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
    }
}

scenario_results = calculator.run_scenario_analysis(inputs)

for scenario, data in scenario_results['scenarios'].items():
    print(f"{scenario}: ${data['enterprise_value']:,.0f}")
```

### 5. Monte Carlo Simulation
```python
# Add Monte Carlo specifications to inputs
inputs.monte_carlo_specs = {
    "ebit_margin": {
        "distribution": "normal",
        "params": { "mean": 0.18, "std": 0.02 }
    },
    "weighted_average_cost_of_capital": {
        "distribution": "normal",
        "params": { "mean": 0.095, "std": 0.01 }
    }
}

mc_results = calculator.run_monte_carlo_simulation(inputs, runs=1000)

print(f"Mean Enterprise Value: ${mc_results['enterprise_value']['mean']:,.0f}")
print(f"95% Confidence Interval: ${mc_results['enterprise_value']['p5']:,.0f} - ${mc_results['enterprise_value']['p95']:,.0f}")
```

### 6. Sensitivity Analysis
```python
# Add sensitivity analysis data to inputs
inputs.sensitivity_analysis = {
    "wacc_range": [0.075, 0.085, 0.095, 0.105, 0.115],
    "ebit_margin_range": [0.14, 0.16, 0.18, 0.20, 0.22]
}

sensitivity_results = calculator.run_sensitivity_analysis(inputs)

print("WACC Sensitivity:")
for wacc, value in sensitivity_results['wacc_sensitivity'].items():
    print(f"  {wacc:.1%}: ${value:,.0f}")
```

## 📈 Financial Calculations

### DCF Valuation Process
1. **Revenue Projections**: Multi-year revenue forecasts
2. **EBIT Calculation**: Revenue × EBIT margin
3. **NOPAT**: EBIT × (1 - tax rate)
4. **Free Cash Flow**: NOPAT + Depreciation - CapEx - NWC changes
5. **Terminal Value**: Gordon Growth Model
6. **Present Value**: Discount FCF and terminal value
7. **Enterprise Value**: Sum of present values
8. **Equity Value**: Enterprise value - net debt
9. **Share Price**: Equity value ÷ shares outstanding

### APV Method
1. **Unlevered FCF**: Same as DCF but without financing effects
2. **Unlevered Value**: Discount unlevered FCF at unlevered cost of equity
3. **Tax Shields**: Present value of interest tax shields
4. **APV**: Unlevered value + tax shields - net debt

### WACC Calculation
- **Target Capital Structure**: Uses target debt ratio to avoid circular dependency
- **Cost of Equity**: CAPM with Hamada equation for levered beta
- **Cost of Debt**: After-tax cost of debt
- **WACC**: Weighted average of cost of equity and cost of debt

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest test_finance_calculator.py -v
```

The test suite covers:
- DCF valuation calculations
- APV valuation calculations
- Comparable multiples analysis
- Scenario analysis
- Sensitivity analysis
- Monte Carlo simulation
- Input validation and error handling
- JSON integration

## 📋 Dependencies

- **NumPy**: Numerical computations and array operations
- **Pandas**: Data manipulation and analysis

Install with:
```bash
pip install numpy pandas
```

## 🎯 Key Financial Metrics

- **Enterprise Value**: Total value of the business
- **Equity Value**: Value available to shareholders
- **Terminal Value**: Value beyond projection period
- **WACC**: Weighted average cost of capital
- **Free Cash Flow**: Cash available to all investors
- **Net Debt**: Total debt minus cash and cash equivalents

## 🔍 Validation and Error Handling

The system includes comprehensive validation:
- **Input Validation**: Checks for required fields and data types
- **Financial Validation**: Validates terminal growth < WACC, positive values
- **Error Handling**: Graceful handling of calculation errors
- **Warning Suppression**: Clean output without calculation warnings

## 📝 Notes

- All monetary values are in millions of dollars
- Percentages are expressed as decimals (e.g., 0.20 for 20%)
- The debt schedule maps year indices to debt amounts
- Monte Carlo simulation uses 1,000 runs by default (configurable)
- All methods are mathematically verified and tested

## 🤝 Contributing

This finance calculator is designed to be modular and extensible. Key areas for enhancement:
- Additional valuation methods (LBO, sum-of-parts)
- More sophisticated sensitivity analysis (two-way, tornado charts)
- Integration with financial data providers
- Web interface for easier input
- Export capabilities (Excel, PDF reports)
- Additional Monte Carlo distributions
- Real-time market data integration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions, issues, or contributions, please open an issue on the project repository. 