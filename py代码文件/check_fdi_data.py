"""
检查FDI（外商直接投资）原始数据结构
"""

import pandas as pd
from pathlib import Path

FDI_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\1996-2023年地级市外商直接投资FDI.xls")

print("=" * 100)
print("FDI原始数据结构检查")
print("=" * 100)

# 读取数据
df_fdi = pd.read_excel(FDI_FILE)

print(f"\n数据规模: {df_fdi.shape}")
print(f"  行数: {df_fdi.shape[0]}")
print(f"  列数: {df_fdi.shape[1]}")

print(f"\n前10行数据:")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df_fdi.head(10))

print(f"\n所有列名:")
for i, col in enumerate(df_fdi.columns):
    print(f"[{i:2d}] {col}")

print(f"\n数据类型:")
print(df_fdi.dtypes)

# 检查时间范围
print(f"\n时间范围:")
if '年份' in df_fdi.columns or 'year' in df_fdi.columns.str.lower():
    year_col = '年份' if '年份' in df_fdi.columns else df_fdi.columns[0]
    year_range = df_fdi[year_col].dropna()
    print(f"  起始年份: {year_range.min()}")
    print(f"  结束年份: {year_range.max()}")

# 检查城市数量
print(f"\n城市数量:")
if '城市' in df_fdi.columns or '地级市' in df_fdi.columns:
    city_col = '城市' if '城市' in df_fdi.columns else '地级市'
    num_cities = df_fdi[city_col].nunique()
    print(f"  城市数: {num_cities}")

# 检查缺失值
print(f"\n缺失值统计:")
missing_stats = df_fdi.isna().sum()
for col, count in missing_stats.items():
    if count > 0:
        missing_rate = count / len(df_fdi) * 100
        print(f"  {col}: {count} ({missing_rate:.2f}%)")

# 随机抽取几个城市查看
print(f"\n典型城市数据示例:")
sample_cities = df_fdi.iloc[:, 1].unique()[:5] if len(df_fdi.columns) > 1 else []
for city in sample_cities:
    city_data = df_fdi[df_fdi.iloc[:, 1] == city]
    print(f"\n  {city}:")
    print(f"    观测数: {len(city_data)}")
    if len(city_data) > 0:
        print(f"    前5年数据:")
        for idx, row in city_data.head(5).iterrows():
            print(f"      {row.iloc[0]}年: {row.iloc[-1]}")
