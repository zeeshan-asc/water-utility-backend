"""
Display detailed responses from AI/ML endpoints
"""

import requests
import json
import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8084"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_response(response_data, indent=2):
    """Pretty print JSON response"""
    print(json.dumps(response_data, indent=indent, ensure_ascii=False))

def test_ai_health():
    """Test AI health endpoint"""
    print_section("1. AI Health Check - GET /api/v0/ai/health")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v0/ai/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        if response.status_code == 200:
            data = response.json()
            print_response(data)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_generate_sql():
    """Test SQL generation endpoint"""
    print_section("2. Generate SQL - GET /api/v0/ai/generate-sql")
    
    question = "What is the total revenue?"
    print(f"Question: {question}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v0/ai/generate-sql",
            params={"question": question},
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        if response.status_code == 200:
            data = response.json()
            print_response(data)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_ask_sql_only():
    """Test ask endpoint without SQL execution"""
    print_section("3. Ask Question (SQL Only) - POST /api/v0/ai/ask")
    
    payload = {
        "question": "What was the total revenue in 2024?",
        "run_sql": False
    }
    print(f"Question: {payload['question']}")
    print(f"Run SQL: {payload['run_sql']}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        if response.status_code == 200:
            data = response.json()
            print_response(data)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_ask_with_execution():
    """Test ask endpoint with SQL execution"""
    print_section("4. Ask Question (With SQL Execution) - POST /api/v0/ai/ask")
    
    payload = {
        "question": "What was the total revenue in 2024?",
        "run_sql": True
    }
    print(f"Question: {payload['question']}")
    print(f"Run SQL: {payload['run_sql']}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        if response.status_code == 200:
            data = response.json()
            print_response(data)
            
            # Show summary separately if present
            if 'summary' in data and data['summary']:
                print("\n" + "-"*80)
                print("SUMMARY:")
                print("-"*80)
                print(data['summary'])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_run_sql():
    """Test direct SQL execution"""
    print_section("5. Run SQL Directly - POST /api/v0/ai/run-sql")
    
    payload = {
        "sql": "SELECT COUNT(*) as total_records FROM water_data"
    }
    print(f"SQL Query: {payload['sql']}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/run-sql",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        if response.status_code == 200:
            data = response.json()
            print_response(data)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_error_handling():
    """Test error handling"""
    print_section("6. Error Handling - POST /api/v0/ai/ask (Missing Question)")
    
    payload = {}  # Missing question
    print("Request Payload: {} (missing 'question' field)\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID', 'N/A')}\n")
        
        data = response.json()
        print_response(data)
    except Exception as e:
        print(f"Error: {str(e)}")

def test_additional_questions():
    """Test additional natural language questions"""
    print_section("7. Additional Natural Language Questions")
    
    questions = [
        "Show me revenue by quarter for 2023",
        "Which departments had the highest budget variance?",
        "What is the average operating margin?",
        "Show me months with non-revenue water above 25%"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}: {question} ---\n")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v0/ai/ask",
                json={
                    "question": question,
                    "run_sql": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"SQL Generated:")
                print(f"  {data.get('sql', 'N/A')}")
                print(f"\nResults:")
                print(f"  Rows: {data.get('row_count', 0)}")
                print(f"  Columns: {data.get('column_count', 0)}")
                
                if data.get('data'):
                    print(f"\nData Preview (first 3 rows):")
                    preview = data['data'][:3]
                    print(json.dumps(preview, indent=2, ensure_ascii=False))
                
                if data.get('summary'):
                    print(f"\nSummary:")
                    print(f"  {data['summary'][:200]}...")
            else:
                print(f"Error: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  AI/ML ENDPOINT RESPONSES - DETAILED VIEW")
    print("="*80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("Server is not responding correctly")
            return
    except:
        print("ERROR: Server is not running!")
        print("Please start the server first: python app.py")
        return
    
    # Run all tests
    test_ai_health()
    test_generate_sql()
    test_ask_sql_only()
    test_ask_with_execution()
    test_run_sql()
    test_error_handling()
    test_additional_questions()
    
    print("\n" + "="*80)
    print("  ALL TESTS COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

