#!/usr/bin/env python3
"""
Finance Calculator Debugger

A comprehensive debugger that runs the finance calculator step by step,
validates inputs, and provides detailed error information and troubleshooting.
"""

import json
import sys
import traceback
from typing import Dict, Any, List, Optional
from dataclasses import fields
import pandas as pd

# Import the finance calculator components
from finance_calculator import CleanModularFinanceCalculator, create_financial_inputs_from_json, FinancialInputs
from params import ValuationParameters
from drivers import project_ebit_series, project_free_cash_flow
from wacc import calculate_weighted_average_cost_of_capital, calculate_unlevered_cost_of_equity
from dcf import calculate_dcf_valuation_wacc, calculate_adjusted_present_value
from multiples import run_multiples_analysis
from scenario import run_scenarios
from sensitivity import run_sensitivity_analysis
from monte_carlo import run_monte_carlo

class ValuationDebugger:
    """Debugger for the finance calculator with step-by-step validation."""
    
    def __init__(self):
        self.calculator = CleanModularFinanceCalculator()
        self.debug_info = []
        self.errors = []
        self.warnings = []
        
    def log_info(self, message: str):
        """Log informational message."""
        self.debug_info.append(f"ℹ️  {message}")
        print(f"ℹ️  {message}")
        
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error message with optional exception details."""
        error_msg = f"❌ {message}"
        if exception:
            error_msg += f"\n   Exception: {type(exception).__name__}: {str(exception)}"
            error_msg += f"\n   Traceback: {traceback.format_exc()}"
        self.errors.append(error_msg)
        print(error_msg)
        
    def log_warning(self, message: str):
        """Log warning message."""
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  {message}")
        
    def log_success(self, message: str):
        """Log success message."""
        print(f"✅ {message}")
        
    def validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """Validate the basic JSON structure."""
        self.log_info("Step 1: Validating JSON structure...")
        
        required_keys = ["financial_inputs"]
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            self.log_error(f"Missing required top-level keys: {missing_keys}")
            return False
            
        self.log_success("JSON structure is valid")
        return True
        
    def validate_financial_inputs(self, financial_data: Dict[str, Any]) -> List[str]:
        """Validate financial inputs and return list of missing fields."""
        self.log_info("Step 2: Validating financial inputs...")
        
        required_fields = [
            "revenue", "ebit_margin", "tax_rate", "terminal_growth", 
            "wacc", "share_count", "cost_of_debt"
        ]
        
        # Also check for new field names
        new_field_mappings = {
            "terminal_growth": "terminal_growth_rate",
            "wacc": "weighted_average_cost_of_capital"
        }
        
        missing_fields = []
        for field in required_fields:
            # Check if field exists or if new field name exists
            field_exists = field in financial_data
            new_field_exists = field in new_field_mappings and new_field_mappings[field] in financial_data
            
            if not field_exists and not new_field_exists:
                missing_fields.append(field)
            elif field_exists and financial_data[field] is None:
                missing_fields.append(field)
            elif new_field_exists and financial_data[new_field_mappings[field]] is None:
                missing_fields.append(field)
                
        if missing_fields:
            self.log_error(f"Missing required financial fields: {missing_fields}")
        else:
            self.log_success("All required financial fields present")
            
        # Log which field names are being used
        for field in ["terminal_growth", "wacc"]:
            if field in financial_data:
                self.log_info(f"Using old field name: {field}")
            elif field in new_field_mappings and new_field_mappings[field] in financial_data:
                self.log_info(f"Using new field name: {new_field_mappings[field]} (instead of {field})")
            
        # Check for empty lists
        list_fields = ["revenue", "capex", "depreciation", "nwc_changes"]
        for field in list_fields:
            if field in financial_data and isinstance(financial_data[field], list):
                if len(financial_data[field]) == 0:
                    self.log_warning(f"Empty list for field: {field}")
                    
        return missing_fields
        
    def validate_data_types(self, financial_data: Dict[str, Any]) -> bool:
        """Validate data types of financial inputs."""
        self.log_info("Step 3: Validating data types...")
        
        type_checks = [
            ("revenue", list),
            ("ebit_margin", (int, float)),
            ("tax_rate", (int, float)),
            ("terminal_growth", (int, float)),
            ("wacc", (int, float)),
            ("share_count", (int, float)),
            ("cost_of_debt", (int, float))
        ]
        
        # Add checks for new field names
        new_type_checks = [
            ("terminal_growth_rate", (int, float)),
            ("weighted_average_cost_of_capital", (int, float))
        ]
        
        type_errors = []
        for field, expected_type in type_checks:
            if field in financial_data:
                if not isinstance(financial_data[field], expected_type):
                    expected_name = expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)
                    actual_name = type(financial_data[field]).__name__
                    type_errors.append(f"{field}: expected {expected_name}, got {actual_name}")
                    
        # Check new field names
        for field, expected_type in new_type_checks:
            if field in financial_data:
                if not isinstance(financial_data[field], expected_type):
                    expected_name = expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)
                    actual_name = type(financial_data[field]).__name__
                    type_errors.append(f"{field}: expected {expected_name}, got {actual_name}")
                    
        if type_errors:
            self.log_error(f"Data type errors: {type_errors}")
            return False
            
        self.log_success("All data types are correct")
        return True
        
    def validate_data_values(self, financial_data: Dict[str, Any]) -> bool:
        """Validate that data values are within reasonable ranges."""
        self.log_info("Step 4: Validating data values...")
        
        value_checks = [
            ("ebit_margin", 0.0, 1.0, "EBIT margin should be between 0 and 1"),
            ("tax_rate", 0.0, 1.0, "Tax rate should be between 0 and 1"),
            ("terminal_growth", -0.1, 0.2, "Terminal growth should be between -10% and 20%"),
            ("wacc", 0.0, 1.0, "WACC should be between 0 and 1"),
            ("share_count", 0.0, float('inf'), "Share count should be positive"),
            ("cost_of_debt", 0.0, 1.0, "Cost of debt should be between 0 and 1")
        ]
        
        value_errors = []
        for field, min_val, max_val, message in value_checks:
            if field in financial_data:
                value = financial_data[field]
                if not (min_val <= value <= max_val):
                    value_errors.append(f"{field}: {value} - {message}")
                    
        if value_errors:
            self.log_warning(f"Value range warnings: {value_errors}")
            
        # Check for negative values in lists
        list_fields = ["revenue", "capex", "depreciation", "nwc_changes"]
        for field in list_fields:
            if field in financial_data and isinstance(financial_data[field], list):
                negative_values = [val for val in financial_data[field] if val < 0]
                if negative_values:
                    self.log_warning(f"Negative values found in {field}: {negative_values}")
                    
        self.log_success("Data value validation completed")
        return True
        
    def validate_list_lengths(self, financial_data: Dict[str, Any]) -> bool:
        """Validate that all lists have the same length."""
        self.log_info("Step 5: Validating list lengths...")
        
        list_fields = ["revenue", "capex", "depreciation", "nwc_changes"]
        list_lengths = {}
        
        for field in list_fields:
            if field in financial_data and isinstance(financial_data[field], list):
                list_lengths[field] = len(financial_data[field])
                
        if len(set(list_lengths.values())) > 1:
            self.log_error(f"Inconsistent list lengths: {list_lengths}")
            return False
            
        if list_lengths:
            self.log_success(f"All lists have consistent length: {list(list_lengths.values())[0]}")
            
        return True
        
    def test_financial_inputs_creation(self, data: Dict[str, Any]) -> Optional[FinancialInputs]:
        """Test creation of FinancialInputs object."""
        self.log_info("Step 6: Testing FinancialInputs creation...")
        
        try:
            inputs = create_financial_inputs_from_json(data)
            self.log_success("FinancialInputs object created successfully")
            return inputs
        except Exception as e:
            self.log_error("Failed to create FinancialInputs object", e)
            return None
            
    def test_valuation_parameters_conversion(self, inputs: FinancialInputs) -> Optional[ValuationParameters]:
        """Test conversion to ValuationParameters."""
        self.log_info("Step 7: Testing ValuationParameters conversion...")
        
        try:
            params = self.calculator._convert_to_valuation_params(inputs)
            self.log_success("ValuationParameters object created successfully")
            return params
        except Exception as e:
            self.log_error("Failed to create ValuationParameters object", e)
            return None
            
    def test_dcf_calculation(self, inputs: FinancialInputs) -> bool:
        """Test DCF calculation."""
        self.log_info("Step 8: Testing DCF calculation...")
        
        try:
            result = self.calculator.run_dcf_valuation(inputs)
            if "error" not in result:
                self.log_success(f"DCF calculation successful - EV: ${result.get('enterprise_value', 0):,.0f}")
                return True
            else:
                self.log_error(f"DCF calculation failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            self.log_error("DCF calculation failed with exception", e)
            return False
            
    def test_apv_calculation(self, inputs: FinancialInputs) -> bool:
        """Test APV calculation."""
        self.log_info("Step 9: Testing APV calculation...")
        
        try:
            result = self.calculator.run_apv_valuation(inputs)
            if "error" not in result:
                self.log_success(f"APV calculation successful - EV: ${result.get('enterprise_value', 0):,.0f}")
                return True
            else:
                self.log_error(f"APV calculation failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            self.log_error("APV calculation failed with exception", e)
            return False
            
    def test_comparable_multiples(self, inputs: FinancialInputs) -> bool:
        """Test comparable multiples analysis."""
        self.log_info("Step 10: Testing comparable multiples analysis...")
        
        if not inputs.comparable_multiples:
            self.log_warning("No comparable multiples data provided - skipping test")
            return True
            
        try:
            result = self.calculator.run_comparable_multiples(inputs)
            if "error" not in result:
                self.log_success("Comparable multiples analysis successful")
                return True
            else:
                self.log_error(f"Comparable multiples analysis failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            self.log_error("Comparable multiples analysis failed with exception", e)
            return False
            
    def test_scenario_analysis(self, inputs: FinancialInputs) -> bool:
        """Test scenario analysis."""
        self.log_info("Step 11: Testing scenario analysis...")
        
        if not inputs.scenarios:
            self.log_warning("No scenario data provided - skipping test")
            return True
            
        try:
            result = self.calculator.run_scenario_analysis(inputs)
            if isinstance(result, dict) and "scenarios" in result:
                self.log_success("Scenario analysis successful")
                return True
            else:
                self.log_error(f"Scenario analysis failed: Unexpected result format")
                return False
        except Exception as e:
            self.log_error(f"Scenario analysis failed with exception: {str(e)}", e)
            return False
            
    def test_sensitivity_analysis(self, inputs: FinancialInputs) -> bool:
        """Test sensitivity analysis."""
        self.log_info("Step 12: Testing sensitivity analysis...")
        
        if not inputs.sensitivity_analysis:
            self.log_warning("No sensitivity analysis data provided - skipping test")
            return True
            
        try:
            result = self.calculator.run_sensitivity_analysis(inputs)
            if isinstance(result, dict) and "sensitivity_results" in result:
                self.log_success("Sensitivity analysis successful")
                return True
            else:
                self.log_error(f"Sensitivity analysis failed: Unexpected result format")
                return False
        except Exception as e:
            self.log_error(f"Sensitivity analysis failed with exception: {str(e)}", e)
            return False
            
    def test_monte_carlo_simulation(self, inputs: FinancialInputs) -> bool:
        """Test Monte Carlo simulation."""
        self.log_info("Step 13: Testing Monte Carlo simulation...")
        
        if not inputs.monte_carlo_specs:
            self.log_warning("No Monte Carlo specifications provided - skipping test")
            return True
            
        try:
            result = self.calculator.run_monte_carlo_simulation(inputs, runs=100)  # Reduced runs for testing
            if "error" not in result:
                self.log_success("Monte Carlo simulation successful")
                return True
            else:
                self.log_error(f"Monte Carlo simulation failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            self.log_error("Monte Carlo simulation failed with exception", e)
            return False
            
    def test_comprehensive_valuation(self, inputs: FinancialInputs) -> bool:
        """Test comprehensive valuation."""
        self.log_info("Step 14: Testing comprehensive valuation...")
        
        try:
            result = self.calculator.run_comprehensive_valuation(inputs)
            if "valuation_summary" in result:
                self.log_success("Comprehensive valuation successful")
                return True
            else:
                self.log_error("Comprehensive valuation failed - no valuation summary in result")
                return False
        except Exception as e:
            self.log_error("Comprehensive valuation failed with exception", e)
            return False
            
    def generate_debug_report(self) -> Dict[str, Any]:
        """Generate a comprehensive debug report."""
        report = {
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_info": len(self.debug_info)
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "debug_info": self.debug_info
        }
        return report
        
    def debug_valuation(self, input_file: str) -> Dict[str, Any]:
        """Main debug function that runs all validation steps."""
        print("🔍 Finance Calculator Debugger")
        print("=" * 50)
        
        # Step 1: Load and validate JSON
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            self.log_success(f"Successfully loaded input file: {input_file}")
        except FileNotFoundError:
            self.log_error(f"Input file not found: {input_file}")
            return self.generate_debug_report()
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in input file: {e}")
            return self.generate_debug_report()
        except Exception as e:
            self.log_error(f"Unexpected error loading file: {e}")
            return self.generate_debug_report()
            
        # Step 2: Validate JSON structure
        if not self.validate_json_structure(data):
            return self.generate_debug_report()
            
        # Step 3: Validate financial inputs
        financial_data = data.get("financial_inputs", {})
        missing_fields = self.validate_financial_inputs(financial_data)
        
        # Step 4: Validate data types
        if not self.validate_data_types(financial_data):
            return self.generate_debug_report()
            
        # Step 5: Validate data values
        self.validate_data_values(financial_data)
        
        # Step 6: Validate list lengths
        if not self.validate_list_lengths(financial_data):
            return self.generate_debug_report()
            
        # Step 7: Test FinancialInputs creation
        inputs = self.test_financial_inputs_creation(data)
        if inputs is None:
            return self.generate_debug_report()
            
        # Step 8: Test ValuationParameters conversion
        params = self.test_valuation_parameters_conversion(inputs)
        if params is None:
            return self.generate_debug_report()
            
        # Step 9-14: Test individual components
        self.test_dcf_calculation(inputs)
        self.test_apv_calculation(inputs)
        self.test_comparable_multiples(inputs)
        self.test_scenario_analysis(inputs)
        self.test_sensitivity_analysis(inputs)
        self.test_monte_carlo_simulation(inputs)
        self.test_comprehensive_valuation(inputs)
        
        # Generate final report
        report = self.generate_debug_report()
        
        print("\n" + "=" * 50)
        print("📊 DEBUG SUMMARY")
        print("=" * 50)
        print(f"Total Errors: {report['summary']['total_errors']}")
        print(f"Total Warnings: {report['summary']['total_warnings']}")
        print(f"Total Info Messages: {report['summary']['total_info']}")
        
        if report['summary']['total_errors'] == 0:
            print("\n✅ All validation steps passed successfully!")
        else:
            print(f"\n❌ Found {report['summary']['total_errors']} error(s) that need to be fixed.")
            
        return report

def main():
    """Main function to run the debugger."""
    if len(sys.argv) != 2:
        print("Usage: python debug_valuation.py <input_file.json>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    debugger = ValuationDebugger()
    report = debugger.debug_valuation(input_file)
    
    # Save debug report to file
    debug_report_file = input_file.replace('.json', '_debug_report.json')
    with open(debug_report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Debug report saved to: {debug_report_file}")

if __name__ == "__main__":
    main() 