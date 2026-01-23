"""
Comprehensive Endpoint Testing Script

Tests all API endpoints (Dashboard + AI/ML) to ensure they work correctly.
Run this script while the server is running on http://localhost:8084
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Base URL
BASE_URL = "http://localhost:8084"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_test(name: str):
    """Print test name"""
    print(f"{Colors.BLUE}Testing: {Colors.RESET}{name}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.RESET}")

def test_endpoint(method: str, url: str, expected_status: int = 200, 
                  data: Dict[str, Any] = None, params: Dict[str, Any] = None,
                  description: str = "") -> tuple[bool, Dict[str, Any]]:
    """
    Test an API endpoint
    
    Returns:
        (success: bool, response_data: dict)
    """
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print_error(f"Unsupported method: {method}")
            return False, {}
        
        # Check status code
        if response.status_code != expected_status:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False, {}
        
        # Check response format
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print_error("Response is not valid JSON")
            return False, {}
        
        # Check Request ID header
        request_id = response.headers.get('X-Request-ID', '')
        if request_id:
            print_success(f"Request ID: {request_id}")
        
        # Check success field if present
        if 'success' in response_data:
            if not response_data['success']:
                print_error(f"API returned success=false: {response_data.get('error', 'Unknown error')}")
                return False, response_data
        
        print_success(f"Status: {response.status_code}")
        if description:
            print_info(description)
        
        return True, response_data
    
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed. Is the server running on {BASE_URL}?")
        return False, {}
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False, {}
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False, {}


def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    print_header("DASHBOARD ENDPOINTS")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Root endpoint
    print_test("GET /")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/")
    if success:
        results['passed'] += 1
        if 'endpoints' in data:
            print_success(f"Found {len(data.get('endpoints', {}))} endpoints")
    else:
        results['failed'] += 1
    
    # Test 2: Health check
    print_test("GET /health")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/health")
    if success:
        results['passed'] += 1
        if 'status' in data:
            print_success(f"Status: {data['status']}")
    else:
        results['failed'] += 1
    
    # Test 3: Financial KPIs
    print_test("GET /api/v0/dashboard/kpis")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/kpis")
    if success and 'data' in data:
        results['passed'] += 1
        kpis = data['data']
        print_success(f"Retrieved {len(kpis)} KPIs")
        if 'total_revenue' in kpis:
            print_info(f"Total Revenue: ${kpis.get('total_revenue', 0):.2f}M")
    else:
        results['failed'] += 1
    
    # Test 4: Revenue Summary
    print_test("GET /api/v0/dashboard/revenue/summary")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/revenue/summary")
    if success and 'data' in data:
        results['passed'] += 1
        summary = data['data']
        print_success("Revenue summary retrieved")
        if 'total_revenue' in summary:
            print_info(f"Total Revenue: ${summary.get('total_revenue', 0):.2f}M")
    else:
        results['failed'] += 1
    
    # Test 5: Revenue Trends (monthly)
    print_test("GET /api/v0/dashboard/revenue/trends?period=monthly")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/revenue/trends", 
                                  params={'period': 'monthly'})
    if success and 'data' in data:
        results['passed'] += 1
        trends = data['data']
        print_success(f"Retrieved {len(trends)} trend periods")
    else:
        results['failed'] += 1
    
    # Test 6: Revenue Trends (quarterly)
    print_test("GET /api/v0/dashboard/revenue/trends?period=quarterly")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/revenue/trends", 
                                  params={'period': 'quarterly'})
    if success and 'data' in data:
        results['passed'] += 1
        trends = data['data']
        print_success(f"Retrieved {len(trends)} quarterly trends")
    else:
        results['failed'] += 1
    
    # Test 7: Budget Variance
    print_test("GET /api/v0/dashboard/budget-variance")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/budget-variance")
    if success and 'data' in data:
        results['passed'] += 1
        variance_data = data['data']
        if isinstance(variance_data, list):
            print_success(f"Retrieved {len(variance_data)} variance records")
        else:
            print_success("Budget variance retrieved")
    else:
        results['failed'] += 1
    
    # Test 8: AR Aging
    print_test("GET /api/v0/dashboard/ar-aging")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/ar-aging")
    if success and 'data' in data:
        results['passed'] += 1
        ar_data = data['data']
        print_success("AR aging data retrieved")
        if 'total_ar' in ar_data:
            print_info(f"Total AR: ${ar_data.get('total_ar', 0):.2f}M")
    else:
        results['failed'] += 1
    
    # Test 9: Debt Metrics
    print_test("GET /api/v0/dashboard/debt")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/debt")
    if success and 'data' in data:
        results['passed'] += 1
        debt_data = data['data']
        print_success("Debt metrics retrieved")
        if 'debt_service_coverage' in debt_data:
            print_info(f"DSCR: {debt_data.get('debt_service_coverage', 0):.2f}")
    else:
        results['failed'] += 1
    
    # Test 10: Alerts
    print_test("GET /api/v0/dashboard/alerts")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/alerts")
    if success and 'data' in data:
        results['passed'] += 1
        alerts_data = data['data']
        if 'alerts' in alerts_data:
            print_success(f"Retrieved {len(alerts_data.get('alerts', []))} alerts")
        else:
            print_success("Alerts data retrieved")
    else:
        results['failed'] += 1
    
    # Test 11: Scenarios
    print_test("GET /api/v0/dashboard/scenarios")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/dashboard/scenarios")
    if success and 'data' in data:
        results['passed'] += 1
        scenarios_data = data['data']
        if 'scenarios' in scenarios_data:
            print_success(f"Retrieved {len(scenarios_data.get('scenarios', []))} scenarios")
        else:
            print_success("Scenarios data retrieved")
    else:
        results['failed'] += 1
    
    return results


def test_ai_endpoints():
    """Test all AI/ML endpoints"""
    print_header("AI/ML ENDPOINTS")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: AI Health Check
    print_test("GET /api/v0/ai/health")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/ai/health")
    if success:
        results['passed'] += 1
        if 'status' in data:
            print_success(f"AI Status: {data.get('status', 'unknown')}")
    else:
        results['failed'] += 1
        print_info("AI endpoints may not work if AI service is not configured")
        return results
    
    # Test 2: Generate SQL (simple question)
    print_test("GET /api/v0/ai/generate-sql?question=What is the total revenue?")
    results['total'] += 1
    success, data = test_endpoint('GET', f"{BASE_URL}/api/v0/ai/generate-sql",
                                  params={'question': 'What is the total revenue?'})
    if success and 'sql' in data:
        results['passed'] += 1
        print_success("SQL generated successfully")
        print_info(f"SQL: {data.get('sql', '')[:100]}...")
    else:
        results['failed'] += 1
    
    # Test 3: Ask Question (without running SQL)
    print_test("POST /api/v0/ai/ask (SQL only)")
    results['total'] += 1
    success, data = test_endpoint('POST', f"{BASE_URL}/api/v0/ai/ask",
                                  data={
                                      'question': 'What was the total revenue in 2024?',
                                      'run_sql': False
                                  })
    if success and 'sql' in data:
        results['passed'] += 1
        print_success("Question processed successfully")
        print_info(f"SQL: {data.get('sql', '')[:100]}...")
    else:
        results['failed'] += 1
    
    # Test 4: Ask Question (with SQL execution)
    print_test("POST /api/v0/ai/ask (with SQL execution)")
    results['total'] += 1
    success, data = test_endpoint('POST', f"{BASE_URL}/api/v0/ai/ask",
                                  data={
                                      'question': 'What was the total revenue in 2024?',
                                      'run_sql': True
                                  })
    if success:
        results['passed'] += 1
        if 'data' in data:
            print_success("SQL executed successfully")
            print_info(f"Rows returned: {data.get('row_count', 0)}")
            if 'summary' in data:
                print_info(f"Summary: {data.get('summary', '')[:100]}...")
        else:
            print_success("Question processed (no data returned)")
    else:
        results['failed'] += 1
    
    # Test 5: Run SQL directly
    print_test("POST /api/v0/ai/run-sql")
    results['total'] += 1
    success, data = test_endpoint('POST', f"{BASE_URL}/api/v0/ai/run-sql",
                                  data={
                                      'sql': 'SELECT COUNT(*) as total_records FROM water_data'
                                  })
    if success and 'data' in data:
        results['passed'] += 1
        print_success("SQL executed successfully")
        print_info(f"Rows returned: {data.get('row_count', 0)}")
    else:
        results['failed'] += 1
    
    # Test 6: Error handling - missing question
    print_test("POST /api/v0/ai/ask (error handling)")
    results['total'] += 1
    success, data = test_endpoint('POST', f"{BASE_URL}/api/v0/ai/ask",
                                  expected_status=400,
                                  data={})
    if not success or (data.get('success') == False):
        results['passed'] += 1
        print_success("Error handling works correctly")
    else:
        results['failed'] += 1
    
    return results


def print_summary(dashboard_results: Dict, ai_results: Dict):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_passed = dashboard_results['passed'] + ai_results['passed']
    total_failed = dashboard_results['failed'] + ai_results['failed']
    total_tests = dashboard_results['total'] + ai_results['total']
    
    print(f"{Colors.BOLD}Dashboard Endpoints:{Colors.RESET}")
    print(f"  Passed: {Colors.GREEN}{dashboard_results['passed']}{Colors.RESET} / {dashboard_results['total']}")
    print(f"  Failed: {Colors.RED}{dashboard_results['failed']}{Colors.RESET} / {dashboard_results['total']}")
    
    print(f"\n{Colors.BOLD}AI/ML Endpoints:{Colors.RESET}")
    print(f"  Passed: {Colors.GREEN}{ai_results['passed']}{Colors.RESET} / {ai_results['total']}")
    print(f"  Failed: {Colors.RED}{ai_results['failed']}{Colors.RESET} / {ai_results['total']}")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.RESET}")
    print(f"  Total Passed: {Colors.GREEN}{total_passed}{Colors.RESET} / {total_tests}")
    print(f"  Total Failed: {Colors.RED}{total_failed}{Colors.RESET} / {total_tests}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  Success Rate: {Colors.GREEN if success_rate >= 80 else Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
    
    if total_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some tests failed. Check the output above for details.{Colors.RESET}")


def main():
    """Main test function"""
    print_header("AQUASENTINEL API ENDPOINT TESTING")
    print(f"{Colors.CYAN}Testing endpoints on: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.CYAN}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is running and responding")
        else:
            print_error(f"Server returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Please start the server first: python app.py")
        return
    
    # Run tests
    dashboard_results = test_dashboard_endpoints()
    ai_results = test_ai_endpoints()
    
    # Print summary
    print_summary(dashboard_results, ai_results)


if __name__ == "__main__":
    main()

