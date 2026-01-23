"""Test Vanna AI endpoint with the specific question"""
import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_URL = "http://localhost:8084/api/v0/ai/ask"
QUESTION = "Show me months with non-revenue water above 25%"

print("=" * 80)
print("Testing Vanna AI Endpoint")
print("=" * 80)
print(f"Question: {QUESTION}")
print(f"Endpoint: {API_URL}")
print()

try:
    # Test the ask endpoint
    payload = {
        "question": QUESTION,
        "run_sql": True
    }
    
    print("Sending request...")
    response = requests.post(API_URL, json=payload, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("=" * 80)
        print("Response:")
        print("=" * 80)
        print(json.dumps(data, indent=2))
        
        print()
        print("=" * 80)
        print("Analysis:")
        print("=" * 80)
        
        if data.get('success'):
            sql = data.get('sql', '')
            print(f"✓ Success: {data.get('success')}")
            print(f"✓ SQL Generated: {sql[:200]}...")
            print(f"✓ Type: {data.get('type', 'unknown')}")
            
            if 'data' in data and data['data']:
                print(f"✓ Rows Returned: {data.get('row_count', 0)}")
                print(f"✓ Columns Returned: {data.get('column_count', 0)}")
            else:
                print("⚠ No data returned (empty result or SQL not executed)")
            
            if 'summary' in data and data.get('summary'):
                print(f"✓ Summary: {data.get('summary', '')[:200]}...")
            
            if 'error' in data:
                print(f"✗ Error: {data.get('error')}")
        else:
            print(f"✗ Failed: {data.get('error', 'Unknown error')}")
    else:
        print(f"✗ Request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to the API")
    print("  Make sure the Flask app is running on http://localhost:8084")
    print("  Run: python app.py")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()


