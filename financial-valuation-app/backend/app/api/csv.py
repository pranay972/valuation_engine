from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import pandas as pd
import tempfile
from app.services.finance_core_service import FinanceCoreService

csv_bp = Blueprint('csv', __name__)

@csv_bp.route('/upload', methods=['POST'])
def upload_csv():
    """Upload and parse CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'File must be a CSV'
            }), 400
        
        # Read CSV file
        df = pd.read_csv(file)
        
        # Parse CSV data into the expected format
        parsed_data = parse_csv_to_form_data(df)
        
        return jsonify({
            'success': True,
            'data': parsed_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing CSV: {str(e)}'
        }), 500

@csv_bp.route('/sample', methods=['GET'])
def download_sample_csv():
    """Download sample CSV file"""
    try:
        # Create sample CSV data that matches sample_input.json
        sample_data = {
            'Field': [
                'Company Name', 'Valuation Date', 'Forecast Years',
                'Revenue Year 1', 'Revenue Year 2', 'Revenue Year 3', 'Revenue Year 4', 'Revenue Year 5',
                'EBIT Margin', 'Tax Rate',
                'CapEx Year 1', 'CapEx Year 2', 'CapEx Year 3', 'CapEx Year 4', 'CapEx Year 5',
                'Depreciation Year 1', 'Depreciation Year 2', 'Depreciation Year 3', 'Depreciation Year 4', 'Depreciation Year 5',
                'NWC Changes Year 1', 'NWC Changes Year 2', 'NWC Changes Year 3', 'NWC Changes Year 4', 'NWC Changes Year 5',
                'WACC', 'Terminal Growth Rate', 'Share Count', 'Cost of Debt', 'Cash Balance',
                'Risk Free Rate', 'Market Risk Premium', 'Levered Beta', 'Unlevered Beta', 'Target Debt Ratio', 'Unlevered Cost of Equity',
                'Use Input WACC', 'Use Debt Schedule', 'Current Debt Balance',
                'EV/EBITDA Multiple 1', 'EV/EBITDA Multiple 2', 'EV/EBITDA Multiple 3', 'EV/EBITDA Multiple 4', 'EV/EBITDA Multiple 5',
                'EV/Revenue Multiple 1', 'EV/Revenue Multiple 2', 'EV/Revenue Multiple 3', 'EV/Revenue Multiple 4', 'EV/Revenue Multiple 5',
                'P/E Multiple 1', 'P/E Multiple 2', 'P/E Multiple 3', 'P/E Multiple 4', 'P/E Multiple 5',
                'Optimistic EBIT Margin', 'Optimistic Terminal Growth', 'Optimistic WACC',
                'Pessimistic EBIT Margin', 'Pessimistic Terminal Growth', 'Pessimistic WACC',
                'MC EBIT Margin Mean', 'MC EBIT Margin Std', 'MC Terminal Growth Mean', 'MC Terminal Growth Std', 'MC WACC Mean', 'MC WACC Std',
                'Sensitivity EBIT Margin 1', 'Sensitivity EBIT Margin 2', 'Sensitivity EBIT Margin 3', 'Sensitivity EBIT Margin 4', 'Sensitivity EBIT Margin 5', 'Sensitivity EBIT Margin 6', 'Sensitivity EBIT Margin 7',
                'Sensitivity Terminal Growth 1', 'Sensitivity Terminal Growth 2', 'Sensitivity Terminal Growth 3', 'Sensitivity Terminal Growth 4', 'Sensitivity Terminal Growth 5',
                'Sensitivity WACC 1', 'Sensitivity WACC 2', 'Sensitivity WACC 3', 'Sensitivity WACC 4', 'Sensitivity WACC 5'
            ],
            'Value': [
                'TechCorp Inc.', '2024-01-01', 5,
                1250.0, 1375.0, 1512.5, 1663.8, 1830.1,
                0.18, 0.25,
                187.5, 206.3, 226.9, 249.6, 274.5,
                125.0, 137.5, 151.3, 166.4, 183.0,
                -25.0, -27.5, -30.3, -33.3, -36.6,
                0.095, 0.025, 45.2, 0.065, 50.0,
                0.03, 0.06, 1.2, 1.2, 0.3, 0.0,
                True, False, 150.0,
                12.5, 14.2, 13.8, 15.1, 13.9,
                2.8, 3.1, 2.9, 3.3, 3.0,
                18.5, 22.1, 20.8, 24.3, 21.4,
                0.22, 0.035, 0.085,
                0.14, 0.015, 0.105,
                0.18, 0.02, 0.025, 0.005, 0.095, 0.01,
                0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21,
                0.02, 0.0225, 0.025, 0.0275, 0.03,
                0.085, 0.09, 0.095, 0.10, 0.105
            ],
            'Description': [
                'Name of the company being valued', 'Date of valuation (YYYY-MM-DD)', 'Number of years to forecast',
                'Revenue for year 1 (millions)', 'Revenue for year 2 (millions)', 'Revenue for year 3 (millions)', 'Revenue for year 4 (millions)', 'Revenue for year 5 (millions)',
                'EBIT margin as decimal', 'Corporate tax rate as decimal',
                'Capital expenditures year 1 (millions)', 'Capital expenditures year 2 (millions)', 'Capital expenditures year 3 (millions)', 'Capital expenditures year 4 (millions)', 'Capital expenditures year 5 (millions)',
                'Depreciation year 1 (millions)', 'Depreciation year 2 (millions)', 'Depreciation year 3 (millions)', 'Depreciation year 4 (millions)', 'Depreciation year 5 (millions)',
                'Net working capital changes year 1 (millions) - negative = cash generation', 'Net working capital changes year 2 (millions) - negative = cash generation', 'Net working capital changes year 3 (millions) - negative = cash generation', 'Net working capital changes year 4 (millions) - negative = cash generation', 'Net working capital changes year 5 (millions) - negative = cash generation',
                'Weighted average cost of capital as decimal', 'Terminal growth rate as decimal', 'Shares outstanding (millions)', 'Cost of debt as decimal', 'Cash balance (millions)',
                'Risk-free rate as decimal', 'Market risk premium as decimal', 'Levered beta', 'Unlevered beta', 'Target debt ratio as decimal', 'Unlevered cost of equity (calculated if 0)',
                'Use input WACC directly (True) or calculate WACC (False)', 'Use detailed debt schedule (True) or simple net debt (False)', 'Current debt balance (millions)',
                'Comparable company EV/EBITDA multiple', 'Comparable company EV/EBITDA multiple', 'Comparable company EV/EBITDA multiple', 'Comparable company EV/EBITDA multiple', 'Comparable company EV/EBITDA multiple',
                'Comparable company EV/Revenue multiple', 'Comparable company EV/Revenue multiple', 'Comparable company EV/Revenue multiple', 'Comparable company EV/Revenue multiple', 'Comparable company EV/Revenue multiple',
                'Comparable company P/E multiple', 'Comparable company P/E multiple', 'Comparable company P/E multiple', 'Comparable company P/E multiple', 'Comparable company P/E multiple',
                'Optimistic scenario EBIT margin', 'Optimistic scenario terminal growth rate', 'Optimistic scenario WACC',
                'Pessimistic scenario EBIT margin', 'Pessimistic scenario terminal growth rate', 'Pessimistic scenario WACC',
                'Monte Carlo EBIT margin mean', 'Monte Carlo EBIT margin standard deviation', 'Monte Carlo terminal growth mean', 'Monte Carlo terminal growth standard deviation', 'Monte Carlo WACC mean', 'Monte Carlo WACC standard deviation',
                'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin', 'Sensitivity analysis EBIT margin',
                'Sensitivity analysis terminal growth rate', 'Sensitivity analysis terminal growth rate', 'Sensitivity analysis terminal growth rate', 'Sensitivity analysis terminal growth rate', 'Sensitivity analysis terminal growth rate',
                'Sensitivity analysis WACC', 'Sensitivity analysis WACC', 'Sensitivity analysis WACC', 'Sensitivity analysis WACC', 'Sensitivity analysis WACC'
            ]
        }
        
        # Create temporary CSV file
        df = pd.DataFrame(sample_data)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        # Send file and clean up
        response = send_file(temp_file.name, as_attachment=True, download_name='sample_valuation_input.csv', mimetype='text/csv')
        
        # Clean up temp file after sending
        os.unlink(temp_file.name)
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating sample CSV: {str(e)}'
        }), 500

def parse_csv_to_form_data(df):
    """Parse CSV data into the expected form format"""
    try:
        # Create a dictionary to store the parsed data
        parsed_data = {}
        
        # Extract basic company info
        company_name_row = df[df['Field'] == 'Company Name']
        if not company_name_row.empty:
            parsed_data['company_name'] = company_name_row.iloc[0]['Value']
        
        # Extract financial inputs
        financial_inputs = {}
        
        # Revenue projections
        revenue_data = []
        for i in range(1, 6):
            revenue_row = df[df['Field'] == f'Revenue Year {i}']
            if not revenue_row.empty:
                revenue_data.append(float(revenue_row.iloc[0]['Value']))
        if revenue_data:
            financial_inputs['revenue'] = revenue_data
        
        # CapEx projections
        capex_data = []
        for i in range(1, 6):
            capex_row = df[df['Field'] == f'CapEx Year {i}']
            if not capex_row.empty:
                capex_data.append(float(capex_row.iloc[0]['Value']))
        if capex_data:
            financial_inputs['capex'] = capex_data
        
        # Depreciation projections
        depreciation_data = []
        for i in range(1, 6):
            dep_row = df[df['Field'] == f'Depreciation Year {i}']
            if not dep_row.empty:
                depreciation_data.append(float(dep_row.iloc[0]['Value']))
        if depreciation_data:
            financial_inputs['depreciation'] = depreciation_data
        
        # NWC changes
        nwc_data = []
        for i in range(1, 6):
            nwc_row = df[df['Field'] == f'NWC Changes Year {i}']
            if not nwc_row.empty:
                nwc_data.append(float(nwc_row.iloc[0]['Value']))
        if nwc_data:
            financial_inputs['nwc_changes'] = nwc_data
        
        # Single values
        single_fields = [
            'EBIT Margin', 'Tax Rate', 'WACC', 'Terminal Growth Rate', 
            'Share Count', 'Cost of Debt', 'Cash Balance', 'Risk Free Rate',
            'Market Risk Premium', 'Levered Beta', 'Unlevered Beta', 
            'Target Debt Ratio', 'Unlevered Cost of Equity'
        ]
        
        for field in single_fields:
            field_row = df[df['Field'] == field]
            if not field_row.empty:
                value = field_row.iloc[0]['Value']
                # Convert to appropriate type
                if isinstance(value, str) and value.lower() in ['true', 'false']:
                    financial_inputs[field.lower().replace(' ', '_')] = value.lower() == 'true'
                else:
                    try:
                        financial_inputs[field.lower().replace(' ', '_')] = float(value)
                    except:
                        financial_inputs[field.lower().replace(' ', '_')] = value
        
        # Add financial inputs to parsed data
        if financial_inputs:
            parsed_data['financial_inputs'] = financial_inputs
        
        # Extract comparable multiples
        multiples = {}
        ev_ebitda = []
        ev_revenue = []
        pe_ratio = []
        
        for i in range(1, 6):
            ev_ebitda_row = df[df['Field'] == f'EV/EBITDA Multiple {i}']
            if not ev_ebitda_row.empty:
                ev_ebitda.append(float(ev_ebitda_row.iloc[0]['Value']))
        
        for i in range(1, 6):
            ev_revenue_row = df[df['Field'] == f'EV/Revenue Multiple {i}']
            if not ev_revenue_row.empty:
                ev_revenue.append(float(ev_revenue_row.iloc[0]['Value']))
        
        for i in range(1, 6):
            pe_row = df[df['Field'] == f'P/E Multiple {i}']
            if not pe_row.empty:
                pe_ratio.append(float(pe_row.iloc[0]['Value']))
        
        if ev_ebitda:
            multiples['EV/EBITDA'] = ev_ebitda
        if ev_revenue:
            multiples['EV/Revenue'] = ev_revenue
        if pe_ratio:
            multiples['P/E'] = pe_ratio
        
        if multiples:
            parsed_data['comparable_multiples'] = multiples
        
        # Extract scenarios
        scenarios = {}
        optimistic_row = df[df['Field'] == 'Optimistic EBIT Margin']
        if not optimistic_row.empty:
            scenarios['optimistic'] = {
                'ebit_margin': float(optimistic_row.iloc[0]['Value'])
            }
        
        optimistic_growth_row = df[df['Field'] == 'Optimistic Terminal Growth']
        if not optimistic_growth_row.empty and 'optimistic' in scenarios:
            scenarios['optimistic']['terminal_growth_rate'] = float(optimistic_growth_row.iloc[0]['Value'])
        
        optimistic_wacc_row = df[df['Field'] == 'Optimistic WACC']
        if not optimistic_wacc_row.empty and 'optimistic' in scenarios:
            scenarios['optimistic']['weighted_average_cost_of_capital'] = float(optimistic_wacc_row.iloc[0]['Value'])
        
        pessimistic_row = df[df['Field'] == 'Pessimistic EBIT Margin']
        if not pessimistic_row.empty:
            scenarios['pessimistic'] = {
                'ebit_margin': float(pessimistic_row.iloc[0]['Value'])
            }
        
        pessimistic_growth_row = df[df['Field'] == 'Pessimistic Terminal Growth']
        if not pessimistic_growth_row.empty and 'pessimistic' in scenarios:
            scenarios['pessimistic']['terminal_growth_rate'] = float(pessimistic_growth_row.iloc[0]['Value'])
        
        pessimistic_wacc_row = df[df['Field'] == 'Pessimistic WACC']
        if not pessimistic_wacc_row.empty and 'pessimistic' in scenarios:
            scenarios['pessimistic']['weighted_average_cost_of_capital'] = float(pessimistic_wacc_row.iloc[0]['Value'])
        
        if scenarios:
            parsed_data['scenarios'] = scenarios
        
        # Extract Monte Carlo specs
        mc_specs = {}
        
        mc_ebit_mean_row = df[df['Field'] == 'MC EBIT Margin Mean']
        if not mc_ebit_mean_row.empty:
            mc_specs['ebit_margin'] = {
                'distribution': 'normal',
                'params': {
                    'mean': float(mc_ebit_mean_row.iloc[0]['Value']),
                    'std': 0.02  # Default value
                }
            }
        
        mc_ebit_std_row = df[df['Field'] == 'MC EBIT Margin Std']
        if not mc_ebit_std_row.empty and 'ebit_margin' in mc_specs:
            mc_specs['ebit_margin']['params']['std'] = float(mc_ebit_std_row.iloc[0]['Value'])
        
        mc_growth_mean_row = df[df['Field'] == 'MC Terminal Growth Mean']
        if not mc_growth_mean_row.empty:
            mc_specs['terminal_growth_rate'] = {
                'distribution': 'normal',
                'params': {
                    'mean': float(mc_growth_mean_row.iloc[0]['Value']),
                    'std': 0.005  # Default value
                }
            }
        
        mc_growth_std_row = df[df['Field'] == 'MC Terminal Growth Std']
        if not mc_growth_std_row.empty and 'terminal_growth_rate' in mc_specs:
            mc_specs['terminal_growth_rate']['params']['std'] = float(mc_growth_std_row.iloc[0]['Value'])
        
        mc_wacc_mean_row = df[df['Field'] == 'MC WACC Mean']
        if not mc_wacc_mean_row.empty:
            mc_specs['weighted_average_cost_of_capital'] = {
                'distribution': 'normal',
                'params': {
                    'mean': float(mc_wacc_mean_row.iloc[0]['Value']),
                    'std': 0.01  # Default value
                }
            }
        
        mc_wacc_std_row = df[df['Field'] == 'MC WACC Std']
        if not mc_wacc_std_row.empty and 'weighted_average_cost_of_capital' in mc_specs:
            mc_specs['weighted_average_cost_of_capital']['params']['std'] = float(mc_wacc_std_row.iloc[0]['Value'])
        
        if mc_specs:
            parsed_data['monte_carlo_specs'] = mc_specs
        
        # Extract sensitivity analysis
        sensitivity = {}
        
        ebit_sensitivity = []
        for i in range(1, 8):
            ebit_row = df[df['Field'] == f'Sensitivity EBIT Margin {i}']
            if not ebit_row.empty:
                ebit_sensitivity.append(float(ebit_row.iloc[0]['Value']))
        if ebit_sensitivity:
            sensitivity['ebit_margin'] = ebit_sensitivity
        
        growth_sensitivity = []
        for i in range(1, 6):
            growth_row = df[df['Field'] == f'Sensitivity Terminal Growth {i}']
            if not growth_row.empty:
                growth_sensitivity.append(float(growth_row.iloc[0]['Value']))
        if growth_sensitivity:
            sensitivity['terminal_growth_rate'] = growth_sensitivity
        
        wacc_sensitivity = []
        for i in range(1, 6):
            wacc_row = df[df['Field'] == f'Sensitivity WACC {i}']
            if not wacc_row.empty:
                wacc_sensitivity.append(float(wacc_row.iloc[0]['Value']))
        if wacc_sensitivity:
            sensitivity['weighted_average_cost_of_capital'] = wacc_sensitivity
        
        if sensitivity:
            parsed_data['sensitivity_analysis'] = sensitivity
        
        return parsed_data
        
    except Exception as e:
        raise Exception(f'Error parsing CSV: {str(e)}')
