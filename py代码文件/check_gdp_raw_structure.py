"""
检查原始GDP数据的列结构
"""

import pandas as pd
from pathlib import Path

GDP_RAW_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
df_gdp_raw = pd.read_excel(GDP_RAW_FILE)

print("=" * 80)
print("原始GDP数据结构")
print("=" * 80)
print(f"Shape: {df_gdp_raw.shape}")
print(f"\n列名及示例数据:")
print("-" * 100)

# 打印前5行，每列都显示
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df_gdp_raw.head(5))

print("\n" + "=" * 80)
print("列名列表")
print("=" * 80)
for i, col in enumerate(df_gdp_raw.columns):
    print(f"[{i:2d}] {col}")

# 检查几个问题城市的具体数据
df_clean = pd.read_excel(Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx"))
problem_obs = df_clean[df_clean['gdp_deflator'] < 0.6].sort_values('gdp_deflator').head(10)

print("\n" + "=" * 80)
print("清洗后数据中GDP平减指数最低的10个观测")
print("=" * 80)
print(problem_obs[['city_name', 'year', 'gdp_deflator', 'gdp_real']].to_string(index=False))
