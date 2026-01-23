"""
Integration tests for API routes

Tests the full HTTP endpoints to ensure they work correctly.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRoutes:
    """Test suite for API routes"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_kpis_endpoint(self, client):
        """Test financial KPIs endpoint"""
        response = client.get('/api/v0/dashboard/kpis')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'success' in data
        assert data['success'] == True
        assert 'data' in data
        
        kpis = data['data']
        assert 'operating_margin' in kpis
        assert 'days_sales_outstanding' in kpis
        
        # Check Request ID header
        assert 'X-Request-ID' in response.headers
    
    def test_revenue_summary_endpoint(self, client):
        """Test revenue summary endpoint"""
        response = client.get('/api/v0/dashboard/revenue/summary')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        
        summary = data['data']
        assert 'actual_revenue' in summary
        assert 'budgeted_revenue' in summary
        assert 'variance' in summary
    
    def test_revenue_trends_endpoint(self, client):
        """Test revenue trends endpoint"""
        response = client.get('/api/v0/dashboard/revenue/trends?period=monthly')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_ar_aging_endpoint(self, client):
        """Test AR aging endpoint"""
        response = client.get('/api/v0/dashboard/ar-aging')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        
        ar_data = data['data']
        assert 'current' in ar_data
        assert 'days_30' in ar_data
        assert 'days_60' in ar_data
    
    def test_debt_endpoint(self, client):
        """Test debt metrics endpoint"""
        response = client.get('/api/v0/dashboard/debt')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        
        debt = data['data']
        assert 'debt_service_coverage' in debt
        assert 'status' in debt
    
    def test_alerts_endpoint(self, client):
        """Test efficiency alerts endpoint"""
        response = client.get('/api/v0/dashboard/alerts?limit=5')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        
        alerts_data = data['data']
        assert 'alerts' in alerts_data
        assert 'alert_types' in alerts_data
    
    def test_scenarios_endpoint(self, client):
        """Test scenarios endpoint"""
        response = client.get('/api/v0/dashboard/scenarios')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert 'data' in data
        
        scenarios_data = data['data']
        assert 'scenarios' in scenarios_data
        assert 'scenario_types' in scenarios_data
    
    def test_request_id_in_response(self, client):
        """Test that Request ID is included in response headers"""
        response = client.get('/api/v0/dashboard/kpis')
        
        assert 'X-Request-ID' in response.headers
        request_id = response.headers['X-Request-ID']
        assert len(request_id) > 0
        assert '-' in request_id  # UUIDs contain dashes
    
    def test_error_handling(self, client):
        """Test error handling for invalid endpoints"""
        response = client.get('/api/v0/dashboard/invalid-endpoint')
        assert response.status_code == 404


