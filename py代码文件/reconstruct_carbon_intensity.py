"""
重新计算碳排放强度变量
使用公式：碳排放强度 = 碳排放总量（吨）/ 实际GDP（亿元，2000年基期）
"""

import pandas as pd
from pathlib import Path

# 文件路径
CARBON_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\地级市碳排放强度.xlsx")
GDP_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
CLEANED_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版_新版.xlsx")

print("=" * 80)
print("重新计算碳排放强度")
print("=" * 80)

# 读取碳排放数据
print("\n[步骤1/4] 读取碳排放数据...")
df_carbon_raw = pd.read_excel(CARBON_FILE)
print(f"原始碳排放数据: {df_carbon_raw.shape}")

# 读取GDP数据
print("\n[步骤2/4] 读取GDP数据...")
df_gdp_raw = pd.read_excel(GDP_FILE)
print(f"原始GDP数据: {df_gdp_raw.shape}")

# 提取关键变量
print("\n提取碳排放总量和GDP变量...")

# 碳排放数据：根据位置提取
# 列位置：年份[0], 代码[1], 城市[3], 碳排放总量[6], GDP[7], 原碳排放强度[8]
df_carbon = df_carbon_raw.iloc[:, [0, 1, 3, 6]].copy()
df_carbon.columns = ['year', 'city_code', 'city_name', 'carbon_emissions_tons']
df_carbon['year'] = df_carbon['year'].astype('Int64')

print(f"\n碳排放数据:")
print(f"  Shape: {df_carbon.shape}")
print(f"  Columns: {list(df_carbon.columns)}")
print(f"  碳排放总量范围: {df_carbon['carbon_emissions_tons'].min():.0f} - {df_carbon['carbon_emissions_tons'].max():.0f} 吨")

# GDP数据：根据位置提取
# 列位置：省份[0], 城市[1], 年份[2], 实际GDP[5]
df_gdp = df_gdp_raw.iloc[:, [1, 2, 5]].copy()
df_gdp.columns = ['city_name', 'year', 'gdp_real_2000']
df_gdp['year'] = df_gdp['year'].astype('Int64')

print(f"\nGDP数据:")
print(f"  Shape: {df_gdp.shape}")
print(f"  Columns: {list(df_gdp.columns)}")
print(f"  实际GDP范围: {df_gdp['gdp_real_2000'].min():.2f} - {df_gdp['gdp_real_2000'].max():.2f} 亿元")

# 合并碳排放和GDP数据
print("\n[步骤3/4] 合并数据并计算碳排放强度...")
df_merged = pd.merge(
    df_carbon,
    df_gdp,
    on=['city_name', 'year'],
    how='inner'
)

print(f"合并后数据: {df_merged.shape}")
print(f"  唯一城市数: {df_merged['city_name'].nunique()}")

# 计算新的碳排放强度
# 公式：碳排放强度 = 碳排放总量（吨）/ 实际GDP（亿元）
# 结果单位：吨/亿元 = 万吨/亿元
df_merged['carbon_intensity_new'] = df_merged['carbon_emissions_tons'] / df_merged['gdp_real_2000']

print(f"\n新计算的碳排放强度:")
print(f"  均值: {df_merged['carbon_intensity_new'].mean():.4f}")
print(f"  标准差: {df_merged['carbon_intensity_new'].std():.4f}")
print(f"  范围: {df_merged['carbon_intensity_new'].min():.4f} - {df_merged['carbon_intensity_new'].max():.4f}")
print(f"  单位: 吨/亿元（即万吨/亿元）")

# 筛选2007-2023年数据
df_filtered = df_merged[
    (df_merged['year'] >= 2007) &
    (df_merged['year'] <= 2023)
].copy()

print(f"\n筛选2007-2023年后: {df_filtered.shape}")
print(f"  城市数: {df_filtered['city_name'].nunique()}")

# 读取清洗后的数据集（用于获取其他变量）
print("\n[步骤4/4] 更新清洗后数据集...")
df_cleaned = pd.read_excel(CLEANED_FILE)
print(f"清洗后数据: {df_cleaned.shape}")

# 删除旧的carbon_intensity列
if 'carbon_intensity' in df_cleaned.columns:
    df_cleaned = df_cleaned.drop(columns=['carbon_intensity'])
    print("已删除旧的carbon_intensity列")

# 合并新的碳排放强度数据
df_final = pd.merge(
    df_cleaned,
    df_filtered[['year', 'city_name', 'carbon_intensity_new']],
    on=['year', 'city_name'],
    how='left'
)

# 重命名新变量
df_final = df_final.rename(columns={'carbon_intensity_new': 'carbon_intensity'})

# 检查缺失情况
print(f"\n最终数据: {df_final.shape}")
print(f"  缺失值统计:")
missing_count = df_final['carbon_intensity'].isnull().sum()
if missing_count > 0:
    missing_pct = missing_count / len(df_final) * 100
    print(f"    carbon_intensity: {missing_count} ({missing_pct:.2f}%)")
else:
    print(f"    carbon_intensity: 0 (0%) - 完整！")

# 描述性统计
print(f"\n更新后的碳排放强度描述性统计:")
print(f"  观测数: {df_final['carbon_intensity'].notna().sum()}")
print(f"  均值: {df_final['carbon_intensity'].mean():.4f}")
print(f"  标准差: {df_final['carbon_intensity'].std():.4f}")
print(f"  最小值: {df_final['carbon_intensity'].min():.4f}")
print(f"  最大值: {df_final['carbon_intensity'].max():.4f}")

# 保存更新后的数据
print(f"\n保存到: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_final.to_excel(writer, sheet_name='清洗后数据', index=False)

print(f"\n文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
print("\n碳排放强度变量更新完成！")
print("新变量基于：碳排放总量（吨）/ 实际GDP（亿元，2000年基期）")
