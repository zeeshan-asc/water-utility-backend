# -*- coding: utf-8 -*-
"""Verify that all components are using the updated daily data"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import sqlite3
from pathlib import Path
from services.dashboard_service import DashboardService

print("=" * 60)
print("DATA UPDATE VERIFICATION")
print("=" * 60)

# Check CSV file
print("\n1. CSV File (data/data.csv):")
csv_path = Path("data/data.csv")
if csv_path.exists():
    df_csv = pd.read_csv(csv_path)
    print(f"   [OK] Records: {len(df_csv)}")
    print(f"   [OK] Date range: {df_csv['date'].min()} to {df_csv['date'].max()}")
    print(f"   [OK] Unique dates: {df_csv['date'].nunique()}")
    print(f"   [OK] First date: {df_csv['date'].iloc[0]}")
    print(f"   [OK] Last date: {df_csv['date'].iloc[-1]}")
else:
    print("   [ERROR] CSV file not found!")

# Check Database
print("\n2. Database (database/water_data.db):")
db_path = Path("database/water_data.db")
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM water_data")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(date), MAX(date) FROM water_data")
    dates = cursor.fetchone()
    cursor.execute("SELECT COUNT(DISTINCT date) FROM water_data")
    unique_dates = cursor.fetchone()[0]
    print(f"   [OK] Records: {count}")
    print(f"   [OK] Date range: {dates[0]} to {dates[1]}")
    print(f"   [OK] Unique dates: {unique_dates}")
    conn.close()
else:
    print("   [ERROR] Database file not found!")

# Check Dashboard Service
print("\n3. Dashboard Service:")
try:
    service = DashboardService()
    print(f"   [OK] Records loaded: {len(service.main_data)}")
    print(f"   [OK] Date range: {service.main_data['date'].min()} to {service.main_data['date'].max()}")
    print(f"   [OK] First date: {service.main_data['date'].iloc[0]}")
    print(f"   [OK] Last date: {service.main_data['date'].iloc[-1]}")
except Exception as e:
    print(f"   [ERROR] Error: {e}")

# Check Vanna Database Connection
print("\n4. Vanna Database Connection:")
try:
    from core.custom_vanna import MyVanna
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    # Check database path
    sqlite_env_path = os.getenv('SQLITE_DB_PATH', 'database/water_data.db')
    project_root = Path(__file__).resolve().parent
    sqlite_path = Path(sqlite_env_path)
    if not sqlite_path.is_absolute():
        sqlite_path = (project_root / sqlite_path).resolve()
    
    print(f"   [OK] Database path: {sqlite_path}")
    print(f"   [OK] Database exists: {sqlite_path.exists()}")
    
    if sqlite_path.exists():
        conn = sqlite3.connect(str(sqlite_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM water_data")
        count = cursor.fetchone()[0]
        print(f"   [OK] Records: {count}")
        conn.close()
except Exception as e:
    print(f"   [ERROR] Error: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)

