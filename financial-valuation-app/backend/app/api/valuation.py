from flask import Blueprint, request, jsonify
from app import db
from app.models import Analysis, AnalysisInput, analysis_input_schema
from app.services.finance_core_service import FinanceCoreService
from app.services.celery_service import run_valuation_task
import sys
import os

valuation_bp = Blueprint('valuation', __name__)

# Add finance core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'finance_core'))

@valuation_bp.route('/<int:analysis_id>/inputs', methods=['POST'])
def submit_inputs(analysis_id):
    """Submit input data for analysis"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        data = request.get_json()
        
        # Debug logging
        print(f"DEBUG: Received data for analysis {analysis_id}: {data}")
        print(f"DEBUG: Analysis type: {analysis.analysis_type}")
        
        # Validate required financial inputs
        required_fields = [
            'revenue', 'ebit_margin', 'tax_rate', 'capex', 'depreciation',
            'nwc_changes', 'share_count'
        ]
        
        financial_inputs = data.get('financial_inputs', {})
        print(f"DEBUG: Financial inputs: {financial_inputs}")
        
        for field in required_fields:
            if field not in financial_inputs:
                print(f"DEBUG: Missing required field: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required financial input: {field}'
                }), 400
        
        # Validate analysis-specific inputs based on analysis type
        if analysis.analysis_type == 'dcf_wacc':
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: weighted_average_cost_of_capital'
                }), 400
            if 'terminal_growth_rate' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: terminal_growth_rate'
                }), 400
            if 'cost_of_debt' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: cost_of_debt'
                }), 400
                
        elif analysis.analysis_type == 'apv':
            if 'terminal_growth_rate' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: terminal_growth_rate'
                }), 400
            if 'cost_of_debt' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: cost_of_debt'
                }), 400
            if 'unlevered_cost_of_equity' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: unlevered_cost_of_equity'
                }), 400
                
        elif analysis.analysis_type == 'multiples':
            if 'comparable_multiples' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: comparable_multiples'
                }), 400
                
        elif analysis.analysis_type == 'scenario':
            if 'scenarios' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: scenarios'
                }), 400
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: weighted_average_cost_of_capital'
                }), 400
            if 'terminal_growth_rate' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: terminal_growth_rate'
                }), 400
            if 'cost_of_debt' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: cost_of_debt'
                }), 400
                
        elif analysis.analysis_type == 'sensitivity':
            if 'sensitivity_analysis' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: sensitivity_analysis'
                }), 400
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: weighted_average_cost_of_capital'
                }), 400
            if 'terminal_growth_rate' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: terminal_growth_rate'
                }), 400
            if 'cost_of_debt' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: cost_of_debt'
                }), 400
                
        elif analysis.analysis_type == 'monte_carlo':
            if 'monte_carlo_specs' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: monte_carlo_specs'
                }), 400
            if 'weighted_average_cost_of_capital' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: weighted_average_cost_of_capital'
                }), 400
            if 'terminal_growth_rate' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: terminal_growth_rate'
                }), 400
            if 'cost_of_debt' not in financial_inputs:
                return jsonify({
                    'success': False,
                    'error': 'Missing required field: cost_of_debt'
                }), 400
        
        # Create or update analysis input
        existing_input = AnalysisInput.query.filter_by(analysis_id=analysis_id).first()
        if existing_input:
            existing_input.financial_inputs = financial_inputs
            existing_input.comparable_multiples = data.get('comparable_multiples')
            existing_input.scenarios = data.get('scenarios')
            existing_input.sensitivity_analysis = data.get('sensitivity_analysis')
            existing_input.monte_carlo_specs = data.get('monte_carlo_specs')
            analysis_input = existing_input
        else:
            analysis_input = AnalysisInput(
                analysis_id=analysis_id,
                financial_inputs=financial_inputs,
                comparable_multiples=data.get('comparable_multiples'),
                scenarios=data.get('scenarios'),
                sensitivity_analysis=data.get('sensitivity_analysis'),
                monte_carlo_specs=data.get('monte_carlo_specs')
            )
            db.session.add(analysis_input)
        
        # Update analysis status
        analysis.status = 'processing'
        db.session.commit()
        
        # Start background task for calculation
        task = run_valuation_task.delay(analysis_id)
        
        # Store the task ID in the analysis record
        analysis.task_id = task.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': analysis_input_schema.dump(analysis_input),
            'task_id': task.id,
            'message': 'Inputs submitted successfully. Analysis started in background.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@valuation_bp.route('/<int:analysis_id>/inputs', methods=['GET'])
def get_inputs(analysis_id):
    """Get input data for analysis"""
    try:
        analysis_input = AnalysisInput.query.filter_by(analysis_id=analysis_id).first()
        if not analysis_input:
            return jsonify({
                'success': False,
                'error': 'No inputs found for this analysis'
            }), 404
        
        return jsonify({
            'success': True,
            'data': analysis_input_schema.dump(analysis_input)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@valuation_bp.route('/<int:analysis_id>/validate', methods=['POST'])
def validate_inputs(analysis_id):
    """Validate input data before submission"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        data = request.get_json()
        
        # Basic validation
        validation_errors = []
        
        financial_inputs = data.get('financial_inputs', {})
        
        # Check array lengths
        array_fields = ['revenue', 'capex', 'depreciation', 'nwc_changes']
        for field in array_fields:
            if field in financial_inputs:
                if not isinstance(financial_inputs[field], list):
                    validation_errors.append(f'{field} must be an array')
                elif len(financial_inputs[field]) < 1:
                    validation_errors.append(f'{field} must have at least one value')
        
        # Check percentage values
        percentage_fields = ['ebit_margin', 'tax_rate', 'terminal_growth_rate']
        for field in percentage_fields:
            if field in financial_inputs:
                value = financial_inputs[field]
                if not isinstance(value, (int, float)) or value < 0 or value > 1:
                    validation_errors.append(f'{field} must be a decimal between 0 and 1')
        
        # Check positive values
        positive_fields = ['share_count']
        for field in positive_fields:
            if field in financial_inputs:
                value = financial_inputs[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    validation_errors.append(f'{field} must be a positive number')
        
        if validation_errors:
            return jsonify({
                'success': False,
                'errors': validation_errors
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Inputs are valid'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@valuation_bp.route('/csv/sample', methods=['GET'])
def download_sample_csv():
    """Download sample CSV template"""
    import csv
    import io
    from flask import Response
    
    csv_data = [
        ['Field', 'Value', 'Description'],
        ['Company Name', 'TechCorp Inc.', 'Name of the company being valued'],
        ['Valuation Date', '2024-01-01', 'Date of valuation (YYYY-MM-DD)'],
        ['Forecast Years', '5', 'Number of years to forecast'],
        ['Revenue Year 1', '1250.0', 'Revenue for year 1 (millions)'],
        ['Revenue Year 2', '1375.0', 'Revenue for year 2 (millions)'],
        ['Revenue Year 3', '1512.5', 'Revenue for year 3 (millions)'],
        ['Revenue Year 4', '1663.8', 'Revenue for year 4 (millions)'],
        ['Revenue Year 5', '1830.1', 'Revenue for year 5 (millions)'],
        ['EBIT Margin', '0.18', 'EBIT margin as decimal'],
        ['Tax Rate', '0.25', 'Corporate tax rate as decimal'],
        ['CapEx Year 1', '187.5', 'Capital expenditures year 1 (millions)'],
        ['CapEx Year 2', '206.3', 'Capital expenditures year 2 (millions)'],
        ['CapEx Year 3', '226.9', 'Capital expenditures year 3 (millions)'],
        ['CapEx Year 4', '249.6', 'Capital expenditures year 4 (millions)'],
        ['CapEx Year 5', '274.5', 'Capital expenditures year 5 (millions)'],
        ['Depreciation Year 1', '125.0', 'Depreciation year 1 (millions)'],
        ['Depreciation Year 2', '137.5', 'Depreciation year 2 (millions)'],
        ['Depreciation Year 3', '151.3', 'Depreciation year 3 (millions)'],
        ['Depreciation Year 4', '166.4', 'Depreciation year 4 (millions)'],
        ['Depreciation Year 5', '183.0', 'Depreciation year 5 (millions)'],
        ['NWC Changes Year 1', '-25.0', 'Net working capital changes year 1 (millions)'],
        ['NWC Changes Year 2', '-27.5', 'Net working capital changes year 2 (millions)'],
        ['NWC Changes Year 3', '-30.3', 'Net working capital changes year 3 (millions)'],
        ['NWC Changes Year 4', '-33.3', 'Net working capital changes year 4 (millions)'],
        ['NWC Changes Year 5', '-36.6', 'Net working capital changes year 5 (millions)'],
        ['WACC', '0.095', 'Weighted average cost of capital as decimal'],
        ['Terminal Growth Rate', '0.025', 'Terminal growth rate as decimal'],
        ['Share Count', '45.2', 'Shares outstanding (millions)'],
        ['Cost of Debt', '0.065', 'Cost of debt as decimal'],
        ['Cash Balance', '50.0', 'Cash balance (millions)'],
        ['Risk Free Rate', '0.03', 'Risk-free rate as decimal'],
        ['Market Risk Premium', '0.06', 'Market risk premium as decimal'],
        ['Levered Beta', '1.2', 'Levered beta'],
        ['Unlevered Beta', '1.2', 'Unlevered beta'],
        ['Target Debt Ratio', '0.3', 'Target debt ratio as decimal'],
        ['Cost of Equity', '0.14', 'Cost of equity as decimal']
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sample_input.csv'}
    )

@valuation_bp.route('/csv/upload', methods=['POST'])
def upload_csv():
    """Upload and parse CSV file"""
    import csv
    import io
    import os
    import sys
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Read and parse CSV
        csv_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        # Convert to the format expected by the valuation engine
        form_data = {}
        for row in csv_reader:
            if row['Field'] and row['Value']:
                form_data[row['Field']] = row['Value']
        
        # Convert CSV data to JSON format using the finance core converter
        try:
            # Save uploaded file temporarily
            temp_csv_path = f"/tmp/uploaded_{file.filename}"
            with open(temp_csv_path, 'w') as f:
                f.write(csv_data)
            
            # Use the finance core converter
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'finance_core'))
            from csv_to_json_converter import csv_to_json
            
            json_data = csv_to_json(temp_csv_path)
            
            # Clean up temp file
            os.remove(temp_csv_path)
            
            return jsonify({
                'success': True,
                'data': json_data,
                'message': 'CSV uploaded and converted successfully'
            })
            
        except Exception as conversion_error:
            return jsonify({
                'success': False,
                'error': f'CSV conversion error: {str(conversion_error)}'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'CSV parsing error: {str(e)}'}), 400

@valuation_bp.route('/csv/validate', methods=['POST'])
def validate_csv():
    """Validate CSV data without converting"""
    import csv
    import io
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Read and parse CSV
        csv_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(csv_reader)
        
        # Basic validation
        validation_errors = []
        
        # Check required headers
        if not rows:
            validation_errors.append('CSV file is empty')
        else:
            required_headers = ['Field', 'Value', 'Description']
            first_row = rows[0]
            missing_headers = [h for h in required_headers if h not in first_row]
            if missing_headers:
                validation_errors.append(f'Missing required headers: {missing_headers}')
        
        # Check for key financial fields
        if not validation_errors:
            field_values = {row['Field']: row['Value'] for row in rows if row['Field']}
            key_fields = [
                'Company Name', 'Revenue Year 1', 'EBIT Margin', 'Tax Rate',
                'WACC', 'Terminal Growth Rate', 'Share Count'
            ]
            missing_key_fields = [field for field in key_fields if field not in field_values]
            if missing_key_fields:
                validation_errors.append(f'Missing key financial fields: {missing_key_fields}')
        
        if validation_errors:
            return jsonify({
                'success': False,
                'errors': validation_errors
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'CSV format is valid',
            'row_count': len(rows)
        })
        
    except Exception as e:
        return jsonify({'error': f'CSV validation error: {str(e)}'}), 400 