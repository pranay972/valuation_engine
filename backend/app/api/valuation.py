"""
Valuation API endpoints.
"""

from flask import Blueprint, request, jsonify
import traceback
import os

from app.services.valuation_service import ValuationService

bp = Blueprint('valuation', __name__, url_prefix='/api/valuation')
valuation_service = ValuationService()


@bp.route('/calculate', methods=['POST'])
def calculate_valuation():
    """
    Calculate comprehensive valuation.
    
    Expected JSON payload:
    {
        "company_name": "TechCorp Inc.",
        "valuation_date": "2024-01-01",
        "financial_inputs": {
            "revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
            "ebit_margin": 0.18,
            "tax_rate": 0.25,
            "capex": [187.5, 206.3, 226.9, 249.6, 274.5],
            "depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
            "nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
            "terminal_growth": 0.025,
            "wacc": 0.095,
            "share_count": 45.2,
            "cost_of_debt": 0.065
        }
    }
    """
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format",
                "details": "Request must be JSON"
            }), 400
        
        # Get request data
        request_data = request.get_json()
        
        # Validate required fields
        if 'financial_inputs' not in request_data:
            return jsonify({
                "error": "Missing required field",
                "details": "financial_inputs is required"
            }), 400
        
        # Calculate valuation
        result = valuation_service.calculate_valuation(request_data)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({
            "error": "Calculation error",
            "details": str(e)
        }), 400
        
    except Exception as e:
        error_details = traceback.format_exc() if os.environ.get('FLASK_DEBUG') == 'True' else None
        return jsonify({
            "error": "Internal server error",
            "details": error_details
        }), 500


@bp.route('/sample', methods=['GET'])
def get_sample_data():
    """Get sample valuation data for testing."""
    try:
        sample_data = valuation_service.get_sample_data()
        return jsonify(sample_data), 200
    except Exception as e:
        error_details = traceback.format_exc() if os.environ.get('FLASK_DEBUG') == 'True' else None
        return jsonify({
            "error": "Failed to get sample data",
            "details": error_details
        }), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check for the valuation service."""
    return jsonify({
        "status": "healthy",
        "service": "valuation",
        "message": "Valuation service is running"
    }), 200 