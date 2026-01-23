"""
Test script for AI/ML endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8084"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_ai_health():
    """Test AI health endpoint"""
    print("\n" + "="*60)
    print("Testing AI Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/v0/ai/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate_sql():
    """Test SQL generation"""
    print("\n" + "="*60)
    print("Testing Generate SQL Endpoint")
    print("="*60)
    try:
        question = "What was the total revenue in 2024?"
        response = requests.get(
            f"{BASE_URL}/api/v0/ai/generate-sql",
            params={"question": question},
            timeout=30
        )
        print(f"Question: {question}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"SQL: {data.get('sql', 'N/A')}")
        print(f"Type: {data.get('type', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_ask_question():
    """Test ask endpoint with SQL execution"""
    print("\n" + "="*60)
    print("Testing Ask Endpoint (with SQL execution)")
    print("="*60)
    try:
        payload = {
            "question": "What was the total revenue in 2024?",
            "run_sql": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json=payload,
            timeout=30
        )
        print(f"Question: {payload['question']}")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            print(f"SQL: {data.get('sql', 'N/A')[:200]}...")
            print(f"Row Count: {data.get('row_count', 0)}")
            print(f"Column Count: {data.get('column_count', 0)}")
            if data.get('data'):
                print(f"Sample Data: {json.dumps(data['data'][:2], indent=2)}")
            if data.get('summary'):
                print(f"Summary: {data['summary'][:200]}...")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ask_simple():
    """Test ask endpoint with simple question"""
    print("\n" + "="*60)
    print("Testing Ask Endpoint (simple question)")
    print("="*60)
    try:
        payload = {
            "question": "Show me revenue by quarter for 2023",
            "run_sql": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json=payload,
            timeout=30
        )
        print(f"Question: {payload['question']}")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            print(f"SQL: {data.get('sql', 'N/A')}")
            print(f"Row Count: {data.get('row_count', 0)}")
            if data.get('data'):
                print(f"Data: {json.dumps(data['data'], indent=2)}")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI/ML Backend Test Suite")
    print("="*60)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("Server is running!")
    except:
        print("ERROR: Server is not running!")
        print("Please start the server with: python app.py")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("AI Health Check", test_ai_health()))
    results.append(("Generate SQL", test_generate_sql()))
    results.append(("Ask Question (Total Revenue)", test_ask_question()))
    results.append(("Ask Question (Revenue by Quarter)", test_ask_simple()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

