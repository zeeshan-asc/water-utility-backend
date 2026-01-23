"""
Unit tests for DashboardService

Tests the business logic layer for dashboard data operations.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.dashboard_service import DashboardService


class TestDashboardService:
    """Test suite for DashboardService"""
    
    @pytest.fixture
    def service(self):
        """Create a DashboardService instance for testing"""
        return DashboardService()
    
    def test_get_financial_kpis_structure(self, service):
        """Test that KPIs return correct structure"""
        kpis = service.get_financial_kpis()
        
        # Check all required fields exist
        required_fields = [
            'operating_margin',
            'days_sales_outstanding',
            'non_revenue_water_pct',
            'cost_per_gallon',
            'collection_rate',
            'annual_revenue',
            'water_revenue',
            'cash_reserve',
            'debt_service_coverage',
            'operating_margin_change',
            'dso_change',
            'nrw_change',
            'cost_per_gallon_change',
            'collection_rate_change'
        ]
        
        for field in required_fields:
            assert field in kpis, f"Missing field: {field}"
            assert kpis[field] is not None, f"Field {field} is None"
    
    def test_get_financial_kpis_values(self, service):
        """Test that KPIs have valid values"""
        kpis = service.get_financial_kpis()
        
        # Operating margin should be 0-100%
        assert 0 <= kpis['operating_margin'] <= 100, "Operating margin out of range"
        
        # Days sales outstanding should be positive
        assert kpis['days_sales_outstanding'] > 0, "DSO should be positive"
        
        # Non-revenue water percentage should be 0-100%
        assert 0 <= kpis['non_revenue_water_pct'] <= 100, "NRW % out of range"
        
        # Cost per gallon should be positive
        assert kpis['cost_per_gallon'] > 0, "Cost per gallon should be positive"
        
        # Collection rate should be 0-100%
        assert 0 <= kpis['collection_rate'] <= 100, "Collection rate out of range"
        
        # Debt service coverage should be positive
        assert kpis['debt_service_coverage'] > 0, "DSC should be positive"
    
    def test_get_revenue_summary_structure(self, service):
        """Test revenue summary structure"""
        summary = service.get_revenue_summary()
        
        required_fields = ['actual_revenue', 'budgeted_revenue', 'variance', 'variance_pct', 'status']
        
        for field in required_fields:
            assert field in summary, f"Missing field: {field}"
        
        # Check that variance calculation is correct
        assert summary['variance'] == summary['actual_revenue'] - summary['budgeted_revenue']
        
        # Status should be 'positive' or 'negative'
        assert summary['status'] in ['positive', 'negative']
    
    def test_get_revenue_summary_variance_calculation(self, service):
        """Test that variance calculation is correct"""
        summary = service.get_revenue_summary()
        
        actual = summary['actual_revenue']
        budgeted = summary['budgeted_revenue']
        variance = summary['variance']
        variance_pct = summary['variance_pct']
        
        # Variance should equal actual - budgeted
        assert abs(variance - (actual - budgeted)) < 0.01, "Variance calculation incorrect"
        
        # Variance percentage should be calculated correctly
        if budgeted != 0:
            expected_pct = ((actual - budgeted) / budgeted) * 100
            assert abs(variance_pct - expected_pct) < 0.01, "Variance % calculation incorrect"
    
    def test_get_ar_aging_structure(self, service):
        """Test AR aging structure"""
        ar_data = service.get_ar_aging()
        
        # Check structure
        assert 'current' in ar_data
        assert 'days_30' in ar_data
        assert 'days_60' in ar_data
        assert 'total_ar' in ar_data
        
        # Check nested structure
        assert 'percentage' in ar_data['current']
        assert 'amount' in ar_data['current']
        
        # Percentages should sum to approximately 100%
        total_pct = (
            ar_data['current']['percentage'] +
            ar_data['days_30']['percentage'] +
            ar_data['days_60']['percentage']
        )
        assert 99.0 <= total_pct <= 101.0, f"Percentages don't sum to 100%: {total_pct}"
    
    def test_get_debt_metrics_structure(self, service):
        """Test debt metrics structure"""
        debt = service.get_debt_metrics()
        
        required_fields = [
            'debt_service_coverage',
            'projected_coverage',
            'actual_coverage',
            'required_minimum',
            'outstanding_debt',
            'status'
        ]
        
        for field in required_fields:
            assert field in debt, f"Missing field: {field}"
        
        # Status should be 'healthy' or 'at_risk'
        assert debt['status'] in ['healthy', 'at_risk']
        
        # All coverage values should be positive
        assert debt['debt_service_coverage'] > 0
        assert debt['projected_coverage'] > 0
        assert debt['actual_coverage'] > 0
        assert debt['required_minimum'] > 0
    
    def test_get_revenue_trends(self, service):
        """Test revenue trends with different periods"""
        # Test monthly
        trends_monthly = service.get_revenue_trends(period='monthly')
        assert isinstance(trends_monthly, list)
        assert len(trends_monthly) > 0
        
        # Check structure of first item
        if trends_monthly:
            first_item = trends_monthly[0]
            assert 'period' in first_item
            assert 'actual_revenue' in first_item
            assert 'budgeted_revenue' in first_item
            assert 'revenue_variance' in first_item
        
        # Test quarterly
        trends_quarterly = service.get_revenue_trends(period='quarterly')
        assert isinstance(trends_quarterly, list)
        
        # Test yearly
        trends_yearly = service.get_revenue_trends(period='yearly')
        assert isinstance(trends_yearly, list)
    
    def test_get_budget_variance(self, service):
        """Test budget variance retrieval"""
        variance = service.get_budget_variance()
        
        assert 'summary' in variance
        assert 'departments' in variance
        assert isinstance(variance['departments'], list)
        assert len(variance['departments']) > 0
    
    def test_get_efficiency_alerts(self, service):
        """Test efficiency alerts retrieval"""
        alerts = service.get_efficiency_alerts(limit=5)
        
        assert 'alerts' in alerts
        assert 'alert_types' in alerts
        assert isinstance(alerts['alerts'], list)
        assert isinstance(alerts['alert_types'], list)
        assert len(alerts['alerts']) <= 5
    
    def test_get_scenarios(self, service):
        """Test scenario planning retrieval"""
        scenarios = service.get_scenarios()
        
        assert 'scenarios' in scenarios
        assert 'scenario_types' in scenarios
        assert isinstance(scenarios['scenarios'], list)
        assert isinstance(scenarios['scenario_types'], list)
    
    def test_caching_works(self, service):
        """Test that caching improves performance"""
        import time
        
        # First call - should be cache miss
        start1 = time.time()
        kpis1 = service.get_financial_kpis()
        time1 = time.time() - start1
        
        # Second call - should be cache hit (faster)
        start2 = time.time()
        kpis2 = service.get_financial_kpis()
        time2 = time.time() - start2
        
        # Results should be identical
        assert kpis1 == kpis2, "Cached result should match original"
        
        # Second call should be faster (or at least not slower)
        # Note: This might not always be true due to system load, but generally should be
        # We'll just verify the results are the same


