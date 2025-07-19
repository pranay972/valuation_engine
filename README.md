# Financial Valuation Engine

A comprehensive, professional-grade financial valuation application built with Streamlit. This tool provides enterprise-level DCF valuation, Monte Carlo simulation, comparable multiples analysis, and scenario testing - all with an intuitive, finance-professional-friendly interface.

## Features

### **Core Valuation Methods**
- **WACC DCF**: Standard discounted cash flow using weighted average cost of capital
- **APV DCF**: Adjusted present value method with tax shield calculations
- **Mid-year vs Year-end conventions**: Flexible cash flow timing assumptions

### **Advanced Analysis**
- **Monte Carlo Simulation**: Uncertainty analysis with customizable probability distributions
- **Comparable Multiples**: Peer company analysis using industry-standard ratios
- **Scenario Analysis**: "What-if" testing with optimistic/pessimistic scenarios
- **Sensitivity Analysis**: Parameter impact assessment with interactive visualizations

### **Professional UI/UX**
- **User-friendly inputs**: Guided interfaces for debt schedules, sensitivity ranges, and scenarios
- **Real-time validation**: Comprehensive error checking and warnings
- **Interactive visualizations**: Charts, heatmaps, and distribution plots
- **Export capabilities**: Excel and CSV downloads with professional formatting

### **Financial Best Practices**
- **Consistent units**: All numbers in raw format (e.g., 1,000,000 for one million)
- **Circular reference detection**: Prevents infinite loops in scenario definitions
- **Terminal value warnings**: Alerts for unsustainable growth assumptions
- **Outlier filtering**: Robust statistical analysis in multiples comparisons

## Requirements

### **Python Version**
- Python 3.8 or higher

### **Dependencies**
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
plotly>=5.0.0
openpyxl>=3.0.0
```

## Installation

### **Option 1: Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd valuation

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### **Option 2: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### **Option 3: Minimal Installation**
```bash
# Install only essential dependencies
pip install -r requirements-minimal.txt

# Run the app
streamlit run app.py
```

## Quick Start Guide

### **1. Launch the App**
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

### **2. Select Analyses**
In the sidebar, choose which valuation methods to run:
- ✅ **WACC DCF** (recommended for most cases)
- ✅ **APV DCF** (for companies with significant debt)
- ✅ **Monte Carlo** (for uncertainty analysis)
- ✅ **Comparable Multiples** (for peer comparison)
- ✅ **Scenario Analysis** (for sensitivity testing)

### **3. Enter Financial Data**
Use the **Financial Projections** tab to input your data:

#### **Driver-Based Input (Recommended)**
- **Revenue Series**: Enter projected revenues (e.g., `100000000,110000000,120000000`)
- **EBIT Margin**: Expected operating margin as percentage
- **CapEx Series**: Capital expenditure projections
- **Depreciation Series**: Depreciation projections
- **NWC Changes**: Net working capital changes

#### **Direct FCF Input**
- **Free Cash Flow Series**: Direct FCF projections if you prefer

### **4. Set Valuation Assumptions**
- **WACC**: Weighted average cost of capital
- **Tax Rate**: Effective corporate tax rate
- **Terminal Growth**: Long-term growth rate
- **Mid-Year Convention**: Check if cash flows occur mid-year

### **5. Configure Advanced Analysis**
- **Monte Carlo**: Define probability distributions for key variables
- **Comparable Multiples**: Upload peer company CSV file
- **Scenarios**: Set optimistic/pessimistic parameter overrides
- **Sensitivity**: Define parameter ranges for testing

### **6. Run Valuation**
Click **"Run Valuation"** to execute all selected analyses.

## Sample Data

### **Sample Inputs**
Use `sample_inputs.txt` for quick testing:
```
# Revenue Series (comma-separated)
100000000,110000000,120000000,130000000,140000000

# EBIT Margin (%)
20

# Capital Expenditure Series
10000000,11000000,12000000,13000000,14000000

