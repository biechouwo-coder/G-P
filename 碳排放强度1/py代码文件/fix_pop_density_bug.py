"""
Fix pop_density bug caused by incorrect column extraction in merge_final.py

Root cause: merge_final.py extracted column 9 (empty) instead of column 8 (actual pop_density)
This caused pop_density to be filled with constant values later.

Solution: Re-read raw pop_density data and update all values correctly.
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("FIXING POP_DENSITY BUG")
print("=" * 80)

# Read current dataset
print("\n[1/5] Loading current dataset...")
df_current = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
print(f"Current dataset: {len(df_current)} observations, {df_current['city_name'].nunique()} cities")

# Read raw pop_density data
print("\n[2/5] Reading raw pop_density data...")
df_pop_raw = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

# Extract correct columns: year[0], city[2], pop_density[8]
df_pop = df_pop_raw.iloc[:, [0, 2, 8]].copy()
df_pop.columns = ['year', 'city_name', 'pop_density_raw']

# Filter to 2007-2023
df_pop = df_pop[(df_pop['year'] >= 2007) & (df_pop['year'] <= 2023)].copy()

print(f"Raw pop_density data: {len(df_pop)} observations")
print(f"Pop_density range: {df_pop['pop_density_raw'].min():.2f} - {df_pop['pop_density_raw'].max():.2f}")

# Check for missing in raw data
missing_raw = df_pop['pop_density_raw'].isnull().sum()
print(f"Missing values in raw data: {missing_raw} ({missing_raw/len(df_pop)*100:.2f}%)")

# Merge with current dataset to update pop_density
print("\n[3/5] Merging correct pop_density values...")
df_current['year'] = df_current['year'].astype(int)

df_merged = pd.merge(
    df_current,
    df_pop,
    on=['year', 'city_name'],
    how='left',
    indicator='pop_src'
)

print(f"Merge results:")
print(f"  Both (current had value): {(df_merged['pop_src'] == 'both').sum()}")
print(f"  Left only (current missing, raw has): {(df_merged['pop_src'] == 'left_only').sum()}")
print(f"  Right only (should be 0): {(df_merged['pop_src'] == 'right_only').sum()}")

# Check if pop_density_raw has values where current pop_density is 3880.018924
print("\n[4/5] Checking problematic value 3880.018924...")
problematic_value = 3880.018924
current_problematic = df_current['pop_density'] == problematic_value
print(f"Current dataset: {current_problematic.sum()} observations with value {problematic_value}")

# Compare with raw values
if current_problematic.sum() > 0:
    problematic_cities = df_current[current_problematic]['city_name'].unique()
    print(f"\nAffected cities ({len(problematic_cities)}):")

    for city in problematic_cities[:10]:  # Show first 10
        city_data = df_current[(df_current['city_name'] == city) & current_problematic]
        years = sorted(city_data['year'].values)
        print(f"  {city}: {len(years)} years affected ({min(years)}-{max(years)})")

# Update pop_density with correct values from raw data
print("\n[5/5] Updating pop_density values...")

# Before update
before_mean = df_current['pop_density'].mean()
before_std = df_current['pop_density'].std()
before_constant = df_current.groupby('city_name')['pop_density'].std()
num_constant_before = (before_constant == 0).sum()

print(f"Before update:")
print(f"  Mean: {before_mean:.2f}")
print(f"  Std: {before_std:.2f}")
print(f"  Cities with constant pop_density: {num_constant_before}")

# Update pop_density where we have raw data
mask_has_raw = df_merged['pop_density_raw'].notnull()
df_current.loc[mask_has_raw, 'pop_density'] = df_merged.loc[mask_has_raw, 'pop_density_raw']

# After update
after_mean = df_current['pop_density'].mean()
after_std = df_current['pop_density'].std()
after_constant = df_current.groupby('city_name')['pop_density'].std()
num_constant_after = (after_constant == 0).sum()

print(f"\nAfter update:")
print(f"  Mean: {after_mean:.2f}")
print(f"  Std: {after_std:.2f}")
print(f"  Cities with constant pop_density: {num_constant_after}")

# Verify Shanghai and Dongguan specifically
print("\n=== Verification ===")
print("\nShanghai pop_density (2010-2023):")
shanghai = df_current[df_current['city_name'] == '上海市'].sort_values('year')
print(shanghai[['year', 'pop_density']].tail(14))

print("\nDongguan pop_density (2010-2023):")
dongguan = df_current[df_current['city_name'] == '东莞市'].sort_values('year')
print(dongguan[['year', 'pop_density']].tail(14))

# Recalculate ln_pop_density
print("\n[6/6] Recalculating ln_pop_density...")
df_current['ln_pop_density'] = np.log(df_current['pop_density'])

# Check for any remaining issues
print("\n=== Final Data Quality Check ===")
missing_pop = df_current['pop_density'].isnull().sum()
missing_ln_pop = df_current['ln_pop_density'].isnull().sum()
print(f"Missing pop_density: {missing_pop}")
print(f"Missing ln_pop_density: {missing_ln_pop}")

# Check regression-ready observations
regression_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density',
                  'industrial_advanced', 'fdi_openness', 'ln_road_area']
df_regression = df_current.dropna(subset=regression_vars)
print(f"\nRegression-ready observations: {len(df_regression)}")

# Save corrected dataset
output_path = '总数据集_2007-2023_完整版_无缺失FDI_修正pop_density.xlsx'
print(f"\n[7/7] Saving corrected dataset to {output_path}...")
df_current.to_excel(output_path, index=False)
print(f"[OK] Saved!")

print("\n" + "=" * 80)
print("POP_DENSITY BUG FIX COMPLETED!")
print("=" * 80)
print("\nSummary:")
print(f"  - Updated pop_density with correct values from raw data")
print(f"  - Reduced cities with constant pop_density: {num_constant_before} → {num_constant_after}")
print(f"  - Recalculated ln_pop_density")
print(f"  - Saved to: {output_path}")
