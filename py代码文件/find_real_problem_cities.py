"""
找出真正的异常城市
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("找出GDP平减指数真正异常的城市")
print("=" * 100)

# 读取清洗后的数据
df_clean = pd.read_excel(Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx"))

# 找出最低的10个观测
lowest_10 = df_clean.sort_values('gdp_deflator').head(10)

print("\n清洗后数据中GDP平减指数最低的10个观测:")
print("-" * 100)
print(lowest_10[['city_name', 'year', 'gdp_deflator', 'gdp_real']].to_string(index=False))

# 读取原始GDP数据
df_gdp_raw = pd.read_excel(
    Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
)

# 在原始数据中查找这些城市
print("\n" + "=" * 100)
print("在原始GDP数据中验证这些城市")
print("=" * 100)

problem_cities = lowest_10['city_name'].unique()

for city in problem_cities:
    print(f"\n{'='*80}")
    print(f"城市: {city}")
    print(f"{'='*80}")

    # 在原始数据中查找
    city_raw = df_gdp_raw[df_gdp_raw.iloc[:, 1] == city]

    if len(city_raw) > 0:
        print("\n原始数据（所有年份）:")
        print(f"{'年份':<6} {'名义GDP':<12} {'GDP指数':<10} {'实际GDP':<12} {'GDP平减指数':<12}")
        print("-" * 60)
        for idx, row in city_raw.iterrows():
            year = int(row.iloc[2])
            gdp_nominal = row.iloc[3]
            gdp_index = row.iloc[4]
            gdp_real = row.iloc[5]
            gdp_deflator = row.iloc[6]
            print(f"{year:<6} {gdp_nominal:<12.2f} {gdp_index:<10.2f} {gdp_real:<12.2f} {gdp_deflator:<12.4f}")

        # 在清洗后数据中的情况
        city_clean = df_clean[df_clean['city_name'] == city]
        print("\n清洗后数据中的情况（低值观测）:")
        print(f"{'年份':<6} {'实际GDP':<12} {'GDP平减指数':<12}")
        print("-" * 40)
        low_values = city_clean[city_clean['gdp_deflator'] < 0.8].sort_values('year')
        for idx, row in low_values.iterrows():
            print(f"{row['year']:<6} {row['gdp_real']:<12.2f} {row['gdp_deflator']:<12.4f}")
    else:
        print("未在原始GDP数据中找到该城市！")

print("\n" + "=" * 100)
print("关键发现")
print("=" * 100)

# 检查是否存在数据合并错误
print("\n检查是否存在数据合并错误（不同城市的数据被混淆）:")
print("-" * 100)

# 随机选择几个异常观测
sample_problems = lowest_10.head(3)

for idx, row in sample_problems.iterrows():
    city_name = row['city_name']
    year = row['year']
    gdp_deflator_clean = row['gdp_deflator']
    gdp_real_clean = row['gdp_real']

    # 在原始数据中查找该城市该年份
    city_raw = df_gdp_raw[df_gdp_raw.iloc[:, 1] == city_name]
    city_raw_year = city_raw[city_raw.iloc[:, 2] == year]

    if len(city_raw_year) > 0:
        gdp_deflator_raw = city_raw_year.iloc[0, 6]
        gdp_real_raw = city_raw_year.iloc[0, 5]

        match = "✓" if abs(gdp_deflator_clean - gdp_deflator_raw) < 0.01 else "✗ 不匹配！"

        print(f"\n{city_name} {year}年:")
        print(f"  原始数据: gdp_deflator={gdp_deflator_raw:.4f}, gdp_real={gdp_real_raw:.2f}")
        print(f"  清洗后数据: gdp_deflator={gdp_deflator_clean:.4f}, gdp_real={gdp_real_clean:.2f}")
        print(f"  匹配: {match}")
    else:
        print(f"\n{city_name} {year}年: 未在原始数据中找到")
