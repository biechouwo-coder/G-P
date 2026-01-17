import pandas as pd

df_pop = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

# Get all city names
cities = df_pop.iloc[:, 2].dropna().unique()
print(f'人口数据中总共有 {len(cities)} 个城市')

# Search for specific cities
search_cities = ['七台河市', '七台河', '丹东市', '丹东', '佳木斯市', '九江市']

print('\n查找特定城市:')
for target in search_cities:
    # Exact match
    exact_matches = [c for c in cities if c == target]
    # Partial match
    partial_matches = [c for c in cities if target in c or c in target]

    if exact_matches:
        print(f'{target}: EXACT MATCH - {exact_matches[0]}')
    elif partial_matches:
        print(f'{target}: PARTIAL MATCH - {partial_matches[:3]}')
    else:
        print(f'{target}: NOT FOUND')

# Compare with total dataset cities
print('\n=== 与总数据集对比 ===')
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
total_cities = set(df_total['city_name'].unique())
pop_cities = set(cities)

print(f'总数据集城市数: {len(total_cities)}')
print(f'人口数据集城市数: {len(pop_cities)}')

only_in_total = total_cities - pop_cities
print(f'\n仅在总数据集中的城市: {len(only_in_total)}')
if len(only_in_total) > 0:
    print('前20个:')
    for city in list(only_in_total)[:20]:
        print(f'  - {city}')

# Check specific problematic cities
print('\n检查缺失GDP的城市是否在人口数据中:')
missing_gdp_cities = df_total[df_total['gdp_per_capita'].isnull()]['city_name'].unique()[:10]

for city in missing_gdp_cities:
    if city in pop_cities:
        print(f'  {city}: YES')
    else:
        # Try fuzzy match
        fuzzy = [c for c in pop_cities if city.replace('市', '') in c or c.replace('市', '') in city]
        if fuzzy:
            print(f'  {city}: MAYBE -> {fuzzy[0]}')
        else:
            print(f'  {city}: NO')
