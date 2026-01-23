"""
Generate comprehensive water utility data for 3 years (2022-2024)
Daily data - Single CSV file with all metrics matching the dashboard
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)

# Generate dates for 3 years (daily data)
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
dates = []
current_date = start_date
while current_date <= end_date:
    dates.append(current_date)
    current_date += timedelta(days=1)

# Create base DataFrame
df = pd.DataFrame({
    'date': dates,
    'year': [d.year for d in dates],
    'month': [d.month for d in dates],
    'quarter': [f"Q{((d.month-1)//3)+1}" for d in dates],
})

# Financial KPIs - Base values matching dashboard (annual totals)
annual_revenue = 26.5  # $26.5M annual revenue (shown in dashboard)
annual_water_revenue = 47.2  # $47.2M water revenue
monthly_revenue_base = annual_revenue / 12  # ~2.21M per month
daily_revenue_base = monthly_revenue_base / 30  # ~73.7K per day
monthly_water_revenue_base = annual_water_revenue / 12  # ~3.93M per month
daily_water_revenue_base = monthly_water_revenue_base / 30  # ~131K per day
base_operating_margin = 0.184  # 18.4%
base_dso = 38  # Days Sales Outstanding
base_nrw = 0.231  # 23.1% Non-Revenue Water
base_cost_per_gallon = 4.27  # $4.27
base_collection_rate = 0.942  # 94.2%
base_cash_reserve = 4.2  # $4.2M
base_dscr = 2.9  # 2.9x Debt Service Coverage

# Generate daily data with realistic trends
n_days = len(dates)
daily_revenues = []
daily_budgets = []
daily_water_revenues = []
daily_margins = []
daily_dso = []
daily_nrw = []
daily_costs = []
daily_collection = []
daily_cash = []
daily_dscr = []

for i, date in enumerate(dates):
    # Revenue trends - increasing over time with some variance
    # Dashboard shows $26.5M annual, so daily should average ~73.7K
    day_of_year = date.timetuple().tm_yday
    trend = 1 + (i * 0.0001)  # Upward trend over 3 years (slower for daily)
    seasonal = 1 + 0.08 * np.sin(2 * np.pi * day_of_year / 365)  # Seasonal variation
    weekly = 1 + 0.02 * np.sin(2 * np.pi * date.weekday() / 7)  # Weekly pattern (weekends lower)
    noise = np.random.normal(1, 0.05)  # Random variation (higher for daily)
    
    daily_rev = daily_revenue_base * trend * seasonal * weekly * noise
    daily_budget = daily_rev * 0.845  # Budget ~84.5% of actual (matching dashboard: $22.4M vs $26.5M)
    daily_revenues.append(round(daily_rev, 2))
    daily_budgets.append(round(daily_budget, 2))
    
    # Water revenue - similar trend
    water_rev = daily_water_revenue_base * trend * seasonal * weekly * noise
    daily_water_revenues.append(round(water_rev, 2))
    
    # Operating margin - improving over time (slowly for daily)
    margin = base_operating_margin + (i * 0.00002) + np.random.normal(0, 0.005)
    daily_margins.append(round(max(0.15, min(0.22, margin)), 4))
    
    # DSO - decreasing (improving) - changes slowly day by day
    dso = base_dso - (i * 0.003) + np.random.normal(0, 0.5)
    daily_dso.append(round(max(30, min(45, dso)), 1))
    
    # NRW - decreasing (improving) - changes slowly day by day
    nrw = base_nrw - (i * 0.00003) + np.random.normal(0, 0.005)
    daily_nrw.append(round(max(0.20, min(0.26, nrw)), 4))
    
    # Cost per gallon - slight increase
    cost = base_cost_per_gallon + (i * 0.0003) + np.random.normal(0, 0.03)
    daily_costs.append(round(max(4.0, min(4.5, cost)), 2))
    
    # Collection rate - improving
    collection = base_collection_rate + (i * 0.00001) + np.random.normal(0, 0.003)
    daily_collection.append(round(max(0.92, min(0.97, collection)), 4))
    
    # Cash reserve - growing (changes slowly day by day)
    cash = base_cash_reserve + (i * 0.0006) + np.random.normal(0, 0.05)
    daily_cash.append(round(max(3.5, min(5.0, cash)), 2))
    
    # DSCR - historical trend matching dashboard
    # Dashboard shows: 2023 (below 1.4), 2024 (just above 1.5), 2025 (above 1.6)
    year = date.year
    if year == 2022:
        base_dscr = 1.35 + (i / 1095 * 0.10)  # Improves from 1.35 to 1.45 over year
    elif year == 2023:
        base_dscr = 1.40 + ((i - 365) / 365 * 0.10)  # Improves from 1.40 to 1.50
    elif year == 2024:
        base_dscr = 1.50 + ((i - 730) / 365 * 0.10)  # Improves from 1.50 to 1.60
    else:
        base_dscr = 1.60
    
    dscr = base_dscr + np.random.normal(0, 0.02)
    daily_dscr.append(round(max(1.3, min(1.7, dscr)), 2))

# Add financial metrics
df['actual_revenue'] = daily_revenues
df['budgeted_revenue'] = daily_budgets
df['revenue_variance'] = df['actual_revenue'] - df['budgeted_revenue']
df['revenue_variance_pct'] = (df['revenue_variance'] / df['budgeted_revenue'] * 100).round(2)
df['operating_margin'] = daily_margins
df['days_sales_outstanding'] = daily_dso
df['non_revenue_water_pct'] = daily_nrw
df['cost_per_gallon'] = daily_costs
df['collection_rate'] = daily_collection
df['water_revenue'] = daily_water_revenues
df['cash_reserve'] = daily_cash
df['debt_service_coverage'] = daily_dscr

# AR Aging - Current, 30 days, 60+ days
# Match database schema column names
df['total_ar'] = [round(1.2 + np.random.normal(0, 0.05), 2) for _ in range(n_days)]
# Convert percentages to decimals (47% -> 0.47)
df['current_pct'] = 0.47  # 47% as decimal
df['days_30_pct'] = 0.23  # 23% as decimal
df['days_60_pct'] = 0.12  # 12% as decimal

# DSCR metrics - match database schema column names
df['required_minimum'] = 1.5  # Database expects required_minimum
df['actual_coverage'] = df['debt_service_coverage']  # Use the DSCR we already calculated
# Projected coverage should be slightly higher than actual
df['projected_coverage'] = df['actual_coverage'] + np.random.normal(0.05, 0.02, n_days)
df['projected_coverage'] = df['projected_coverage'].clip(lower=df['actual_coverage'])

# Revenue breakdown by sector (for FY24 Revenue Performance Summary)
# Residential: ~60% of revenue, Commercial: ~40%
df['residential_revenue'] = df['actual_revenue'] * (0.60 + np.random.normal(0, 0.02, n_days))
df['commercial_revenue'] = df['actual_revenue'] * (0.40 + np.random.normal(0, 0.02, n_days))

# Department Budgets (in thousands) - convert monthly to daily
# Store as JSON for database ingestion
departments_list = ['Personnel', 'Operations', 'Infrastructure', 'Maintenance', 'Utilities']
departments_json = []

for i, date in enumerate(dates):
    dept_data = []
    base_budgets_monthly = {
        'Personnel': 500,
        'Operations': 800,
        'Infrastructure': 600,
        'Maintenance': 400,
        'Utilities': 350
    }
    
    for dept in departments_list:
        base_monthly = base_budgets_monthly[dept]
        base_daily = base_monthly / 30  # Convert to daily
        
        # Budget with slight growth and daily variation
        day_of_year = date.timetuple().tm_yday
        seasonal = 1 + 0.05 * np.sin(2 * np.pi * day_of_year / 365)
        budget = base_daily * (1 + i * 0.00003) * seasonal + np.random.normal(0, base_daily * 0.05)
        budget = round(budget, 2)
        
        # Actual spending - Operations and Infrastructure tend to overspend
        if dept in ['Operations', 'Infrastructure']:
            actual = budget * (1.05 + np.random.normal(0, 0.03))  # 5% over budget
        else:
            actual = budget * (0.95 + np.random.normal(0, 0.03))  # Under budget
        
        actual = round(actual, 2)
        variance = round(actual - budget, 2)
        variance_pct = round((variance / budget * 100) if budget != 0 else 0, 2)
        
        dept_data.append({
            'department': dept,
            'budget': budget,
            'actual': actual,
            'variance': variance,
            'variance_pct': variance_pct
        })
    
    departments_json.append(json.dumps(dept_data))

df['departments'] = departments_json

# Calculate monthly expenses from department JSON data
monthly_expenses_list = []
for dept_json in departments_json:
    dept_data = json.loads(dept_json)
    total_actual = sum(dept['actual'] for dept in dept_data)  # Sum of all department actuals in thousands
    monthly_expenses_list.append(total_actual / 1000)  # Convert to millions

# Daily operational metrics
df['monthly_revenue'] = df['actual_revenue']  # Keep same column name for compatibility
df['monthly_expenses'] = monthly_expenses_list
df['monthly_margin'] = df['monthly_revenue'] - df['monthly_expenses']

# Debt metrics
df['outstanding_debt'] = [round(8.1 + np.random.normal(0, 0.05), 2) for _ in range(n_days)]

# Projections (12-month forward-looking) - use 365 day window for daily data
df['projected_revenue_12m'] = df['actual_revenue'].rolling(window=365, min_periods=1).sum()
df['expected_operating_expenses'] = df['monthly_expenses'].rolling(window=365, min_periods=1).sum()
df['capital_investment_plan'] = [round(3.2 + np.random.normal(0, 0.05), 2) for _ in range(n_days)]
df['projected_net_income'] = df['projected_revenue_12m'] - df['expected_operating_expenses'] - df['capital_investment_plan']

# Scenario Planning - Store as JSON for database ingestion
# Calculate annual values for scenarios
annual_revenue_proj = df['actual_revenue'] * 365 / 1000  # Convert daily to annual in millions
annual_expenses_proj = df['monthly_expenses'] * 12  # Convert monthly to annual in millions

scenarios_json = []
for i, date in enumerate(dates):
    # Base scenario values from dashboard
    scenario_data = [{
        'scenario': 'Base Scenario',
        'projected_revenue': round(annual_revenue_proj.iloc[i], 2),
        'projected_expenses': round(annual_expenses_proj.iloc[i], 2),
        'debt_service_coverage': round(df.iloc[i]['debt_service_coverage'], 2),
        'net_income': round(annual_revenue_proj.iloc[i] - annual_expenses_proj.iloc[i], 2),
        'financial_viability': 'Healthy'
    }]
    scenarios_json.append(json.dumps(scenario_data))

df['scenarios'] = scenarios_json

# AI Insights & Alerts - Store as JSON for database ingestion
# Pre-calculate alert values
revenue_leakage_daily_loss = 285
revenue_leakage_efficiency_gap = 23
cost_optimization_daily_recovery = 52.2

alerts_json = []
for i, date in enumerate(dates):
    daily_rev = df.iloc[i]['actual_revenue']
    # Generate alerts matching dashboard
    alerts_data = [
        {
            'alert_type': 'Revenue Optimization Opportunity',
            'description': 'Analysis suggests implementing dynamic pricing during peak demand hours could increase quarterly revenue by 2-3%.',
            'potential_impact_k': round(daily_rev * 0.025 * 90 / 1000, 2),  # 2.5% of daily * 90 days in thousands
            'confidence_level': 92.0
        },
        {
            'alert_type': 'Q1 Profitability Forecast',
            'description': f'Based on current trajectory, Q1 net income expected to reach ${annual_revenue_proj.iloc[i] - annual_expenses_proj.iloc[i]:.1f}M, 3.6% above budget forecast.',
            'potential_impact_k': round((annual_revenue_proj.iloc[i] - annual_expenses_proj.iloc[i]) * 0.036 * 1000, 2),  # 3.6% above budget
            'confidence_level': 85.0
        },
        {
            'alert_type': 'Revenue Leakage Detected',
            'description': f'${revenue_leakage_daily_loss:.0f}K daily loss from NRW represents {revenue_leakage_efficiency_gap:.0f}% efficiency gap vs. industry benchmark of 15%.',
            'potential_impact_k': revenue_leakage_daily_loss,
            'confidence_level': 80.0
        },
        {
            'alert_type': 'Cost Optimization Opportunity',
            'description': f'Reducing NRW by 5% could recover ${cost_optimization_daily_recovery:.1f}K in daily revenue without operational changes.',
            'potential_impact_k': cost_optimization_daily_recovery,
            'confidence_level': 87.0
        }
    ]
    alerts_json.append(json.dumps(alerts_data))

df['alerts'] = alerts_json

# Keep individual alert fields for backward compatibility (if needed)
df['revenue_optimization_confidence'] = 92
df['revenue_optimization_impact_pct'] = 2.5
df['profitability_forecast_confidence'] = 85
df['profitability_forecast_net_income'] = 19.8
df['revenue_leakage_confidence'] = 80
df['revenue_leakage_daily_loss'] = revenue_leakage_daily_loss
df['revenue_leakage_efficiency_gap'] = revenue_leakage_efficiency_gap
df['cost_optimization_confidence'] = 87
df['cost_optimization_daily_recovery'] = cost_optimization_daily_recovery

# Ensure all numeric columns are properly formatted
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Round to appropriate decimal places
df = df.round({
    'actual_revenue': 2,
    'budgeted_revenue': 2,
    'revenue_variance': 2,
    'revenue_variance_pct': 2,
    'operating_margin': 4,
    'days_sales_outstanding': 1,
    'non_revenue_water_pct': 4,
    'cost_per_gallon': 2,
    'collection_rate': 4,
    'water_revenue': 2,
    'cash_reserve': 2,
    'debt_service_coverage': 2,
    'monthly_revenue': 2,
    'monthly_expenses': 2,
    'monthly_margin': 2,
})

# Save to CSV
output_file = 'data/data.csv'
df.to_csv(output_file, index=False)

print(f"Generated comprehensive daily data file: {output_file}")
print(f"   Total records: {len(df)}")
print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
print(f"   Columns: {len(df.columns)}")
print(f"\nSample data (first 3 days):")
print(df.head(3).to_string())
print(f"\nSample data (last 3 days):")
print(df.tail(3).to_string())
print(f"\nSummary statistics:")
print(df[['actual_revenue', 'budgeted_revenue', 'operating_margin', 'debt_service_coverage']].describe())

