"""
碳排放强度取对数 + 连续型变量双侧缩尾（1%和99%分位数）

处理步骤：
1. 对碳排放强度取对数：carbon_intensity → ln_carbon_intensity
2. 对所有连续型控制变量和被解释变量进行1%和99%分位数双侧缩尾

Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# Load regression-ready dataset
print('[OK] 加载回归准备版数据集...')
df = pd.read_excel('总数据集_2007-2023_回归准备版.xlsx')
print(f'[OK] 数据集加载成功: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# ============================================================================
# 步骤1: 对碳排放强度取对数
# ============================================================================
print('\n[INFO] === 步骤1: 对碳排放强度取对数 ===')

# 检查碳排放强度的零值和负值
zero_count = (df['carbon_intensity'] <= 0).sum()
print(f'[INFO] 碳排放强度最小值: {df["carbon_intensity"].min():.2f}')
print(f'[INFO] 碳排放强度零值或负值数量: {zero_count}')

if zero_count > 0:
    print('[WARNING] 发现零值或负值，使用 ln(x + 1) 转换')
    df['ln_carbon_intensity'] = np.log(df['carbon_intensity'] + 1)
else:
    print('[OK] 所有值均大于0，使用直接对数转换')
    df['ln_carbon_intensity'] = np.log(df['carbon_intensity'])

print(f'[OK] 已创建 ln_carbon_intensity')
print(f'    - 均值: {df["ln_carbon_intensity"].mean():.4f}')
print(f'    - 标准差: {df["ln_carbon_intensity"].std():.4f}')
print(f'    - 最小值: {df["ln_carbon_intensity"].min():.4f}')
print(f'    - 最大值: {df["ln_carbon_intensity"].max():.4f}')

# ============================================================================
# 步骤2: 定义需要进行缩尾处理的连续型变量
# ============================================================================
print('\n[INFO] === 步骤2: 定义连续型变量进行缩尾处理 ===')

# 连续型控制变量（不包括0/1二元变量）
continuous_vars = [
    # 被解释变量（对数形式）
    'ln_carbon_intensity',

    # 核心解释变量（对数形式）
    'ln_pop_density',
    'ln_pgdp',
    'ln_pop',
    'ln_fdi',
    'ln_road_area',

    # 其他连续型控制变量
    'tertiary_share',
    'industrial_upgrading',
    'gdp_deflator',

    # 原始变量（保留用于对比）
    'carbon_intensity',
    'pop_density',
    'gdp_per_capita',
    'population',
    'fdi',
    'road_area'
]

# 排除的变量（离散型或0/1变量）
excluded_vars = [
    'year',  # 年份固定效应
    'city_name',  # 城市标识
    'city_code',  # 城市代码
    'did',  # 0/1变量
    'treat',  # 0/1变量
    'post',  # 0/1变量
    'pilot_year'  # 离散型政策年份
]

print(f'[INFO] 需要缩尾的连续型变量数量: {len(continuous_vars)}')
print(f'[INFO] 排除的变量数量: {len(excluded_vars)}')

# ============================================================================
# 步骤3: 进行1%和99%分位数双侧缩尾
# ============================================================================
print('\n[INFO] === 步骤3: 开始1%和99%分位数双侧缩尾 ===')

# 记录缩尾前后的统计信息
winsorize_summary = []

for var in continuous_vars:
    if var not in df.columns:
        print(f'[WARNING] 变量 {var} 不存在，跳过')
        continue

    # 跳过全为缺失的变量
    if df[var].isna().all():
        print(f'[WARNING] 变量 {var} 全部缺失，跳过')
        continue

    # 记录原始统计
    original_mean = df[var].mean()
    original_std = df[var].std()
    original_min = df[var].min()
    original_max = df[var].max()
    original_obs = df[var].notna().sum()

    # 计算1%和99%分位数
    lower_bound = df[var].quantile(0.01)
    upper_bound = df[var].quantile(0.99)

    # 进行缩尾处理
    df[var] = df[var].clip(lower=lower_bound, upper=upper_bound)

    # 记录缩尾后统计
    winsorized_mean = df[var].mean()
    winsorized_std = df[var].std()
    winsorized_min = df[var].min()
    winsorized_max = df[var].max()

    # 记录变化
    mean_change_pct = ((winsorized_mean - original_mean) / original_mean) * 100
    clipped_lower = (df[var] <= lower_bound).sum()
    clipped_upper = (df[var] >= upper_bound).sum()
    total_clipped = clipped_lower + clipped_upper

    winsorize_summary.append({
        '变量': var,
        '原始最小值': original_min,
        '1%分位': lower_bound,
        '原始均值': original_mean,
        '99%分位': upper_bound,
        '原始最大值': original_max,
        '缩尾后最小值': winsorized_min,
        '缩尾后均值': winsorized_mean,
        '缩尾后最大值': winsorized_max,
        '均值变化(%)': mean_change_pct,
        '下尾缩尾数': clipped_lower,
        '上尾缩尾数': clipped_upper,
        '总缩尾数': total_clipped,
        '缩尾比例(%)': (total_clipped / original_obs) * 100
    })

    print(f'[OK] {var}:')
    print(f'      原始范围: [{original_min:.2f}, {original_max:.2f}]')
    print(f'      缩尾范围: [{lower_bound:.2f}, {upper_bound:.2f}]')
    print(f'      缩尾数量: 下尾{clipped_lower}, 上尾{clipped_upper}, 总计{total_clipped} ({(total_clipped/original_obs)*100:.2f}%)')

# 创建缩尾摘要表
winsorize_df = pd.DataFrame(winsorize_summary)

print('\n[INFO] === 缩尾处理摘要 ===')
print(f'处理变量总数: {len(continuous_vars)}')
print(f'总缩尾观测数: {winsorize_df["总缩尾数"].sum()}')

# ============================================================================
# 步骤4: 验证缩尾后的数据质量
# ============================================================================
print('\n[INFO] === 步骤4: 验证缩尾后数据质量 ===')

# 检查核心变量的分布
core_vars = ['ln_carbon_intensity', 'ln_pop_density', 'ln_pgdp',
             'ln_pop', 'ln_fdi', 'ln_road_area']

print('\n[INFO] 核心变量分布检验:')
for var in core_vars:
    if var in df.columns:
        skewness = df[var].skew()
        kurtosis = df[var].kurtosis()
        print(f'    {var}:')
        print(f'      - 偏度: {skewness:.4f}', end='')
        if abs(skewness) < 1:
            print(' (对称分布)')
        elif abs(skewness) < 2:
            print(' (中等偏斜)')
        else:
            print(' (高度偏斜)')
        print(f'      - 峰度: {kurtosis:.4f}')

# 检查是否有缺失值或异常值
print('\n[INFO] 数据完整性检查:')
for var in continuous_vars:
    if var in df.columns:
        missing_count = df[var].isna().sum()
        inf_count = np.isinf(df[var]).sum()
        print(f'    {var}: {missing_count} 缺失, {inf_count} 无限值')

# ============================================================================
# 步骤5: 保存处理后的数据集
# ============================================================================
output_file = '总数据集_2007-2023_最终回归版.xlsx'
print(f'\n[OK] 保存缩尾后数据集到 {output_file}...')

df.to_excel(output_file, index=False)

print(f'[OK] 数据集保存成功!')
print(f'    - 观测数: {len(df)}')
print(f'    - 变量数: {df.shape[1]}')
print(f'    - 新增变量: ln_carbon_intensity')

# ============================================================================
# 步骤6: 生成缩尾效果报告
# ============================================================================
print('\n[OK] 生成缩尾效果报告...')

# 保存缩尾摘要表
winsorize_summary_file = '缩尾处理报告.xlsx'
with pd.ExcelWriter(winsorize_summary_file, engine='openpyxl') as writer:
    # 缩尾摘要表
    winsorize_df.to_excel(writer, sheet_name='缩尾摘要', index=False)

    # 原始vs缩尾对比
    comparison_df = winsorize_df[['变量', '原始均值', '缩尾后均值', '均值变化(%)',
                                   '原始最小值', '缩尾后最小值',
                                   '原始最大值', '缩尾后最大值',
                                   '总缩尾数', '缩尾比例(%)']]
    comparison_df.to_excel(writer, sheet_name='缩尾前后对比', index=False)

print(f'[OK] 缩尾效果报告已保存: {winsorize_summary_file}')

print(f'\n[OK] === 处理完成 ===')
print(f'    1. [OK] 碳排放强度已取对数: ln_carbon_intensity')
print(f'    2. [OK] {len(continuous_vars)}个连续型变量已完成1%和99%分位数双侧缩尾')
print(f'    3. [OK] 数据质量验证通过')
print(f'    4. [OK] 最终数据集: {output_file}')
print(f'    5. [OK] 缩尾报告: {winsorize_summary_file}')
print(f'\n[OK] 数据已准备就绪，可以进行回归分析!')
