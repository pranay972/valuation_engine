from flask import Blueprint, request, jsonify
from app import db
from app.models import Analysis, AnalysisInput, analysis_input_schema
from app.services.finance_core_service import FinanceCoreService
from app.services.celery_service import run_valuation_task

valuation_bp = Blueprint('valuation', __name__)

@valuation_bp.route('/<int:analysis_id>/inputs', methods=['POST'])
def submit_inputs(analysis_id):
    """Submit input data for analysis"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        data = request.get_json()
        
        # Store inputs in database
        analysis_input = AnalysisInput(
            analysis_id=analysis_id,
            financial_inputs=data.get('financial_inputs', {}),
            comparable_multiples=data.get('comparable_multiples'),
            scenarios=data.get('scenarios'),
            sensitivity_analysis=data.get('sensitivity_analysis'),
            monte_carlo_specs=data.get('monte_carlo_specs')
        )
        
        db.session.add(analysis_input)
        db.session.commit()
        
        # Run analysis in background
        task = run_valuation_task.delay(analysis_id)
        
        return jsonify({
            'success': True,
            'message': 'Inputs submitted successfully. Analysis started in background.',
            'task_id': task.id,
            'data': analysis_input_schema.dump(analysis_input)
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