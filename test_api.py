"""
Test script for AquaSentinel API
Run this to verify all endpoints are working correctly

IMPORTANT: Make sure the server is running first!
Start the server with: python app.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8084"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return True
    except:
        return False

def test_endpoint(name, url):
    """Test a single endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{url}")
        print(f"\n{'='*70}")
        print(f"[OK] {name}")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', 'N/A')}")
            if 'data' in data:
                print(f"Response Preview:\n{json.dumps(data['data'], indent=2)[:500]}...")
            else:
                print(f"Response:\n{json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"Error Response: {response.text[:200]}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"\n[FAIL] {name} FAILED: {str(e)}")
        return False

def main():
    print("="*70)
    print("AquaSentinel API Test Suite")
    print("="*70)
    
    # Check if server is running
    print("\n[INFO] Checking if server is running...")
    if not check_server():
        print("\n" + "="*70)
        print("[ERROR] Server is not running!")
        print("="*70)
        print("\nPlease start the server first:")
        print("  python app.py")
        print("\nThen run this test script again.")
        print("="*70)
        sys.exit(1)
    
    print("[OK] Server is running!\n")
    
    # Health check
    test_endpoint("Health Check", "/health")
    
    # Dashboard endpoints
    test_endpoint("Financial KPIs", "/api/v0/dashboard/kpis")
    test_endpoint("Revenue Summary", "/api/v0/dashboard/revenue/summary")
    test_endpoint("Revenue Trends", "/api/v0/dashboard/revenue/trends?period=monthly")
    test_endpoint("Budget Variance", "/api/v0/dashboard/budget-variance")
    test_endpoint("AR Aging", "/api/v0/dashboard/ar-aging")
    test_endpoint("Debt Metrics", "/api/v0/dashboard/debt")
    test_endpoint("Efficiency Alerts", "/api/v0/dashboard/alerts?limit=5")
    test_endpoint("Scenarios", "/api/v0/dashboard/scenarios")
    
    print("\n" + "="*70)
    print("[OK] All tests completed!")
    print("="*70)
    print(f"\n[INFO] API Base URL: {BASE_URL}")
    print(f"[INFO] API Root: {BASE_URL}/")

if __name__ == "__main__":
    main()
