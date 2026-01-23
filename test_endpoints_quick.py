"""
Quick endpoint test to verify routes are working
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE_URL = "http://localhost:8084"

def test_endpoint(name, method, url, data=None, params=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
        
        status = response.status_code
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        if status == 200:
            return True, response_data
        else:
            return False, f"Status {status}: {response_data}"
    except requests.exceptions.ConnectionError:
        return False, "Server not running"
    except Exception as e:
        return False, str(e)

def main():
    print("="*70)
    print("  ENDPOINT TESTING")
    print("="*70)
    print(f"Base URL: {BASE_URL}\n")
    
    # Check if server is running
    print("1. Checking if server is running...")
    success, result = test_endpoint("Health", "GET", f"{BASE_URL}/health")
    if not success:
        print(f"   [FAIL] FAILED: {result}")
        print("\n[WARN] Server is not running! Please start it with: python app.py")
        return
    print(f"   [OK] Server is running: {result}\n")
    
    # Test AI endpoints
    print("2. Testing AI Endpoints:")
    print("-" * 70)
    
    tests = [
        ("AI Health", "GET", f"{BASE_URL}/api/v0/ai/health", None, None),
        ("Generate SQL", "GET", f"{BASE_URL}/api/v0/ai/generate-sql", None, {"question": "What is the total revenue?"}),
        ("Ask Question", "POST", f"{BASE_URL}/api/v0/ai/ask", {"question": "What was the total revenue in 2024?", "run_sql": False}, None),
    ]
    
    for name, method, url, data, params in tests:
        if params:
            success, result = test_endpoint(name, method, url, params=params)
        elif data:
            success, result = test_endpoint(name, method, url, data=data)
        else:
            success, result = test_endpoint(name, method, url)
        
        if success:
            print(f"   [OK] {name}: OK")
            if isinstance(result, dict):
                if 'sql' in result:
                    print(f"      SQL: {result.get('sql', '')[:80]}...")
                elif 'status' in result:
                    print(f"      Status: {result.get('status')}")
        else:
            print(f"   [FAIL] {name}: {result}")
    
    print("\n3. Testing Dashboard Endpoints:")
    print("-" * 70)
    
    dashboard_tests = [
        ("KPIs", "GET", f"{BASE_URL}/api/v0/dashboard/kpis"),
        ("Revenue Summary", "GET", f"{BASE_URL}/api/v0/dashboard/revenue/summary"),
    ]
    
    for name, method, url in dashboard_tests:
        success, result = test_endpoint(name, method, url)
        if success:
            print(f"   [OK] {name}: OK")
        else:
            print(f"   [FAIL] {name}: {result}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

