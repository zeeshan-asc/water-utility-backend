"""Test script for chatbot functionality"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_conversational():
    """Test conversational questions"""
    print("\n" + "="*60)
    print("Testing Conversational Questions")
    print("="*60)
    
    questions = [
        "hi",
        "hello",
        "how are you?",
        "what can you do?",
        "help me",
        "thanks"
    ]
    
    for question in questions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v0/ai/ask",
                json={"question": question, "run_sql": True},
                timeout=30
            )
            data = response.json()
            
            print(f"\nQuestion: {question}")
            print(f"  Type: {data.get('type')}")
            if data.get('text'):
                print(f"  Response: {data.get('text')[:100]}...")
            if data.get('sql'):
                print(f"  SQL: {data.get('sql')[:80]}...")
            print(f"  Success: {data.get('success')}")
            
        except Exception as e:
            print(f"  Error: {e}")

def test_sql_queries():
    """Test SQL queries"""
    print("\n" + "="*60)
    print("Testing SQL Queries")
    print("="*60)
    
    questions = [
        "What was the total revenue in 2024?",
        "Show me revenue by quarter for 2023"
    ]
    
    for question in questions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v0/ai/ask",
                json={"question": question, "run_sql": True},
                timeout=30
            )
            data = response.json()
            
            print(f"\nQuestion: {question}")
            print(f"  Type: {data.get('type')}")
            if data.get('sql'):
                print(f"  SQL: {data.get('sql')[:80]}...")
            if data.get('data'):
                print(f"  Data: {len(data.get('data'))} rows")
            print(f"  Success: {data.get('success')}")
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("Chatbot Test Suite")
    test_conversational()
    test_sql_queries()
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

