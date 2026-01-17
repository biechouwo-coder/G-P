import pandas as pd
import numpy as np

# Read raw data - need to use column positions
df_raw = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('=== Raw Pop Density Data ===')
print(f'Shape: {df_raw.shape}')
print(f'\nColumn 8 should be pop_density (人口密度)')
print(f'Column 2 should be city_name (地级市)')
print(f'Column 0 should be year (年份)')

# Extract relevant columns
year_col = df_raw.iloc[:, 0]
city_col = df_raw.iloc[:, 2]
pop_density_col = df_raw.iloc[:, 8]

# Check Shanghai (上海市)
print('\n=== Shanghai in Raw Data ===')
shanghai_mask = df_raw.iloc[:, 2].str.contains('上海', na=False)
shanghai_raw = df_raw[shanghai_mask]
print(f'Found {len(shanghai_raw)} rows for Shanghai')
print('\nShanghai pop_density by year:')
for idx in shanghai_raw.index:
    yr = df_raw.iloc[idx, 0]
    pd_val = df_raw.iloc[idx, 8]
    print(f'{int(yr)}: {pd_val}')

# Check Dongguan (东莞市)
print('\n=== Dongguan in Raw Data ===')
dongguan_mask = df_raw.iloc[:, 2].str.contains('东莞', na=False)
dongguan_raw = df_raw[dongguan_mask]
print(f'Found {len(dongguan_raw)} rows for Dongguan')
print('\nDongguan pop_density by year:')
for idx in dongguan_raw.index:
    yr = df_raw.iloc[idx, 0]
    pd_val = df_raw.iloc[idx, 8]
    print(f'{int(yr)}: {pd_val}')

# Check if 3880.018924 exists in raw data
print('\n=== Searching for 3880.018924 in raw data ===')
target = 3880.018924
count = (pop_density_col == target).sum()
print(f'Found {count} exact matches')
count_close = (np.abs(pop_density_col - target) < 0.000001).sum()
print(f'Found {count_close} close matches (within 0.000001)')

# Check for suspicious patterns
print('\n=== Checking for constant values in recent years ===')
# Check years 2013-2023 (columns might be year-specific)
# Actually the data seems to be in long format with year in column 0
print('Unique years in data:', sorted(year_col.unique()))

# Check which cities have constant pop_density in 2013-2023
print('\n=== Checking for cities with pop_density stuck at 3880 ===')
recent_mask = year_col >= 2013
recent_data = df_raw[recent_mask]

# Group by city and check if all values are the same
city_constancy = {}
for city in recent_data.iloc[:, 2].unique():
    city_data = recent_data[recent_data.iloc[:, 2] == city]
    pd_values = city_data.iloc[:, 8].values
    if len(pd_values) > 1 and np.all(pd_values == pd_values[0]):
        if pd_values[0] > 3000:  # Only high density cities
            city_constancy[city] = pd_values[0]

print(f'Found {len(city_constancy)} cities with constant high pop_density since 2013:')
for city, val in city_constancy.items():
    print(f'{city}: {val}')
