"""Display test questions"""
import json

with open('test_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print("=" * 80)
print("20 TEST QUESTIONS FOR VANNA AI (Different from Training Data)")
print("=" * 80)
print()

for i, q in enumerate(questions, 1):
    print(f"{i}. {q['question']}")
    print(f"   Category: {q['category']}")
    print()

print("=" * 80)
print(f"Total: {len(questions)} questions")
print("=" * 80)







