"""Debug aggregation issue"""
import pandas as pd
from pathlib import Path

data_dir = Path("data")
df = pd.read_csv(data_dir / 'data.csv')
df['date'] = pd.to_datetime(df['date'])

print("Original data shape:", df.shape)
print("Sample dates:", df['date'].head(10).tolist())

# Test monthly aggregation
df['period'] = df['date'].dt.strftime('%Y-%m')
print("\nPeriods created:", df['period'].unique()[:10])

# Group by period
grouped = df.groupby('period').agg({
    'actual_revenue': 'sum',
    'budgeted_revenue': 'sum',
    'revenue_variance': 'sum'
}).reset_index()

print("\nAfter grouping:")
print("Grouped shape:", grouped.shape)
print("Sample grouped data:")
print(grouped.head(10).to_string(index=False))


