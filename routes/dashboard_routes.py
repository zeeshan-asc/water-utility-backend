"""
Dashboard Routes

Thin controller layer for dashboard API endpoints.
Follows SOLID principles - routes only handle HTTP concerns.
"""

from flask import Blueprint, request, jsonify, g
import logging
from services.dashboard_service import DashboardService

logger = logging.getLogger('aquasentinel.api')

def get_request_id():
    """Get request ID from Flask g object, fallback to 'unknown'."""
    return getattr(g, 'request_id', 'unknown')

# Create Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v0/dashboard')

# Initialize service
dashboard_service = DashboardService()


@dashboard_bp.route('/kpis', methods=['GET'])
def get_financial_kpis():
    """
    Get current financial KPIs for the dashboard header.
    
    Returns:
        JSON response with all financial KPIs with changes
    """
    try:
        request_id = get_request_id()
        logger.info(f"[{request_id}] Financial KPIs requested")
        
        result = dashboard_service.get_financial_kpis()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        request_id = get_request_id()
        logger.error(f"[{request_id}] Error in financial KPIs endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/revenue/summary', methods=['GET'])
def get_revenue_summary():
    """
    Get revenue performance summary with variance analysis.
    
    Returns:
        JSON response with revenue summary
    """
    try:
        request_id = get_request_id()
        logger.info(f"[{request_id}] Revenue summary requested")
        
        result = dashboard_service.get_revenue_summary()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        request_id = get_request_id()
        logger.error(f"[{request_id}] Error in revenue summary endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/revenue/trends', methods=['GET'])
def get_revenue_trends():
    """
    Get revenue trends over time for charting.
    
    Query Parameters:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        period: Optional period aggregation (monthly/quarterly/yearly)
        
    Returns:
        JSON response with revenue trend data
    """
    try:
        start_date = request.args.get('start_date', default=None)
        end_date = request.args.get('end_date', default=None)
        period = request.args.get('period', default='monthly')
        
        request_id = get_request_id()
        logger.info(f"[{request_id}] Revenue trends requested - period: {period}")
        
        result = dashboard_service.get_revenue_trends(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        request_id = get_request_id()
        logger.error(f"[{request_id}] Error in revenue trends endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/budget-variance', methods=['GET'])
def get_budget_variance():
    """
    Get budget variance by department.
    
    Query Parameters:
        department: Optional department filter
        year: Optional year filter
        
    Returns:
        JSON response with budget variance data
    """
    try:
        department = request.args.get('department', default=None)
        year = request.args.get('year', default=None, type=int)
        
        request_id = get_request_id()
        logger.info(f"[{request_id}] Budget variance requested - department: {department}, year: {year}")
        
        result = dashboard_service.get_budget_variance(
            department=department,
            year=year
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        request_id = get_request_id()
        logger.error(f"[{request_id}] Error in budget variance endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/ar-aging', methods=['GET'])
def get_ar_aging():
    """
    Get current accounts receivable aging distribution.
    
    Returns:
        JSON response with AR aging data
    """
    try:
        request_id = get_request_id()
        logger.info(f"[{request_id}] AR aging requested")
        
        result = dashboard_service.get_ar_aging()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in AR aging endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/debt', methods=['GET'])
def get_debt_metrics():
    """
    Get current debt sustainability metrics.
    
    Returns:
        JSON response with debt metrics
    """
    try:
        request_id = get_request_id()
        logger.info(f"[{request_id}] Debt metrics requested")
        
        result = dashboard_service.get_debt_metrics()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in debt metrics endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/alerts', methods=['GET'])
def get_efficiency_alerts():
    """
    Get efficiency alerts and optimization opportunities.
    
    Query Parameters:
        alert_type: Optional alert type filter
        limit: Maximum number of alerts (default: 10)
        
    Returns:
        JSON response with alerts data
    """
    try:
        alert_type = request.args.get('alert_type', default=None)
        limit = request.args.get('limit', default=10, type=int)
        
        request_id = get_request_id()
        logger.info(f"[{request_id}] Efficiency alerts requested - type: {alert_type}, limit: {limit}")
        
        result = dashboard_service.get_efficiency_alerts(
            alert_type=alert_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in efficiency alerts endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    """
    Get scenario planning projections.
    
    Query Parameters:
        year: Optional year filter
        
    Returns:
        JSON response with scenario data
    """
    try:
        year = request.args.get('year', default=None, type=int)
        
        request_id = get_request_id()
        logger.info(f"[{request_id}] Scenarios requested - year: {year}")
        
        result = dashboard_service.get_scenarios(year=year)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in scenarios endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

