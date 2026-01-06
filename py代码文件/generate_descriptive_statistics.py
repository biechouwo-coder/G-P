"""
Generate comprehensive descriptive statistics table for the final dataset
Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# Load final dataset
print('[OK] Loading final dataset...')
df = pd.read_excel('总数据集_2007-2023_完整版.xlsx')

print(f'[OK] Dataset loaded: {df.shape[0]} observations × {df.shape[1]} variables')

# Select variables for descriptive statistics (exclude ID variables)
stats_vars = [
    'year',
    'population',
    'pop_density',
    'gdp_real',
    'gdp_per_capita',
    'gdp_deflator',
    'carbon_intensity',
    'tertiary_share',
    'industrial_upgrading',
    'pilot_year',
    'treat',
    'post',
    'did',
    'fdi',
    'fdi_openness',
    'road_area',
    'ln_road_area'
]

# Chinese names for variables
var_names_cn = {
    'year': '年份',
    'population': '年末总人口（万人）',
    'pop_density': '人口密度（人/平方公里）',
    'gdp_real': '实际GDP（亿元，2000年基期）',
    'gdp_per_capita': '人均实际GDP（元/人，2000年基期）',
    'gdp_deflator': 'GDP平减指数',
    'carbon_intensity': '碳排放强度（吨/亿元，2000年基期）',
    'tertiary_share': '第三产业比重',
    'industrial_upgrading': '产业结构升级（第三/第二产业）',
    'pilot_year': '试点开始年份',
    'treat': '处理组（是否为试点城市）',
    'post': '政策时间（是否为政策后）',
    'did': 'DID政策变量',
    'fdi': '外商直接投资（百万美元）',
    'fdi_openness': 'FDI开放度（FDI/GDP）',
    'road_area': '人均道路面积（平方米/人）',
    'ln_road_area': '人均道路面积对数'
}

# Calculate descriptive statistics
print('[OK] Calculating descriptive statistics...')

stats_data = []
for var in stats_vars:
    col_data = df[var].dropna()

    stats_dict = {
        '变量名称': var_names_cn.get(var, var),
        '变量代码': var,
        '观测值': len(col_data),
        '均值': col_data.mean(),
        '标准差': col_data.std(),
        '最小值': col_data.min(),
        '最大值': col_data.max(),
        '中位数': col_data.median(),
        '缺失值': df[var].isna().sum(),
        '缺失比例(%)': (df[var].isna().sum() / len(df)) * 100
    }

    stats_data.append(stats_dict)

# Create DataFrame
stats_df = pd.DataFrame(stats_data)

# Format numeric columns
for col in ['均值', '标准差', '最小值', '最大值', '中位数']:
    stats_df[col] = stats_df[col].apply(lambda x: f"{x:.4f}")

stats_df['缺失比例(%)'] = stats_df['缺失比例(%)'].apply(lambda x: f"{x:.2f}")

# Save to Excel
output_file = '描述性统计表_完整版.xlsx'
print(f'[OK] Saving to {output_file}...')

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Main statistics table
    stats_df.to_excel(writer, sheet_name='描述性统计', index=False)

    # Variable definitions
    definitions = pd.DataFrame({
        '变量代码': list(var_names_cn.keys()),
        '变量名称': list(var_names_cn.values())
    })
    definitions.to_excel(writer, sheet_name='变量定义', index=False)

    # Sample overview
    overview = pd.DataFrame({
        '指标': ['观测数', '城市数', '年份数', '起始年份', '结束年份', '变量数'],
        '数值': [
            df.shape[0],
            df['city_name'].nunique(),
            df['year'].nunique(),
            df['year'].min(),
            df['year'].max(),
            df.shape[1]
        ]
    })
    overview.to_excel(writer, sheet_name='样本概览', index=False)

    # City-year distribution
    city_counts = df.groupby('year')['city_name'].nunique().reset_index()
    city_counts.columns = ['年份', '城市数']
    city_counts.to_excel(writer, sheet_name='每年城市数', index=False)

print(f'[OK] Descriptive statistics table generated successfully!')
print(f'    - Total variables: {len(stats_vars)}')
print(f'    - Output file: {output_file}')
print(f'    - Sheets included: 描述性统计, 变量定义, 样本概览, 每年城市数')

# Display key statistics in console
print('\n[INFO] Key Statistics Summary:')
print(f'    Total observations: {df.shape[0]:,}')
print(f'    Total cities: {df["city_name"].nunique()}')
print(f'    Years: {df["year"].min()}-{df["year"].max()}')
print(f'    Pilot cities (treat=1): {(df["treat"]==1).sum():,}')
print(f'    Non-pilot cities (treat=0): {(df["treat"]==0).sum():,}')

# Display mean values for key variables
print('\n[INFO] Mean Values for Key Variables:')
key_vars = ['pop_density', 'gdp_per_capita', 'carbon_intensity',
            'tertiary_share', 'fdi_openness', 'ln_road_area']
for var in key_vars:
    mean_val = df[var].mean()
    print(f'    {var_names_cn[var]}: {mean_val:.4f}')
