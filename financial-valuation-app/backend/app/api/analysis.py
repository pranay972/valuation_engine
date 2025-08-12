from flask import Blueprint, request, jsonify
from app import db
from app.models import Analysis, analysis_schema, analyses_schema
from app.services.finance_core_service import FinanceCoreService
import sys
import os

analysis_bp = Blueprint('analysis', __name__)

# Add finance core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'finance_core'))

@analysis_bp.route('/types', methods=['GET'])
def get_analysis_types():
    """Get available analysis types"""
    analysis_types = [
        {
            'id': 'dcf_wacc',
            'name': 'DCF Valuation (WACC)',
            'description': 'Standard discounted cash flow using weighted average cost of capital',
            'icon': '📊',
            'complexity': 'Medium'
        },
        {
            'id': 'apv',
            'name': 'APV Valuation',
            'description': 'Adjusted Present Value method separating unlevered value from financing effects',
            'icon': '💰',
            'complexity': 'High'
        },
        {
            'id': 'multiples',
            'name': 'Comparable Multiples',
            'description': 'Relative valuation using peer company ratios',
            'icon': '📈',
            'complexity': 'Low'
        },
        {
            'id': 'scenario',
            'name': 'Scenario Analysis',
            'description': 'Multiple scenarios with different parameter combinations',
            'icon': '🎯',
            'complexity': 'Medium'
        },
        {
            'id': 'sensitivity',
            'name': 'Sensitivity Analysis',
            'description': 'Parameter impact analysis on key valuation drivers',
            'icon': '🔍',
            'complexity': 'Medium'
        },
        {
            'id': 'monte_carlo',
            'name': 'Monte Carlo Simulation',
            'description': 'Risk analysis with probability distributions',
            'icon': '🎲',
            'complexity': 'High'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': analysis_types
    })

@analysis_bp.route('/', methods=['GET', 'POST'])
def analyses():
    """Handle both GET (list all) and POST (create new) for analyses"""
    if request.method == 'GET':
        """Get all analyses"""
        try:
            analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
            return jsonify({
                'success': True,
                'data': analyses_schema.dump(analyses)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    elif request.method == 'POST':
        """Create a new analysis"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or 'analysis_type' not in data:
                return jsonify({
                    'success': False,
                    'error': 'analysis_type is required'
                }), 400
            
            # Create new analysis
            analysis = Analysis(
                name=data.get('name', f"{data['analysis_type'].replace('_', ' ').title()} Analysis"),
                analysis_type=data['analysis_type'],
                company_name=data.get('company_name', 'Unknown Company'),
                status='pending'
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': analysis_schema.dump(analysis)
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@analysis_bp.route('/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        return jsonify({
            'success': True,
            'data': analysis_schema.dump(analysis)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/<int:analysis_id>', methods=['PUT'])
def update_analysis(analysis_id):
    """Update an analysis"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            analysis.name = data['name']
        if 'company_name' in data:
            analysis.company_name = data['company_name']
        if 'status' in data:
            analysis.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': analysis_schema.dump(analysis)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/<int:analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    """Delete an analysis"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Analysis deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 