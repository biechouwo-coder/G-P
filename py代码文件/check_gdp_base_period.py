"""
检查原始GDP数据的基期问题
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("检查原始GDP数据的基期设置")
print("=" * 80)

# 读取原始GDP数据
GDP_RAW_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
df_gdp_raw = pd.read_excel(GDP_RAW_FILE)

print(f"\n原始GDP数据规模: {df_gdp_raw.shape}")
print(f"前3行数据:")
print(df_gdp_raw.head(3))

# 查看列名
print(f"\n所有列名:")
for i, col in enumerate(df_gdp_raw.columns):
    print(f"  [{i}] {col}")

# 检查几个异常城市的原始数据
print("\n" + "=" * 80)
print("检查异常城市的原始GDP数据")
print("=" * 80)

# 读取清洗后的数据
df_clean = pd.read_excel(Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx"))

# 找出GDP平减指数<1的城市
problem_cities = df_clean[df_clean['gdp_deflator'] < 0.6]['city_name'].unique()[:5]
print(f"\n检查的城市（gdp_deflator < 0.6）: {', '.join(problem_cities)}")

# 在原始数据中查找这些城市
for city in problem_cities:
    print(f"\n{'='*80}")
    print(f"城市: {city}")
    print(f"{'='*80}")

    city_raw = df_gdp_raw[df_gdp_raw.iloc[:, 1] == city]  # 假设列1是城市名

    if len(city_raw) > 0:
        print(f"\n原始数据（前10年）:")
        # 打印年份、实际GDP、GDP平减指数
        for idx, row in city_raw.head(10).iterrows():
            year = row.iloc[2]  # 假设列2是年份
            gdp_real = row.iloc[5]  # 假设列5是实际GDP
            gdp_deflator = row.iloc[6]  # 假设列6是GDP平减指数
            print(f"  {int(year)}年: gdp_real={gdp_real:.2f}, gdp_deflator={gdp_deflator:.4f}")
    else:
        print("  未找到该城市数据")

print("\n" + "=" * 80)
print("基期分析结论")
print("=" * 80)

# 检查2000年的GDP平减指数
print("\n检查各城市2000年的GDP平减指数:")
for city in problem_cities:
    city_raw = df_gdp_raw[df_gdp_raw.iloc[:, 1] == city]
    if len(city_raw) > 0:
        city_2000 = city_raw[city_raw.iloc[:, 2] == 2000]
        if len(city_2000) > 0:
            deflator_2000 = city_2000.iloc[0, 6]  # GDP平减指数
            print(f"  {city:12s}: {deflator_2000:.4f}")
