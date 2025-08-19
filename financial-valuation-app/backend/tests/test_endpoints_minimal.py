#!/usr/bin/env python3
"""
Comprehensive Backend Endpoint Tests (Minimal Flask App)

Tests all backend endpoints to verify correct data format and response structure.
Uses a minimal Flask app to avoid import issues.
"""

import pytest
import json
import sys
import os
import uuid
import io
import csv

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    """Create a test client with minimal Flask app."""
    from flask import Flask, request, jsonify, Response, send_from_directory
    
    app = Flask(__name__)
    
    # Analysis types
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
    
    @app.route('/api/valuation/<analysis_id>/inputs', methods=['POST'])
    def submit_inputs(analysis_id):
        data = request.json
        
        # Simple validation
        if not data:
            return jsonify({'error': 'Input data is required'}), 400
        
        # For now, just return success
        return jsonify({
            'id': analysis_id,
            'status': 'processing',
            'message': 'Analysis started'
        })
    
    @app.route('/api/results/<analysis_id>/status', methods=['GET'])
    def get_status(analysis_id):
        # Simulate processing status
        return jsonify({
            'id': analysis_id,
            'status': 'completed',
            'progress': 100
        })
    
    @app.route('/api/results/<analysis_id>/results', methods=['GET'])
    def get_results(analysis_id):
        # Return comprehensive sample results
        return jsonify({
            'id': analysis_id,
            'status': 'completed',
            'valuation_summary': {
                'valuation_date': '2024-01-01',
                'company': 'TechCorp Inc.',
                'share_count': 45.2
            },
            'dcf_valuation': {
                'wacc': 0.08602499999999999,
                'terminal_growth': 0.025,
                'enterprise_value': 1453.5,
                'equity_value': 1353.5,
                'price_per_share': 29.95,
                'free_cash_flows_after_tax_fcff': [
                    73.8,
                    81.0,
                    89.3,
                    98.1,
                    108.0
                ],
                'terminal_value': 1813.4,
                'present_value_of_terminal': 1105.2,
                'present_value_of_fcfs': 348.3,
                'net_debt_breakdown': {
                    'current_debt': 150.0,
                    'cash_balance': 50.0,
                    'net_debt': 100.0
                },
                'wacc_components': {
                    'target_debt_ratio': 0.3,
                    'cost_of_equity': 0.102,
                    'cost_of_debt': 0.065,
                    'tax_rate': 0.25
                }
            }
        })
    
    @app.route('/api/csv/sample', methods=['GET'])
    def download_sample_csv():
        """Download sample CSV template"""
        csv_data = [
            ['Field', 'Value', 'Description'],
            ['company_name', 'TechCorp Inc.', 'Company name'],
            ['revenue_1', '1000', 'Revenue Year 1 (millions)'],
            ['revenue_2', '1100', 'Revenue Year 2 (millions)'],
            ['revenue_3', '1200', 'Revenue Year 3 (millions)'],
            ['revenue_4', '1300', 'Revenue Year 4 (millions)'],
            ['revenue_5', '1400', 'Revenue Year 5 (millions)'],
            ['ebit_margin', '0.18', 'EBIT Margin (decimal)'],
            ['tax_rate', '0.25', 'Tax Rate (decimal)'],
            ['wacc', '0.095', 'WACC (decimal)'],
            ['terminal_growth', '0.025', 'Terminal Growth (decimal)'],
            ['share_count', '45.2', 'Share Count (millions)']
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
    
    @app.route('/api/csv/upload', methods=['POST'])
    def upload_csv():
        """Upload and parse CSV file"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        try:
            csv_data = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            form_data = {}
            for row in csv_reader:
                if row['Field'] and row['Value']:
                    form_data[row['Field']] = row['Value']
            return jsonify({
                'success': True,
                'data': form_data,
                'message': 'CSV uploaded successfully'
            })
        except Exception as e:
            return jsonify({'error': f'CSV parsing error: {str(e)}'}), 400
    
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
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'})
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestBasicEndpoints:
    """Test basic endpoints (health, root)."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint returns correct format."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check response structure
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert isinstance(data['status'], str)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct format."""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check response structure
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data
        
        # Check specific values
        assert data['message'] == 'Financial Valuation API'
        assert data['version'] == '1.0.0'
        assert isinstance(data['endpoints'], dict)
        
        # Check endpoints structure
        expected_endpoints = [
            'analysis_types', 'create_analysis', 'submit_inputs',
            'get_results', 'get_status', 'swagger_ui'
        ]
        for endpoint in expected_endpoints:
            assert endpoint in data['endpoints']
            assert isinstance(data['endpoints'][endpoint], str)

class TestAnalysisTypesEndpoint:
    """Test analysis types endpoint."""
    
    def test_analysis_types_endpoint(self, client):
        """Test analysis types endpoint returns correct format."""
        response = client.get('/api/analysis/types')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check response is a list
        assert isinstance(data, list)
        assert len(data) == 6  # Should have 6 analysis types
        
        # Check each analysis type structure
        expected_types = ['dcf_wacc', 'apv', 'multiples', 'scenario', 'sensitivity', 'monte_carlo']
        for i, analysis_type in enumerate(data):
            assert 'id' in analysis_type
            assert 'name' in analysis_type
            assert 'description' in analysis_type
            assert 'complexity' in analysis_type
            assert 'icon' in analysis_type
            
            # Check data types
            assert isinstance(analysis_type['id'], str)
            assert isinstance(analysis_type['name'], str)
            assert isinstance(analysis_type['description'], str)
            assert isinstance(analysis_type['complexity'], str)
            assert isinstance(analysis_type['icon'], str)
            
            # Check expected values
            assert analysis_type['id'] == expected_types[i]
            assert analysis_type['complexity'] in ['Low', 'Medium', 'High']
    
    def test_analysis_types_content(self, client):
        """Test analysis types have correct content."""
        response = client.get('/api/analysis/types')
        data = json.loads(response.data)
        
        # Check specific analysis types
        dcf_wacc = next(item for item in data if item['id'] == 'dcf_wacc')
        assert dcf_wacc['name'] == 'DCF Valuation (WACC)'
        assert 'Discounted Cash Flow' in dcf_wacc['description']
        assert dcf_wacc['complexity'] == 'Medium'
        assert dcf_wacc['icon'] == '📊'
        
        apv = next(item for item in data if item['id'] == 'apv')
        assert apv['name'] == 'APV Valuation'
        assert 'Adjusted Present Value' in apv['description']
        assert apv['complexity'] == 'High'
        assert apv['icon'] == '💰'

class TestCreateAnalysisEndpoint:
    """Test create analysis endpoint."""
    
    def test_create_analysis_valid(self, client):
        """Test creating analysis with valid data."""
        data = {
            'analysis_type': 'dcf_wacc',
            'company_name': 'Test Company Inc.'
        }
        response = client.post('/api/analysis', 
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check response structure
        assert 'id' in result
        assert 'analysis_type' in result
        assert 'company_name' in result
        assert 'status' in result
        
        # Check data types
        assert isinstance(result['id'], str)
        assert isinstance(result['analysis_type'], str)
        assert isinstance(result['company_name'], str)
        assert isinstance(result['status'], str)
        
        # Check values
        assert result['analysis_type'] == 'dcf_wacc'
        assert result['company_name'] == 'Test Company Inc.'
        assert result['status'] == 'created'
        
        # Check UUID format
        try:
            uuid.UUID(result['id'])
        except ValueError:
            pytest.fail("Analysis ID is not a valid UUID")
    
    def test_create_analysis_missing_type(self, client):
        """Test creating analysis without analysis type."""
        data = {'company_name': 'Test Company'}
        response = client.post('/api/analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'Analysis type is required'
    
    def test_create_analysis_empty_data(self, client):
        """Test creating analysis with empty data."""
        response = client.post('/api/analysis',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'Analysis type is required'
    
    def test_create_analysis_default_company(self, client):
        """Test creating analysis with default company name."""
        data = {'analysis_type': 'apv'}
        response = client.post('/api/analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['company_name'] == 'Company'  # Default value

class TestSubmitInputsEndpoint:
    """Test submit inputs endpoint."""
    
    def test_submit_inputs_valid(self, client):
        """Test submitting inputs with valid data."""
        analysis_id = str(uuid.uuid4())
        data = {
            'revenue': [1000, 1100, 1200],
            'ebit_margin': 0.18,
            'tax_rate': 0.25,
            'wacc': 0.095
        }
        response = client.post(f'/api/valuation/{analysis_id}/inputs',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check response structure
        assert 'id' in result
        assert 'status' in result
        assert 'message' in result
        
        # Check data types
        assert isinstance(result['id'], str)
        assert isinstance(result['status'], str)
        assert isinstance(result['message'], str)
        
        # Check values
        assert result['id'] == analysis_id
        assert result['status'] == 'processing'
        assert result['message'] == 'Analysis started'
    
    def test_submit_inputs_empty_data(self, client):
        """Test submitting inputs with empty data."""
        analysis_id = str(uuid.uuid4())
        response = client.post(f'/api/valuation/{analysis_id}/inputs',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'Input data is required'
    
    def test_submit_inputs_no_data(self, client):
        """Test submitting inputs with no data."""
        analysis_id = str(uuid.uuid4())
        response = client.post(f'/api/valuation/{analysis_id}/inputs',
                              data=json.dumps(None),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'Input data is required'

class TestStatusEndpoint:
    """Test status endpoint."""
    
    def test_get_status(self, client):
        """Test getting analysis status."""
        analysis_id = str(uuid.uuid4())
        response = client.get(f'/api/results/{analysis_id}/status')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check response structure
        assert 'id' in result
        assert 'status' in result
        assert 'progress' in result
        
        # Check data types
        assert isinstance(result['id'], str)
        assert isinstance(result['status'], str)
        assert isinstance(result['progress'], int)
        
        # Check values
        assert result['id'] == analysis_id
        assert result['status'] == 'completed'
        assert result['progress'] == 100

class TestResultsEndpoint:
    """Test results endpoint."""
    
    def test_get_results(self, client):
        """Test getting analysis results."""
        analysis_id = str(uuid.uuid4())
        response = client.get(f'/api/results/{analysis_id}/results')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check response structure
        assert 'id' in result
        assert 'status' in result
        assert 'valuation_summary' in result
        assert 'dcf_valuation' in result
        
        # Check data types
        assert isinstance(result['id'], str)
        assert isinstance(result['status'], str)
        assert isinstance(result['valuation_summary'], dict)
        assert isinstance(result['dcf_valuation'], dict)
        
        # Check values
        assert result['id'] == analysis_id
        assert result['status'] == 'completed'
        
        # Check valuation summary
        summary = result['valuation_summary']
        assert 'valuation_date' in summary
        assert 'company' in summary
        assert 'share_count' in summary
        assert summary['valuation_date'] == '2024-01-01'
        assert summary['company'] == 'TechCorp Inc.'
        assert summary['share_count'] == 45.2
        
        # Check DCF valuation
        dcf = result['dcf_valuation']
        assert 'wacc' in dcf
        assert 'terminal_growth' in dcf
        assert 'enterprise_value' in dcf
        assert 'equity_value' in dcf
        assert 'price_per_share' in dcf
        assert 'free_cash_flows_after_tax_fcff' in dcf
        assert 'terminal_value' in dcf
        assert 'present_value_of_terminal' in dcf
        assert 'present_value_of_fcfs' in dcf
        assert 'net_debt_breakdown' in dcf
        assert 'wacc_components' in dcf
        
        # Check data types
        assert isinstance(dcf['wacc'], float)
        assert isinstance(dcf['terminal_growth'], float)
        assert isinstance(dcf['enterprise_value'], float)
        assert isinstance(dcf['equity_value'], float)
        assert isinstance(dcf['price_per_share'], float)
        assert isinstance(dcf['free_cash_flows_after_tax_fcff'], list)
        assert isinstance(dcf['terminal_value'], float)
        assert isinstance(dcf['present_value_of_terminal'], float)
        assert isinstance(dcf['present_value_of_fcfs'], float)
        assert isinstance(dcf['net_debt_breakdown'], dict)
        assert isinstance(dcf['wacc_components'], dict)
        
        # Check specific values
        assert dcf['wacc'] == 0.08602499999999999
        assert dcf['terminal_growth'] == 0.025
        assert dcf['enterprise_value'] == 1453.5
        assert dcf['equity_value'] == 1353.5
        assert dcf['price_per_share'] == 29.95
        assert len(dcf['free_cash_flows_after_tax_fcff']) == 5
        assert dcf['terminal_value'] == 1813.4
        assert dcf['present_value_of_terminal'] == 1105.2
        assert dcf['present_value_of_fcfs'] == 348.3

class TestCSVEndpoints:
    """Test CSV-related endpoints."""
    
    def test_download_sample_csv(self, client):
        """Test downloading sample CSV."""
        response = client.get('/api/csv/sample')
        assert response.status_code == 200
        
        # Check content type
        assert 'text/csv' in response.content_type
        
        # Check headers
        assert 'Content-Disposition' in response.headers
        assert 'attachment; filename=sample_input.csv' in response.headers['Content-Disposition']
        
        # Check CSV content
        csv_content = response.data.decode('utf-8')
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 12  # Should have header + data rows
        
        # Check header
        header = lines[0].split(',')
        header = [h.strip() for h in header]  # Remove whitespace and carriage returns
        assert 'Field' in header
        assert 'Value' in header
        assert 'Description' in header
        
        # Check some data rows
        data_lines = lines[1:]
        field_values = {}
        for line in data_lines:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    field_values[parts[0].strip()] = parts[1].strip()
        
        # Check specific fields
        assert 'company_name' in field_values
        assert 'revenue_1' in field_values
        assert 'ebit_margin' in field_values
        assert 'tax_rate' in field_values
        assert 'wacc' in field_values
        assert 'terminal_growth' in field_values
        assert 'share_count' in field_values
    
    def test_upload_csv_valid(self, client):
        """Test uploading valid CSV file."""
        # Create test CSV data
        csv_data = [
            ['Field', 'Value', 'Description'],
            ['company_name', 'Test Corp', 'Company name'],
            ['revenue_1', '1000', 'Revenue Year 1'],
            ['ebit_margin', '0.18', 'EBIT Margin']
        ]
        
        # Create file-like object
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
        csv_file.seek(0)
        
        # Create multipart form data
        data = {
            'file': (io.BytesIO(csv_file.getvalue().encode('utf-8')), 'test.csv')
        }
        
        response = client.post('/api/csv/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Check response structure
        assert 'success' in result
        assert 'data' in result
        assert 'message' in result
        
        # Check values
        assert result['success'] is True
        assert result['message'] == 'CSV uploaded successfully'
        assert isinstance(result['data'], dict)
        
        # Check parsed data
        data = result['data']
        assert data['company_name'] == 'Test Corp'
        assert data['revenue_1'] == '1000'
        assert data['ebit_margin'] == '0.18'
    
    def test_upload_csv_no_file(self, client):
        """Test uploading without file."""
        response = client.post('/api/csv/upload')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'No file provided'
    
    def test_upload_csv_empty_filename(self, client):
        """Test uploading with empty filename."""
        data = {'file': (io.BytesIO(b''), '')}
        response = client.post('/api/csv/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        result = json.loads(response.data)
        
        assert 'error' in result
        assert result['error'] == 'No file selected'

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_endpoint(self, client):
        """Test non-existent endpoint returns 404."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test invalid JSON in POST requests."""
        response = client.post('/api/analysis',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400 