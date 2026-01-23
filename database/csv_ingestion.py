"""
CSV Ingestion Script for Water Utility Data Database.

This script reads data from data/data.csv and loads it into a SQLite database
with a schema designed for water utility financial and operational data.

Usage:
    python database/csv_ingestion.py
"""

import os
import sqlite3
import pandas as pd
import json
import logging
from pathlib import Path
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = Path(__file__).parent / "water_data.db"
CSV_PATH = Path(__file__).parent.parent / "data" / "data.csv"


def create_database_schema(conn: sqlite3.Connection) -> None:
    """
    Create the database schema for water utility data.
    
    Args:
        conn: SQLite database connection
    """
    logger.info("Creating database schema...")
    cursor = conn.cursor()
    
    # Drop tables if they exist (for re-running the script)
    cursor.execute("DROP TABLE IF EXISTS departments")
    cursor.execute("DROP TABLE IF EXISTS alerts")
    cursor.execute("DROP TABLE IF EXISTS scenarios")
    cursor.execute("DROP TABLE IF EXISTS water_data")
    
    # Create the main water_data table
    cursor.execute("""
        CREATE TABLE water_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            year INTEGER,
            month INTEGER,
            quarter TEXT,
            actual_revenue REAL,
            budgeted_revenue REAL,
            revenue_variance REAL,
            operating_margin REAL,
            days_sales_outstanding INTEGER,
            non_revenue_water_pct REAL,
            cost_per_gallon REAL,
            collection_rate REAL,
            debt_service_coverage REAL,
            water_revenue REAL,
            cash_reserve REAL,
            current_pct REAL,
            days_30_pct REAL,
            days_60_pct REAL,
            total_ar REAL,
            projected_coverage REAL,
            required_minimum REAL,
            actual_coverage REAL,
            outstanding_debt REAL,
            monthly_expenses REAL,
            monthly_margin REAL,
            monthly_revenue REAL
        )
    """)
    
    # Create departments table (normalized from JSON)
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            department TEXT NOT NULL,
            budget REAL,
            actual REAL,
            variance REAL,
            variance_pct REAL,
            FOREIGN KEY (date) REFERENCES water_data(date)
        )
    """)
    
    # Create alerts table (normalized from JSON)
    cursor.execute("""
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            alert_type TEXT,
            description TEXT,
            potential_impact_k REAL,
            confidence_level REAL,
            FOREIGN KEY (date) REFERENCES water_data(date)
        )
    """)
    
    # Create scenarios table (normalized from JSON)
    cursor.execute("""
        CREATE TABLE scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            scenario TEXT,
            projected_revenue REAL,
            projected_expenses REAL,
            debt_service_coverage REAL,
            net_income REAL,
            financial_viability TEXT,
            FOREIGN KEY (date) REFERENCES water_data(date)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX idx_date ON water_data(date)")
    cursor.execute("CREATE INDEX idx_year ON water_data(year)")
    cursor.execute("CREATE INDEX idx_quarter ON water_data(quarter)")
    cursor.execute("CREATE INDEX idx_departments_date ON departments(date)")
    cursor.execute("CREATE INDEX idx_alerts_date ON alerts(date)")
    cursor.execute("CREATE INDEX idx_scenarios_date ON scenarios(date)")
    
    conn.commit()
    logger.info("Database schema created successfully")


def parse_json_column(value: str) -> list:
    """
    Parse JSON column value.
    
    Args:
        value: JSON string from CSV
        
    Returns:
        List of dictionaries
    """
    if pd.isna(value) or value == '':
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {value[:100]}")
        return []


