#!/usr/bin/env python3
"""
CSV to JSON Converter for Financial Valuation Inputs

This script converts CSV input files to JSON format for use with the financial valuation calculator.
It handles the conversion of valuation input data from CSV format to the structured JSON format
required by the valuation engine.
"""

import csv
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

def csv_to_json(csv_file: str) -> Dict[str, Any]:
    """
    Convert CSV input to JSON format for valuation.
    
    Args:
        csv_file: Path to the CSV input file
        
    Returns:
        Dict containing the structured JSON data for valuation
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file is malformed
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file '{csv_file}' not found")
    
    csv_data = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                field = row.get('Field', '').strip() if row.get('Field') else ''
                value = row.get('Value', '').strip() if row.get('Value') else ''
                description = row.get('Description', '').strip() if row.get('Description') else ''
                
                if not field or not value:
                    continue
                
                # Type conversion
                try:
                    if field in ['Forecast Years']:
                        value = int(float(value))
                    elif field in ['Share Count']:
                        value = float(value)
                    elif field in ['Company Name', 'Valuation Date']:
                        value = str(value)
                    elif field in ['Use Input WACC', 'Use Debt Schedule']:
                        value = value.lower() == 'true'
                    elif field in ['EBIT Margin', 'Tax Rate', 'WACC', 'Terminal Growth Rate', 'Cost of Debt', 'Cost of Equity', 'Cash Balance', 'Risk Free Rate', 'Market Risk Premium', 'Levered Beta', 'Unlevered Beta', 'Target Debt Ratio', 'Unlevered Cost of Equity', 'Current Debt Balance', 'Optimistic EBIT Margin', 'Optimistic Terminal Growth', 'Optimistic WACC', 'Pessimistic EBIT Margin', 'Pessimistic Terminal Growth', 'Pessimistic WACC', 'MC EBIT Margin Mean', 'MC EBIT Margin Std', 'MC Terminal Growth Mean', 'MC Terminal Growth Std', 'MC WACC Mean', 'MC WACC Std', 'Sensitivity EBIT Margin 1', 'Sensitivity EBIT Margin 2', 'Sensitivity EBIT Margin 3', 'Sensitivity EBIT Margin 4', 'Sensitivity EBIT Margin 5', 'Sensitivity EBIT Margin 6', 'Sensitivity EBIT Margin 7', 'Sensitivity Terminal Growth 1', 'Sensitivity Terminal Growth 2', 'Sensitivity Terminal Growth 3', 'Sensitivity Terminal Growth 4', 'Sensitivity Terminal Growth 5', 'Sensitivity WACC 1', 'Sensitivity WACC 2', 'Sensitivity WACC 3', 'Sensitivity WACC 4', 'Sensitivity WACC 5']:
                        value = float(value)
                    elif 'Year' in field:  # All year-specific fields should be floats
                        value = float(value)
                    else:
                        value = float(value)
                except (ValueError, TypeError):
                    value = str(value)
                
                csv_data[field] = value
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Create JSON structure
    json_data = {
        "company_name": csv_data.get('Company Name', 'Unknown Company'),
        "valuation_date": csv_data.get('Valuation Date', datetime.now().strftime('%Y-%m-%d')),
        "forecast_years": csv_data.get('Forecast Years', 5),
        "financial_inputs": {
            "revenue": [
                csv_data.get('Revenue Year 1', 0),
                csv_data.get('Revenue Year 2', 0),
                csv_data.get('Revenue Year 3', 0),
                csv_data.get('Revenue Year 4', 0),
                csv_data.get('Revenue Year 5', 0)
            ],
            "ebit_margin": csv_data.get('EBIT Margin', 0),
            "tax_rate": csv_data.get('Tax Rate', 0.25),
            "capex": [
                csv_data.get('CapEx Year 1', 0),
                csv_data.get('CapEx Year 2', 0),
                csv_data.get('CapEx Year 3', 0),
                csv_data.get('CapEx Year 4', 0),
                csv_data.get('CapEx Year 5', 0)
            ],
            "depreciation": [
                csv_data.get('Depreciation Year 1', 0),
                csv_data.get('Depreciation Year 2', 0),
                csv_data.get('Depreciation Year 3', 0),
                csv_data.get('Depreciation Year 4', 0),
                csv_data.get('Depreciation Year 5', 0)
            ],
            "nwc_changes": [
                csv_data.get('NWC Changes Year 1', 0),
                csv_data.get('NWC Changes Year 2', 0),
                csv_data.get('NWC Changes Year 3', 0),
                csv_data.get('NWC Changes Year 4', 0),
                csv_data.get('NWC Changes Year 5', 0)
            ],
            "weighted_average_cost_of_capital": csv_data.get('WACC', 0),
            "terminal_growth_rate": csv_data.get('Terminal Growth Rate', 0),
            "share_count": csv_data.get('Share Count', 0),
            "cost_of_debt": csv_data.get('Cost of Debt', 0),
            "cash_balance": csv_data.get('Cash Balance', 0),
            "cost_of_capital": {
                "risk_free_rate": csv_data.get('Risk Free Rate', 0),
                "market_risk_premium": csv_data.get('Market Risk Premium', 0),
                "levered_beta": csv_data.get('Levered Beta', 0),
                "unlevered_beta": csv_data.get('Unlevered Beta', 0),
                "target_debt_to_value_ratio": csv_data.get('Target Debt Ratio', 0),
                "unlevered_cost_of_equity": csv_data.get('Unlevered Cost of Equity', 0),
                "cost_of_equity": csv_data.get('Cost of Equity', 0)
            },
            "use_input_wacc": csv_data.get('Use Input WACC', True),
            "use_debt_schedule": csv_data.get('Use Debt Schedule', False),
            "debt_schedule": {
                "0": csv_data.get('Current Debt Balance', 0),
                "1": csv_data.get('Debt Balance Year 1', 0),
                "2": csv_data.get('Debt Balance Year 2', 0),
                "3": csv_data.get('Debt Balance Year 3', 0),
                "4": csv_data.get('Debt Balance Year 4', 0),
                "5": csv_data.get('Debt Balance Year 5', 0)
            }
        },
        "comparable_multiples": {
            "EV/EBITDA": [
                csv_data.get('EV/EBITDA Multiple 1', 0),
                csv_data.get('EV/EBITDA Multiple 2', 0),
                csv_data.get('EV/EBITDA Multiple 3', 0),
                csv_data.get('EV/EBITDA Multiple 4', 0),
                csv_data.get('EV/EBITDA Multiple 5', 0)
            ],
            "EV/Revenue": [
                csv_data.get('EV/Revenue Multiple 1', 0),
                csv_data.get('EV/Revenue Multiple 2', 0),
                csv_data.get('EV/Revenue Multiple 3', 0),
                csv_data.get('EV/Revenue Multiple 4', 0),
                csv_data.get('EV/Revenue Multiple 5', 0)
            ],
            "P/E": [
                csv_data.get('P/E Multiple 1', 0),
                csv_data.get('P/E Multiple 2', 0),
                csv_data.get('P/E Multiple 3', 0),
                csv_data.get('P/E Multiple 4', 0),
                csv_data.get('P/E Multiple 5', 0)
            ]
        },
        "scenarios": {
            "optimistic": {
                "ebit_margin": csv_data.get('Optimistic EBIT Margin', 0),
                "terminal_growth_rate": csv_data.get('Optimistic Terminal Growth', 0),
                "weighted_average_cost_of_capital": csv_data.get('Optimistic WACC', 0)
            },
            "pessimistic": {
                "ebit_margin": csv_data.get('Pessimistic EBIT Margin', 0),
                "terminal_growth_rate": csv_data.get('Pessimistic Terminal Growth', 0),
                "weighted_average_cost_of_capital": csv_data.get('Pessimistic WACC', 0)
            }
        },
        "monte_carlo_specs": {
            "ebit_margin": {
                "distribution": "normal",
                "params": {
                    "mean": csv_data.get('MC EBIT Margin Mean', 0),
                    "std": csv_data.get('MC EBIT Margin Std', 0)
                }
            },
            "terminal_growth_rate": {
                "distribution": "normal",
                "params": {
                    "mean": csv_data.get('MC Terminal Growth Mean', 0),
                    "std": csv_data.get('MC Terminal Growth Std', 0)
                }
            },
            "weighted_average_cost_of_capital": {
                "distribution": "normal",
                "params": {
                    "mean": csv_data.get('MC WACC Mean', 0),
                    "std": csv_data.get('MC WACC Std', 0)
                }
            }
        },
        "sensitivity_analysis": {
            "ebit_margin": [
                csv_data.get('Sensitivity EBIT Margin 1', 0),
                csv_data.get('Sensitivity EBIT Margin 2', 0),
                csv_data.get('Sensitivity EBIT Margin 3', 0),
                csv_data.get('Sensitivity EBIT Margin 4', 0),
                csv_data.get('Sensitivity EBIT Margin 5', 0),
                csv_data.get('Sensitivity EBIT Margin 6', 0),
                csv_data.get('Sensitivity EBIT Margin 7', 0)
            ],
            "terminal_growth_rate": [
                csv_data.get('Sensitivity Terminal Growth 1', 0),
                csv_data.get('Sensitivity Terminal Growth 2', 0),
                csv_data.get('Sensitivity Terminal Growth 3', 0),
                csv_data.get('Sensitivity Terminal Growth 4', 0),
                csv_data.get('Sensitivity Terminal Growth 5', 0)
            ],
            "weighted_average_cost_of_capital": [
                csv_data.get('Sensitivity WACC 1', 0),
                csv_data.get('Sensitivity WACC 2', 0),
                csv_data.get('Sensitivity WACC 3', 0),
                csv_data.get('Sensitivity WACC 4', 0),
                csv_data.get('Sensitivity WACC 5', 0)
            ]
        }
    }
    
    return json_data

def convert_csv_to_json_file(input_csv: str, output_json: str = None) -> str:
    """
    Convert CSV file to JSON file.
    
    Args:
        input_csv: Path to the input CSV file
        output_json: Path to the output JSON file (optional)
        
    Returns:
        Path to the created JSON file
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file is malformed
    """
    # Generate output filename if not provided
    if output_json is None:
        base_name = os.path.splitext(os.path.basename(input_csv))[0]
        output_json = f"{base_name}.json"
    
    # Convert CSV to JSON
    json_data = csv_to_json(input_csv)
    
    # Write JSON file
    try:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Error writing JSON file: {str(e)}")
    
    return output_json

def main():
    """Main function to run the CSV to JSON converter."""
    if len(sys.argv) < 2:
        print("Usage: python csv_to_json_converter.py <input_csv> [output_json]")
        print("Example: python csv_to_json_converter.py valuation_input.csv")
        print("Example: python csv_to_json_converter.py valuation_input.csv output.json")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        output_file = convert_csv_to_json_file(input_csv, output_json)
        print(f"✅ Successfully converted '{input_csv}' to '{output_file}'")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 