-- DDL for Water Utility Data Database
-- Financial and operational data for water utility management

-- Main water_data table
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
);

-- Departments table (normalized from JSON)
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    department TEXT NOT NULL,
    budget REAL,
    actual REAL,
    variance REAL,
    variance_pct REAL,
    FOREIGN KEY (date) REFERENCES water_data(date)
);

-- Alerts table (normalized from JSON)
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    alert_type TEXT,
    description TEXT,
    potential_impact_k REAL,
    confidence_level REAL,
    FOREIGN KEY (date) REFERENCES water_data(date)
);

-- Scenarios table (normalized from JSON)
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
);

-- Indexes for performance optimization
CREATE INDEX idx_date ON water_data(date);
CREATE INDEX idx_year ON water_data(year);
CREATE INDEX idx_quarter ON water_data(quarter);
CREATE INDEX idx_departments_date ON departments(date);
CREATE INDEX idx_alerts_date ON alerts(date);
CREATE INDEX idx_scenarios_date ON scenarios(date);

