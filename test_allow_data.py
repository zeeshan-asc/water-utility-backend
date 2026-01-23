"""
Test that allow_llm_to_see_data is working correctly
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

def test_generate_sql():
    print("\n" + "="*70)
    print("TESTING allow_llm_to_see_data FIX")
    print("="*70 + "\n")
    
    question = "what was the revenue"
    
    print(f"Question: {question}")
    print("-" * 70)
    
    try:
        # Test generate-sql endpoint
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/generate-sql",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            sql = data.get('sql', '')
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Success: {data.get('success', False)}")
            print(f"✅ Type: {data.get('type', 'unknown')}")
            print(f"\nSQL Generated:")
            print(f"   {sql[:200]}...")
            
            # Check if we got the error message
            if "not allowed to see the data" in sql or "allow_llm_to_see_data" in sql:
                print("\n❌ ERROR: Still getting the 'not allowed to see data' error!")
                print("   The fix may not be working. Check server logs.")
            else:
                print("\n✅ SUCCESS: SQL generated without the 'not allowed' error!")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text[:300]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("   Please start the server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_generate_sql()




