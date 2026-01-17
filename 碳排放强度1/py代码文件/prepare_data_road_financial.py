import pandas as pd
import numpy as np

# Read merged dataset with financial development
df = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')
print(f"[INFO] 原始数据集形状: {df.shape}")
print(f"[INFO] 列名: {list(df.columns)}")

# Select required variables
variables_needed = ['city_name', 'year', 'treat', 'post', 'did',  # DID变量
                   'ln_carbon_intensity',  # 因变量
                   'ln_pgdp', 'ln_pop_density', 'industrial_advanced', 'ln_road_area', 'financial_development']  # 控制变量

df_selected = df[variables_needed].copy()
print(f"\n[INFO] 选择变量后形状: {df_selected.shape}")

# Check missing data
print(f"\n[INFO] 缺失值检查:")
for var in variables_needed:
    missing = df_selected[var].isnull().sum()
    rate = (missing / len(df_selected)) * 100
    print(f"  {var}: {missing}/{len(df_selected)} ({rate:.2f}%)")

# Drop rows with missing values (listwise deletion)
df_clean = df_selected.dropna()
print(f"\n[INFO] 删除缺失值后形状: {df_clean.shape}")
print(f"[INFO] 删除了 {len(df_selected) - len(df_clean)} 条观测")

# Check sample balance
treat_cities = df_clean[df_clean['treat'] == 1]['city_name'].nunique()
control_cities = df_clean[df_clean['treat'] == 0]['city_name'].nunique()
print(f"\n[INFO] 样本平衡性:")
print(f"  处理组城市数: {treat_cities}")
print(f"  控制组城市数: {control_cities}")

# Descriptive statistics for key variables
print(f"\n[INFO] 描述性统计:")
stats_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density', 'industrial_advanced', 'ln_road_area', 'financial_development']
print(df_clean[stats_vars].describe())

# Check year coverage
print(f"\n[INFO] 年份覆盖:")
print(f"  年份范围: {df_clean['year'].min()} - {df_clean['year'].max()}")
print(f"  年份数: {df_clean['year'].nunique()}")

# Save prepared dataset
output_file = '人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/回归分析数据集.xlsx'
df_clean.to_excel(output_file, index=False)
print(f"\n[OK] 数据集已保存到: {output_file}")
print(f"[INFO] 最终样本: {len(df_clean)} 条观测 × {df_clean['city_name'].nunique()} 个城市")
