# Financial Valuation Calculator

A professional-grade financial valuation calculator with comprehensive analysis capabilities, implementing industry-standard methodologies for DCF, APV, comparable multiples, scenario analysis, sensitivity analysis, and Monte Carlo simulation.

## 🚀 Features

### Core Valuation Methods
- **DCF (Discounted Cash Flow)** - Standard WACC methodology
- **APV (Adjusted Present Value)** - Tax shield analysis
- **Comparable Multiples** - Relative valuation using peer companies
- **Scenario Analysis** - Multiple scenarios with different assumptions
- **Sensitivity Analysis** - Parameter impact analysis
- **Monte Carlo Simulation** - Risk analysis with probability distributions

### Key Capabilities
- ✅ Professional-grade calculations
- ✅ Comprehensive input validation
- ✅ Robust error handling
- ✅ CSV to CSV workflow pipeline
- ✅ JSON input/output support
- ✅ Detailed reporting and analysis
- ✅ Unit test coverage (50+ tests)
- ✅ Debugging tools

## 📋 Requirements

- Python 3.8+
- pandas
- numpy
- scipy

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance_core
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Quick Start

1. **Prepare your input data** in CSV format (see `valuation_input.csv` for template)
2. **Run the valuation**
   ```bash
   python main.py valuation_input.csv
   ```
3. **Review results** in the generated CSV report

### CSV to JSON Conversion

If you need to convert CSV input to JSON format for programmatic use:

```bash
# Convert CSV to JSON
python csv_to_json_converter.py valuation_input.csv

# Convert with custom output filename
python csv_to_json_converter.py valuation_input.csv my_valuation_input.json
```

### Programmatic Usage

```python
from finance_calculator import CleanModularFinanceCalculator, create_financial_inputs_from_json

# Create calculator instance
calculator = CleanModularFinanceCalculator()

# Load inputs from JSON
with open('sample_input.json', 'r') as f:
    input_data = json.load(f)
inputs = create_financial_inputs_from_json(input_data)

# Run comprehensive valuation
results = calculator.run_comprehensive_valuation(
    inputs=inputs,
    company_name="Example Corp",
    valuation_date="2024-01-01"
)

# Access results
dcf_value = results['dcf_valuation']['enterprise_value']
apv_value = results['apv_valuation']['enterprise_value']
```

### Individual Methods

```python
# DCF Valuation
dcf_result = calculator.run_dcf_valuation(inputs)

# APV Valuation
apv_result = calculator.run_apv_valuation(inputs)

# Comparable Multiples
multiples_result = calculator.run_comparable_multiples(inputs)

# Scenario Analysis
scenario_result = calculator.run_scenario_analysis(inputs)

# Sensitivity Analysis
sensitivity_result = calculator.run_sensitivity_analysis(inputs)

# Monte Carlo Simulation
monte_carlo_result = calculator.run_monte_carlo_simulation(inputs, runs=1000)
```

## 📊 Input Data Structure

### Required Fields
- `revenue` - Revenue projections (list of floats)
- `ebit_margin` - EBIT margin percentage (float)
- `capex` - Capital expenditure projections (list of floats)
- `depreciation` - Depreciation projections (list of floats)
- `nwc_changes` - Net working capital changes (list of floats)
- `tax_rate` - Corporate tax rate (float)
- `terminal_growth` - Terminal growth rate (float)
- `wacc` - Weighted average cost of capital (float)
- `share_count` - Number of shares outstanding (float)
- `cost_of_debt` - Cost of debt (float)

### Optional Fields
- `cash_balance` - Cash and cash equivalents (float)
- `debt_schedule` - Debt repayment schedule (dict)
- `comparable_multiples` - Peer company multiples (dict)
- `scenarios` - Scenario definitions (dict)
- `sensitivity_analysis` - Sensitivity ranges (dict)
- `monte_carlo_specs` - Monte Carlo specifications (dict)

### Example Input Structure

```json
{
  "company_name": "Example Corp",
  "valuation_date": "2024-01-01",
  "financial_inputs": {
    "revenue": [1000, 1100, 1200, 1300, 1400],
    "ebit_margin": 0.15,
    "tax_rate": 0.25,
    "capex": [200, 220, 240, 260, 280],
    "depreciation": [150, 160, 170, 180, 190],
    "nwc_changes": [50, 55, 60, 65, 70],
    "wacc": 0.10,
    "terminal_growth": 0.03,
    "share_count": 100,
    "cost_of_debt": 0.06,
    "cash_balance": 500
  },
  "comparable_multiples": {
    "EV/EBITDA": [12.5, 14.2, 13.8, 15.1],
    "P/E": [18.5, 22.1, 20.8, 24.3]
  }
}
```

