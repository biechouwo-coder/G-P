"""
添加第二产业占比变量并创建新数据集
计算公式: secondary_share = 1 - tertiary_share

Created: 2025-01-08
"""

import pandas as pd
import os

# 创建新文件夹
output_dir = '二产占比模型_分析结果'
os.makedirs(output_dir, exist_ok=True)

print('[OK] === 第一步：加载PSM匹配后数据集 ===')
df = pd.read_excel('倾向得分匹配_匹配后数据集.xlsx')
print(f'[OK] 原始数据集: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# ============================================================================
# 第二步：添加第二产业占比变量
# ============================================================================
print('\n[OK] === 第二步：添加第二产业占比变量 ===')

# 计算第二产业占比（假设只有二产和三产，一产占比很小）
# secondary_share = 1 - tertiary_share
df['secondary_share'] = 1 - df['tertiary_share']

# 检查合理性
print(f'[INFO] tertiary_share 范围: [{df["tertiary_share"].min():.4f}, {df["tertiary_share"].max():.4f}]')
print(f'[INFO] secondary_share 范围: [{df["secondary_share"].min():.4f}, {df["secondary_share"].max():.4f}]')
print(f'[INFO] secondary_share 均值: {df["secondary_share"].mean():.4f}')
print(f'[INFO] secondary_share 标准差: {df["secondary_share"].std():.4f}')

# 创建平方项
df['secondary_share_sq'] = df['secondary_share'] ** 2

print(f'[OK] 新增变量:')
print(f'    - secondary_share: 第二产业占比')
print(f'    - secondary_share_sq: 第二产业占比平方项')

# ============================================================================
# 第三步：保存新数据集
# ============================================================================
print('\n[OK] === 第三步：保存新数据集 ===')

output_file = f'{output_dir}/PSM匹配后数据集_含二产占比.xlsx'
df.to_excel(output_file, index=False)
print(f'[OK] 新数据集已保存: {output_file}')

print('\n[OK] 数据准备完成！')
print(f'[INFO] 样本量: {df.shape[0]} 观测值')
print(f'[INFO] 城市数: {df["city_name"].nunique()} 个')
print(f'[INFO] 年份数: {df["year"].nunique()} 年')
