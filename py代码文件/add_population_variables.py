"""
添加人口相关变量：总人口和人均GDP
"""

import pandas as pd
from pathlib import Path

# 文件路径
POP_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\298个地级市人口密度1998-2024年无缺失.xlsx")
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")

print("=" * 80)
print("添加人口相关变量")
print("=" * 80)

# 读取原始人口数据
print("\n[步骤1/3] 读取原始人口数据...")
df_pop_raw = pd.read_excel(POP_FILE)
print(f"原始人口数据: {df_pop_raw.shape}")

# 提取关键列：年份[0], 城市[2], 代码[4], 常住人口[6]
df_pop = df_pop_raw.iloc[:, [0, 2, 4, 6]].copy()
df_pop.columns = ['year', 'city_name', 'city_code', 'population']
df_pop['year'] = df_pop['year'].astype('Int64')

print(f"\n提取后人口数据:")
print(f"  Shape: {df_pop.shape}")
print(f"  Columns: {list(df_pop.columns)}")
print(f"  人口范围: {df_pop['population'].min():.0f} - {df_pop['population'].max():.0f} 万人")

# 筛选2007-2023年
df_pop_filtered = df_pop[
    (df_pop['year'] >= 2007) &
    (df_pop['year'] <= 2023)
].copy()

print(f"\n筛选2007-2023年后: {df_pop_filtered.shape}")

# 读取清洗后的数据
print("\n[步骤2/3] 读取清洗后数据...")
df_cleaned = pd.read_excel(INPUT_FILE)
print(f"清洗后数据: {df_cleaned.shape}")

# 合并总人口数据
df_merged = pd.merge(
    df_cleaned,
    df_pop_filtered[['year', 'city_name', 'population']],
    on=['year', 'city_name'],
    how='left'
)

print(f"\n合并后数据: {df_merged.shape}")
print(f"  缺失人口数据: {df_merged['population'].isnull().sum()}")

# 计算人均实际GDP（2000年基期）
# gdp_real单位：亿元
# population单位：万人
# 人均GDP = (gdp_real × 10000) / population  （元/人）
df_merged['gdp_per_capita'] = (df_merged['gdp_real'] * 10000) / df_merged['population']

print(f"\n[步骤3/3] 计算人均实际GDP...")
print(f"  人均GDP范围: {df_merged['gdp_per_capita'].min():.0f} - {df_merged['gdp_per_capita'].max():.0f} 元/人")
print(f"  人均GDP均值: {df_merged['gdp_per_capita'].mean():.0f} 元/人")

# 重新排列列顺序
cols = ['year', 'city_name', 'city_code', 'population', 'pop_density',
        'gdp_real', 'gdp_per_capita', 'gdp_deflator',
        'carbon_intensity', 'tertiary_share', 'industrial_upgrading']

# 确保所有列都存在
available_cols = [c for c in cols if c in df_merged.columns]
remaining_cols = [c for c in df_merged.columns if c not in cols]
df_final = df_merged[available_cols + remaining_cols]

print(f"\n最终数据集:")
print(f"  Shape: {df_final.shape}")
print(f"  Columns: {list(df_final.columns)}")

# 描述性统计
print(f"\n新增变量描述性统计:")
print(f"\n总人口（万人）:")
print(f"  均值: {df_final['population'].mean():.2f}")
print(f"  标准差: {df_final['population'].std():.2f}")
print(f"  范围: {df_final['population'].min():.2f} - {df_final['population'].max():.2f}")

print(f"\n人均实际GDP（元/人）:")
print(f"  均值: {df_final['gdp_per_capita'].mean():.0f}")
print(f"  标准差: {df_final['gdp_per_capita'].std():.0f}")
print(f"  范围: {df_final['gdp_per_capita'].min():.0f} - {df_final['gdp_per_capita'].max():.0f}")

# 保存更新后的数据
print(f"\n保存到: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_final.to_excel(writer, sheet_name='清洗后数据', index=False)

print(f"\n文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
print("\n人口相关变量添加完成！")
