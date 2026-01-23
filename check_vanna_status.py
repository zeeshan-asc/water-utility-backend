# -*- coding: utf-8 -*-
"""Check Vanna training status and compare with temp folder setup"""

import sys
import io
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("VANNA TRAINING STATUS CHECK")
print("=" * 70)

# Check current training SQL data
print("\n1. Current Training SQL Data (training_sql_data.json):")
current_sql_file = Path("training_sql_data.json")
if current_sql_file.exists():
    with open(current_sql_file, 'r') as f:
        current_data = json.load(f)
    print(f"   [OK] Found {len(current_data)} question-SQL pairs")
    print(f"   [OK] Sample questions:")
    for i, pair in enumerate(current_data[:3], 1):
        print(f"      {i}. {pair['question'][:70]}...")
else:
    print("   [ERROR] File not found!")

# Check temp folder training SQL data
print("\n2. Temp Folder Training SQL Data (temp/utmb-backend/training_sql_data.json):")
temp_sql_file = Path("temp/utmb-backend/training_sql_data.json")
if temp_sql_file.exists():
    with open(temp_sql_file, 'r') as f:
        temp_data = json.load(f)
    
    # Handle different formats
    if isinstance(temp_data, dict) and 'training_pairs' in temp_data:
        pairs = temp_data['training_pairs']
        print(f"   [OK] Found {len(pairs)} question-SQL pairs")
        print(f"   [OK] Sample questions:")
        for i, pair in enumerate(pairs[:3], 1):
            print(f"      {i}. {pair['question'][:70]}...")
    elif isinstance(temp_data, list):
        print(f"   [OK] Found {len(temp_data)} question-SQL pairs")
        print(f"   [OK] Sample questions:")
        for i, pair in enumerate(temp_data[:3], 1):
            print(f"      {i}. {pair['question'][:70]}...")
    else:
        print(f"   [WARNING] Unknown format in temp file")
else:
    print("   [WARNING] Temp file not found (may not exist)")

# Check schema files
print("\n3. Schema Files:")
current_schema = Path("schema/water_data.sql")
temp_schema = Path("temp/utmb-backend/schema/financial_data.sql")

if current_schema.exists():
    with open(current_schema, 'r') as f:
        current_schema_content = f.read()
    print(f"   [OK] Current schema: {len(current_schema_content)} characters")
    print(f"   [OK] Tables defined: {current_schema_content.count('CREATE TABLE')}")
else:
    print("   [ERROR] Current schema not found!")

if temp_schema.exists():
    with open(temp_schema, 'r') as f:
        temp_schema_content = f.read()
    print(f"   [OK] Temp schema: {len(temp_schema_content)} characters")
    print(f"   [OK] Tables defined: {temp_schema_content.count('CREATE TABLE')}")
else:
    print("   [WARNING] Temp schema not found")

# Check Vanna training data in Pinecone
print("\n4. Vanna Training Data in Pinecone:")
try:
    from core.custom_vanna import MyVanna
    from dotenv import load_dotenv
    load_dotenv()
    
    vn = MyVanna(config={'model': 'gpt-4o-mini', 'temperature': 0.7})
    training_data = vn.get_training_data()
    
    if training_data is not None and not training_data.empty:
        print(f"   [OK] Total training records: {len(training_data)}")
        
        if 'training_data_type' in training_data.columns:
            type_counts = training_data['training_data_type'].value_counts()
            print(f"   [OK] Training data by type:")
            for data_type, count in type_counts.items():
                print(f"      - {data_type}: {count} records")
        
        print(f"   [OK] Sample training records:")
        for i, row in training_data.head(3).iterrows():
            question = row.get('question', 'N/A')
            if question and len(question) > 70:
                question = question[:70] + "..."
            print(f"      {i+1}. [{row.get('training_data_type', 'unknown')}] {question}")
    else:
        print("   [WARNING] No training data found in Pinecone!")
        
except Exception as e:
    print(f"   [ERROR] Could not check Pinecone: {e}")

# Check documentation trainer
print("\n5. Documentation Training:")
try:
    from training.services.documentation_trainer import DocumentationTrainer
    doc_trainer = DocumentationTrainer()
    print(f"   [OK] Documentation trainer initialized")
    print(f"   [OK] Documentation file: {doc_trainer.doc_file if hasattr(doc_trainer, 'doc_file') else 'N/A'}")
except Exception as e:
    print(f"   [ERROR] Documentation trainer error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("Current setup appears to be:")
print("  - Schema: water_data.sql (water utility schema)")
print("  - Training SQL: training_sql_data.json (water utility queries)")
print("  - Documentation: column_descriptions.json (if exists)")
print("  - Vanna: Trained on water utility data")
print("\nTemp folder setup:")
print("  - Schema: financial_data.sql (financial data schema)")
print("  - Training SQL: training_sql_data.json (financial queries)")
print("  - Documentation: column_descriptions.json (financial columns)")
print("  - Vanna: Trained on financial data")
print("\n[NOTE] These are DIFFERENT datasets - current is water utility, temp is financial")
print("=" * 70)

