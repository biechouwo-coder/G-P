import pandas as pd

# Read GDP data
df = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)

# Create a proper DataFrame with named columns
df_gdp = df.iloc[:, :7].copy()
df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

print('=== GDP数据缺失情况分析 ===\n')
print(f'总观测数: {len(df_gdp)}')
print(f'城市数量: {df_gdp["city_name"].nunique()}')
print(f'年份范围: {df_gdp["year"].min():.0f} - {df_gdp["year"].max():.0f}')

print('\n=== 实际GDP缺失情况 ===')
missing_gdp = df_gdp[df_gdp['real_gdp'].isnull()]
print(f'缺失观测数: {len(missing_gdp)}')
print(f'缺失率: {len(missing_gdp) / len(df_gdp) * 100:.2f}%')
print(f'缺失城市数: {missing_gdp["city_name"].nunique()}')

print('\n缺失城市列表:')
missing_cities = missing_gdp['city_name'].unique()
for i, city in enumerate(missing_cities, 1):
    print(f'{i}. {city}')

print('\n按年份分布缺失情况:')
for year in sorted(missing_gdp['year'].dropna().unique()):
    year_missing = missing_gdp[missing_gdp['year'] == year]
    print(f'{year:.0f}年: {len(year_missing)}个城市缺失')

print('\n=== GDP平减指数缺失情况 ===')
missing_deflator = df_gdp[df_gdp['gdp_deflator'].isnull()]
print(f'缺失观测数: {len(missing_deflator)}')
print(f'缺失率: {len(missing_deflator) / len(df_gdp) * 100:.2f}%')

print('\n=== 2007-2023年期间数据覆盖情况 ===')
df_2007_2023 = df_gdp[(df_gdp['year'] >= 2007) & (df_gdp['year'] <= 2023)]
print(f'2007-2023年总观测数: {len(df_2007_2023)}')
print(f'2007-2023年城市数: {df_2007_2023["city_name"].nunique()}')

missing_2007_2023 = df_2007_2023[df_2007_2023['real_gdp'].isnull()]
print(f'2007-2023年缺失GDP的观测数: {len(missing_2007_2023)}')
print(f'2007-2023年缺失GDP的城市数: {missing_2007_2023["city_name"].nunique()}')

print('\n2007-2023年缺失GDP的城市:')
cities_missing_2007 = missing_2007_2023['city_name'].unique()
for i, city in enumerate(cities_missing_2007[:30], 1):
    print(f'{i}. {city}')
if len(cities_missing_2007) > 30:
    print(f'... 还有 {len(cities_missing_2007) - 30} 个城市')
