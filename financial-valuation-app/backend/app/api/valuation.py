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