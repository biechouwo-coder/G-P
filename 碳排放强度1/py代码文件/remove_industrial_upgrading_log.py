"""
删除产业整体升级对数形式变量，保留水平值

Created: 2025-01-09
Reason: 用户要求使用第三产业/第二产业的比值（水平值），不使用对数形式
"""

import pandas as pd

print('[OK] === 第一步：加载数据 ===')

# 读取包含产业升级变量的数据集
print('[OK] 读取数据集...')
df = pd.read_excel('总数据集_2007-2023_含产业升级变量.xlsx')
print(f'[OK] 数据集加载成功: {df.shape[0]} 观测 × {df.shape[1]} 变量')

print('\n[OK] === 第二步：删除对数形式变量 ===')

# 检查industrial_upgrading变量是否存在
if 'industrial_upgrading' in df.columns:
    print(f'[OK] 找到industrial_upgrading变量（对数形式）')
    print(f'[OK] 该变量观测数: {df["industrial_upgrading"].notna().sum()}')
    print(f'[OK] 该变量缺失数: {df["industrial_upgrading"].isna().sum()}')

    # 删除industrial_upgrading列
    df = df.drop('industrial_upgrading', axis=1)
    print(f'[OK] 已删除industrial_upgrading变量')
else:
    print(f'[WARNING] 未找到industrial_upgrading变量')

print('\n[OK] === 第三步：验证industrial_advanced变量 ===')

# 检查industrial_advanced变量是否存在
if 'industrial_advanced' in df.columns:
    print(f'[OK] 找到industrial_advanced变量（水平值）')
    print(f'[OK] 该变量观测数: {df["industrial_advanced"].notna().sum()}')
    print(f'[OK] 该变量缺失数: {df["industrial_advanced"].isna().sum()}')

    # 显示描述性统计
    print(f'\n[OK] industrial_advanced描述性统计:')
    mask = df['industrial_advanced'].notna()
    print(f'    样本量: {mask.sum()}')
    print(f'    均值: {df.loc[mask, "industrial_advanced"].mean():.4f}')
    print(f'    标准差: {df.loc[mask, "industrial_advanced"].std():.4f}')
    print(f'    最小值: {df.loc[mask, "industrial_advanced"].min():.4f}')
    print(f'    中位数: {df.loc[mask, "industrial_advanced"].median():.4f}')
    print(f'    最大值: {df.loc[mask, "industrial_advanced"].max():.4f}')
else:
    print(f'[ERROR] 未找到industrial_advanced变量')

print('\n[OK] === 第四步：保存数据 ===')

# 保存数据集
output_file = '总数据集_2007-2023_最终回归版.xlsx'
df.to_excel(output_file, index=False)
print(f'[OK] 数据已保存: {output_file}')
print(f'[OK] 最终数据集: {df.shape[0]} 观测 × {df.shape[1]} 变量')

print('\n[OK] === 变量清单 ===')
print(f'[OK] 总变量数: {df.shape[1]}')
print(f'[OK] 变量列表:')
for i, col in enumerate(df.columns, 1):
    print(f'    {i:2d}. {col}')

print('\n[OK] === 任务完成 ===')
print(f'[OK] 已删除: industrial_upgrading（对数形式）')
print(f'[OK] 保留: industrial_advanced（水平值 = 第三产业增加值/第二产业增加值）')
print(f'[OK] 说明: 第三产业/第二产业比值，不需要取对数')
