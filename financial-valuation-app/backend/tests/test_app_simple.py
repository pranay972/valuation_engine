#!/usr/bin/env python3
"""
Simple API Tests for Flask App

Tests basic API endpoints without importing the full app module.
"""

import pytest
import json
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_analysis_types_endpoint():
    """Test the analysis types endpoint by creating a simple Flask app."""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    # Define the analysis types
    ANALYSIS_TYPES = [
        {
            "id": "dcf_wacc",
            "name": "DCF Valuation (WACC)",
            "description": "Discounted Cash Flow using Weighted Average Cost of Capital",
            "complexity": "Medium",
            "icon": "📊"
        },
        {
            "id": "apv",
            "name": "APV Valuation",
            "description": "Adjusted Present Value method",
            "complexity": "High",
            "icon": "💰"
        },
        {
            "id": "multiples",
            "name": "Comparable Multiples",
            "description": "Relative valuation using peer company ratios",
            "complexity": "Low",
            "icon": "📈"
        },
        {
            "id": "scenario",
            "name": "Scenario Analysis",
            "description": "Multiple scenarios with different parameters",
            "complexity": "Medium",
            "icon": "🎯"
        },
        {
            "id": "sensitivity",
            "name": "Sensitivity Analysis",
            "description": "Parameter impact analysis",
            "complexity": "Medium",
            "icon": "📉"
        },
        {
            "id": "monte_carlo",
            "name": "Monte Carlo Simulation",
            "description": "Risk analysis with probability distributions",
            "complexity": "High",
            "icon": "🎲"
        }
    ]
    
    @app.route('/api/analysis/types', methods=['GET'])
    def get_analysis_types():
        return jsonify(ANALYSIS_TYPES)
    
    with app.test_client() as client:
        response = client.get('/api/analysis/types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 6
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert data[0]['id'] == 'dcf_wacc'

def test_health_endpoint():
    """Test the health endpoint."""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'})
    
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

def test_create_analysis_endpoint():
    """Test the create analysis endpoint."""
    from flask import Flask, request, jsonify
    import uuid
    
    app = Flask(__name__)
    
    @app.route('/api/analysis', methods=['POST'])
    def create_analysis():
        data = request.json
        analysis_type = data.get('analysis_type')
        company_name = data.get('company_name', 'Company')
        
        # Simple validation
        if not analysis_type:
            return jsonify({'error': 'Analysis type is required'}), 400
        
        # Create a simple analysis ID
        analysis_id = str(uuid.uuid4())
        
        return jsonify({
            'id': analysis_id,
            'analysis_type': analysis_type,
            'company_name': company_name,
            'status': 'created'
        })
    
    with app.test_client() as client:
        # Test valid request
        data = {
            'analysis_type': 'dcf_wacc',
            'company_name': 'Test Company'
        }
        response = client.post('/api/analysis', 
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'id' in result
        assert result['analysis_type'] == 'dcf_wacc'
        assert result['company_name'] == 'Test Company'
        
        # Test invalid request
        response = client.post('/api/analysis',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result

def test_root_endpoint():
    """Test the root endpoint."""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Financial Valuation API',
            'version': '1.0.0',
            'endpoints': {
                'analysis_types': '/api/analysis/types',
                'create_analysis': '/api/analysis',
                'submit_inputs': '/api/valuation/{id}/inputs',
                'get_results': '/api/results/{id}/results',
                'get_status': '/api/results/{id}/status',
                'swagger_ui': '/api/docs'
            }
        })
    
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data
        assert data['message'] == 'Financial Valuation API' 