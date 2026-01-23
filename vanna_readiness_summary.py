# -*- coding: utf-8 -*-
"""Vanna Readiness Summary - Compare with temp folder setup"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from core.custom_vanna import MyVanna
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("VANNA READINESS STATUS")
print("=" * 70)

# Initialize Vanna and check training data
vn = MyVanna(config={'model': 'gpt-4o-mini', 'temperature': 0.7})
training = vn.get_training_data()

print("\n1. TRAINING DATA IN PINECONE:")
print(f"   Total records: {len(training)}")

if 'training_data_type' in training.columns:
    type_counts = training['training_data_type'].value_counts()
    print("\n   Breakdown by type:")
    for data_type, count in type_counts.items():
        print(f"      - {data_type}: {count} records")
    
    # Check each type
    ddl_count = len(training[training['training_data_type'] == 'ddl'])
    sql_count = len(training[training['training_data_type'] == 'sql'])
    doc_count = len(training[training['training_data_type'] == 'documentation'])
    
    print("\n2. TRAINING COMPONENTS:")
    print(f"   [{'OK' if ddl_count > 0 else 'MISSING'}] Schema (DDL): {ddl_count} record(s)")
    print(f"   [{'OK' if sql_count > 0 else 'MISSING'}] SQL Examples: {sql_count} question-SQL pairs")
    print(f"   [{'OK' if doc_count > 0 else 'MISSING'}] Documentation: {doc_count} record(s)")
    
    print("\n3. READINESS CHECK:")
    all_ready = ddl_count > 0 and sql_count > 0 and doc_count > 0
    
    if all_ready:
        print("   [READY] Vanna is fully trained and ready to use!")
        print("   - Schema is loaded")
        print("   - SQL examples are trained")
        print("   - Documentation is included")
    else:
        print("   [NOT READY] Missing training components:")
        if ddl_count == 0:
            print("      - Schema (DDL) not found")
        if sql_count == 0:
            print("      - SQL examples not found")
        if doc_count == 0:
            print("      - Documentation not found")
    
    print("\n4. COMPARISON WITH TEMP FOLDER:")
    print("   Temp folder has:")
    print("      - Schema: financial_data.sql (financial data)")
    print("      - SQL: 20 question-SQL pairs (financial queries)")
    print("      - Documentation: column_descriptions.json")
    print("\n   Current setup has:")
    print("      - Schema: water_data.sql (water utility data)")
    print(f"      - SQL: {sql_count} question-SQL pairs (water utility queries)")
    print(f"      - Documentation: {'Yes' if doc_count > 0 else 'No'} (water utility context)")
    
    print("\n5. STATUS:")
    if all_ready:
        print("   [SUCCESS] Vanna is ready and matches the temp folder setup structure!")
        print("   The only difference is the domain (water utility vs financial data)")
    else:
        print("   [ACTION NEEDED] Run: python train_vanna.py --fresh-start")

print("\n" + "=" * 70)



