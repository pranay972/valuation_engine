# Finance Core - Financial Valuation Engine

This module provides the core financial calculation engine for the Financial Valuation Application.

## Core Components

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

## Analysis Types

1. **DCF Valuation (WACC)** - Standard discounted cash flow using weighted average cost of capital
2. **APV Valuation** - Adjusted Present Value method separating unlevered value from financing effects
3. **Comparable Multiples** - Relative valuation using peer company ratios
4. **Scenario Analysis** - Multiple scenarios with different parameter combinations
5. **Sensitivity Analysis** - Parameter impact analysis on key valuation drivers
6. **Monte Carlo Simulation** - Risk analysis with probability distributions

## Usage

The finance core is integrated into the Flask backend through the `FinanceCoreService` class in `backend/app/services/finance_core_service.py`.

## Dependencies

- numpy
- pandas

These dependencies are managed by the main backend `pyproject.toml` file. 