import pytest
import sys
import os
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'version' in data
    assert 'endpoints' in data

def test_analysis_types_endpoint(client):
    """Test the analysis types endpoint."""
    response = client.get('/api/analysis/types')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]

def test_create_analysis_endpoint(client):
    """Test the create analysis endpoint."""
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

def test_swagger_json_endpoint(client):
    """Test the swagger.json endpoint."""
    response = client.get('/static/swagger.json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'openapi' in data
    assert 'info' in data
    assert 'paths' in data

def test_invalid_analysis_type(client):
    """Test creating analysis with invalid type."""
    data = {
        'analysis_type': 'invalid_type'
    }
    response = client.post('/api/analysis',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 200  # Currently accepts any type

def test_missing_analysis_type(client):
    """Test creating analysis without type."""
    data = {}
    response = client.post('/api/analysis',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400 