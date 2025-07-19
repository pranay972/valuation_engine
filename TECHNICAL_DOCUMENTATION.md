# Technical Documentation: Financial Valuation Engine

**Author: Pranay Upreti**  
**Version: 2.0**  
**Last Updated: 2024**

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Modules](#core-modules)
3. [Data Structures](#data-structures)
4. [Valuation Calculations](#valuation-calculations)
5. [Financial Projections](#financial-projections)
6. [Monte Carlo Simulation](#monte-carlo-simulation)
7. [Comparable Multiples Analysis](#comparable-multiples-analysis)
8. [Scenario Analysis](#scenario-analysis)
9. [Sensitivity Analysis](#sensitivity-analysis)
10. [User Interface](#user-interface)
11. [Error Handling](#error-handling)
12. [Testing](#testing)
13. [Deployment](#deployment)
14. [Troubleshooting Guide](#troubleshooting-guide)

---

## Architecture Overview

### System Design
The application follows a modular architecture with clear separation of concerns:

```
app.py (UI Layer)
    ↓
Core Modules (Business Logic)
    ↓
Data Structures (Type Safety)
    ↓
Financial Calculations (Pure Functions)
```

### Key Design Principles
- **Modularity**: Each analysis type is self-contained
- **Type Safety**: Comprehensive type hints and validation
- **Error Handling**: Graceful degradation with informative messages
- **Reproducibility**: Fixed random seeds for Monte Carlo
- **Performance**: Optimized calculations and memory management

---

## Core Modules

### 1. `app.py` - Main Application
**Purpose**: Streamlit web interface and workflow orchestration

#### Key Functions:

##### `main()`
- **Purpose**: Entry point and main application loop
- **Responsibilities**:
  - Initialize session state
  - Render UI components
  - Handle user interactions
  - Coordinate between modules
  - Display results

##### `parse_series_input(input_text: str, name: str) -> list`
- **Purpose**: Parse comma-separated numeric inputs
- **Input**: String like "1000000,1100000,1200000"
- **Output**: List of floats
- **Error Handling**: Returns empty list on invalid input

##### `create_user_friendly_debt_input(revenue_input)`
- **Purpose**: Create interactive debt schedule input
- **Features**:
  - Dynamic year generation based on revenue length
  - Input validation
  - Visual feedback

##### `create_user_friendly_sensitivity_input()`
- **Purpose**: Create sensitivity analysis parameter inputs
- **Features**:
  - Range sliders for parameters
  - Step size configuration
  - Validation

##### `create_user_friendly_scenario_input()`
- **Purpose**: Create scenario analysis parameter inputs
- **Features**:
  - JSON input with validation
  - Circular reference detection
  - Parameter override system

##### `run_valuation_analyses(params, analyses, comps_file, mc_runs)`
- **Purpose**: Orchestrate all valuation analyses
- **Parameters**:
  - `params`: ValuationParams object
  - `analyses`: List of analysis types to run
  - `comps_file`: Optional comparable companies file
  - `mc_runs`: Number of Monte Carlo simulations
- **Returns**: Dictionary with all analysis results

##### `display_results(results, params)`
- **Purpose**: Render comprehensive results display
- **Features**:
  - Summary metrics
  - Detailed expandable sections
  - Interactive charts
  - Download functionality

### 2. `params.py` - Data Structures
**Purpose**: Define and validate all input parameters

#### `ValuationParams` Dataclass
```python
@dataclass
class ValuationParams:
    # Financial Projections
    revenue: List[float]
    ebit_margin: float
    capex: List[float]
    depreciation: List[float]
    nwc_changes: List[float]
    fcf_series: List[float]
    
    # Capital Structure
    share_count: float
    cost_of_debt: float
    debt_schedule: Dict[int, float]
    
    # Valuation Assumptions
    wacc: float
    tax_rate: float
    terminal_growth: float
    mid_year_convention: bool
    
    # Advanced Analysis
    mc_specs: Dict[str, Dict]
    scenarios: Dict[str, Dict]
    sensitivity_ranges: Dict[str, List[float]]
```

#### Validation Methods:
- **`validate_financial_projections()`**: Ensures positive revenues and valid margins
- **`validate_valuation_assumptions()`**: Checks WACC > growth rate
- **`validate_series_lengths()`**: Ensures all series have same length
- **`validate_debt_schedule()`**: Validates debt schedule format

### 3. `valuation.py` - Core DCF Calculations
**Purpose**: Implement WACC and APV DCF methodologies

#### `calc_dcf_series(params: ValuationParams) -> Tuple[float, float, Optional[float]]`
**WACC DCF Implementation**:

1. **Free Cash Flow Calculation**:
   ```python
   # For each year in projection period
   fcf = ebit * (1 - tax_rate) + depreciation - capex - nwc_changes
   ```

2. **Terminal Value Calculation**:
   ```python
   # Terminal value = FCF_n * (1 + g) / (WACC - g)
   terminal_fcf = fcf[-1] * (1 + terminal_growth)
   terminal_value = terminal_fcf / (wacc - terminal_growth)
   ```

3. **Discounting**:
   ```python
   # Discount each FCF to present value
   pv_fcf = fcf[i] / (1 + wacc)^(i+1)  # or i+0.5 for mid-year
   
   # Discount terminal value
   pv_terminal = terminal_value / (1 + wacc)^n
   ```

4. **Enterprise Value**:
   ```python
   enterprise_value = sum(pv_fcf) + pv_terminal
   ```

5. **Equity Value**:
   ```python
   equity_value = enterprise_value - net_debt
   price_per_share = equity_value / shares_outstanding
   ```

#### `calc_apv(params: ValuationParams) -> Tuple[float, float, Optional[float]]`
**APV Implementation**:

1. **Unlevered FCF**:
   ```python
   # Same as WACC but without tax shield effects
   unlevered_fcf = ebit * (1 - tax_rate) + depreciation - capex - nwc_changes
   ```

2. **Tax Shield Calculation**:
   ```python
   # Tax shield = interest * tax_rate
   tax_shield = debt * cost_of_debt * tax_rate
   ```

3. **Discounting**:
   ```python
   # Unlevered FCF discounted at unlevered cost of equity
   # Tax shields discounted at cost of debt
   ```

4. **APV Value**:
   ```python
   apv_value = unlevered_value + pv_tax_shields
   ```

### 4. `drivers.py` - Financial Projections
**Purpose**: Calculate financial metrics from drivers

#### `project_ebit(revenues: List[float], ebit_margin: float) -> List[float]`
```python
def project_ebit(revenues: List[float], ebit_margin: float) -> List[float]:
    """Calculate EBIT from revenue and margin."""
    return [revenue * ebit_margin for revenue in revenues]
```

#### `project_fcf(revenues, ebits, capex, depreciation, nwc_changes, tax_rate) -> List[float]`
```python
def project_fcf(revenues, ebits, capex, depreciation, nwc_changes, tax_rate):
    """Calculate Free Cash Flow from components."""
    fcfs = []
    for i in range(len(revenues)):
        # NOPAT = EBIT * (1 - tax_rate)
        nopat = ebits[i] * (1 - tax_rate)
        
        # FCF = NOPAT + Depreciation - CapEx - NWC Changes
        fcf = nopat + depreciation[i] - capex[i] - nwc_changes[i]
        fcfs.append(fcf)
    
    return fcfs
```

### 5. `montecarlo.py` - Uncertainty Analysis
**Purpose**: Monte Carlo simulation for parameter uncertainty

#### `run_monte_carlo(params: ValuationParams, runs: int = 2000) -> Dict[str, pd.DataFrame]`
**Implementation Steps**:

1. **Parameter Sampling**:
   ```python
   # For each parameter with distribution specification
   if param_spec["dist"] == "normal":
       samples = np.random.normal(
           loc=param_spec["params"]["loc"],
           scale=param_spec["params"]["scale"],
           size=runs
       )
   elif param_spec["dist"] == "uniform":
       samples = np.random.uniform(
           low=param_spec["params"]["low"],
           high=param_spec["params"]["high"],
           size=runs
       )
   ```

2. **Valuation Runs**:
   ```python
   # For each sample set
   for i in range(runs):
       # Create modified params with sampled values
       modified_params = copy.deepcopy(params)
       modified_params.wacc = wacc_samples[i]
       modified_params.terminal_growth = growth_samples[i]
       
       # Run valuation
       ev, eqv, pps = calc_dcf_series(modified_params)
       
       # Store results
       results.append({
           "Run": i,
           "Enterprise Value": ev,
           "Equity Value": eqv,
           "Price per Share": pps
       })
   ```

3. **Statistical Analysis**:
   ```python
   # Calculate distribution statistics
   mean_ev = np.mean(enterprise_values)
   median_ev = np.median(enterprise_values)
   std_ev = np.std(enterprise_values)
   percentiles = np.percentile(enterprise_values, [5, 25, 50, 75, 95])
   ```

### 6. `multiples.py` - Comparable Analysis
**Purpose**: Comparable company multiples analysis

#### `run_multiples_analysis(params: ValuationParams, comps: pd.DataFrame) -> pd.DataFrame`
**Implementation Steps**:

1. **Calculate Our Metrics**:
   ```python
   # EBITDA = EBIT + Depreciation
   ebitda = ebits[-1] + depreciation[-1]
   
   # Earnings = NOPAT = EBIT * (1 - tax_rate)
   earnings = ebits[-1] * (1 - tax_rate)
   
   # FCF = last year free cash flow
   fcf = fcfs[-1]
   
   # Revenue = last year revenue
   revenue = revenues[-1]
   ```

2. **Process Each Multiple**:
   ```python
   for col in comps.columns:
       if "/" not in col:
           continue
       
       # Parse multiple (e.g., "EV/EBITDA" -> ["EV", "EBITDA"])
       numerator, denominator = col.split("/")
       
       # Get our corresponding metric
       our_metric = metric_map[denominator]
       
       # Get peer multiples
       peer_multiples = comps[col].dropna()
       
       # Filter outliers (3 standard deviations)
       mean_mult = peer_multiples.mean()
       std_mult = peer_multiples.std()
       filtered_multiples = peer_multiples[
           (peer_multiples >= mean_mult - 3*std_mult) &
           (peer_multiples <= mean_mult + 3*std_mult)
       ]
       
       # Calculate implied values
       implied_evs = filtered_multiples * our_metric
   ```

3. **Summary Statistics**:
   ```python
   result = {
       "Multiple": col,
       "Mean Implied EV": implied_evs.mean(),
       "Median Implied EV": implied_evs.median(),
       "Std Dev Implied EV": implied_evs.std(),
       "Min Implied EV": implied_evs.min(),
       "Max Implied EV": implied_evs.max(),
       "Peer Count": len(filtered_multiples),
       "Our Metric": our_metric,
       "Mean Multiple": filtered_multiples.mean()
   }
   ```

### 7. `scenario.py` - Scenario Analysis
**Purpose**: "What-if" scenario testing

#### `run_scenarios(params: ValuationParams) -> pd.DataFrame`
**Implementation Steps**:

1. **Circular Reference Detection**:
   ```python
   def detect_circular_references(scenarios: Dict) -> List[str]:
       """Detect circular references in scenario definitions."""
       # Build dependency graph
       # Use topological sort to detect cycles
   ```

2. **Scenario Execution**:
   ```python
   for scenario_name, overrides in scenarios.items():
       # Create modified parameters
       modified_params = copy.deepcopy(params)
       
       # Apply overrides
       for param_name, value in overrides.items():
           setattr(modified_params, param_name, value)
       
       # Run valuation
       ev, eqv, pps = calc_dcf_series(modified_params)
       
       # Store results
       results.append({
           "Scenario": scenario_name,
           "Enterprise Value": ev,
           "Equity Value": eqv,
           "Price per Share": pps
       })
   ```

### 8. `sensitivity.py` - Sensitivity Analysis
**Purpose**: Parameter impact assessment

#### `run_sensitivity_analysis(params: ValuationParams) -> pd.DataFrame`
**Implementation Steps**:

1. **Parameter Range Generation**:
   ```python
   for param_name, range_values in sensitivity_ranges.items():
       for value in range_values:
           # Create modified parameters
           modified_params = copy.deepcopy(params)
           setattr(modified_params, param_name, value)
           
           # Run valuation
           ev, eqv, pps = calc_dcf_series(modified_params)
           
           # Store results
           results.append({
               "Parameter": param_name,
               "Value": value,
               "Enterprise Value": ev,
               "Equity Value": eqv,
               "Price per Share": pps
           })
   ```

---

## Financial Calculations Deep Dive

### DCF Methodology

#### 1. Free Cash Flow to Firm (FCFF)
```python
# FCFF = NOPAT + Depreciation - CapEx - Change in NWC
# Where NOPAT = EBIT * (1 - Tax Rate)

def calculate_fcff(ebit, tax_rate, depreciation, capex, nwc_change):
    nopat = ebit * (1 - tax_rate)
    fcff = nopat + depreciation - capex - nwc_change
    return fcff
```

#### 2. Terminal Value
```python
# Terminal Value = FCF_n * (1 + g) / (WACC - g)
# Where g = terminal growth rate

def calculate_terminal_value(last_fcf, terminal_growth, wacc):
    terminal_fcf = last_fcf * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    return terminal_value
```

#### 3. Discounting
```python
# Present Value = Future Value / (1 + discount_rate)^periods

def discount_cash_flows(fcfs, wacc, mid_year=False):
    pv_fcfs = []
    for i, fcf in enumerate(fcfs):
        if mid_year:
            period = i + 0.5  # Mid-year convention
        else:
            period = i + 1    # Year-end convention
        
        pv = fcf / ((1 + wacc) ** period)
        pv_fcfs.append(pv)
    
    return pv_fcfs
```

### WACC Calculation
```python
# WACC = (E/V * Re) + (D/V * Rd * (1 - T))
# Where:
# E = Market value of equity
# D = Market value of debt
# V = Total value (E + D)
# Re = Cost of equity
# Rd = Cost of debt
# T = Tax rate

def calculate_wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
    total_value = equity_value + debt_value
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return wacc
```

### APV Methodology
```python
# APV = Unlevered Value + Present Value of Tax Shields

def calculate_apv(unlevered_value, tax_shields, cost_of_debt):
    # Discount tax shields at cost of debt
    pv_tax_shields = sum([
        ts / ((1 + cost_of_debt) ** (i + 1))
        for i, ts in enumerate(tax_shields)
    ])
    
    apv = unlevered_value + pv_tax_shields
    return apv
```

---

## Error Handling Strategy

### 1. Input Validation
```python
def validate_financial_inputs(params: ValuationParams) -> List[str]:
    errors = []
    
    # Check for positive revenues
    if any(r <= 0 for r in params.revenue):
        errors.append("All revenues must be positive")
    
    # Check WACC > growth rate
    if params.wacc <= params.terminal_growth:
        errors.append("WACC must be greater than terminal growth rate")
    
    # Check series lengths
    if len(set([len(params.revenue), len(params.capex), 
                len(params.depreciation), len(params.nwc_changes)])) > 1:
        errors.append("All financial series must have the same length")
    
    return errors
```

### 2. Graceful Degradation
```python
def safe_calculation(func, *args, **kwargs):
    """Wrapper for safe calculation execution."""
    try:
        return func(*args, **kwargs)
    except ZeroDivisionError:
        return None, "Division by zero error"
    except ValueError as e:
        return None, f"Invalid input: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
```

### 3. User-Friendly Messages
```python
ERROR_MESSAGES = {
    "negative_valuation": "Valuation is negative. Check your assumptions.",
    "invalid_multiples": "No valid multiples found in comparable companies data.",
    "circular_reference": "Circular reference detected in scenario definitions.",
    "insufficient_data": "Insufficient data for analysis."
}
```

---

## Testing Strategy

### 1. Unit Tests
```python
def test_dcf_calculation():
    """Test basic DCF calculation."""
    params = ValuationParams(
        revenue=[1000000, 1100000],
        ebit_margin=0.20,
        capex=[100000, 110000],
        depreciation=[50000, 55000],
        nwc_changes=[20000, 22000],
        wacc=0.10,
        tax_rate=0.21,
        terminal_growth=0.02,
        # ... other required fields
    )
    
    ev, eqv, pps = calc_dcf_series(params)
    
    assert ev > 0, "Enterprise value should be positive"
    assert eqv > 0, "Equity value should be positive"
    assert pps > 0, "Price per share should be positive"
```

### 2. Integration Tests
```python
def test_full_valuation_workflow():
    """Test complete valuation workflow."""
    # Test with sample data
    # Verify all analysis types work together
    # Check output formats
```

### 3. Edge Case Testing
```python
def test_edge_cases():
    """Test edge cases and error conditions."""
    # Test with zero revenues
    # Test with negative margins
    # Test with extreme growth rates
    # Test with empty comparable companies
```

---

## Performance Optimization

### 1. Monte Carlo Optimization
```python
# Pre-generate random samples
def optimize_monte_carlo(runs: int, param_specs: Dict):
    """Pre-generate all random samples for efficiency."""
    samples = {}
    for param_name, spec in param_specs.items():
        if spec["dist"] == "normal":
            samples[param_name] = np.random.normal(
                loc=spec["params"]["loc"],
                scale=spec["params"]["scale"],
                size=runs
            )
    return samples
```

### 2. Memory Management
```python
# Use generators for large datasets
def process_large_dataset(data):
    """Process large datasets without loading everything into memory."""
    for chunk in pd.read_csv('large_file.csv', chunksize=1000):
        yield process_chunk(chunk)
```

### 3. Caching
```python
# Cache expensive calculations
@st.cache_data
def expensive_calculation(params):
    """Cache expensive calculations in Streamlit."""
    return complex_valuation_calculation(params)
```

---

## Deployment Considerations

### 1. Streamlit Cloud Deployment
```yaml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### 2. Environment Variables
```bash
# .env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 3. Dependencies Management
```txt
# requirements.txt - Production
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
plotly>=5.0.0
openpyxl>=3.0.0

# requirements-minimal.txt - Minimal deployment
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Negative Valuations
**Symptoms**: Enterprise value or equity value is negative
**Causes**:
- EBIT margin is 0 or negative
- Terminal growth >= WACC
- Negative free cash flows
**Solutions**:
- Check EBIT margin is positive
- Ensure terminal growth < WACC
- Review cash flow projections

#### 2. "No valid multiples found" Error
**Symptoms**: Multiples analysis fails
**Causes**:
- CSV file doesn't have proper column names
- Non-numeric data in multiple columns
- Missing required metrics
**Solutions**:
- Ensure column names follow "EV/EBITDA" format
- Check all multiple values are numeric
- Verify company has positive metrics

#### 3. Memory Issues
**Symptoms**: App crashes or becomes slow
**Causes**:
- Too many Monte Carlo runs
- Large comparable companies dataset
- Multiple scenarios with complex calculations
**Solutions**:
- Reduce Monte Carlo simulation count
- Filter comparable companies
- Limit number of scenarios

#### 4. Import Errors
**Symptoms**: Module import failures
**Causes**:
- Missing dependencies
- Python version incompatibility
- Virtual environment issues
**Solutions**:
- Install requirements: `pip install -r requirements.txt`
- Use Python 3.8+
- Activate virtual environment

#### 5. Type Checking Warnings
**Symptoms**: Red squiggles in IDE
**Causes**:
- Pandas type complexity
- IDE type inference limitations
**Solutions**:
- Add `# type: ignore` comments
- Use type ignore at function level
- Ignore warnings (they don't affect functionality)

### Debug Mode
```python
# Enable debug mode in app.py
DEBUG = True

if DEBUG:
    st.write("Debug info:", locals())
    st.write("Session state:", st.session_state)
```

### Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Entering function")
    # ... function logic
    logger.debug("Exiting function")
```

---

## Maintenance Checklist

### Daily Operations
- [ ] Monitor app performance
- [ ] Check for user-reported issues
- [ ] Verify sample data accuracy

### Weekly Tasks
- [ ] Review error logs
- [ ] Update comparable companies data
- [ ] Test all analysis types
- [ ] Backup user data (if applicable)

### Monthly Tasks
- [ ] Update dependencies
- [ ] Review and update documentation
- [ ] Performance optimization review
- [ ] Security audit

### Quarterly Tasks
- [ ] Major feature updates
- [ ] Code refactoring
- [ ] User feedback analysis
- [ ] Market data validation

---

## Future Enhancements

### Planned Features
1. **Real-time Market Data Integration**
2. **Advanced Risk Metrics**
3. **Portfolio Analysis**
4. **API Endpoints**
5. **Mobile Optimization**

### Technical Improvements
1. **Async Processing**
2. **Database Integration**
3. **Advanced Caching**
4. **Machine Learning Integration**
5. **Real-time Collaboration**

---

This documentation provides a comprehensive understanding of the financial valuation engine's architecture, implementation, and maintenance requirements. Use it as a reference for debugging, extending, and maintaining the application. 