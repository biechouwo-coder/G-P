import pandas as pd

# Load datasets
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
df_gdp = df_gdp.iloc[:, :7].copy()
df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

# Filter for 2007-2023
df_gdp_2007 = df_gdp[(df_gdp['year'] >= 2007) & (df_gdp['year'] <= 2023)]

print('=== 城市名称匹配检查 ===\n')
print(f'总数据集城市数: {df_total["city_name"].nunique()}')
print(f'GDP数据集城市数(2007-2023): {df_gdp_2007["city_name"].nunique()}')

# Get unique city names
total_cities = set(df_total['city_name'].unique())
gdp_cities = set(df_gdp_2007['city_name'].unique())

# Cities in GDP but not in total
only_in_gdp = gdp_cities - total_cities
print(f'\n仅在GDP数据集中的城市: {len(only_in_gdp)}')
for city in sorted(list(only_in_gdp))[:15]:
    print(f'  - {city}')

# Cities in total but missing GDP
missing_gdp_in_total = df_total[df_total['gdp_per_capita'].isnull()]['city_name'].unique()
print(f'\n总数据集中缺失GDP的城市: {len(missing_gdp_in_total)}')

# Check if these cities exist in GDP data with different names
print('\n检查部分缺失GDP的城市是否在GDP数据集中:')
for city in list(missing_gdp_in_total)[:10]:
    # Direct match
    if city in gdp_cities:
        print(f'  {city}: YES (名称一致)')
    else:
        # Try fuzzy match (remove suffixes)
        found = False
        for gdp_city in gdp_cities:
            if city in gdp_city or gdp_city in city:
                print(f'  {city}: MAYBE -> "{gdp_city}"')
                found = True
                break
        if not found:
            print(f'  {city}: NO 未找到')

# Sample comparison
print('\n=== 城市名称示例对比 ===')
print('总数据集城市示例:', sorted(list(total_cities))[:10])
print('GDP数据集城市示例:', sorted(list(gdp_cities))[:10])
