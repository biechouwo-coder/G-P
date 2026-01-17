"""
第四步：计算碳排放强度并进行清洗
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("第四步：计算碳排放强度并进行清洗")
print("=" * 80)

# 1. 读取合并后的数据
df = pd.read_excel('合并后数据集_2007-2019_修正版.xlsx')

print(f"\n原始数据: {df.shape[0]} 行观测")
print(f"同时有碳排放和GDP数据的观测数: {df[['emission_million_tons', 'real_gdp_100m_yuan']].notnull().all(axis=1).sum()}")

# 2. 计算碳排放强度
# CEADs排放量单位：百万吨
# 实际GDP单位：亿元
# 碳排放强度目标单位：吨/万元
#
# 公式：
# 碳排放强度(吨/万元) = (排放量(百万吨) × 100万吨/百万吨) / (GDP(亿元) × 10000万元/亿元)
#                    = (排放量(百万吨) / GDP(亿元)) × (100/10000)
#                    = (排放量(百万吨) / GDP(亿元)) × 0.01
#
# 简化：
# 碳排放强度(吨/万元) = (emission_million_tons / real_gdp_100m_yuan) × 100
#                      = emission_million_tons / real_gdp_100m_yuan * 100
#                      = emission_million_tons / (real_gdp_100m_yuan / 100)
#                      = emission_million_tons / real_gdp_1b_yuan

# 首先将GDP转换为"亿元"为单位（已经是了，无需转换）
# 然后计算碳排放强度
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
df['ln_carbon_intensity_ceads_raw'] = np.log(df['carbon_intensity_ceads'])  # 未缩尾的对数

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

# 7. 对比原有碳排放强度数据
if 'carbon_intensity' in df.columns:
    print("\n" + "-" * 80)
    print("与原有碳排放强度数据对比")
    print("-" * 80)

    # 找出同时有两组数据的观测
    df_compare = df[df['carbon_intensity_ceads_winsor'].notnull() & df['carbon_intensity'].notnull()]

    if len(df_compare) > 0:
        print(f"同时有CEADs和原有碳排放数据的观测数: {len(df_compare)}")

        print("\n原有数据描述性统计:")
        print(df_compare['carbon_intensity'].describe())

        print("\nCEADs数据描述性统计:")
        print(df_compare['carbon_intensity_ceads_winsor'].describe())

        # 计算相关系数
        corr = df_compare[['carbon_intensity', 'carbon_intensity_ceads_winsor']].corr().iloc[0, 1]
        print(f"\n两组数据相关系数: {corr:.4f}")

# 8. 保留核心变量并保存
print("\n" + "=" * 80)
print("保存最终数据集")
print("=" * 80)

# 选择要保留的变量
core_vars = ['year', 'city_name', 'city_code',
             'carbon_intensity_ceads', 'carbon_intensity_ceads_winsor',
             'ln_carbon_intensity_ceads', 'ln_carbon_intensity_ceads_raw',
             'emission_million_tons', 'real_gdp_100m_yuan',
             'ln_pgdp', 'ln_pop_density', 'pop_density',
             'tertiary_share', 'industrial_advanced',
             'fdi_openness', 'ln_road_area', 'financial_development',
             'treat', 'post', 'did', 'pilot_year']

# 找出存在的变量
existing_vars = [var for var in core_vars if var in df.columns]

df_final = df[existing_vars].copy()

output_file = 'CEADs_最终数据集_2007-2019.xlsx'
df_final.to_excel(output_file, index=False)
print(f"[OK] 最终数据集已保存: {output_file}")
print(f"数据集形状: {df_final.shape}")
print(f"保留变量数: {len(existing_vars)}")

print("\n" + "=" * 80)
print("第四步完成！")
print("=" * 80)
