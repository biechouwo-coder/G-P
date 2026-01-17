import pandas as pd

df = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_完整版.xlsx')
missing = df[df['ln_pgdp'].isnull()]

print(f'缺失人均GDP的观测数: {len(missing)}')
print(f'涉及城市数: {missing["city_name"].nunique()}')

print('\n这些城市及其观测数:')
cities = missing['city_name'].unique()
for i, city in enumerate(cities, 1):
    city_count = len(missing[missing['city_name'] == city])
    print(f'{i}. {city}: {city_count} observations')

print('\n按年份分布:')
print(missing['year'].value_counts().sort_index())

# Check if these are mostly 2023 data
print(f'\n2023年的缺失: {len(missing[missing["year"] == 2023])}')
print(f'其他年份的缺失: {len(missing[missing["year"] != 2023])}')
