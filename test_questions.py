"""
Interactive script to test various questions on the AI/ML endpoints
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

# Sample questions organized by category
QUESTIONS = {
    "Financial": [
        "What is the total revenue?",
        "What was the total revenue in 2024?",
        "Show me revenue by department",
        "Which department has the highest revenue?",
        "What is the budget variance?",
        "Show me departments with negative budget variance",
    ],
    "Trends": [
        "Show me revenue trends by month",
        "What are the quarterly revenue trends?",
        "Display revenue trends by year",
        "Compare revenue between 2023 and 2024",
    ],
    "AR & Debt": [
        "What is the total accounts receivable?",
        "Show me AR aging breakdown",
        "What is the total debt?",
        "Show me debt metrics",
    ],
    "Alerts": [
        "Show me all active alerts",
        "What alerts are currently active?",
        "Display critical alerts",
    ],
    "Complex": [
        "Show me revenue with corresponding budget variance",
        "Find departments where revenue increased by more than 10%",
        "Show me the top 5 departments by revenue",
    ]
}

def test_question(question, run_sql=True):
    """Test a single question"""
    print(f"\n{'='*70}")
    print(f"Question: {question}")
    print(f"{'='*70}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v0/ai/ask",
            json={"question": question, "run_sql": run_sql},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Success!")
            print(f"\n📝 Generated SQL:")
            print(f"   {data.get('sql', 'N/A')}")
            
            if run_sql and 'data' in data:
                print(f"\n📊 Results:")
                print(f"   Rows returned: {data.get('row_count', 0)}")
                if data.get('data'):
                    # Show first few rows
                    rows = data['data'][:3]
                    for i, row in enumerate(rows, 1):
                        print(f"   Row {i}: {row}")
                    if len(data['data']) > 3:
                        print(f"   ... and {len(data['data']) - 3} more rows")
            
            if 'summary' in data and data['summary']:
                print(f"\n📄 Summary:")
                print(f"   {data['summary']}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("AI/ML QUESTION TESTING SCRIPT")
    print("="*70)
    print(f"\nBase URL: {BASE_URL}\n")
    
    print("Choose an option:")
    print("1. Test all questions (SQL only)")
    print("2. Test all questions (with execution)")
    print("3. Test by category")
    print("4. Enter custom question")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🧪 Testing all questions (SQL generation only)...\n")
        for category, questions in QUESTIONS.items():
            print(f"\n📁 Category: {category}")
            for question in questions:
                test_question(question, run_sql=False)
    
    elif choice == "2":
        print("\n🧪 Testing all questions (with SQL execution)...\n")
        for category, questions in QUESTIONS.items():
            print(f"\n📁 Category: {category}")
            for question in questions:
                test_question(question, run_sql=True)
    
    elif choice == "3":
        print("\n📁 Available categories:")
        for i, category in enumerate(QUESTIONS.keys(), 1):
            print(f"   {i}. {category}")
        
        cat_choice = input("\nEnter category number: ").strip()
        try:
            cat_index = int(cat_choice) - 1
            category = list(QUESTIONS.keys())[cat_index]
            questions = QUESTIONS[category]
            
            print(f"\n🧪 Testing questions from '{category}' category...\n")
            for question in questions:
                test_question(question, run_sql=True)
        except (ValueError, IndexError):
            print("❌ Invalid category number")
    
    elif choice == "4":
        question = input("\nEnter your question: ").strip()
        if question:
            run_sql = input("Execute SQL? (y/n): ").strip().lower() == 'y'
            test_question(question, run_sql=run_sql)
        else:
            print("❌ No question provided")
    
    elif choice == "5":
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()




