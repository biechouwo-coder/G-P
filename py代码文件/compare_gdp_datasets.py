import pandas as pd

# Load datasets
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
df_gdp = df_gdp.iloc[:, :7].copy()
df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

print('=== 数据集对比分析 ===\n')
print(f'总数据集城市数: {df_total["city_name"].nunique()}')
print(f'GDP数据集城市数: {df_gdp["city_name"].nunique()}')

print('\n在GDP数据中但不在总数据集中的城市:')
missing_in_total = set(df_gdp['city_name'].unique()) - set(df_total['city_name'].unique())
print(f'数量: {len(missing_in_total)}')
for city in list(missing_in_total)[:20]:
    print(f'  - {city}')

print('\n在总数据集中但不在GDP数据中的城市:')
missing_in_gdp = set(df_total['city_name'].unique()) - set(df_gdp['city_name'].unique())
print(f'数量: {len(missing_in_gdp)}')
for city in list(missing_in_gdp)[:20]:
    print(f'  - {city}')

# Check which cities have missing GDP in total dataset
print('\n=== 总数据集中GDP缺失的城市 ===')
missing_gdp_total = df_total[df_total['gdp_per_capita'].isnull()]['city_name'].unique()
print(f'数量: {len(missing_gdp_total)}')
print('这些城市在GDP数据集中是否存在:')
for city in list(missing_gdp_total)[:10]:
    in_gdp = city in df_gdp['city_name'].values
    print(f'  {city}: {"存在" if in_gdp else "不存在"}')
