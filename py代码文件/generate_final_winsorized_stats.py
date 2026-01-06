"""
生成缩尾处理后的描述性统计表
包含 ln_carbon_intensity（因变量）和所有缩尾后的控制变量
Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# Load final winsorized dataset
print('[OK] 加载最终回归版数据集...')
df = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')

print(f'[OK] 数据集加载成功: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# Define variables for descriptive statistics
stats_vars = [
    # Dependent variable (log-transformed)
    'ln_carbon_intensity',

    # Policy variable
    'did',
    'treat',
    'post',

    # Core control variables (log-transformed & winsorized)
    'ln_pop_density',
    'ln_pgdp',
    'ln_pop',
    'ln_fdi',
    'ln_road_area',

    # Other control variables (winsorized)
    'tertiary_share',
    'gdp_deflator',
    'industrial_upgrading'
]

# Chinese names for variables
var_names_cn = {
    'ln_carbon_intensity': '碳排放强度对数（吨/亿元，2000年基期）',
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
    'ln_carbon_intensity': 'Log Carbon Emission Intensity (tons/100M yuan, 2000 base)',
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
print('[OK] 计算描述性统计...')

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
            '偏度': col_data.skew(),
            '峰度': col_data.kurtosis(),
            '缺失数': df[var].isna().sum(),
            '缺失比例(%)': (df[var].isna().sum() / len(df)) * 100
        }

        stats_data.append(stats_dict)

# Create DataFrame
stats_df = pd.DataFrame(stats_data)

# Format numeric columns
for col in ['均值', '标准差', '最小值', '25%分位', '中位数', '75%分位', '最大值', '偏度', '峰度']:
    stats_df[col] = stats_df[col].apply(lambda x: f"{x:.4f}")

stats_df['缺失比例(%)'] = stats_df['缺失比例(%)'].apply(lambda x: f"{x:.2f}")

# Save to Excel
output_file = '描述性统计表_最终回归版.xlsx'
print(f'[OK] 保存到 {output_file}...')

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
        '指标': ['总观测数', '城市数', '年份数', '起始年份', '结束年份', '总变量数', '回归用变量数', '数据状态'],
        '数值': [
            f'{df.shape[0]:,}',
            f"{df['city_name'].nunique()}",
            f"{df['year'].nunique()}",
            f"{df['year'].min()}",
            f"{df['year'].max()}",
            f"{df.shape[1]}",
            f"{len(stats_vars)}",
            '已缩尾处理'
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
    key_vars = ['ln_carbon_intensity', 'did', 'ln_pop_density', 'ln_pgdp',
                'ln_pop', 'ln_fdi', 'ln_road_area', 'tertiary_share']
    corr_matrix = df[key_vars].corr()
    corr_matrix.to_excel(writer, sheet_name='相关系数矩阵')

    # Distribution summary
    dist_summary = []
    for var in key_vars:
        if var in df.columns:
            skew = df[var].skew()
            kurt = df[var].kurtosis()
            dist_type = '对称分布' if abs(skew) < 1 else ('中等偏斜' if abs(skew) < 2 else '高度偏斜')
            dist_summary.append({
                '变量': var,
                '偏度': f"{skew:.4f}",
                '峰度': f"{kurt:.4f}",
                '分布类型': dist_type
            })
    dist_df = pd.DataFrame(dist_summary)
    dist_df.to_excel(writer, sheet_name='分布检验', index=False)

print(f'[OK] 描述性统计表生成成功!')
print(f'    - 输出文件: {output_file}')
print(f'    - 包含工作表:')
print(f'      1. 描述性统计 - 主统计表（含偏度和峰度）')
print(f'      2. 变量定义 - 中英文对照')
print(f'      3. 样本概览 - 样本总体信息')
print(f'      4. 政策变量统计 - 政策变量分布')
print(f'      5. 相关系数矩阵 - 核心变量相关性')
print(f'      6. 分布检验 - 偏度和峰度检验')

# Display key statistics in console
print('\n[INFO] 核心统计摘要:')
print(f'    总观测数: {df.shape[0]:,}')
print(f'    城市数: {df["city_name"].nunique()}')
print(f'    年份: {df["year"].min()}-{df["year"].max()}')
print(f'    试点城市: {df[df["treat"]==1]["city_name"].nunique()}')
print(f'    非试点城市: {df[df["treat"]==0]["city_name"].nunique()}')

# Display mean values for regression variables
print('\n[INFO] 回归变量均值（缩尾后）:')
key_regression_vars = ['ln_carbon_intensity', 'did', 'ln_pop_density',
                       'ln_pgdp', 'ln_pop', 'ln_fdi', 'ln_road_area']
for var in key_regression_vars:
    if var in df.columns:
        mean_val = df[var].mean()
        print(f'    {var_names_cn[var]}: {mean_val:.4f}')

# Check distribution quality
print('\n[INFO] 数据分布质量检验（缩尾后）:')
for var in key_regression_vars:
    if var in df.columns:
        skewness = df[var].skew()
        kurtosis = df[var].kurtosis()
        print(f'    {var}:')
        print(f'      - 偏度: {skewness:.4f}', end='')
        if abs(skewness) < 0.5:
            print(' (优秀)')
        elif abs(skewness) < 1:
            print(' (良好)')
        else:
            print(' (可接受)')
        print(f'      - 峰度: {kurtosis:.4f}')

print(f'\n[OK] 描述性统计表生成完毕!')
print(f'[OK] 数据已完全准备就绪，可进行DID回归分析!')
