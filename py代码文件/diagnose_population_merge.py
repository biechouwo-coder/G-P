import pandas as pd

# Load datasets
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
df_pop = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

# Rename population data columns properly
df_pop_clean = df_pop.iloc[:, :9].copy()
df_pop_clean.columns = ['year', 'province', 'city_name', 'city_code', 'city_code_2',
                        'area', 'population', 'population_2', 'pop_density']

# Filter for 2007-2023
df_pop_clean = df_pop_clean[(df_pop_clean['year'] >= 2007) & (df_pop_clean['year'] <= 2023)]

print('人口数据集:')
print(f'  观测数: {len(df_pop_clean)}')
print(f'  城市数: {df_pop_clean["city_name"].nunique()}')

# Test with a specific city
test_city = '七台河市'
print(f'\n=== 测试城市: {test_city} ===')

# Get population data for this city
pop_city = df_pop_clean[df_pop_clean['city_name'] == test_city][['year', 'city_name', 'population', 'pop_density']]
print(f'\n人口数据中的记录 ({len(pop_city)} 条):')
print(pop_city.head())

# Get total dataset record for this city
total_city = df_total[df_total['city_name'] == test_city][['year', 'city_name', 'population', 'pop_density']]
print(f'\n总数据集中的记录 ({len(total_city)} 条):')
print(total_city.head())

# Try to merge
print('\n=== 尝试手动合并 ===')
merged = pd.merge(
    df_total[df_total['city_name'] == test_city][['year', 'city_name']],
    pop_city[['year', 'city_name', 'population', 'pop_density']],
    on=['year', 'city_name'],
    how='left'
)
print(f'合并结果 ({len(merged)} 条):')
print(merged)

# Check data types
print('\n=== 数据类型检查 ===')
print(f'人口数据集 year 类型: {pop_city["year"].dtype}')
print(f'总数据集 year 类型: {total_city["year"].dtype}')
print(f'人口数据集 city_name 类型: {pop_city["city_name"].dtype}')
print(f'总数据集 city_name 类型: {total_city["city_name"].dtype}')

# Check for whitespace
print('\n=== 城市名称检查 (使用repr) ===')
if len(pop_city) > 0:
    print(f'人口数据: {repr(pop_city["city_name"].iloc[0])}')
if len(total_city) > 0:
    print(f'总数据集: {repr(total_city["city_name"].iloc[0])}')
