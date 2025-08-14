# Finance Core - Financial Valuation Engine

Core financial calculation engine providing 6 professional analysis methods.

## 🎯 Core Components

### Main Calculator
- **`finance_calculator.py`** - Main calculator class with all analysis methods
- **`params.py`** - Valuation parameters and data structures
- **`drivers.py`** - Financial projection and calculation drivers

### Analysis Modules
- **`dcf.py`** - Discounted Cash Flow (WACC) and APV calculations
- **`wacc.py`** - Weighted Average Cost of Capital calculations
- **`multiples.py`** - Comparable company multiples analysis
- **`scenario.py`** - Scenario analysis with multiple parameter sets
- **`sensitivity.py`** - Sensitivity analysis for key parameters
- **`monte_carlo.py`** - Monte Carlo simulation with probability distributions

### Support
- **`error_messages.py`** - Error handling and validation utilities

## 📊 Analysis Types

1. **DCF (WACC)** - Standard discounted cash flow using weighted average cost of capital
2. **APV** - Adjusted Present Value method separating unlevered value from financing effects
3. **Comparable Multiples** - Relative valuation using peer company ratios
4. **Scenario Analysis** - Multiple scenarios with different parameter combinations
5. **Sensitivity Analysis** - Parameter impact analysis on key valuation drivers
6. **Monte Carlo** - Risk analysis with probability distributions

## 🔗 Integration

The finance core is integrated into the Flask backend through the `FinanceCoreService` class in `backend/app/services/finance_core_service.py`.

## 📋 Dependencies

- **numpy** - Numerical computations
- **pandas** - Data manipulation

Dependencies are managed by the main backend `pyproject.toml` file. 