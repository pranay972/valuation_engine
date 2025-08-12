"""Main Valuation Workflow Script - CSV to CSV valuation pipeline."""

import os
import csv
from datetime import datetime
from pathlib import Path
from finance_calculator import FinancialValuationEngine, parse_financial_inputs
from input_validator import InputValidator
from csv_to_json_converter import csv_to_json

def generate_csv_report(input_data, results_data, company_name):
    """Generate CSV report inline."""
    report = []
    
    # Company information
    report.extend([
        ["COMPANY INFORMATION"],
        ["Metric", "Value"],
        ["Company", company_name],
        ["Valuation Date", input_data.get('valuation_date', datetime.now().strftime('%Y-%m-%d'))],
        ["Report Date", datetime.now().strftime('%Y-%m-%d')],
        [""],
        
        ["KEY METRICS"],
        ["Metric", "Value"],
        ["Tax Rate", f"{input_data.get('financial_inputs', {}).get('tax_rate', 0):.1%}"],
        ["Terminal Growth", f"{input_data.get('financial_inputs', {}).get('terminal_growth_rate', 0):.1%}"],
        ["Share Count (M)", f"{input_data.get('financial_inputs', {}).get('share_count', 0):.1f}"],
        ["WACC", f"{input_data.get('financial_inputs', {}).get('weighted_average_cost_of_capital', 0):.1%}"],
        ["Cost of Equity", f"{results_data.get('dcf_valuation', {}).get('wacc_components', {}).get('cost_of_equity', 0):.1%}"],
        ["Cost of Debt", f"{input_data.get('financial_inputs', {}).get('cost_of_debt', 0):.1%}"],
        ["Target Debt Ratio", f"{input_data.get('financial_inputs', {}).get('cost_of_capital', {}).get('target_debt_to_value_ratio', 0):.1%}"],
        ["Risk Free Rate", f"{input_data.get('financial_inputs', {}).get('cost_of_capital', {}).get('risk_free_rate', 0):.1%}"],
        ["Market Risk Premium", f"{input_data.get('financial_inputs', {}).get('cost_of_capital', {}).get('market_risk_premium', 0):.1%}"],
        ["Levered Beta", f"{input_data.get('financial_inputs', {}).get('cost_of_capital', {}).get('levered_beta', 0):.1f}"],
        ["Cash Balance ($M)", f"{input_data.get('financial_inputs', {}).get('cash_balance', 0):.1f}"],
        [""],
        
        ["FINANCIAL PROJECTIONS"],
        ["Metric", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    ])
    
    # Financial projections
    revenue = input_data.get('financial_inputs', {}).get('revenue', [])
    ebit_margin = input_data.get('financial_inputs', {}).get('ebit_margin', 0)
    tax_rate = input_data.get('financial_inputs', {}).get('tax_rate', 0)
    depreciation = input_data.get('financial_inputs', {}).get('depreciation', [])
    capex = input_data.get('financial_inputs', {}).get('capex', [])
    nwc_changes = input_data.get('financial_inputs', {}).get('nwc_changes', [])
    
    # Calculate projections
    for i in range(5):
        if i < len(revenue):
            rev = revenue[i]
            ebit = rev * ebit_margin
            taxes = ebit * tax_rate
            nopat = ebit - taxes
            dep = depreciation[i] if i < len(depreciation) else 0
            cap_ex = capex[i] if i < len(capex) else 0
            nwc = nwc_changes[i] if i < len(nwc_changes) else 0
            fcf = nopat + dep - cap_ex - nwc
            
            if i == 0:
                report.extend([
                    ["Revenue ($M)", f"{rev:.1f}", "", "", "", ""],
                    ["EBIT ($M)", f"{ebit:.1f}", "", "", "", ""],
                    ["EBIT Margin (%)", f"{ebit_margin:.1%}", "", "", "", ""],
                    ["Taxes ($M)", f"{taxes:.2f}", "", "", "", ""],
                    ["NOPAT ($M)", f"{nopat:.2f}", "", "", "", ""],
                    ["Depreciation & Amortization ($M)", f"{dep:.1f}", "", "", "", ""],
                    ["CapEx ($M)", f"{cap_ex:.1f}", "", "", "", ""],
                    ["Change in NWC ($M)", f"{nwc:.1f}", "", "", "", ""],
                    ["UFCF ($M)", f"{fcf:.1f}", "", "", "", ""]
                ])
            else:
                report[-(9):] = [
                    ["Revenue ($M)", f"{rev:.1f}"],
                    ["EBIT ($M)", f"{ebit:.1f}"],
                    ["EBIT Margin (%)", f"{ebit_margin:.1%}"],
                    ["Taxes ($M)", f"{taxes:.2f}"],
                    ["NOPAT ($M)", f"{nopat:.2f}"],
                    ["Depreciation & Amortization ($M)", f"{dep:.1f}"],
                    ["CapEx ($M)", f"{cap_ex:.1f}"],
                    ["Change in NWC ($M)", f"{nwc:.1f}"],
                    ["UFCF ($M)", f"{fcf:.1f}"]
                ]
    
    # Valuation results
    dcf_results = results_data.get('dcf_valuation', {})
    apv_results = results_data.get('apv_valuation', {})
    comp_results = results_data.get('comparable_valuation', {})
    
    report.extend([
        [""],
        ["VALUATION RESULTS"],
        ["Method", "Enterprise Value", "Equity Value", "Price per Share"],
        ["DCF (WACC)", f"${dcf_results.get('enterprise_value', 0):,.0f}", f"${dcf_results.get('equity_value', 0):,.0f}", f"${dcf_results.get('price_per_share', 0):.2f}"],
        ["APV", f"${apv_results.get('enterprise_value', 0):,.0f}", f"${apv_results.get('equity_value', 0):,.0f}", f"${apv_results.get('price_per_share', 0):.2f}"],
        ["Comparable (Mean)", f"${float(comp_results.get('ev_multiples', {}).get('mean_ev', 0)):,.0f}", "", ""],
        [""],
        
        ["WACC BREAKDOWN"],
        ["Component", "Value"],
        ["WACC (Input)", f"{input_data.get('financial_inputs', {}).get('weighted_average_cost_of_capital', 0):.1%}"],
        ["Cost of Equity", f"{dcf_results.get('wacc_components', {}).get('cost_of_equity', 0):.1%}"],
        ["Cost of Debt", f"{dcf_results.get('wacc_components', {}).get('cost_of_debt', 0):.1%}"],
        [""],
        
        ["SCENARIO ANALYSIS"],
        ["Scenario", "Price per Share"]
    ])
    
    # Scenarios
    scenarios = results_data.get('scenarios', {}).get('scenarios', {})
    for scenario_name, scenario_data in scenarios.items():
        report.append([
            scenario_name.replace('_', ' ').title(),
            f"${float(scenario_data.get('price_per_share', 0)):.2f}"
        ])
    
    # Monte Carlo
    mc_results = results_data.get('monte_carlo_simulation', {})
    report.extend([
        [""],
        ["MONTE CARLO SIMULATION"],
        ["Metric", "Value"],
        ["Mean EV", f"${float(mc_results.get('wacc_method', {}).get('mean_ev', 0)):,.0f}"],
        ["95% CI Lower", f"${float(mc_results.get('wacc_method', {}).get('confidence_interval_95', [0, 0])[0]):,.0f}"],
        ["95% CI Upper", f"${float(mc_results.get('wacc_method', {}).get('confidence_interval_95', [0, 0])[1]):,.0f}"]
    ])
    
    # Add Sensitivity Analysis Tables
    sensitivity_results = results_data.get('sensitivity_analysis', {}).get('sensitivity_results', {})
    if sensitivity_results:
        # EBIT Margin Sensitivity
        if 'ebit_margin' in sensitivity_results:
            report.extend([
                [""],
                ["EBIT MARGIN SENSITIVITY"],
                ["EBIT Margin", "Enterprise Value", "Price per Share"]
            ])
            ebit_sensitivity = sensitivity_results['ebit_margin']['ev']
            for ebit_margin, ev_value in ebit_sensitivity.items():
                price_value = sensitivity_results['ebit_margin']['price_per_share'].get(ebit_margin, 0)
                report.append([
                    f"{float(ebit_margin):.1%}",
                    f"${float(ev_value):,.0f}",
                    f"${float(price_value):.2f}"
                ])
        
        # Terminal Growth Sensitivity
        if 'terminal_growth_rate' in sensitivity_results:
            report.extend([
                [""],
                ["TERMINAL GROWTH SENSITIVITY"],
                ["Terminal Growth", "Enterprise Value", "Price per Share"]
            ])
            growth_sensitivity = sensitivity_results['terminal_growth_rate']['ev']
            for growth_rate, ev_value in growth_sensitivity.items():
                price_value = sensitivity_results['terminal_growth_rate']['price_per_share'].get(growth_rate, 0)
                report.append([
                    f"{float(growth_rate):.1%}",
                    f"${float(ev_value):,.0f}",
                    f"${float(price_value):.2f}"
                ])
        
        # WACC Sensitivity
        if 'weighted_average_cost_of_capital' in sensitivity_results:
            report.extend([
                [""],
                ["WACC SENSITIVITY"],
                ["WACC", "Enterprise Value", "Price per Share"]
            ])
            wacc_sensitivity = sensitivity_results['weighted_average_cost_of_capital']['ev']
            for wacc, ev_value in wacc_sensitivity.items():
                price_value = sensitivity_results['weighted_average_cost_of_capital']['price_per_share'].get(wacc, 0)
                report.append([
                    f"{float(wacc):.1%}",
                    f"${float(ev_value):,.0f}",
                    f"${float(price_value):.2f}"
                ])
    
    return report

def run_valuation_workflow(input_csv="valuation_input.csv"):
    """Run the complete valuation workflow from CSV input to CSV output."""
    
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV file '{input_csv}' not found")
    
    # Convert CSV to JSON
    input_data = csv_to_json(input_csv)
    
    # Validate inputs
    try:
        InputValidator.validate_financial_inputs(input_data)
    except Exception as e:
        print(f"Warning: Input validation issues: {e}")
    
    # Run valuation
    engine = FinancialValuationEngine()
    inputs = parse_financial_inputs(input_data)
    results_data = engine.perform_comprehensive_valuation(inputs)
    
    # Generate report
    company_name = input_data.get('company_name', 'Unknown Company')
    report_data = generate_csv_report(input_data, results_data, company_name)
    
    output_file = f"{company_name.replace(' ', '_')}_Valuation_Report.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(report_data)
    
    return output_file

def main():
    """Main function to run the valuation workflow."""
    import sys
    
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "valuation_input.csv"
    
    try:
        output_file = run_valuation_workflow(input_csv)
        print(f"Valuation completed: {output_file}")
    except Exception as e:
        print(f"Valuation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 