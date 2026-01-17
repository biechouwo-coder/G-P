"""
添加人均道路面积变量到主数据集（地级市级别）
功能：
1. 读取地级市道路面积数据
2. 提取并筛选2007-2023年数据
3. 标准化城市代码格式
4. 左连接合并到主数据集
5. 计算对数人均道路面积

作者：Claude Code
日期：2025-01-06
版本：2.0 - 使用地级市级别数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("添加人均道路面积变量（地级市级别）")
print("=" * 80)
print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 文件路径
ROAD_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\各省+地级市+县级市人均道路面积.xlsx")
MAIN_DATA = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版.xlsx")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版.xlsx")

# ================================
# 步骤1：读取道路面积数据（地级市级别）
# ================================
print("\n[步骤1/5] 读取地级市道路面积数据...")

try:
    # 读取第2个sheet："地级市+地级市"
    df_road = pd.read_excel(ROAD_FILE, sheet_name=1)
    print(f"[OK] 原始数据维度: {df_road.shape}")
    print(f"  Sheet: 地级市+地级市")
except FileNotFoundError:
    print(f"[ERROR] 找不到文件 {ROAD_FILE}")
    exit(1)

# ================================
# 步骤2：提取关键字段并筛选
# ================================
print("\n[步骤2/5] 提取关键字段并筛选2007-2023年数据...")

# 数据结构：[年份, 省份, 省份代码, 城市, 城市代码, 人均道路面积, 人均道路面积 线性插值, ...]
# 使用列位置提取（避免中文编码问题）
# 索引: 0=年份, 3=城市, 4=城市代码, 6=人均道路面积（线性插值）
df_road_clean = df_road.iloc[:, [0, 3, 4, 6]].copy()

# 重命名列
df_road_clean.columns = ['year', 'city_name', 'city_code', 'road_area']

print(f"提取后数据结构:")
print(df_road_clean.head(10))

# 筛选2007-2023年
df_road_clean['year'] = pd.to_numeric(df_road_clean['year'], errors='coerce')
df_road_clean = df_road_clean[
    (df_road_clean['year'] >= 2007) &
    (df_road_clean['year'] <= 2023)
]

print(f"\n[OK] 筛选后数据维度: {df_road_clean.shape}")
print(f"  年份范围: {df_road_clean['year'].min()} - {df_road_clean['year'].max()}")
print(f"  城市数量: {df_road_clean['city_name'].nunique()}")

# ================================
# 步骤3：标准化城市代码
# ================================
print("\n[步骤3/5] 标准化城市代码格式...")

print(f"标准化前城市代码示例: {df_road_clean['city_code'].head().tolist()}")

# 转换城市代码为整数（去除小数点）
df_road_clean['city_code'] = pd.to_numeric(df_road_clean['city_code'], errors='coerce').astype('Int64')

# 去重：确保每个城市每年只有一条记录
before_dedup = len(df_road_clean)
df_road_clean = df_road_clean.drop_duplicates(subset=['year', 'city_code'], keep='first')
after_dedup = len(df_road_clean)

print(f"[OK] 标准化后城市代码示例: {df_road_clean['city_code'].head().tolist()}")
print(f"[OK] 去重: {before_dedup} -> {after_dedup} (去除{before_dedup - after_dedup}条重复)")

# 检查road_area数据
print(f"\n道路面积数据统计:")
print(df_road_clean['road_area'].describe())

# 检查缺失值
road_missing = df_road_clean['road_area'].isna().sum()
road_missing_rate = road_missing / len(df_road_clean) * 100
print(f"缺失值: {road_missing} ({road_missing_rate:.2f}%)")

# ================================
# 步骤4：合并到主数据集
# ================================
print("\n[步骤4/5] 合并到主数据集...")

# 读取主数据集
df_main = pd.read_excel(MAIN_DATA)

print(f"[OK] 主数据集维度: {df_main.shape}")
print(f"  列名: {list(df_main.columns)}")

# 如果已存在road_area和ln_road_area列，先删除
if 'road_area' in df_main.columns:
    print(f"\n[注意] 检测到已存在的road_area列，将重新计算")
    df_main = df_main.drop(columns=['road_area', 'ln_road_area'])
    print(f"[OK] 已删除旧的road_area和ln_road_area列")

# 检查主数据集的city_code格式
print(f"\n主数据集城市代码示例: {df_main['city_code'].head().tolist()}")

# 左连接（以主数据集为基准，使用city_code和year匹配）
df_merged = pd.merge(
    df_main,
    df_road_clean[['year', 'city_code', 'road_area']],
    on=['year', 'city_code'],
    how='left'
)

print(f"\n[OK] 合并后数据维度: {df_merged.shape}")
print(f"  新增列: road_area")

# 统计合并情况
matched = df_merged['road_area'].notna().sum()
total = len(df_merged)
match_rate = matched / total * 100

print(f"\n合并匹配情况:")
print(f"  成功匹配: {matched} ({match_rate:.2f}%)")
print(f"  未匹配: {total - matched} ({100 - match_rate:.2f}%)")

if match_rate < 50:
    print(f"\n[WARNING] 匹配率较低，请检查city_code格式是否一致")

# ================================
# 步骤5：计算对数人均道路面积
# ================================
print("\n[步骤5/5] 计算对数人均道路面积...")

# 计算ln(road_area + 1)，加1是为了处理0值
df_merged['ln_road_area'] = np.log(df_merged['road_area'] + 1)

print(f"[OK] 对数道路面积统计:")
print(df_merged['ln_road_area'].describe())

# 检查异常值
print(f"\n数据质量检查:")
print(f"  road_area = 0 的观测: {(df_merged['road_area'] == 0).sum()}")
print(f"  road_area < 0 的观测: {(df_merged['road_area'] < 0).sum()}")
print(f"  ln_road_area = 0 的观测: {(df_merged['ln_road_area'] == 0).sum()} (即road_area=0)")

# ================================
# 保存数据
# ================================
print("\n[保存] 保存更新后的数据集...")

# 保存
df_merged.to_excel(OUTPUT_FILE, index=False)

print(f"[OK] 数据已保存到: {OUTPUT_FILE}")

# ================================
# 生成报告
# ================================
print("\n" + "=" * 80)
print("人均道路面积变量添加总结（地级市级别）")
print("=" * 80)

print(f"\n1. 原始数据:")
print(f"   - 观测数: {len(df_road_clean)}")
print(f"   - 城市数: {df_road_clean['city_name'].nunique()}")
print(f"   - 年份范围: {df_road_clean['year'].min()} - {df_road_clean['year'].max()}")

print(f"\n2. 数据质量:")
print(f"   - 道路面积缺失率: {road_missing_rate:.2f}%")
print(f"   - 合并匹配率: {match_rate:.2f}%")

print(f"\n3. 最终数据集:")
print(f"   - 观测数: {len(df_merged)}")
print(f"   - 变量数: {len(df_merged.columns)}")
print(f"   - 新增变量: road_area, ln_road_area")

print(f"\n4. 描述性统计:")
print(f"   - road_area 均值: {df_merged['road_area'].mean():.2f} 平方米/人")
print(f"   - road_area 中位数: {df_merged['road_area'].median():.2f} 平方米/人")
print(f"   - road_area 范围: {df_merged['road_area'].min():.2f} - {df_merged['road_area'].max():.2f}")
print(f"   - ln_road_area 均值: {df_merged['ln_road_area'].mean():.4f}")

print(f"\n5. 变量说明:")
print(f"   - road_area: 人均道路面积（平方米/人），地级市级别")
print(f"   - ln_road_area: 对数人均道路面积，ln(road_area + 1)")
print(f"   - 加1是为了处理0值，避免对数运算报错")

print("\n[OK] 人均道路面积变量添加完成！")
print("=" * 80)
