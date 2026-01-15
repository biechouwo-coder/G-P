import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel('人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/回归分析数据集.xlsx')

print(f"[INFO] 数据集形状: {df.shape}")
print(f"[INFO] 年份范围: {df['year'].min()} - {df['year'].max()}")
print(f"[INFO] 城市数: {df['city_name'].nunique()}")

# 检查人口密度变量的统计
print(f"\n{'='*80}")
print(f"人口密度变量（ln_pop_density）检查")
print(f"{'='*80}")

print(f"\nln_pop_density 描述性统计:")
print(df['ln_pop_density'].describe())

# 检查原始 pop_density 变量
if 'pop_density' in df.columns:
    print(f"\npop_density 描述性统计:")
    print(df['pop_density'].describe())

# 检查每个城市的 pop_density 标准差（查找常数）
print(f"\n{'='*80}")
print(f"检查每个城市的 pop_density 变异情况")
print(f"{'='*80}")

city_std = df.groupby('city_name')['ln_pop_density'].std().sort_values()
print(f"\nln_pop_density 标准差最小的10个城市（可能存在问题）:")
print(city_std.head(10))

print(f"\nln_pop_density 标准差为0的城市（常数值，数据错误）:")
constant_cities = city_std[city_std == 0]
if len(constant_cities) > 0:
    print(f"发现 {len(constant_cities)} 个城市的ln_pop_density为常数:")
    for city in constant_cities.index:
        city_data = df[df['city_name'] == city]
        print(f"  {city}: ln_pop_density = {city_data['ln_pop_density'].iloc[0]:.6f}, {len(city_data)}年数据")
else:
    print("未发现标准差为0的城市")

# 检查上海和东莞（之前有问题的城市）
print(f"\n{'='*80}")
print(f"检查之前发现问题的城市（上海、东莞）")
print(f"{'='*80}")

problem_cities = ['上海市', '东莞市']
for city in problem_cities:
    city_data = df[df['city_name'] == city].sort_values('year')
    if len(city_data) > 0:
        print(f"\n{city}:")
        print(f"  观测数: {len(city_data)}")
        print(f"  ln_pop_density 范围: {city_data['ln_pop_density'].min():.6f} - {city_data['ln_pop_density'].max():.6f}")
        print(f"  ln_pop_density 标准差: {city_data['ln_pop_density'].std():.6f}")
        if 'pop_density' in df.columns:
            print(f"  pop_density 范围: {city_data['pop_density'].min():.2f} - {city_data['pop_density'].max():.2f}")
            print(f"  pop_density 标准差: {city_data['pop_density'].std():.2f}")

        # 检查是否有重复值
        unique_values = city_data['ln_pop_density'].nunique()
        total_values = len(city_data)
        print(f"  唯一值数量: {unique_values}/{total_values}")
        if unique_values < total_values:
            print(f"  [WARNING] 存在重复值!")

# 检查主要城市
print(f"\n{'='*80}")
print(f"主要城市人口密度检查")
print(f"{'='*80}")

major_cities = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '南京市', '成都市', '武汉市']
for city in major_cities:
    city_data = df[df['city_name'] == city]
    if len(city_data) > 0:
        print(f"{city}: ln_pop_density 均值={city_data['ln_pop_density'].mean():.6f}, 标准差={city_data['ln_pop_density'].std():.6f}, 观测数={len(city_data)}")

# 检查缺失值
print(f"\n{'='*80}")
print(f"缺失值检查")
print(f"{'='*80}")
print(f"ln_pop_density 缺失数: {df['ln_pop_density'].isnull().sum()}/{len(df)}")

# 检查异常值
print(f"\n{'='*80}")
print(f"异常值检查（极值）")
print(f"{'='*80}")
print(f"ln_pop_density 最小10个值:")
print(df.nsmallest(10, 'ln_pop_density')[['city_name', 'year', 'ln_pop_density']])
print(f"\nln_pop_density 最大10个值:")
print(df.nlargest(10, 'ln_pop_density')[['city_name', 'year', 'ln_pop_density']])
