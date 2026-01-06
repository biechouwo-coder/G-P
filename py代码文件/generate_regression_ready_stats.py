"""
Generate Descriptive Statistics for Regression Analysis
Includes both original and log-transformed variables
Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# Load regression-ready dataset
print('[OK] Loading regression-ready dataset...')
df = pd.read_excel('总数据集_2007-2023_回归准备版.xlsx')

print(f'[OK] Dataset loaded: {df.shape[0]} observations × {df.shape[1]} variables')

# Define variables for descriptive statistics
# Focus on variables used in regression
stats_vars = [
    # Dependent variable
    'carbon_intensity',

    # Policy variable
    'did',
    'treat',
    'post',

    # Core control variables (log-transformed)
    'ln_pop_density',
    'ln_pgdp',
    'ln_pop',
    'ln_fdi',
    'ln_road_area',

    # Other control variables
    'tertiary_share',
    'gdp_deflator',
    'industrial_upgrading'
]

# Chinese names for variables
var_names_cn = {
    'carbon_intensity': '碳排放强度（吨/亿元，2000年基期）',
    'did': 'DID政策变量',
    'treat': '处理组（是否为试点城市）',
    'post': '政策时间（是否为政策后）',
    'ln_pop_density': '人口密度对数（人/平方公里）',
    'ln_pgdp': '人均GDP对数（元/人，2000年基期）',
    'ln_pop': '人口规模对数（万人）',
    'ln_fdi': '外商直接投资对数（百万美元）',
    'ln_road_area': '人均道路面积对数（平方米/人）',
    'tertiary_share': '第三产业比重',
    'gdp_deflator': 'GDP平减指数',
    'industrial_upgrading': '产业结构升级（第三/第二产业）'
}

# English descriptions
var_names_en = {
    'carbon_intensity': 'Carbon Emission Intensity (tons/100M yuan, 2000 base)',
    'did': 'DID Policy Variable',
    'treat': 'Treatment Group (1 if pilot city)',
    'post': 'Post-policy Period (1 if year >= pilot year)',
    'ln_pop_density': 'Log Population Density (persons/km²)',
    'ln_pgdp': 'Log GDP per Capita (yuan/person, 2000 base)',
    'ln_pop': 'Log Population Size (10,000 persons)',
    'ln_fdi': 'Log FDI (million USD)',
    'ln_road_area': 'Log Road Area per Capita (m²/person)',
    'tertiary_share': 'Tertiary Industry Share',
    'gdp_deflator': 'GDP Deflator (2000 = 1.0)',
    'industrial_upgrading': 'Industrial Upgrading (Tertiary/Secondary)'
}

# Calculate descriptive statistics
print('[OK] Calculating descriptive statistics...')

stats_data = []
for var in stats_vars:
    if var in df.columns:
        col_data = df[var].dropna()

        stats_dict = {
            '变量代码': var,
            '变量名称': var_names_cn.get(var, var),
            'English Name': var_names_en.get(var, var),
            '观测数': len(col_data),
            '均值': col_data.mean(),
            '标准差': col_data.std(),
            '最小值': col_data.min(),
            '25%分位': col_data.quantile(0.25),
            '中位数': col_data.quantile(0.50),
            '75%分位': col_data.quantile(0.75),
            '最大值': col_data.max(),
            '缺失数': df[var].isna().sum(),
            '缺失比例(%)': (df[var].isna().sum() / len(df)) * 100
        }

        stats_data.append(stats_dict)

# Create DataFrame
stats_df = pd.DataFrame(stats_data)

# Format numeric columns
for col in ['均值', '标准差', '最小值', '25%分位', '中位数', '75%分位', '最大值']:
    stats_df[col] = stats_df[col].apply(lambda x: f"{x:.4f}")

stats_df['缺失比例(%)'] = stats_df['缺失比例(%)'].apply(lambda x: f"{x:.2f}")

# Save to Excel
output_file = '描述性统计表_回归分析版.xlsx'
print(f'[OK] Saving to {output_file}...')

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Main statistics table
    stats_df.to_excel(writer, sheet_name='描述性统计', index=False)

    # Variable definitions
    definitions = pd.DataFrame({
        '变量代码': list(var_names_cn.keys()),
        '中文名称': list(var_names_cn.values()),
        '英文名称': list(var_names_en.values())
    })
    definitions.to_excel(writer, sheet_name='变量定义', index=False)

    # Sample overview
    overview = pd.DataFrame({
        '指标': ['总观测数', '城市数', '年份数', '起始年份', '结束年份', '总变量数', '回归用变量数'],
        '数值': [
            f'{df.shape[0]:,}',
            f"{df['city_name'].nunique()}",
            f"{df['year'].nunique()}",
            f"{df['year'].min()}",
            f"{df['year'].max()}",
            f"{df.shape[1]}",
            f"{len(stats_vars)}"
        ]
    })
    overview.to_excel(writer, sheet_name='样本概览', index=False)

    # Policy variable statistics
    policy_stats = pd.DataFrame({
        '统计项': ['处理组城市数', '对照组城市数', '处理组观测数', '对照组观测数',
                  '政策期观测数', '非政策期观测数', 'DID=1观测数'],
        '数值': [
            f"{df[df['treat']==1]['city_name'].nunique()}",
            f"{df[df['treat']==0]['city_name'].nunique()}",
            f"{(df['treat']==1).sum():,}",
            f"{(df['treat']==0).sum():,}",
            f"{(df['post']==1).sum():,}",
            f"{(df['post']==0).sum():,}",
            f"{(df['did']==1).sum():,}"
        ]
    })
    policy_stats.to_excel(writer, sheet_name='政策变量统计', index=False)

    # Correlation matrix (key variables only)
    key_vars = ['carbon_intensity', 'did', 'ln_pop_density', 'ln_pgdp',
                'ln_pop', 'ln_fdi', 'ln_road_area', 'tertiary_share']
    corr_matrix = df[key_vars].corr()
    corr_matrix.to_excel(writer, sheet_name='相关系数矩阵')

print(f'[OK] Descriptive statistics table generated successfully!')
print(f'    - Output file: {output_file}')
print(f'    - Sheets included:')
print(f'      1. 描述性统计 - Main statistics table')
print(f'      2. 变量定义 - Variable definitions (CN/EN)')
print(f'      3. 样本概览 - Sample overview')
print(f'      4. 政策变量统计 - Policy variable statistics')
print(f'      5. 相关系数矩阵 - Correlation matrix')

# Display key statistics in console
print('\n[INFO] 关键统计摘要:')
print(f'    总观测数: {df.shape[0]:,}')
print(f'    城市数: {df["city_name"].nunique()}')
print(f'    年份: {df["year"].min()}-{df["year"].max()}')
print(f'    试点城市: {df[df["treat"]==1]["city_name"].nunique()}')
print(f'    非试点城市: {df[df["treat"]==0]["city_name"].nunique()}')

# Display mean values for regression variables
print('\n[INFO] 核心回归变量均值:')
key_regression_vars = ['carbon_intensity', 'did', 'ln_pop_density',
                       'ln_pgdp', 'ln_pop', 'ln_fdi', 'ln_road_area']
for var in key_regression_vars:
    if var in df.columns:
        mean_val = df[var].mean()
        print(f'    {var_names_cn[var]}: {mean_val:.4f}')

# Check variable distributions for log-transformed variables
print('\n[INFO] 对数变量分布检查:')
log_vars = ['ln_pop_density', 'ln_pgdp', 'ln_pop', 'ln_fdi', 'ln_road_area']
for var in log_vars:
    if var in df.columns:
        skewness = df[var].skew()
        kurtosis = df[var].kurtosis()
        print(f'    {var}:')
        print(f'      - 偏度(Skewness): {skewness:.4f}', end='')
        if abs(skewness) < 1:
            print(' (对称分布)')
        elif abs(skewness) < 2:
            print(' (中等偏斜)')
        else:
            print(' (高度偏斜)')
        print(f'      - 峰度(Kurtosis): {kurtosis:.4f}')

print(f'\n[OK] 描述性统计表生成完毕，可以进行回归分析!')
