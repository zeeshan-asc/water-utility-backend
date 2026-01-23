"""
Comprehensive test suite for all API endpoints
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8084"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(name):
    print(f"{Colors.BLUE}Testing: {Colors.RESET}{name}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.RESET}")

def test_endpoint(name, method, url, expected_status=200, data=None, params=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        else:
            return False, f"Unsupported method: {method}"
        
        success = response.status_code == expected_status
        
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200]
        
        return success, response_data
    
    except requests.exceptions.ConnectionError:
        return False, "Server not running"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, str(e)

def main():
    print_header("COMPREHENSIVE API TEST SUITE")
    print(f"{Colors.CYAN}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.CYAN}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Server Health
    print_header("SERVER HEALTH")
    print_test("GET /health")
    results['total'] += 1
    success, data = test_endpoint("Health", "GET", f"{BASE_URL}/health")
    if success:
        results['passed'] += 1
        print_success("Server is running")
        if isinstance(data, dict):
            print_info(f"Status: {data.get('status', 'unknown')}")
    else:
        results['failed'] += 1
        print_error(f"Server health check failed: {data}")
        print("\n[ERROR] Server is not running! Please start it with: python app.py")
        return
    
    # Test 2: Dashboard Endpoints
    print_header("DASHBOARD ENDPOINTS")
    
    dashboard_tests = [
        ("KPIs", "GET", f"{BASE_URL}/api/v0/dashboard/kpis"),
        ("Revenue Summary", "GET", f"{BASE_URL}/api/v0/dashboard/revenue/summary"),
        ("Revenue Trends (Monthly)", "GET", f"{BASE_URL}/api/v0/dashboard/revenue/trends", None, {"period": "monthly"}),
        ("Revenue Trends (Quarterly)", "GET", f"{BASE_URL}/api/v0/dashboard/revenue/trends", None, {"period": "quarterly"}),
        ("Budget Variance", "GET", f"{BASE_URL}/api/v0/dashboard/budget-variance"),
        ("AR Aging", "GET", f"{BASE_URL}/api/v0/dashboard/ar-aging"),
        ("Debt Metrics", "GET", f"{BASE_URL}/api/v0/dashboard/debt"),
        ("Alerts", "GET", f"{BASE_URL}/api/v0/dashboard/alerts"),
        ("Scenarios", "GET", f"{BASE_URL}/api/v0/dashboard/scenarios"),
    ]
    
    for name, method, url, *args in dashboard_tests:
        params = args[0] if args and isinstance(args[0], dict) else None
        print_test(f"{name}")
        results['total'] += 1
        success, data = test_endpoint(name, method, url, params=params)
        if success:
            results['passed'] += 1
            print_success(f"{name}")
            if isinstance(data, dict) and 'data' in data:
                if isinstance(data['data'], list):
                    print_info(f"Returned {len(data['data'])} items")
                elif isinstance(data['data'], dict):
                    print_info("Data retrieved successfully")
        else:
            results['failed'] += 1
            print_error(f"{name}: {data}")
    
    # Test 3: AI Endpoints
    print_header("AI/ML ENDPOINTS")
    
    # AI Health
    print_test("AI Health Check")
    results['total'] += 1
    success, data = test_endpoint("AI Health", "GET", f"{BASE_URL}/api/v0/ai/health")
    if success:
        results['passed'] += 1
        print_success("AI Health Check")
        if isinstance(data, dict):
            print_info(f"Status: {data.get('status', 'unknown')}")
            print_info(f"Service: {data.get('service', 'unknown')}")
    else:
        results['failed'] += 1
        print_error(f"AI Health: {data}")
    
    # Generate SQL - GET
    print_test("Generate SQL (GET)")
    results['total'] += 1
    success, data = test_endpoint("Generate SQL GET", "GET", 
                                  f"{BASE_URL}/api/v0/ai/generate-sql",
                                  params={"question": "What is the total revenue?"})
    if success:
        results['passed'] += 1
        print_success("Generate SQL (GET)")
        if isinstance(data, dict) and 'sql' in data:
            print_info(f"SQL: {data['sql'][:80]}...")
    else:
        results['failed'] += 1
        print_error(f"Generate SQL (GET): {data}")
    
    # Generate SQL - POST
    print_test("Generate SQL (POST)")
    results['total'] += 1
    success, data = test_endpoint("Generate SQL POST", "POST",
                                  f"{BASE_URL}/api/v0/ai/generate-sql",
                                  data={"question": "What is the total revenue?"})
    if success:
        results['passed'] += 1
        print_success("Generate SQL (POST)")
        if isinstance(data, dict) and 'sql' in data:
            print_info(f"SQL: {data['sql'][:80]}...")
    else:
        results['failed'] += 1
        print_error(f"Generate SQL (POST): {data}")
    
    # Ask Question (SQL only)
    print_test("Ask Question (SQL only)")
    results['total'] += 1
    success, data = test_endpoint("Ask SQL Only", "POST",
                                  f"{BASE_URL}/api/v0/ai/ask",
                                  data={"question": "What was the total revenue in 2024?", "run_sql": False})
    if success:
        results['passed'] += 1
        print_success("Ask Question (SQL only)")
        if isinstance(data, dict) and 'sql' in data:
            print_info(f"SQL: {data['sql'][:80]}...")
    else:
        results['failed'] += 1
        print_error(f"Ask Question (SQL only): {data}")
    
    # Ask Question (with execution)
    print_test("Ask Question (with SQL execution)")
    results['total'] += 1
    success, data = test_endpoint("Ask with Execution", "POST",
                                  f"{BASE_URL}/api/v0/ai/ask",
                                  data={"question": "What was the total revenue in 2024?", "run_sql": True})
    if success:
        results['passed'] += 1
        print_success("Ask Question (with execution)")
        if isinstance(data, dict):
            if 'data' in data:
                print_info(f"Rows: {data.get('row_count', 0)}")
            if 'summary' in data:
                print_info("Summary generated")
    else:
        results['failed'] += 1
        print_error(f"Ask Question (with execution): {data}")
    
    # Run SQL
    print_test("Run SQL Directly")
    results['total'] += 1
    success, data = test_endpoint("Run SQL", "POST",
                                  f"{BASE_URL}/api/v0/ai/run-sql",
                                  data={"sql": "SELECT COUNT(*) as total FROM water_data"})
    if success:
        results['passed'] += 1
        print_success("Run SQL")
        if isinstance(data, dict) and 'data' in data:
            print_info(f"Rows: {data.get('row_count', 0)}")
    else:
        results['failed'] += 1
        print_error(f"Run SQL: {data}")
    
    # Generate Summary
    print_test("Generate Summary")
    results['total'] += 1
    success, data = test_endpoint("Generate Summary", "POST",
                                  f"{BASE_URL}/api/v0/vanna/generate_summary",
                                  data={"question": "What was the total revenue?", 
                                        "sql": "SELECT SUM(actual_revenue) FROM water_data"})
    if success:
        results['passed'] += 1
        print_success("Generate Summary")
        if isinstance(data, dict) and 'summary' in data:
            print_info("Summary generated successfully")
    else:
        results['failed'] += 1
        print_error(f"Generate Summary: {data}")
    
    # Test 4: Error Handling
    print_header("ERROR HANDLING")
    
    print_test("Missing Question Parameter")
    results['total'] += 1
    success, data = test_endpoint("Error Handling", "POST",
                                  f"{BASE_URL}/api/v0/ai/ask",
                                  expected_status=400,
                                  data={})
    if not success or (isinstance(data, dict) and data.get('success') == False):
        results['passed'] += 1
        print_success("Error handling works correctly")
    else:
        results['failed'] += 1
        print_error("Error handling test failed")
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_passed = results['passed']
    total_failed = results['failed']
    total_tests = results['total']
    
    print(f"{Colors.BOLD}Total Tests: {total_tests}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {total_failed}{Colors.RESET}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"{Colors.BOLD}Success Rate: {Colors.GREEN if success_rate >= 80 else Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
    
    if total_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some tests failed. Check the output above for details.{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

if __name__ == "__main__":
    main()





