"""
添加真实的第二产业占比变量（从原始数据中提取）
从"2000-2023地级市产业结构 .xlsx"中提取二产占比

Created: 2025-01-08
"""

import pandas as pd
import os

# 创建新文件夹
output_dir = '二产占比模型_分析结果'
os.makedirs(output_dir, exist_ok=True)

print('[OK] === 第一步：加载原始产业结构数据 ===')
# 读取原始产业结构数据（sheet 1，按索引）
industry_df = pd.read_excel('原始数据/2000-2023地级市产业结构 .xlsx', sheet_name=1)
print(f'[OK] 原始数据加载成功: {industry_df.shape[0]} 行 × {industry_df.shape[1]} 列')

# 显示列名
print('\n[INFO] 原始数据列名:')
for i, col in enumerate(industry_df.columns):
    print(f'  {i}: {col}')

# 提取需要的列（使用列索引，避免中文编码问题）
# 根据输出：10=第二产业占GDP比重（应该是索引10）
industry_subset = industry_df.iloc[:, [0, 1, 2, 10]]  # 年份, 地区名称, 地区代码, 第二产业占GDP比重
industry_subset = industry_subset.copy()  # 避免SettingWithCopyWarning
industry_subset.columns = ['year', 'city_name', 'city_code', 'secondary_share_raw']

print(f'\n[INFO] 提取的列: year, city_name, city_code, secondary_share_raw')
print(f'[INFO] 样本量: {industry_subset.shape[0]}')

# ============================================================================
# 第二步：加载PSM匹配后数据集
# ============================================================================
print('\n[OK] === 第二步：加载PSM匹配后数据集 ===')
df = pd.read_excel('倾向得分匹配_匹配后数据集.xlsx')
print(f'[OK] PSM匹配后数据集: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# ============================================================================
# 第三步：合并二产占比数据
# ============================================================================
print('\n[OK] === 第三步：合并二产占比数据 ===')

# 将年份转换为数值类型
industry_subset['year'] = pd.to_numeric(industry_subset['year'], errors='coerce')
industry_subset['city_code'] = pd.to_numeric(industry_subset['city_code'], errors='coerce')
industry_subset['secondary_share_raw'] = pd.to_numeric(industry_subset['secondary_share_raw'], errors='coerce')

# 删除缺失值
industry_subset = industry_subset.dropna(subset=['year', 'city_code', 'secondary_share_raw'])
print(f'[INFO] 原始二产数据（删除缺失值后）: {industry_subset.shape[0]} 观测')

# 合并数据
df_merged = pd.merge(
    df,
    industry_subset[['year', 'city_code', 'secondary_share_raw']],
    on=['year', 'city_code'],
    how='left'
)

print(f'[INFO] 合并后数据集: {df_merged.shape[0]} 观测 × {df_merged.shape[1]} 变量')

# 检查二产占比的缺失情况
n_missing = df_merged['secondary_share_raw'].isna().sum()
print(f'[INFO] 二产占比缺失值: {n_missing} ({n_missing/len(df_merged)*100:.2f}%)')

# 如果有缺失值，删除这些观测
if n_missing > 0:
    print(f'[WARNING] 删除 {n_missing} 个二产占比缺失的观测')
    df_merged = df_merged.dropna(subset=['secondary_share_raw'])
    print(f'[INFO] 删除后样本量: {df_merged.shape[0]}')

# 转换为比例（原数据可能是百分比）
# 检查数据范围
sec_min = df_merged['secondary_share_raw'].min()
sec_max = df_merged['secondary_share_raw'].max()
sec_mean = df_merged['secondary_share_raw'].mean()

print(f'\n[INFO] 二产占比原始统计:')
print(f'  最小值: {sec_min:.4f}')
print(f'  最大值: {sec_max:.4f}')
print(f'  均值: {sec_mean:.4f}')

# 如果最大值 > 1，说明是百分比，需要除以100
if sec_max > 1:
    print(f'[INFO] 检测到数据为百分比格式，转换为比例（除以100）')
    df_merged['secondary_share'] = df_merged['secondary_share_raw'] / 100
else:
    df_merged['secondary_share'] = df_merged['secondary_share_raw']

# 数据清洗：删除异常值（二产占比应该在0-1之间）
print(f'\n[INFO] 数据清洗：删除异常值（二产占比 < 0 或 > 1）')
before_clean = len(df_merged)
df_merged = df_merged[(df_merged['secondary_share'] >= 0) & (df_merged['secondary_share'] <= 1)]
after_clean = len(df_merged)
print(f'[INFO] 删除异常值: {before_clean - after_clean} 个观测')
print(f'[INFO] 清洗后样本量: {after_clean}')

# 创建平方项
df_merged['secondary_share_sq'] = df_merged['secondary_share'] ** 2

print(f'\n[OK] 二产占比最终统计:')
print(f'  最小值: {df_merged["secondary_share"].min():.4f}')
print(f'  最大值: {df_merged["secondary_share"].max():.4f}')
print(f'  均值: {df_merged["secondary_share"].mean():.4f}')
print(f'  标准差: {df_merged["secondary_share"].std():.4f}')

# ============================================================================
# 第四步：保存新数据集
# ============================================================================
print('\n[OK] === 第四步：保存新数据集 ===')

# 删除临时列
df_merged = df_merged.drop(columns=['secondary_share_raw'])

output_file = f'{output_dir}/PSM匹配后数据集_含二产占比.xlsx'
df_merged.to_excel(output_file, index=False)
print(f'[OK] 新数据集已保存: {output_file}')

print('\n[OK] 数据准备完成！')
print(f'[INFO] 最终样本量: {df_merged.shape[0]} 观测值')
print(f'[INFO] 城市数: {df_merged["city_name"].nunique()} 个')
print(f'[INFO] 年份数: {df_merged["year"].nunique()} 年')
print(f'[INFO] 时间范围: {df_merged["year"].min()}-{df_merged["year"].max()}')
