"""
添加产业结构高级化变量到总数据集（最终修正版）

Created: 2025-01-09
"""

import pandas as pd
import numpy as np

print('[OK] === 第一步：加载数据 ===')

# 读取产业结构数据（有表头）
print('[OK] 读取产业结构数据...')
industry_df = pd.read_excel('原始数据/2000-2023地级市产业结构 .xlsx', sheet_name=1)

# 列0: 年份, 列1: 地级市名称, 列13: 产业整体升级, 列14: 产业结构高级化
industry_extract = industry_df.iloc[:, [0, 1, 13, 14]].copy()
industry_extract.columns = ['year', 'city_name', 'industrial_upgrading', 'industrial_advanced']

# 数据类型转换
industry_extract['year'] = pd.to_numeric(industry_extract['year'], errors='coerce').fillna(0).astype(int)
industry_extract['city_name'] = industry_extract['city_name'].astype(str).str.strip()

print(f'[OK] 产业结构数据: {industry_extract.shape[0]} 观测')
print(f'[OK] 唯一城市数: {industry_extract["city_name"].nunique()}')
print(f'[OK] industrial_upgrading:')
print(f'    样本量: {industry_extract["industrial_upgrading"].notna().sum()}')
print(f'    均值: {industry_extract["industrial_upgrading"].mean():.4f}')
print(f'    范围: [{industry_extract["industrial_upgrading"].min():.4f}, {industry_extract["industrial_upgrading"].max():.4f}]')

print(f'\n[OK] industrial_advanced:')
print(f'    样本量: {industry_extract["industrial_advanced"].notna().sum()}')
print(f'    均值: {industry_extract["industrial_advanced"].mean():.4f}')
print(f'    范围: [{industry_extract["industrial_advanced"].min():.4f}, {industry_extract["industrial_advanced"].max():.4f}]')

# 读取总数据集
print('\n[OK] 读取总数据集...')
main_df = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')
main_df['year'] = pd.to_numeric(main_df['year'], errors='coerce').fillna(0).astype(int)
main_df['city_name'] = main_df['city_name'].astype(str).str.strip()

print(f'[OK] 总数据集: {main_df.shape[0]} 观测 × {main_df.shape[1]} 变量')
print(f'[OK] 唯一城市数: {main_df["city_name"].nunique()}')

print('\n[OK] === 第二步：数据合并 ===')

# 检查城市名称重叠
main_cities = set(main_df['city_name'].unique())
industry_cities = set(industry_extract['city_name'].unique())
overlap = main_cities & industry_cities

print(f'[OK] 城市名称匹配检查:')
print(f'    总数据集城市数: {len(main_cities)}')
print(f'    产业数据城市数: {len(industry_cities)}')
print(f'    重叠城市数: {len(overlap)} ({len(overlap)/len(main_cities)*100:.1f}%)')

# 合并数据
merged_df = pd.merge(
    main_df,
    industry_extract[['year', 'city_name', 'industrial_advanced']],
    on=['year', 'city_name'],
    how='left'
)

print(f'\n[OK] 合并完成: {merged_df.shape[0]} 观测 × {merged_df.shape[1]} 变量')
print(f'[OK] 新增变量数: {merged_df.shape[1] - main_df.shape[1]}')

print('\n[OK] === 第三步：检查合并结果 ===')

# 统计匹配情况
advanced_notna = merged_df['industrial_advanced'].notna().sum()

print(f'[OK] industrial_advanced:')
print(f'    匹配成功: {advanced_notna} / {merged_df.shape[0]} ({advanced_notna/merged_df.shape[0]*100:.1f}%)')
print(f'    缺失: {merged_df["industrial_advanced"].isna().sum()}')

# 显示新增变量的统计
print(f'\n[OK] 合并后变量统计:')
mask = merged_df['industrial_advanced'].notna()
if mask.sum() > 0:
    print(f'industrial_advanced (n={mask.sum()}):')
    print(f'    均值: {merged_df.loc[mask, "industrial_advanced"].mean():.4f}')
    print(f'    标准差: {merged_df.loc[mask, "industrial_advanced"].std():.4f}')
    print(f'    最小值: {merged_df.loc[mask, "industrial_advanced"].min():.4f}')
    print(f'    中位数: {merged_df.loc[mask, "industrial_advanced"].median():.4f}')
    print(f'    最大值: {merged_df.loc[mask, "industrial_advanced"].max():.4f}')

# 显示样本
print(f'\n[OK] 样本数据（前10行已匹配数据）:')
sample_data = merged_df[merged_df['industrial_advanced'].notna()][['city_name', 'year', 'industrial_upgrading', 'industrial_advanced']].head(10)
print(sample_data)

print('\n[OK] === 第四步：保存数据 ===')

# 保存数据
output_file = '总数据集_2007-2023_含产业升级变量.xlsx'
merged_df.to_excel(output_file, index=False)
print(f'[OK] 数据已保存: {output_file}')
print(f'[OK] 最终数据集: {merged_df.shape[0]} 观测 × {merged_df.shape[1]} 变量')

print('\n[OK] === 任务完成 ===')
print(f'[OK] 变量说明:')
print(f'    1. industrial_upgrading (已有): 产业整体升级 = ln(第三产业产值/第二产业产值)')
print(f'    2. industrial_advanced (新增): 产业结构高级化 = 第三产业产值/第二产业产值')
print(f'    注: 两者为对数关系，industrial_upgrading = ln(industrial_advanced)')
