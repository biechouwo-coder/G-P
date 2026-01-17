"""
Data Transformation for Regression Analysis
Purpose: Generate logarithmic variables to prepare for DID regression

Variables to transform:
- pop_density → ln_pop_density (population density)
- gdp_per_capita → ln_pgdp (GDP per capita)
- population → ln_pop (population size)
- fdi → ln_fdi (foreign direct investment)
- road_area → ln_road_area (already exists, will verify)

Note: Use ln(x+1) for variables with zero values to preserve samples
Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# Load final dataset
print('[OK] Loading final dataset...')
df = pd.read_excel('总数据集_2007-2023_完整版.xlsx')
print(f'[OK] Dataset loaded: {df.shape[0]} observations × {df.shape[1]} variables')

# Check for zero values before transformation
print('\n[INFO] Checking for zero/negative values before log transformation...')

vars_to_check = ['pop_density', 'gdp_per_capita', 'population', 'fdi', 'road_area']

for var in vars_to_check:
    if var in df.columns:
        zero_count = (df[var] <= 0).sum()
        neg_count = (df[var] < 0).sum()
        min_val = df[var].min()
        print(f'    {var}:')
        print(f'      - Min value: {min_val:.4f}')
        print(f'      - Zero count: {zero_count} ({zero_count/len(df)*100:.2f}%)')
        print(f'      - Negative count: {neg_count}')

print('\n[OK] Creating logarithmic variables...')

# 1. Population density (pop_density → ln_pop_density)
df['ln_pop_density'] = np.log(df['pop_density'])
print('[OK] Created ln_pop_density')

# 2. GDP per capita (gdp_per_capita → ln_pgdp)
df['ln_pgdp'] = np.log(df['gdp_per_capita'])
print('[OK] Created ln_pgdp')

# 3. Population (population → ln_pop)
df['ln_pop'] = np.log(df['population'])
print('[OK] Created ln_pop')

# 4. FDI (fdi → ln_fdi)
# Use ln(x+1) to handle zero values
df['ln_fdi'] = np.log(df['fdi'] + 1)
print('[OK] Created ln_fdi (using ln(x+1) to handle zeros)')

# 5. Road area (ln_road_area already exists, verify it's correct)
if 'ln_road_area' in df.columns:
    # Check if it was computed as ln(road_area+1)
    expected_ln_road = np.log(df['road_area'] + 1)
    if np.allclose(df['ln_road_area'], expected_ln_road):
        print('[OK] Verified ln_road_area (computed as ln(road_area+1))')
    else:
        print('[WARNING] ln_road_area exists but may not use ln(x+1) transformation')
        print('[INFO] Recomputing ln_road_area as ln(road_area+1)')
        df['ln_road_area'] = np.log(df['road_area'] + 1)
else:
    print('[INFO] Creating ln_road_area')
    df['ln_road_area'] = np.log(df['road_area'] + 1)

print(f'\n[OK] Transformation complete. New shape: {df.shape}')

# Verify new variables
print('\n[INFO] Summary of transformed variables:')

transformed_vars = ['ln_pop_density', 'ln_pgdp', 'ln_pop', 'ln_fdi', 'ln_road_area']

for var in transformed_vars:
    if var in df.columns:
        print(f'\n    {var}:')
        print(f'      - Observations: {df[var].notna().sum()}')
        print(f'      - Mean: {df[var].mean():.4f}')
        print(f'      - Std: {df[var].std():.4f}')
        print(f'      - Min: {df[var].min():.4f}')
        print(f'      - Max: {df[var].max():.4f}')

# Compare with original variables
print('\n[INFO] Comparison: Original vs Log-transformed')
print('\n    Variable            | Original Mean | Log Mean | Scale Reduction')
print('    ' + '-'*70)

comparisons = [
    ('pop_density', 'ln_pop_density'),
    ('gdp_per_capita', 'ln_pgdp'),
    ('population', 'ln_pop'),
    ('fdi', 'ln_fdi'),
    ('road_area', 'ln_road_area')
]

for orig, log_var in comparisons:
    if orig in df.columns and log_var in df.columns:
        orig_mean = df[orig].mean()
        log_mean = df[log_var].mean()
        reduction = orig_mean / np.exp(log_mean) if log_mean > 0 else orig_mean
        print(f'    {orig:20} | {orig_mean:13.2f} | {log_mean:8.4f} | {reduction:.2f}x')

# Check for any infinite values after transformation
print('\n[INFO] Checking for infinite or anomalous values...')
for var in transformed_vars:
    if var in df.columns:
        inf_count = np.isinf(df[var]).sum()
        nan_count = df[var].isna().sum()
        print(f'    {var}: {inf_count} infinite, {nan_count} missing')

# Save updated dataset
output_file = '总数据集_2007-2023_回归准备版.xlsx'
print(f'\n[OK] Saving updated dataset to {output_file}...')

df.to_excel(output_file, index=False)

print(f'[OK] Dataset saved successfully!')
print(f'    - Original variables: {df.shape[1] - 5}')
print(f'    - New log variables: 5')
print(f'    - Total variables: {df.shape[1]}')
print(f'    - Observations: {len(df)}')

# Display variable list
print('\n[INFO] Updated variable list:')
print(f'    Total variables: {len(df.columns.tolist())}')
print(f'\n    Key variables for regression:')
print(f'      - Dependent: carbon_intensity')
print(f'      - Policy: did')
print(f'      - Core controls: ln_pop_density, ln_pgdp, ln_pop, ln_fdi, ln_road_area')
print(f'      - Other controls: tertiary_share, gdp_deflator')

print(f'\n[OK] Data transformation complete! Ready for regression analysis.')
