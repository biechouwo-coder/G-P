import pandas as pd
import numpy as np

# Read raw data
df = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('=== Raw Pop Density Data Structure ===')
print(f'Shape: {df.shape}')
print(f'\nColumns (first 10):')
for i, col in enumerate(df.columns[:10]):
    print(f'{i}: {col}')

print(f'\nFirst 3 rows:')
print(df.head(3))

# Check for the problematic value
print('\n=== Searching for value 3880.01892445986 ===')
target_value = 3880.01892445986
for col in df.columns:
    if df[col].dtype in ['float64', 'int64']:
        count = (df[col] == target_value).sum()
        if count > 0:
            print(f'Column "{col}": {count} occurrences of {target_value}')

# Find Shanghai and Dongguan data
print('\n=== Looking for Shanghai and Dongguan ===')
# Try different column positions for city identifiers
for col_idx in range(min(5, len(df.columns))):
    print(f'Column {col_idx} unique values (first 10):')
    print(df.iloc[:, col_idx].unique()[:10])
    print()

# Check if there's a city name column
print('\nSample rows that contain the problematic value:')
for col in df.columns:
    if df[col].dtype in ['float64', 'int64']:
        mask = df[col] == target_value
        if mask.sum() > 0:
            print(f'\nFound in column "{col}":')
            print(df[mask][df.columns[:5]].head(10))
            break