import pandas as pd

# Test: Try to merge GDP data manually for one city
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
df_gdp = df_gdp.iloc[:, :7].copy()
df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

# Test with a specific city
test_city = '七台河市'
print(f'=== 测试城市: {test_city} ===\n')

# Get this city's data from both datasets
total_city = df_total[df_total['city_name'] == test_city][['year', 'city_name', 'gdp_per_capita', 'population']]
gdp_city = df_gdp[df_gdp['city_name'] == test_city][['year', 'city_name', 'real_gdp']]

print('总数据集中该城市:')
print(total_city.head())

print('\nGDP数据集中该城市:')
print(gdp_city.head())

# Try merging
print('\n=== 尝试基于年份和城市名合并 ===')
merged = pd.merge(
    total_city[['year', 'city_name']],
    gdp_city[['year', 'city_name', 'real_gdp']],
    on=['year', 'city_name'],
    how='left'
)

print(f'合并后观测数: {len(merged)}')
print(f'real_gdp缺失数: {merged["real_gdp"].isnull().sum()}')
print('\n合并结果:')
print(merged.head())

# Check if the issue is with column names or data types
print('\n=== 数据类型检查 ===')
print(f'total_city year type: {total_city["year"].dtype}')
print(f'gdp_city year type: {gdp_city["year"].dtype}')
print(f'total_city city_name type: {total_city["city_name"].dtype}')
print(f'gdp_city city_name type: {gdp_city["city_name"].dtype}')

# Check for whitespace issues
print('\n=== 城市名称检查 ===')
print(f'total_city city_name (repr): {repr(total_city["city_name"].iloc[0])}')
print(f'gdp_city city_name (repr): {repr(gdp_city["city_name"].iloc[0])}')
