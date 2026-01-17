"""
第四步：计算碳排放强度并进行清洗（V2版本）
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("第四步：计算碳排放强度并进行清洗（V2版本 - 修复吉林/北京/上海Bug）")
print("=" * 80)

# 1. 读取合并后的数据
df = pd.read_excel('合并后数据集_2007-2019_修正版V2.xlsx')

print(f"\n原始数据: {df.shape[0]} 行观测")
print(f"同时有碳排放和GDP数据的观测数: {df[['emission_million_tons', 'real_gdp_100m_yuan']].notnull().all(axis=1).sum()}")

# 2. 计算碳排放强度
df['carbon_intensity_ceads'] = (df['emission_million_tons'] / df['real_gdp_100m_yuan']) * 100

print("\n计算碳排放强度后:")
print(f"碳排放强度非缺失观测数: {df['carbon_intensity_ceads'].notnull().sum()}")

# 3. 检查异常值
print("\n碳排放强度描述性统计（缩尾前）:")
print(df['carbon_intensity_ceads'].describe())

# 4. 缩尾处理（Winsorize at 1% and 99%）
print("\n" + "-" * 80)
print("缩尾处理（1%和99%）")
print("-" * 80)

# 计算1%和99%分位数
p01 = df['carbon_intensity_ceads'].quantile(0.01)
p99 = df['carbon_intensity_ceads'].quantile(0.99)

print(f"1%分位数: {p01:.4f}")
print(f"99%分位数: {p99:.4f}")

# 进行缩尾
df['carbon_intensity_ceads_winsor'] = df['carbon_intensity_ceads'].clip(lower=p01, upper=p99)

print("\n碳排放强度描述性统计（缩尾后）:")
print(df['carbon_intensity_ceads_winsor'].describe())

# 5. 生成对数变量
print("\n" + "-" * 80)
print("生成对数变量")
print("-" * 80)

df['ln_carbon_intensity_ceads'] = np.log(df['carbon_intensity_ceads_winsor'])

print("对数碳排放强度描述性统计（基于缩尾后数据）:")
print(df['ln_carbon_intensity_ceads'].describe())

# 6. 检查数据合理性
print("\n" + "=" * 80)
print("数据合理性检查")
print("=" * 80)

print("\n经验值检查（中国城市碳排放强度通常在0.5-5.0吨/万元之间）:")
ci_mean = df['carbon_intensity_ceads_winsor'].mean()
ci_median = df['carbon_intensity_ceads_winsor'].median()
ci_min = df['carbon_intensity_ceads_winsor'].min()
ci_max = df['carbon_intensity_ceads_winsor'].max()

print(f"均值: {ci_mean:.4f} 吨/万元")
print(f"中位数: {ci_median:.4f} 吨/万元")
print(f"最小值: {ci_min:.4f} 吨/万元")
print(f"最大值: {ci_max:.4f} 吨/万元")

if 0.5 <= ci_mean <= 5.0:
    print("\n[OK] 均值在合理范围内")
else:
    print(f"\n[WARNING] 均值异常！当前值: {ci_mean:.4f}")

# 7. 对比V1版本
print("\n" + "=" * 80)
print("与V1版本对比")
print("=" * 80)

print("\nV1版本:")
print("  观测数: 2,271")
print("  城市数: 212")
print("  碳排放强度均值: 2.7980 吨/万元")

print("\nV2版本（修复Bug后）:")
print(f"  观测数: {df['carbon_intensity_ceads_winsor'].notnull().sum()}")
print(f"  城市数: {df[df['carbon_intensity_ceads_winsor'].notnull()]['city_name'].nunique()}")
print(f"  碳排放强度均值: {ci_mean:.4f} 吨/万元")

# 8. 检查新增城市（吉林、北京、上海）
print("\n新增城市详情:")
new_cities = ['吉林市', '北京市', '上海市']
for city in new_cities:
    city_data = df[(df['city_name'] == city) & (df['carbon_intensity_ceads_winsor'].notnull())]
    if len(city_data) > 0:
        mean_ci = city_data['carbon_intensity_ceads_winsor'].mean()
        print(f"  {city}: {len(city_data)}个观测, 平均碳排放强度 {mean_ci:.4f} 吨/万元")
    else:
        print(f"  {city}: 未找到数据")

# 9. 保留核心变量并保存
print("\n" + "=" * 80)
print("保存最终数据集")
print("=" * 80)

# 选择要保留的变量
core_vars = ['year', 'city_name', 'city_code',
             'carbon_intensity_ceads', 'carbon_intensity_ceads_winsor',
             'ln_carbon_intensity_ceads',
             'emission_million_tons', 'real_gdp_100m_yuan',
             'ln_pgdp', 'ln_pop_density', 'pop_density',
             'tertiary_share', 'industrial_advanced',
             'fdi_openness', 'ln_road_area', 'financial_development',
             'treat', 'post', 'did', 'pilot_year']

# 找出存在的变量
existing_vars = [var for var in core_vars if var in df.columns]

df_final = df[existing_vars].copy()

output_file = 'CEADs_最终数据集_2007-2019_V2.xlsx'
df_final.to_excel(output_file, index=False)
print(f"[OK] 最终数据集已保存: {output_file}")
print(f"数据集形状: {df_final.shape}")
print(f"保留变量数: {len(existing_vars)}")

print("\n" + "=" * 80)
print("第四步完成！Bug已修复！")
print("=" * 80)
