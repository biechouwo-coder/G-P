import pandas as pd

# Load datasets
df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')

df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
df_gdp = df_gdp.iloc[:, :7].copy()
df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

# Check a specific city that has GDP data but missing in total dataset
test_city = '台山市'
print(f'=== 检查城市: {test_city} ===\n')

print(f'在GDP数据集中:')
gdp_city = df_gdp[df_gdp['city_name'] == test_city]
print(f'  观测数: {len(gdp_city)}')
if len(gdp_city) > 0:
    print(f'  年份范围: {gdp_city["year"].min():.0f} - {gdp_city["year"].max():.0f}')
    print(f'  实际GDP均值: {gdp_city["real_gdp"].mean():.2f}')
    print('\n  最近5年数据:')
    print(gdp_city[['year', 'real_gdp']].tail())

print(f'\n在总数据集中:')
total_city = df_total[df_total['city_name'] == test_city]
print(f'  观测数: {len(total_city)}')
if len(total_city) > 0:
    print(f'  年份范围: {total_city["year"].min():.0f} - {total_city["year"].max():.0f}')
    print(f'  GDP per capita缺失: {total_city["gdp_per_capita"].isnull().sum()}')
    print(f'  人口缺失: {total_city["population"].isnull().sum()}')
else:
    print('  该城市不存在于总数据集中!')

# Check multiple cities
print('\n\n=== 抽样检查5个有GDP数据但在总数据集中缺失GDP的城市 ===')
missing_gdp_total = df_total[df_total['gdp_per_capita'].isnull()]['city_name'].unique()[:5]

for city in missing_gdp_total:
    print(f'\n城市: {city}')
    gdp_city_data = df_gdp[df_gdp['city_name'] == city]

    if len(gdp_city_data) > 0:
        print(f'  GDP数据集: {len(gdp_city_data)} 条记录')
        print(f'  2007-2023: {len(gdp_city_data[(gdp_city_data["year"] >= 2007) & (gdp_city_data["year"] <= 2023)])} 条记录')
        print(f'  实际GDP缺失: {gdp_city_data["real_gdp"].isnull().sum()}')
    else:
        print('  GDP数据集中无此城市')