## 📈 Output Structure

### DCF Results
```python
{
  "enterprise_value": 5000.0,
  "equity_value": 4500.0,
  "price_per_share": 45.0,
  "free_cash_flows_after_tax_fcff": [150.0, 165.0, 180.0],
  "terminal_value": 3000.0,
  "present_value_of_terminal": 2000.0,
  "wacc": 0.10,
  "terminal_growth": 0.03
}
```

### Comprehensive Results
```python
{
  "valuation_summary": {
    "company": "Example Corp",
    "valuation_date": "2024-01-01",
    "share_count": 100
  },
  "dcf_valuation": { /* DCF results */ },
  "apv_valuation": { /* APV results */ },
  "comparable_valuation": { /* Multiples results */ },
  "scenarios": { /* Scenario results */ },
  "sensitivity_analysis": { /* Sensitivity results */ },
  "monte_carlo_simulation": { /* Monte Carlo results */ }
}
```

## 🧪 Testing

### Run All Tests
```bash
python -m unittest test_finance_calculator test_main -v
```

### Run Specific Test Files
```bash
# Test financial calculator
python -m unittest test_finance_calculator -v

# Test main workflow
python -m unittest test_main -v

# Test CSV to JSON converter
python -m unittest test_csv_to_json_converter -v
```

### Test Coverage
- ✅ 35 tests for financial calculator functionality
- ✅ 15 tests for main workflow functionality
- ✅ 8 tests for CSV to JSON converter functionality
- ✅ Comprehensive edge case coverage
- ✅ Error handling validation
- ✅ Input validation testing

## 🐛 Debugging

### Debug Mode
```bash
python debug_valuation.py sample_input.json
```

The debugger provides:
- Step-by-step validation
- Detailed error messages
- Input validation checks
- Component testing
- Comprehensive debug report

## 📁 Project Structure

```
finance_core/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main.py                      # CSV workflow pipeline
├── csv_to_json_converter.py     # CSV to JSON conversion utility
├── finance_calculator.py        # Main calculator class
├── params.py                    # Parameter structures
├── dcf.py                       # DCF calculations
├── wacc.py                      # WACC calculations
├── multiples.py                 # Comparable multiples
├── scenario.py                  # Scenario analysis
├── sensitivity.py               # Sensitivity analysis
├── monte_carlo.py              # Monte Carlo simulation
├── drivers.py                   # Financial projections
├── error_messages.py           # Error handling
├── input_validator.py          # Input validation
├── debug_valuation.py          # Debugging tools
├── test_finance_calculator.py  # Calculator tests
├── test_main.py                # Workflow tests
├── test_csv_to_json_converter.py # CSV converter tests
├── sample_input.json           # Example input
├── sample_input_valuation_results.json  # Example output
├── valuation_input.csv         # CSV input template
└── TechCorp_Inc._Valuation_Report.csv  # Example report
```

## 🔧 Configuration

### CSV Input Format
The CSV input file should have columns:
- `Field` - Parameter name
- `Value` - Parameter value
- `Description` - Parameter description

### Key Parameters
- **Revenue projections** - 5-year revenue forecasts
- **EBIT margin** - Operating margin percentage
- **WACC** - Weighted average cost of capital
- **Terminal growth** - Long-term growth rate
- **Comparable multiples** - Peer company ratios
- **Scenario parameters** - Optimistic/pessimistic cases
- **Monte Carlo specs** - Distribution parameters

## 📊 Example Reports

The system generates comprehensive CSV reports including:
- Company information
- Key financial metrics
- Financial projections
- Valuation results (DCF, APV, Multiples)
- WACC breakdown
- Scenario analysis
- Monte Carlo simulation results
- Sensitivity analysis tables

## 🚨 Error Handling

The system provides robust error handling:
- Input validation with detailed error messages
- Graceful handling of missing data
- Comprehensive error reporting
- Debug mode for troubleshooting

### Common Error Types
- `FinanceCoreError` - Calculation errors
- `ValueError` - Invalid input values
- `FileNotFoundError` - Missing input files
- `JSONDecodeError` - Invalid JSON format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:
1. Check the debug output
2. Review the test cases
3. Examine the example files
4. Create an issue with detailed information

## 🔄 Version History

- **v1.0.0** - Initial release with comprehensive valuation capabilities
- **v1.1.0** - Added Monte Carlo simulation and enhanced error handling
- **v1.2.0** - Improved CSV workflow and reporting
- **v1.3.0** - Added comprehensive test suite and debugging tools

---

**Note**: This calculator implements industry-standard financial valuation methodologies. Results should be used as part of a comprehensive analysis and not as the sole basis for investment decisions. 