# Number of Shares Outstanding
100000000
```

### **Sample Comparable Companies**
Use `sample_comps.csv` for multiples analysis:
```csv
Company,EV,EBITDA,Revenue,EV/EBITDA,EV/Revenue,P/E
Peer_Company_1,1500000000,180000000,1200000000,8.33,1.25,16.67
```

## Configuration

### **Input Format Standards**
- **All numbers are raw**: Enter 1,000,000 for one million (not 1)
- **Comma-separated series**: Use commas to separate year-by-year values
- **Percentages as decimals**: 20% = 0.20, 5% = 0.05

### **Debt Schedule**
- **Year 0**: Current debt (today)
- **Year 1+**: Projected debt at end of each year
- **Multi-year schedule**: Enter debt for each forecast year

### **Monte Carlo Specifications**
```json
{
  "wacc": {"dist": "normal", "params": {"loc": 0.10, "scale": 0.01}},
  "terminal_growth": {"dist": "uniform", "params": {"low": 0.01, "high": 0.03}}
}
```

### **Scenario Analysis**
```json
{
  "Optimistic": {"ebit_margin": 0.25, "terminal_growth": 0.03, "wacc": 0.09},
  "Pessimistic": {"ebit_margin": 0.15, "terminal_growth": 0.01, "wacc": 0.12}
}
```

## Understanding Results

### **DCF Valuation**
- **Enterprise Value**: Total value of the business
- **Equity Value**: Value available to shareholders
- **Price per Share**: Equity value divided by shares outstanding

### **Monte Carlo Results**
- **Distribution Statistics**: Mean, median, standard deviation
- **Confidence Intervals**: 5th, 25th, 50th, 75th, 95th percentiles
- **Visualizations**: Histograms showing value distributions

### **Comparable Multiples**
- **Implied Enterprise Values**: Based on peer company ratios
- **Multiple Statistics**: Mean, median, range across peers
- **Outlier Filtering**: Removes extreme values for robustness

### **Scenario Analysis**
- **Base Case**: Your current assumptions
- **Optimistic**: Better performance scenario
- **Pessimistic**: Worse performance scenario

## Important Notes

### **Terminal Value Warnings**
- **High Growth (>5%)**: May not be sustainable in perpetuity
- **Negative Growth (<-2%)**: Implies business shrinkage

### **Circular References**
- The app detects and warns about circular references in scenario definitions
- This prevents infinite loops in parameter calculations

### **Data Validation**
- **Revenue**: Must be positive
- **Series Lengths**: All financial series must have the same length
- **WACC vs Growth**: Terminal growth must be less than WACC

## Troubleshooting

### **Common Issues**

#### **"No valid multiples found"**
- Ensure your CSV file has columns with format `EV/EBITDA`, `P/E`, etc.
- Check that the CSV contains numeric data

#### **Negative valuations**
- Verify EBIT margin is properly set (not 0%)
- Check that revenue projections are positive
- Ensure terminal growth < WACC

#### **Import errors**
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

#### **Memory issues with large datasets**
- Reduce Monte Carlo simulation count
- Use smaller comparable company datasets

### **Performance Tips**
- **Monte Carlo**: Use 1,000-2,000 runs for quick testing, 5,000+ for production
- **Large datasets**: Consider filtering comparable companies
- **Multiple scenarios**: Limit to 3-5 scenarios for faster processing

## File Structure

```
valuation/
├── app.py                 # Main Streamlit application
├── valuation.py           # Core DCF calculation functions
├── drivers.py            # Financial projection helpers
├── montecarlo.py         # Monte Carlo simulation engine
├── multiples.py          # Comparable multiples analysis
├── scenario.py           # Scenario analysis functions
├── sensitivity.py        # Sensitivity analysis functions
├── params.py             # Data structures and validation
├── requirements.txt      # Full dependency list
├── requirements-minimal.txt  # Essential dependencies only
├── sample_inputs.txt     # Example input values
├── sample_comps.csv      # Example comparable companies
├── README.md            # This file
└── test/                # Unit tests
    └── test_basic.py    # Basic functionality tests
```

## Testing

Run the test suite to verify functionality:
```bash
pytest test/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the sample data files for examples
3. Open an issue on GitHub with detailed information

## Version History

### **v2.0 (Current)**
- ✅ Complete UI/UX redesign with guided inputs
- ✅ Consistent unit standardization (raw numbers)
- ✅ Enhanced error handling and validation
- ✅ Professional output formatting
- ✅ Comprehensive documentation

### **v1.0**
- Basic DCF functionality
- Simple Monte Carlo simulation
- Basic multiples analysis

---

**Author: Pranay Upreti**

**Built for finance professionals**
