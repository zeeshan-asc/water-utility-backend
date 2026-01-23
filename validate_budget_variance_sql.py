"""
Validate Budget Variance Analysis SQL Queries

This script validates all SQL queries in budget_variance_analysis.sql
against the database and provides detailed test results.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import re

db_path = Path("database/water_data.db")

def extract_queries_from_sql_file(sql_file: Path) -> List[Dict[str, str]]:
    """Extract individual SQL queries from the SQL file"""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by comments that indicate new queries
    queries = []
    current_query = []
    current_name = "Query"
    query_num = 1
    
    lines = content.split('\n')
    for line in lines:
        # Check for comment that indicates query name
        if line.strip().startswith('--') and ('Query' in line or 'Analysis' in line or 'Statistics' in line or 'Trend' in line):
            # Save previous query if exists
            if current_query:
                queries.append({
                    'name': current_name,
                    'sql': '\n'.join(current_query).strip()
                })
                current_query = []
            
            # Extract query name from comment
            current_name = line.replace('--', '').strip()
            query_num += 1
        elif line.strip() and not line.strip().startswith('--'):
            current_query.append(line)
    
    # Add last query
    if current_query:
        queries.append({
            'name': current_name,
            'sql': '\n'.join(current_query).strip()
        })
    
    return queries


def validate_query(sql: str, query_name: str) -> Tuple[bool, pd.DataFrame, str, float]:
    """Validate a single SQL query"""
    import time
    start_time = time.time()
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            df = pd.read_sql_query(sql, conn)
        
        execution_time = (time.time() - start_time) * 1000
        return True, df, None, execution_time
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return False, pd.DataFrame(), str(e), execution_time


def main():
    """Main validation function"""
    sql_file = Path("budget_variance_analysis.sql")
    
    if not sql_file.exists():
        print(f"Error: SQL file not found: {sql_file}")
        return 1
    
    print("=" * 80)
    print("Budget Variance Analysis SQL Validation")
    print("=" * 80)
    print()
    
    # Extract queries
    queries = extract_queries_from_sql_file(sql_file)
    
    if not queries:
        print("No queries found in SQL file")
        return 1
    
    print(f"Found {len(queries)} queries to validate\n")
    
    results = []
    
    # Validate each query
    for i, query_info in enumerate(queries, 1):
        query_name = query_info['name']
        sql = query_info['sql']
        
        print(f"Query {i}: {query_name}")
        print("-" * 80)
        print(f"SQL: {sql[:100]}...")
        
        success, df, error, exec_time = validate_query(sql, query_name)
        
        if success:
            print(f"✓ PASS ({exec_time:.2f}ms)")
            print(f"  Rows returned: {len(df)}")
            print(f"  Columns: {', '.join(df.columns.tolist())}")
            
            if len(df) > 0:
                print(f"\n  Sample data (first 3 rows):")
                print(df.head(3).to_string(index=False))
            
            results.append({
                'query': query_name,
                'success': True,
                'rows': len(df),
                'exec_time': exec_time
            })
        else:
            print(f"✗ FAIL ({exec_time:.2f}ms)")
            print(f"  Error: {error}")
            results.append({
                'query': query_name,
                'success': False,
                'error': error,
                'exec_time': exec_time
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("Validation Summary")
    print("=" * 80)
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print(f"Total Queries: {len(results)}")
    print(f"Passed: {passed} ({passed/len(results)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(results)*100:.1f}%)")
    
    if failed > 0:
        print("\nFailed Queries:")
        for r in results:
            if not r['success']:
                print(f"  - {r['query']}: {r.get('error', 'Unknown error')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


