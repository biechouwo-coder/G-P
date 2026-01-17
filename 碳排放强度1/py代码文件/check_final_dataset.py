import pandas as pd
import numpy as np

# Read final dataset
df = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

print('=== Final Dataset Structure ===')
print(f'Shape: {df.shape}')
print(f'\nColumns: {list(df.columns)}')

# Check for the problematic value in pop_density
print('\n=== Searching for value 3880.01892445986 in pop_density ===')
target_value = 3880.01892445986

if 'pop_density' in df.columns:
    count = (df['pop_density'] == target_value).sum()
    print(f'Found {count} occurrences of {target_value} in pop_density')

    if count > 0:
        print('\nCities with this value:')
        affected_cities = df[df['pop_density'] == target_value].groupby('city_name').size()
        print(affected_cities.head(20))

        print('\nYears with this value (by city):')
        for city in affected_cities.index[:5]:
            city_data = df[(df['city_name'] == city) & (df['pop_density'] == target_value)]
            years = sorted(city_data['year'].unique())
            print(f'{city}: {years}')

# Check Shanghai specifically
print('\n=== Shanghai pop_density values ===')
shanghai = df[df['city_name'] == '上海市']
if len(shanghai) > 0:
    print(f'Shanghai pop_density (2010-2023):')
    print(shanghai[['year', 'pop_density']].sort_values('year'))

# Check Dongguan specifically
print('\n=== Dongguan pop_density values ===')
dongguan = df[df['city_name'] == '东莞市']
if len(dongguan) > 0:
    print(f'Dongguan pop_density (2010-2023):')
    print(dongguan[['year', 'pop_density']].sort_values('year'))

# Statistics on pop_density
print('\n=== Pop Density Statistics ===')
print(df['pop_density'].describe())

# Check for constant values
print('\n=== Cities with constant pop_density (suspicious) ===')
city_stats = df.groupby('city_name')['pop_density'].agg(['std', 'count'])
constant_cities = city_stats[city_stats['std'] == 0]
print(f'Found {len(constant_cities)} cities with constant pop_density')
print(constant_cities.head(20))