def ingest_csv_data(conn: sqlite3.Connection) -> int:
    """
    Ingest CSV data into the database.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        Number of rows inserted
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    
    logger.info(f"Reading CSV from {CSV_PATH}")
    
    # Read CSV with pandas
    df = pd.read_csv(CSV_PATH)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    cursor = conn.cursor()
    rows_inserted = 0
    
    # Prepare insert statements
    insert_main_sql = """
        INSERT INTO water_data 
        (date, year, month, quarter, actual_revenue, budgeted_revenue, revenue_variance,
         operating_margin, days_sales_outstanding, non_revenue_water_pct, cost_per_gallon,
         collection_rate, debt_service_coverage, water_revenue, cash_reserve, current_pct,
         days_30_pct, days_60_pct, total_ar, projected_coverage, required_minimum,
         actual_coverage, outstanding_debt, monthly_expenses, monthly_margin, monthly_revenue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    insert_department_sql = """
        INSERT INTO departments (date, department, budget, actual, variance, variance_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    insert_alert_sql = """
        INSERT INTO alerts (date, alert_type, description, potential_impact_k, confidence_level)
        VALUES (?, ?, ?, ?, ?)
    """
    
    insert_scenario_sql = """
        INSERT INTO scenarios (date, scenario, projected_revenue, projected_expenses,
                              debt_service_coverage, net_income, financial_viability)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # Insert rows
    for _, row in df.iterrows():
        try:
            # Insert main data
            main_values = (
                row['date'],
                int(row['year']) if pd.notna(row['year']) else None,
                int(row['month']) if pd.notna(row['month']) else None,
                str(row['quarter']) if pd.notna(row['quarter']) else None,
                float(row['actual_revenue']) if pd.notna(row['actual_revenue']) else None,
                float(row['budgeted_revenue']) if pd.notna(row['budgeted_revenue']) else None,
                float(row['revenue_variance']) if pd.notna(row['revenue_variance']) else None,
                float(row['operating_margin']) if pd.notna(row['operating_margin']) else None,
                int(row['days_sales_outstanding']) if pd.notna(row['days_sales_outstanding']) else None,
                float(row['non_revenue_water_pct']) if pd.notna(row['non_revenue_water_pct']) else None,
                float(row['cost_per_gallon']) if pd.notna(row['cost_per_gallon']) else None,
                float(row['collection_rate']) if pd.notna(row['collection_rate']) else None,
                float(row['debt_service_coverage']) if pd.notna(row['debt_service_coverage']) else None,
                float(row['water_revenue']) if pd.notna(row['water_revenue']) else None,
                float(row['cash_reserve']) if pd.notna(row['cash_reserve']) else None,
                float(row['current_pct']) if pd.notna(row['current_pct']) else None,
                float(row['days_30_pct']) if pd.notna(row['days_30_pct']) else None,
                float(row['days_60_pct']) if pd.notna(row['days_60_pct']) else None,
                float(row['total_ar']) if pd.notna(row['total_ar']) else None,
                float(row['projected_coverage']) if pd.notna(row['projected_coverage']) else None,
                float(row['required_minimum']) if pd.notna(row['required_minimum']) else None,
                float(row['actual_coverage']) if pd.notna(row['actual_coverage']) else None,
                float(row['outstanding_debt']) if pd.notna(row['outstanding_debt']) else None,
                float(row['monthly_expenses']) if pd.notna(row['monthly_expenses']) else None,
                float(row['monthly_margin']) if pd.notna(row['monthly_margin']) else None,
                float(row['monthly_revenue']) if pd.notna(row['monthly_revenue']) else None,
            )
            
            cursor.execute(insert_main_sql, main_values)
            rows_inserted += 1
            
            # Insert departments
            departments = parse_json_column(row.get('departments', ''))
            for dept in departments:
                cursor.execute(insert_department_sql, (
                    row['date'],
                    dept.get('department'),
                    dept.get('budget'),
                    dept.get('actual'),
                    dept.get('variance'),
                    dept.get('variance_pct')
                ))
            
            # Insert alerts
            alerts = parse_json_column(row.get('alerts', ''))
            for alert in alerts:
                cursor.execute(insert_alert_sql, (
                    row['date'],
                    alert.get('alert_type'),
                    alert.get('description'),
                    alert.get('potential_impact_k'),
                    alert.get('confidence_level')
                ))
            
            # Insert scenarios
            scenarios = parse_json_column(row.get('scenarios', ''))
            for scenario in scenarios:
                cursor.execute(insert_scenario_sql, (
                    row['date'],
                    scenario.get('scenario'),
                    scenario.get('projected_revenue'),
                    scenario.get('projected_expenses'),
                    scenario.get('debt_service_coverage'),
                    scenario.get('net_income'),
                    scenario.get('financial_viability')
                ))
            
        except Exception as e:
            logger.error(f"Error inserting row for date {row.get('date', 'unknown')}: {str(e)}")
            continue
    
    conn.commit()
    logger.info(f"Successfully inserted {rows_inserted} main rows")
    
    # Get counts for related tables
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    scenario_count = cursor.fetchone()[0]
    
    logger.info(f"Inserted {dept_count} department records")
    logger.info(f"Inserted {alert_count} alert records")
    logger.info(f"Inserted {scenario_count} scenario records")
    
    return rows_inserted


def main():
    """Main function to run CSV ingestion."""
    logger.info("=" * 60)
    logger.info("Water Utility Data CSV Ingestion")
    logger.info("=" * 60)
    
    # Ensure database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    logger.info(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        # Create schema
        create_database_schema(conn)
        
        # Ingest data
        rows_inserted = ingest_csv_data(conn)
        
        logger.info("=" * 60)
        logger.info(f"Ingestion completed successfully!")
        logger.info(f"Database location: {DB_PATH}")
        logger.info(f"Total rows inserted: {rows_inserted}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

