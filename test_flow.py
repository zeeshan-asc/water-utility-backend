"""
Test the improved flow: if no SQL, go to summary; if SQL exists, run it then summary
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

def test_flow():
    print("\n" + "="*70)
    print("TESTING IMPROVED FLOW")
    print("="*70 + "\n")
    
    # Test 1: Normal flow - SQL exists, run it then summary
    print("Test 1: SQL exists - should run SQL then generate summary")
    print("-" * 70)
    try:
        # Step 1: Generate SQL
        response1 = requests.post(
            f"{BASE_URL}/api/v0/ai/generate-sql",
            json={"question": "What is the total revenue?"},
            timeout=30
        )
        if response1.status_code == 200:
            data1 = response1.json()
            sql = data1.get('sql')
            question = data1.get('question')
            print(f"✅ Generated SQL: {sql[:80]}...")
            
            # Step 2: Run SQL with summary generation
            response2 = requests.post(
                f"{BASE_URL}/api/v0/ai/run-sql",
                json={
                    "sql": sql,
                    "question": question,
                    "generate_summary": True
                },
                timeout=30
            )
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"✅ SQL executed: {data2.get('row_count', 0)} rows")
                if 'summary' in data2 and data2['summary']:
                    print(f"✅ Summary generated: {data2['summary'][:100]}...")
                else:
                    print("⚠️  No summary generated")
            else:
                print(f"❌ Run SQL failed: {response2.status_code}")
                print(f"   {response2.text[:200]}")
        else:
            print(f"❌ Generate SQL failed: {response1.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*70 + "\n")
    
    # Test 2: No SQL - should go directly to summary
    print("Test 2: No SQL provided - should generate summary directly")
    print("-" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/run-sql",
            json={
                "sql": "",  # Empty SQL
                "question": "What is the total revenue?",
                "generate_summary": True
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Summary generated directly: {data.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*70 + "\n")
    
    # Test 3: Using /ask endpoint (should handle both cases automatically)
    print("Test 3: Using /ask endpoint - should handle flow automatically")
    print("-" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json={
                "question": "What is the total revenue?",
                "run_sql": True
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Type: {data.get('type', 'unknown')}")
            if data.get('sql'):
                print(f"✅ SQL: {data['sql'][:80]}...")
            if data.get('data'):
                print(f"✅ Data: {data.get('row_count', 0)} rows")
            if data.get('summary'):
                print(f"✅ Summary: {data['summary'][:100]}...")
            else:
                print("⚠️  No summary")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_flow()




