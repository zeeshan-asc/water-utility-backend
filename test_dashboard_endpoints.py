"""Test dashboard endpoints to verify fixes"""
import requests
import json

endpoints = [
    '/api/v0/dashboard/budget-variance',
    '/api/v0/dashboard/scenarios',
    '/api/v0/dashboard/alerts?limit=4',
]

base_url = 'http://localhost:8084'

print("=" * 80)
print("Testing Dashboard Endpoints")
print("=" * 80)

for endpoint in endpoints:
    print(f"\nTesting: {endpoint}")
    print("-" * 80)
    try:
        r = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Success: {data.get('success', False)}")
            if 'data' in data:
                print(f"Data keys: {list(data['data'].keys())}")
                # Show sample data
                for key, value in data['data'].items():
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"Error: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {str(e)}")

print("\n" + "=" * 80)
print("Note: If you see 500 errors, restart the Flask app for changes to take effect")
print("=" * 80)


