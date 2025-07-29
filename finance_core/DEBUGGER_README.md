# Finance Calculator Debugger

A comprehensive step-by-step debugger for the finance calculator that validates inputs, detects errors, and provides detailed troubleshooting information.

## Overview

The `debug_valuation.py` script runs the finance calculator step by step and provides detailed information about:
- Input validation
- Data type checking
- Value range validation
- Calculation testing
- Error identification and troubleshooting

## Usage

```bash
python debug_valuation.py <input_file.json>
```

## What the Debugger Does

### Step 1: JSON Structure Validation
- Validates that the JSON file has the required top-level structure
- Checks for presence of `financial_inputs` section
- Reports missing or malformed JSON structure

### Step 2: Financial Inputs Validation
- Checks for all required financial fields
- Supports both old and new field names (e.g., `wacc` vs `weighted_average_cost_of_capital`)
- Reports missing required fields
- Identifies empty lists

### Step 3: Data Type Validation
- Validates that all fields have the correct data types
- Checks for common type errors (strings instead of numbers, etc.)
- Reports specific type mismatches with expected vs actual types

### Step 4: Data Value Validation
- Validates that values are within reasonable ranges
- Checks for negative values in financial projections
- Reports value range warnings

### Step 5: List Length Validation
- Ensures all financial projection lists have the same length
- Reports inconsistent list lengths that would cause calculation errors

### Step 6: FinancialInputs Creation Test
- Tests the creation of the FinancialInputs object
- Reports any errors in the conversion process

### Step 7: ValuationParameters Conversion Test
- Tests the conversion to ValuationParameters
- Reports any errors in the parameter conversion

### Step 8: DCF Calculation Test
- Tests the DCF (Discounted Cash Flow) calculation
- Reports success/failure and enterprise value if successful

### Step 9: APV Calculation Test
- Tests the APV (Adjusted Present Value) calculation
- Reports success/failure and enterprise value if successful

### Step 10: Comparable Multiples Test
- Tests comparable multiples analysis (if data provided)
- Reports success/failure

### Step 11: Scenario Analysis Test
- Tests scenario analysis (if scenarios provided)
- Reports success/failure and provides context for common errors

### Step 12: Sensitivity Analysis Test
- Tests sensitivity analysis (if sensitivity data provided)
- Reports success/failure and provides context for common errors

### Step 13: Monte Carlo Simulation Test
- Tests Monte Carlo simulation (if specifications provided)
- Uses reduced runs (100) for faster testing

### Step 14: Comprehensive Valuation Test
- Tests the full comprehensive valuation
- Reports overall success/failure

## Output

The debugger provides:

1. **Real-time console output** with step-by-step progress
2. **Detailed error messages** with context and troubleshooting hints
3. **Warning messages** for potential issues
4. **Success confirmations** for each step
5. **Summary report** at the end
6. **JSON debug report file** saved as `<input_file>_debug_report.json`

## Error Types Detected

### Critical Errors (❌)
- Missing required fields
- Data type mismatches
- Inconsistent list lengths
- Calculation failures
- File not found
- Invalid JSON

### Warnings (⚠️)
- Value range issues
- Negative values in projections
- Empty lists
- Missing optional data

### Information (ℹ️)
- Step progress
- Field name usage (old vs new)
- Successful validations

## Example Output

```
🔍 Finance Calculator Debugger
==================================================
✅ Successfully loaded input file: sample_input.json
ℹ️  Step 1: Validating JSON structure...
✅ JSON structure is valid
ℹ️  Step 2: Validating financial inputs...
✅ All required financial fields present
ℹ️  Using new field name: terminal_growth_rate (instead of terminal_growth)
ℹ️  Using new field name: weighted_average_cost_of_capital (instead of wacc)
ℹ️  Step 3: Validating data types...
✅ All data types are correct
ℹ️  Step 4: Validating data values...
✅ Data value validation completed
ℹ️  Step 5: Validating list lengths...
✅ All lists have consistent length: 5
ℹ️  Step 6: Testing FinancialInputs creation...
✅ FinancialInputs object created successfully
ℹ️  Step 7: Testing ValuationParameters conversion...
✅ ValuationParameters object created successfully
ℹ️  Step 8: Testing DCF calculation...
✅ DCF calculation successful - EV: $1,454
ℹ️  Step 9: Testing APV calculation...
✅ APV calculation successful - EV: $1,030
ℹ️  Step 10: Testing comparable multiples analysis...
✅ Comparable multiples analysis successful
ℹ️  Step 11: Testing scenario analysis...
❌ Scenario analysis failed: Unknown error
ℹ️  Step 12: Testing sensitivity analysis...
❌ Sensitivity analysis failed: Unknown error
ℹ️  Step 13: Testing Monte Carlo simulation...
✅ Monte Carlo simulation successful
ℹ️  Step 14: Testing comprehensive valuation...
✅ Comprehensive valuation successful

==================================================
📊 DEBUG SUMMARY
==================================================
Total Errors: 2
Total Warnings: 0
Total Info Messages: 16

❌ Found 2 error(s) that need to be fixed.

📄 Debug report saved to: sample_input_debug_report.json
```

## Common Issues and Solutions

### 1. Missing Required Fields
**Error**: `Missing required financial fields: ['terminal_growth', 'wacc']`
**Solution**: Add the missing fields or use new field names (`terminal_growth_rate`, `weighted_average_cost_of_capital`)

### 2. Data Type Errors
**Error**: `ebit_margin: expected (<class 'int'>, <class 'float'>), got str`
**Solution**: Change string values to numbers (e.g., `"0.15"` → `0.15`)

### 3. Inconsistent List Lengths
**Error**: `Inconsistent list lengths: {'revenue': 3, 'capex': 5, 'depreciation': 5}`
**Solution**: Ensure all projection lists have the same length

### 4. Scenario Analysis Failures
**Error**: `Scenario analysis failed: Invalid parameter 'terminal_growth'`
**Solution**: Update scenario parameters to use new field names

### 5. Sensitivity Analysis Failures
**Error**: `Sensitivity analysis failed: Invalid parameter 'wacc'`
**Solution**: Update sensitivity parameters to use new field names

## Debug Report File

The debugger saves a detailed JSON report with:
- Summary statistics (total errors, warnings, info messages)
- Complete list of all errors with details
- Complete list of all warnings
- Complete list of all informational messages

This report can be used for:
- Automated testing
- Error tracking
- Documentation
- Integration with other tools

## Integration

The debugger can be integrated into:
- CI/CD pipelines for automated testing
- Development workflows for validation
- Documentation generation
- Error reporting systems

## Troubleshooting

If the debugger itself fails:
1. Check that all required Python modules are installed
2. Verify the input file path is correct
3. Ensure the input file is valid JSON
4. Check file permissions

The debugger is designed to be robust and provide helpful error messages even when the input data is severely malformed. 