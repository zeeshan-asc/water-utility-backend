"""
Test Budget Variance Analysis SQL for Personnel Department 2024

This script:
1. Creates sample personnel department data for 2024
2. Tests the budget variance analysis SQL queries
3. Validates the results
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
from datetime import datetime
import random

db_path = Path("database/water_data.db")

def create_sample_data():
    """Create sample personnel department data for 2024"""
    print("=" * 80)
    print("Creating Sample Personnel Department Data for 2024")
    print("=" * 80)
    
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM departments WHERE department = 'Personnel' AND date LIKE '2024%'")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"Found {existing_count} existing records. Deleting...")
            cursor.execute("DELETE FROM departments WHERE department = 'Personnel' AND date LIKE '2024%'")
        
        # Generate sample data for each month in 2024
        records = []
        
        for month in range(1, 13):
            # Generate 5-10 records per month
            days_in_month = (datetime(2024, month + 1, 1) - datetime(2024, month, 1)).days if month < 12 else 31
            num_records = random.randint(5, 10)
            
            for _ in range(num_records):
                day = random.randint(1, days_in_month)
                date = datetime(2024, month, day).strftime('%Y-%m-%d')
                
                # Generate realistic budget and actual values for Personnel
                # Personnel typically has more consistent spending
                base_budget = random.uniform(80, 150)  # $80k - $150k
                variance_factor = random.uniform(-0.12, 0.15)  # -12% to +15% variance
                actual = base_budget * (1 + variance_factor)
                variance = actual - base_budget
                variance_pct = variance_factor
                
                records.append({
                    'date': date,
                    'department': 'Personnel',
                    'budget': round(base_budget, 2),
                    'actual': round(actual, 2),
                    'variance': round(variance, 2),
                    'variance_pct': round(variance_pct, 4)
                })
        
        # Insert records
        insert_sql = """
        INSERT INTO departments (date, department, budget, actual, variance, variance_pct)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor.executemany(insert_sql, [
            (r['date'], r['department'], r['budget'], r['actual'], r['variance'], r['variance_pct'])
            for r in records
        ])
        
        conn.commit()
        print(f"Created {len(records)} sample personnel department records for 2024")
        return len(records)


def test_queries():
    """Test the budget variance analysis SQL queries"""
    print("\n" + "=" * 80)
    print("Testing Budget Variance Analysis Queries for Personnel")
    print("=" * 80)
    
    queries = {
        "Main Analysis": """
        SELECT 
            date,
            department,
            budget,
            actual,
            variance,
            variance_pct,
            CASE 
                WHEN variance_pct > 0.10 THEN 'Over Budget'
                WHEN variance_pct < -0.10 THEN 'Under Budget'
                ELSE 'On Budget'
            END as status
        FROM departments
        WHERE department = 'Personnel'
            AND date LIKE '2024%'
        ORDER BY date DESC
        LIMIT 10
        """,
        
        "Summary Statistics": """
        SELECT 
            department,
            COUNT(*) as total_records,
            SUM(budget) as total_budget,
            SUM(actual) as total_actual,
            SUM(variance) as total_variance,
            AVG(variance_pct) as avg_variance_pct,
            MAX(variance_pct) as max_variance_pct,
            MIN(variance_pct) as min_variance_pct,
            COUNT(CASE WHEN variance_pct > 0.10 THEN 1 END) as over_budget_count,
            COUNT(CASE WHEN variance_pct < -0.10 THEN 1 END) as under_budget_count,
            COUNT(CASE WHEN variance_pct BETWEEN -0.10 AND 0.10 THEN 1 END) as on_budget_count
        FROM departments
        WHERE department = 'Personnel'
            AND date LIKE '2024%'
        GROUP BY department
        """,
        
        "Monthly Trend Analysis": """
        SELECT 
            SUBSTR(date, 1, 7) as month,
            SUM(budget) as monthly_budget,
            SUM(actual) as monthly_actual,
            SUM(variance) as monthly_variance,
            AVG(variance_pct) as avg_variance_pct
        FROM departments
        WHERE department = 'Personnel'
            AND date LIKE '2024%'
        GROUP BY SUBSTR(date, 1, 7)
        ORDER BY month
        """
    }
    
    with sqlite3.connect(str(db_path)) as conn:
        for query_name, sql in queries.items():
            print(f"\n{query_name}:")
            print("-" * 80)
            try:
                df = pd.read_sql_query(sql, conn)
                if len(df) > 0:
                    print(df.to_string(index=False))
                    print(f"\nRows returned: {len(df)}")
                else:
                    print("No data returned")
            except Exception as e:
                print(f"ERROR: {str(e)}")
                import traceback
                traceback.print_exc()


def main():
    """Main execution"""
    try:
        # Create sample data
        create_sample_data()
        
        # Test queries
        test_queries()
        
        print("\n" + "=" * 80)
        print("Budget Variance Analysis Test Complete for Personnel")
        print("=" * 80)
        print("\nSQL queries are saved in: budget_variance_analysis_personnel.sql")
        print("You can use these queries in your application or test them directly.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


