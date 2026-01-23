"""Quick demo of sample questions"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE_URL = "http://localhost:8084"

questions = [
    "What is the total revenue?",
    "Show me revenue by department",
    "What was the total revenue in 2024?",
]

print("\n" + "="*70)
print("SAMPLE QUESTIONS DEMO")
print("="*70 + "\n")

for i, question in enumerate(questions, 1):
    print(f"{i}. Question: {question}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json={"question": question, "run_sql": True},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   SQL: {data.get('sql', 'N/A')[:80]}...")
            if 'summary' in data and data['summary']:
                print(f"   Summary: {data['summary'][:100]}...")
            print("   ✅ Success\n")
        else:
            print(f"   ❌ Error: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}\n")

print("="*70)
print("See SUGGESTED_QUESTIONS.md for more examples!")
print("="*70)

