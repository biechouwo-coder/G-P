"""
Merge industrial structure data with the filtered 2007-2023 dataset
"""

import pandas as pd
from pathlib import Path

# File paths
FILTERED_DATA = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023.xlsx")
INDUSTRIAL_DATA = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\2000-2023地级市产业结构 .xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版.xlsx")

print("Reading filtered dataset (2007-2023)...")
df_filtered = pd.read_excel(FILTERED_DATA)
print(f"  Shape: {df_filtered.shape}")
print(f"  Columns: {list(df_filtered.columns)}")

print("\nReading industrial structure data...")
# Read the second sheet (index 1) which contains the actual data
df_industrial = pd.read_excel(INDUSTRIAL_DATA, sheet_name=1)
print(f"  Shape: {df_industrial.shape}")
print(f"  Columns (positions):")
for i, col in enumerate(df_industrial.columns):
    print(f"    [{i}] {col}")

# Extract key columns by position (avoiding encoding issues)
# Based on the structure: year, city_name, city_code, and industrial metrics
print("\nExtracting key columns from industrial structure data...")
# Column positions: [0]=year, [1]=city_name, [3]=province, [7]=secondary_value, [8]=tertiary_value, [11]=tertiary_share, [14]=industrial_upgrading
df_industrial_clean = df_industrial.iloc[:, [0, 1, 2, 11, 14]].copy()
df_industrial_clean.columns = ['year', 'city_name', 'city_code', 'tertiary_share', 'industrial_upgrading']

# Convert year to integer
df_industrial_clean['year'] = df_industrial_clean['year'].astype('Int64')

print(f"\nCleaned industrial structure data:")
print(f"  Shape: {df_industrial_clean.shape}")
print(f"  Columns: {list(df_industrial_clean.columns)}")
print(f"  Year range: {df_industrial_clean['year'].min()} - {df_industrial_clean['year'].max()}")
print(f"  Unique cities: {df_industrial_clean['city_name'].nunique()}")

# Filter to 2007-2023
print("\nFiltering industrial structure data to 2007-2023...")
df_industrial_filtered = df_industrial_clean[
    (df_industrial_clean['year'] >= 2007) &
    (df_industrial_clean['year'] <= 2023)
].copy()
print(f"  After filtering: {df_industrial_filtered.shape}")

# Merge with filtered dataset
print("\nMerging datasets...")
print(f"  Filtered data: {df_filtered.shape}")
print(f"  Industrial structure: {df_industrial_filtered.shape}")

# Merge on city_name and year (left join to preserve all observations in filtered data)
df_merged = pd.merge(
    df_filtered,
    df_industrial_filtered,
    on=['city_name', 'year'],
    how='left',
    indicator='ind_src'
)

# Check merge results
print(f"\nMerge results:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Both datasets: {(df_merged['ind_src'] == 'both').sum()}")
print(f"  Only in filtered data: {(df_merged['ind_src'] == 'left_only').sum()}")

# Remove indicator column
df_merged = df_merged.drop(columns=['ind_src'])

# Handle duplicate city_code columns (if any)
if 'city_code_x' in df_merged.columns and 'city_code_y' in df_merged.columns:
    df_merged['city_code'] = df_merged['city_code_x'].combine_first(df_merged['city_code_y'])
    df_merged = df_merged.drop(columns=['city_code_x', 'city_code_y'])

# Reorder columns for better readability
print("\nFinal column order:")
cols = ['year', 'city_name', 'city_code', 'pop_density', 'gdp_real', 'gdp_deflator',
        'carbon_intensity', 'tertiary_share', 'industrial_upgrading']
# Keep only columns that exist
cols = [c for c in cols if c in df_merged.columns]
# Add any remaining columns
remaining_cols = [c for c in df_merged.columns if c not in cols]
cols = cols + remaining_cols
df_merged = df_merged[cols]

print(f"  Columns: {list(df_merged.columns)}")

# Data quality check
print("\nData quality check:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Total columns: {len(df_merged.columns)}")
print(f"  Unique cities: {df_merged['city_name'].nunique()}")
print(f"  Year range: {df_merged['year'].min()} - {df_merged['year'].max()}")

print("\nMissing values:")
for col in df_merged.columns:
    missing = df_merged[col].isnull().sum()
    if missing > 0:
        pct = missing / len(df_merged) * 100
        print(f"  {col}: {missing} ({pct:.1f}%)")

# Save to Excel
print(f"\nSaving to: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_merged.to_excel(writer, sheet_name='总数据集_2007-2023_完整版', index=False)

print("\nMerge complete!")
print(f"Output file: {OUTPUT_FILE}")
print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
