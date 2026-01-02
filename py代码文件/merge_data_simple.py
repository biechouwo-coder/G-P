#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据合并脚本 - 简化版（跳过.xls文件）
"""

import pandas as pd
from pathlib import Path
import sys

# 设置输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 数据路径配置
DATA_DIR = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据")
OUTPUT_DIR = Path(r"c:\Users\HP\Desktop\毕业论文")
OUTPUT_FILE = OUTPUT_DIR / "总数据集.xlsx"

print("=" * 80)
print("数据合并程序启动（简化版）")
print("=" * 80)

# ============================================
# 步骤1：读取.xlsx格式的数据文件
# ============================================

print("\n[步骤1/4] 读取.xlsx格式数据文件...")

# 1.1 读取人口密度数据
print("\n读取人口密度数据...")
pop_file = DATA_DIR / "298个地级市人口密度1998-2024年无缺失.xlsx"
try:
    df_pop = pd.read_excel(pop_file)
    print(f"✓ 成功: {len(df_pop)} 行 × {len(df_pop.columns)} 列")
    print(f"  列名: {list(df_pop.columns)}")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# 1.2 读取GDP数据
print("\n读取GDP数据...")
gdp_file = DATA_DIR / "296个地级市GDP相关数据（以2000年为基期）.xlsx"
try:
    df_gdp = pd.read_excel(gdp_file)
    print(f"✓ 成功: {len(df_gdp)} 行 × {len(df_gdp.columns)} 列")
    print(f"  列名: {list(df_gdp.columns)}")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

# 1.3 读取碳排放数据
print("\n读取碳排放强度数据...")
carbon_file = DATA_DIR / "地级市碳排放强度.xlsx"
try:
    df_carbon = pd.read_excel(carbon_file)
    print(f"✓ 成功: {len(df_carbon)} 行 × {len(df_carbon.columns)} 列")
    print(f"  列名: {list(df_carbon.columns)}")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

print("\n⚠ 注意：.xls格式的产业结构数据需要手动转换为.xlsx后才能读取")
print("  或者在Excel中使用Power Query功能完成所有数据的合并")

# ============================================
# 步骤2：识别并标准化主键列
# ============================================

print("\n" + "=" * 80)
print("[步骤2/4] 识别主键列...")

def identify_key_columns(df, df_name):
    """识别城市代码和年份列"""
    city_cols = []
    year_cols = []

    for col in df.columns:
        col_str = str(col)
        # 识别城市代码列
        if any(keyword in col for keyword in ['城市代码', '城市编码', '行政代码', 'City_Code', 'city_code', '市代码']):
            if '省' not in col:
                city_cols.append(col)
        # 识别年份列
        if any(keyword in col for keyword in ['年份', '年度', 'Year', 'year', '年']):
            if '占' not in col and '增长' not in col:
                year_cols.append(col)

    return city_cols, year_cols

gdp_city_cols, gdp_year_cols = identify_key_columns(df_gdp, "GDP")
pop_city_cols, pop_year_cols = identify_key_columns(df_pop, "人口密度")
carbon_city_cols, carbon_year_cols = identify_key_columns(df_carbon, "碳排放")

print(f"\nGDP数据: 城市代码列={gdp_city_cols}, 年份列={gdp_year_cols}")
print(f"人口密度数据: 城市代码列={pop_city_cols}, 年份列={pop_year_cols}")
print(f"碳排放数据: 城市代码列={carbon_city_cols}, 年份列={carbon_year_cols}")

# 选择主键列
def get_first(lst, default):
    return lst[0] if lst else default

gdp_city_col = get_first(gdp_city_cols, list(df_gdp.columns)[2] if len(df_gdp.columns) > 2 else '城市代码')
gdp_year_col = get_first(gdp_year_cols, list(df_gdp.columns)[1] if len(df_gdp.columns) > 1 else '年份')

pop_city_col = get_first(pop_city_cols, list(df_pop.columns)[3] if len(df_pop.columns) > 3 else '城市代码')
pop_year_col = get_first(pop_year_cols, list(df_pop.columns)[1] if len(df_pop.columns) > 1 else '年份')

carbon_city_col = get_first(carbon_city_cols, list(df_carbon.columns)[2] if len(df_carbon.columns) > 2 else '城市代码')
carbon_year_col = get_first(carbon_year_cols, list(df_carbon.columns)[1] if len(df_carbon.columns) > 1 else '年份')

# 重命名主键列
print(f"\n标准化主键列名...")
print(f"  GDP: {gdp_city_col}→city_code, {gdp_year_col}→year")
print(f"  人口密度: {pop_city_col}→city_code, {pop_year_col}→year")
print(f"  碳排放: {carbon_city_col}→city_code, {carbon_year_col}→year")

df_gdp = df_gdp.rename(columns={gdp_city_col: 'city_code', gdp_year_col: 'year'})
df_pop = df_pop.rename(columns={pop_city_col: 'city_code', pop_year_col: 'year'})
df_carbon = df_carbon.rename(columns={carbon_city_col: 'city_code', carbon_year_col: 'year'})

print("✓ 主键列已标准化")

# ============================================
# 步骤3：合并数据集
# ============================================

print("\n" + "=" * 80)
print("[步骤3/4] 合并数据集...")

# 3.1 合并人口密度和GDP数据
print("\n合并: 人口密度 + GDP")
df_merged = pd.merge(df_pop, df_gdp, on=['city_code', 'year'], how='outer', indicator='gdp_source')
print(f"  合并后: {len(df_merged)} 行")
print(f"  仅在人口密度中: {(df_merged['gdp_source'] == 'left_only').sum()}")
print(f"  仅在GDP中: {(df_merged['gdp_source'] == 'right_only').sum()}")
print(f"  两边都有: {(df_merged['gdp_source'] == 'both').sum()}")

# 3.2 合并碳排放数据
print("\n合并: 上述结果 + 碳排放")
df_merged = pd.merge(df_merged, df_carbon, on=['city_code', 'year'], how='outer', indicator='carbon_source')
print(f"  合并后: {len(df_merged)} 行")
print(f"  碳排放匹配成功: {(df_merged['carbon_source'] == 'both').sum()}")
print(f"  碳排放未匹配: {(df_merged['carbon_source'] == 'left_only').sum()}")

# 删除indicator列
df_merged = df_merged.drop(columns=['gdp_source', 'carbon_source'], errors='ignore')

# ============================================
# 步骤4：保存合并数据
# ============================================

print("\n" + "=" * 80)
print("[步骤4/4] 保存合并数据...")

# 4.1 保存为Excel
print(f"\n正在保存到: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_merged.to_excel(writer, sheet_name='总数据集', index=False)

print(f"✓ 数据已保存！")

# 4.2 保存数据说明
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
        missing_count = df_merged[col].isnull().sum()
        missing_pct = (missing_count / len(df_merged) * 100) if len(df_merged) > 0 else 0
        f.write(f"{i}. {col}\n")
        f.write(f"   数据类型: {dtype_str}\n")
        f.write(f"   缺失值: {missing_count} ({missing_pct:.2f}%)\n")
        f.write(f"   示例值: {df_merged[col].iloc[0] if len(df_merged) > 0 else 'N/A'}\n\n")

print(f"✓ 变量说明已保存到: {readme_file}")

print("\n" + "=" * 80)
print("数据合并完成！")
print("=" * 80)
print(f"\n✓ 总数据集: {OUTPUT_FILE}")
print(f"✓ 变量说明: {readme_file}")
print(f"\n⚠ 注意：由于无法读取.xls格式的产业结构数据，")
print(f"  当前数据集仅包含：人口密度 + GDP + 碳排放")
print(f"  请手动添加产业结构数据或将其转换为.xlsx格式后重新运行")
