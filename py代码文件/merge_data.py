#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据合并脚本 - 将所有Excel数据文件合并成总数据集
"""

import pandas as pd
from pathlib import Path
import sys

# 设置输出编码为UTF-8，防止中文乱码
sys.stdout.reconfigure(encoding='utf-8')

# 数据路径配置
DATA_DIR = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据")
OUTPUT_DIR = Path(r"c:\Users\HP\Desktop\毕业论文")
OUTPUT_FILE = OUTPUT_DIR / "总数据集.xlsx"

print("=" * 80)
print("数据合并程序启动")
print("=" * 80)

# ============================================
# 步骤1：读取所有数据文件
# ============================================

print("\n[步骤1/5] 读取数据文件...")

# 1.1 读取产业结构数据
print("\n读取产业结构数据...")
industrial_file = DATA_DIR / "2000-2023地级市产业结构 - 面板.xls"
try:
    df_industrial = pd.read_excel(industrial_file)
    print(f"✓ 成功: {len(df_industrial)} 行 × {len(df_industrial.columns)} 列")
    print(f"  列名: {list(df_industrial.columns)[:10]}...")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# 1.2 读取GDP数据
print("\n读取GDP数据...")
gdp_file = DATA_DIR / "296个地级市GDP相关数据（以2000年为基期）.xlsx"
try:
    df_gdp = pd.read_excel(gdp_file)
    print(f"✓ 成功: {len(df_gdp)} 行 × {len(df_gdp.columns)} 列")
    print(f"  列名: {list(df_gdp.columns)[:10]}...")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# 1.3 读取人口密度数据
print("\n读取人口密度数据...")
pop_file = DATA_DIR / "298个地级市人口密度1998-2024年无缺失.xlsx"
try:
    df_pop = pd.read_excel(pop_file)
    print(f"✓ 成功: {len(df_pop)} 行 × {len(df_pop.columns)} 列")
    print(f"  列名: {list(df_pop.columns)[:10]}...")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# 1.4 读取碳排放数据
print("\n读取碳排放强度数据...")
carbon_file = DATA_DIR / "地级市碳排放强度.xlsx"
try:
    df_carbon = pd.read_excel(carbon_file)
    print(f"✓ 成功: {len(df_carbon)} 行 × {len(df_carbon.columns)} 列")
    print(f"  列名: {list(df_carbon.columns)[:10]}...")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# ============================================
# 步骤2：识别并标准化主键列
# ============================================

print("\n" + "=" * 80)
print("[步骤2/5] 识别主键列...")

def identify_key_columns(df, df_name):
    """识别城市代码和年份列"""
    city_cols = []
    year_cols = []

    for col in df.columns:
        col_str = str(col).lower()
        # 识别城市代码列
        if any(keyword in col for keyword in ['城市代码', '城市编码', '行政代码', 'City_Code', 'city_code', '市代码']):
            if '省' not in col:  # 排除省份代码列
                city_cols.append(col)
        # 识别年份列
        if any(keyword in col for keyword in ['年份', '年度', 'Year', 'year', '年']):
            if '占' not in col:  # 排除占比类列
                year_cols.append(col)

    return city_cols, year_cols

ind_city_cols, ind_year_cols = identify_key_columns(df_industrial, "产业结构")
gdp_city_cols, gdp_year_cols = identify_key_columns(df_gdp, "GDP")
pop_city_cols, pop_year_cols = identify_key_columns(df_pop, "人口密度")
carbon_city_cols, carbon_year_cols = identify_key_columns(df_carbon, "碳排放")

print(f"\n产业结构数据: 城市代码列={ind_city_cols}, 年份列={ind_year_cols}")
print(f"GDP数据: 城市代码列={gdp_city_cols}, 年份列={gdp_year_cols}")
print(f"人口密度数据: 城市代码列={pop_city_cols}, 年份列={pop_year_cols}")
print(f"碳排放数据: 城市代码列={carbon_city_cols}, 年份列={carbon_year_cols}")

# 选择主键列（取第一个匹配的）
def get_first(lst, default):
    return lst[0] if lst else default

ind_city_col = get_first(ind_city_cols, '城市代码')
ind_year_col = get_first(ind_year_cols, '年度')

gdp_city_col = get_first(gdp_city_cols, '城市代码')
gdp_year_col = get_first(gdp_year_cols, '年份')

pop_city_col = get_first(pop_city_cols, '城市代码')
pop_year_col = get_first(pop_year_cols, '年份')

carbon_city_col = get_first(carbon_city_cols, '城市代码')
carbon_year_col = get_first(carbon_year_cols, '年份')

# 重命名主键列为标准名称
print("\n标准化主键列名...")
df_industrial = df_industrial.rename(columns={ind_city_col: 'city_code', ind_year_col: 'year'})
df_gdp = df_gdp.rename(columns={gdp_city_col: 'city_code', gdp_year_col: 'year'})
df_pop = df_pop.rename(columns={pop_city_col: 'city_code', pop_year_col: 'year'})
df_carbon = df_carbon.rename(columns={carbon_city_col: 'city_code', carbon_year_col: 'year'})

print("✓ 主键列已标准化为: city_code, year")

# ============================================
# 步骤3：合并数据集
# ============================================

print("\n" + "=" * 80)
print("[步骤3/5] 合并数据集...")

# 3.1 合并产业结构和GDP数据
print("\n合并: 产业结构 + GDP")
df_merged = pd.merge(df_industrial, df_gdp, on=['city_code', 'year'], how='left', indicator='gdp_source')
print(f"  合并后: {len(df_merged)} 行")
print(f"  仅在产业结构数据中: {(df_merged['gdp_source'] == 'left_only').sum()}")
print(f"  仅在GDP数据中: {(df_merged['gdp_source'] == 'right_only').sum()}")
print(f"  两边都有: {(df_merged['gdp_source'] == 'both').sum()}")

# 3.2 合并人口密度数据
print("\n合并: 上述结果 + 人口密度")
df_merged = pd.merge(df_merged, df_pop, on=['city_code', 'year'], how='left', indicator='pop_source')
print(f"  合并后: {len(df_merged)} 行")
print(f"  人口密度匹配成功: {(df_merged['pop_source'] == 'both').sum()}")
print(f"  人口密度未匹配: {(df_merged['pop_source'] == 'left_only').sum()}")

# 3.3 合并碳排放数据
print("\n合并: 上述结果 + 碳排放")
df_merged = pd.merge(df_merged, df_carbon, on=['city_code', 'year'], how='left', indicator='carbon_source')
print(f"  合并后: {len(df_merged)} 行")
print(f"  碳排放匹配成功: {(df_merged['carbon_source'] == 'both').sum()}")
print(f"  碳排放未匹配: {(df_merged['carbon_source'] == 'left_only').sum()}")

# 删除indicator列
df_merged = df_merged.drop(columns=['gdp_source', 'pop_source', 'carbon_source'], errors='ignore')

# ============================================
# 步骤4：数据质量检查
# ============================================

print("\n" + "=" * 80)
print("[步骤4/5] 数据质量检查...")

# 4.1 基本统计
print(f"\n✓ 总行数: {len(df_merged)}")
print(f"✓ 总列数: {len(df_merged.columns)}")
print(f"✓ 唯一城市数: {df_merged['city_code'].nunique()}")
print(f"✓ 年份范围: {df_merged['year'].min()} - {df_merged['year'].max()}")
print(f"✓ 完整观测数(城市×年份): {len(df_merged)}")

# 4.2 缺失值统计
print("\n缺失值统计（前20个变量）:")
missing_stats = df_merged.isnull().sum()
missing_stats = missing_stats[missing_stats > 0].sort_values(ascending=False)
print(missing_stats.head(20))

if len(missing_stats) > 0:
    missing_pct = (missing_stats / len(df_merged) * 100).round(2)
    print(f"\n缺失率最高的5个变量:")
    for var in missing_pct.head(5).index:
        print(f"  {var}: {missing_pct[var]}%")

# 4.3 检查重复观测
duplicates = df_merged.duplicated(subset=['city_code', 'year']).sum()
if duplicates > 0:
    print(f"\n⚠ 警告: 发现 {duplicates} 个重复的city_code-year组合")
else:
    print(f"\n✓ 无重复观测")

# ============================================
# 步骤5：保存合并数据
# ============================================

print("\n" + "=" * 80)
print("[步骤5/5] 保存合并数据...")

# 5.1 保存为Excel
print(f"\n正在保存到: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_merged.to_excel(writer, sheet_name='总数据集', index=False)

print(f"✓ 数据已保存！")

# 5.2 保存数据说明
readme_file = OUTPUT_DIR / "总数据集_变量说明.txt"
with open(readme_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("总数据集 - 变量说明文档\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"文件位置: {OUTPUT_FILE}\n\n")
    f.write(f"数据规模:\n")
    f.write(f"  - 总行数: {len(df_merged)}\n")
    f.write(f"  - 总列数: {len(df_merged.columns)}\n")
    f.write(f"  - 城市数: {df_merged['city_code'].nunique()}\n")
    f.write(f"  - 年份范围: {int(df_merged['year'].min())} - {int(df_merged['year'].max())}\n\n")
    f.write("=" * 80 + "\n")
    f.write("变量列表:\n")
    f.write("=" * 80 + "\n\n")
    for i, col in enumerate(df_merged.columns, 1):
        dtype_str = str(df_merged[col].dtype)
        missing_str = f"{df_merged[col].isnull().sum()} ({df_merged[col].isnull().sum()/len(df_merged)*100:.2f}%)"
        f.write(f"{i}. {col}\n")
        f.write(f"   数据类型: {dtype_str}\n")
        f.write(f"   缺失值: {missing_str}\n")
        f.write(f"   示例值: {df_merged[col].iloc[0] if len(df_merged) > 0 else 'N/A'}\n\n")

print(f"✓ 变量说明已保存到: {readme_file}")

print("\n" + "=" * 80)
print("数据合并完成！")
print("=" * 80)
