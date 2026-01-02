#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据合并脚本
将所有Excel数据文件按照"城市代码-年份"主键合并成总数据集
"""

import pandas as pd
import os
from pathlib import Path

# 数据文件路径
BASE_DIR = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据")
OUTPUT_DIR = Path(r"c:\Users\HP\Desktop\毕业论文")

print("=" * 80)
print("开始数据合并流程")
print("=" * 80)

# ============================================
# 步骤1：读取产业结构数据
# ============================================
print("\n[步骤1/4] 读取产业结构数据...")
industrial_file = BASE_DIR / "2000-2023地级市产业结构 - 面板.xls"

try:
    df_industrial = pd.read_excel(industrial_file)
    print(f"✓ 成功读取: {len(df_industrial)} 行 × {len(df_industrial.columns)} 列")
    print(f"  列名: {list(df_industrial.columns)[:5]}...")
except Exception as e:
    print(f"✗ 读取失败: {e}")
    exit(1)

# 查看数据结构
print("\n产业结构数据样本:")
print(df_industrial.head(3))

# ============================================
# 步骤2：读取GDP数据
# ============================================
print("\n[步骤2/4] 读取GDP数据...")
gdp_file = BASE_DIR / "296个地级市GDP相关数据（以2000年为基期）.xlsx"

try:
    df_gdp = pd.read_excel(gdp_file)
    print(f"✓ 成功读取: {len(df_gdp)} 行 × {len(df_gdp.columns)} 列")
    print(f"  列名: {list(df_gdp.columns)[:5]}...")
except Exception as e:
    print(f"✗ 读取失败: {e}")
    exit(1)

print("\nGDP数据样本:")
print(df_gdp.head(3))

# ============================================
# 步骤3：读取人口密度数据
# ============================================
print("\n[步骤3/4] 读取人口密度数据...")
pop_file = BASE_DIR / "298个地级市人口密度1998-2024年无缺失.xlsx"

try:
    df_pop = pd.read_excel(pop_file)
    print(f"✓ 成功读取: {len(df_pop)} 行 × {len(df_pop.columns)} 列")
    print(f"  列名: {list(df_pop.columns)[:5]}...")
except Exception as e:
    print(f"✗ 读取失败: {e}")
    exit(1)

print("\n人口密度数据样本:")
print(df_pop.head(3))

# ============================================
# 步骤4：读取碳排放数据
# ============================================
print("\n[步骤4/4] 读取碳排放强度数据...")
carbon_file = BASE_DIR / "地级市碳排放强度.xlsx"

try:
    df_carbon = pd.read_excel(carbon_file)
    print(f"✓ 成功读取: {len(df_carbon)} 行 × {len(df_carbon.columns)} 列")
    print(f"  列名: {list(df_carbon.columns)[:5]}...")
except Exception as e:
    print(f"✗ 读取失败: {e}")
    exit(1)

print("\n碳排放数据样本:")
print(df_carbon.head(3))

# ============================================
# 数据探索：识别关键列
# ============================================
print("\n" + "=" * 80)
print("数据结构分析")
print("=" * 80)

print("\n产业结构数据列:")
for i, col in enumerate(df_industrial.columns):
    print(f"  {i+1}. {col}")

print("\n人口密度数据列:")
for i, col in enumerate(df_pop.columns):
    print(f"  {i+1}. {col}")

print("\nGDP数据列:")
for i, col in enumerate(df_gdp.columns):
    print(f"  {i+1}. {col}")

print("\n碳排放数据列:")
for i, col in enumerate(df_carbon.columns):
    print(f"  {i+1}. {col}")

# 保存数据探索结果到文件
report = []
report.append("=" * 80)
report.append("数据合并处理记录")
report.append("=" * 80)
report.append(f"\n处理时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"\n数据文件位置: {BASE_DIR}")

report.append("\n\n## 一、数据集基本信息")
report.append(f"\n1. 产业结构数据")
report.append(f"   - 文件: {industrial_file.name}")
report.append(f"   - 行数: {len(df_industrial)}")
report.append(f"   - 列数: {len(df_industrial.columns)}")
report.append(f"   - 列名: {', '.join(df_industrial.columns[:10])}...")

report.append(f"\n2. GDP数据")
report.append(f"   - 文件: {gdp_file.name}")
report.append(f"   - 行数: {len(df_gdp)}")
report.append(f"   - 列数: {len(df_gdp.columns)}")
report.append(f"   - 列名: {', '.join(df_gdp.columns[:10])}...")

report.append(f"\n3. 人口密度数据")
report.append(f"   - 文件: {pop_file.name}")
report.append(f"   - 行数: {len(df_pop)}")
report.append(f"   - 列数: {len(df_pop.columns)}")
report.append(f"   - 列名: {', '.join(df_pop.columns[:10])}...")

report.append(f"\n4. 碳排放数据")
report.append(f"   - 文件: {carbon_file.name}")
report.append(f"   - 行数: {len(df_carbon)}")
report.append(f"   - 列数: {len(df_carbon.columns)}")
report.append(f"   - 列名: {', '.join(df_carbon.columns[:10])}...")

report.append("\n\n## 二、识别的关键列")
report.append("\n需要确认的主键列（城市代码、年份）:")
report.append("\n产业结构数据可能的主键:")
for col in df_industrial.columns:
    if '代码' in str(col) or 'code' in str(col).lower() or '城市' in str(col) or '年份' in str(col) or '年度' in str(col):
        report.append(f"  - {col}")

report.append("\n人口密度数据可能的主键:")
for col in df_pop.columns:
    if '代码' in str(col) or 'code' in str(col).lower() or '城市' in str(col) or '年份' in str(col) or '年度' in str(col):
        report.append(f"  - {col}")

report.append("\nGDP数据可能的主键:")
for col in df_gdp.columns:
    if '代码' in str(col) or 'code' in str(col).lower() or '城市' in str(col) or '年份' in str(col) or '年度' in str(col):
        report.append(f"  - {col}")

report.append("\n碳排放数据可能的主键:")
for col in df_carbon.columns:
    if '代码' in str(col) or 'code' in str(col).lower() or '城市' in str(col) or '年份' in str(col) or '年度' in str(col):
        report.append(f"  - {col}")

# 保存初步报告
report_path = OUTPUT_DIR / "数据清理计划.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"\n初步分析报告已保存到: {report_path}")
print("\n由于数据结构复杂，建议手动检查上述列名后，再进行自动化合并。")
print("或者我可以尝试智能识别主键列并继续合并。")

# 显示前几行数据供人工检查
print("\n" + "=" * 80)
print("数据预览（请检查主键列）")
print("=" * 80)

print("\n产业结构数据前3行:")
print(df_industrial.head(3).to_string())

print("\n人口密度数据前3行:")
print(df_pop.head(3).to_string())

print("\n" + "=" * 80)
print("数据探索完成！")
print("=" * 80)
