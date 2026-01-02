"""
对比正常城市和异常城市的GDP平减指数
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("GDP平减指数异常原因分析")
print("=" * 100)

# 读取原始数据
GDP_RAW_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\296个地级市GDP相关数据（以2000年为基期）.xlsx")
df_gdp_raw = pd.read_excel(GDP_RAW_FILE)

# 读取清洗后的数据
df_clean = pd.read_excel(Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx"))

print("\n【对比分析】上海（正常）vs 朔州（异常）")
print("=" * 100)

# 上海（正常城市）
shanghai = df_gdp_raw[df_gdp_raw.iloc[:, 1] == '上海市']
print("\n1. 上海市 GDP平减指数（正常）:")
print("-" * 60)
print(f"{'年份':<6} {'名义GDP':<12} {'GDP指数':<10} {'实际GDP':<12} {'GDP平减指数':<12}")
print("-" * 60)
for idx, row in shanghai.head(10).iterrows():
    year = int(row.iloc[2])
    gdp_nominal = row.iloc[3]
    gdp_index = row.iloc[4]
    gdp_real = row.iloc[5]
    gdp_deflator = row.iloc[6]
    print(f"{year:<6} {gdp_nominal:<12.2f} {gdp_index:<10.2f} {gdp_real:<12.2f} {gdp_deflator:<12.4f}")

# 朔州（异常城市）
shuozhou = df_gdp_raw[df_gdp_raw.iloc[:, 1] == '朔州市']
if len(shuozhou) > 0:
    print("\n2. 朔州市 GDP平减指数（异常）:")
    print("-" * 60)
    print(f"{'年份':<6} {'名义GDP':<12} {'GDP指数':<10} {'实际GDP':<12} {'GDP平减指数':<12}")
    print("-" * 60)
    for idx, row in shuozhou.iterrows():
        year = int(row.iloc[2])
        gdp_nominal = row.iloc[3]
        gdp_index = row.iloc[4]
        gdp_real = row.iloc[5]
        gdp_deflator = row.iloc[6]
        print(f"{year:<6} {gdp_nominal:<12.2f} {gdp_index:<10.2f} {gdp_real:<12.2f} {gdp_deflator:<12.4f}")
else:
    print("\n2. 朔州市未在原始GDP数据中找到")

# 检查朔州在清洗后数据中的情况
shuozhou_clean = df_clean[df_clean['city_name'] == '朔州市']
if len(shuozhou_clean) > 0:
    print("\n3. 朔州市在清洗后数据中的情况:")
    print("-" * 60)
    print(f"{'年份':<6} {'实际GDP':<12} {'GDP平减指数':<12}")
    print("-" * 60)
    for idx, row in shuozhou_clean.iterrows():
        print(f"{row['year']:<6} {row['gdp_real']:<12.2f} {row['gdp_deflator']:<12.4f}")

print("\n" + "=" * 100)
print("问题诊断")
print("=" * 100)

# 分析：GDP平减指数的计算逻辑
print("""
GDP平减指数的计算公式：
  GDP平减指数 = 名义GDP / 实际GDP = 名义GDP / (名义GDP / GDP指数 × 基期GDP)

如果以2000年为基期（2000年=1.0），则：
  - 2000年：GDP平减指数应该 = 1.0
  - 2000年后：由于通胀，GDP平减指数应该 > 1.0
  - 如果 < 1.0，说明：该城市的基期不是2000年！

可能的原因：
1. 原始数据中，某些城市的实际GDP是以其他年份为基期计算的
2. 数据合并时，错误地混入了不同基期的数据
3. 某些城市（如朔州）的数据起始年份较晚（如2011年建市），基期可能是建市年份
""")

# 统计问题城市的特征
problem_deflator = df_clean[df_clean['gdp_deflator'] < 0.8]
print(f"\n统计：GDP平减指数 < 0.8 的观测")
print(f"  数量: {len(problem_deflator)} ({len(problem_deflator)/len(df_clean)*100:.2f}%)")
print(f"  涉及城市: {problem_deflator['city_name'].nunique()}个")

# 检查这些城市的年份分布
print(f"\n问题观测的年份分布:")
year_dist = problem_deflator.groupby('year').size().sort_index()
for year, count in year_dist.items():
    print(f"  {year}年: {count}个观测")

# 检查是否是新建城市
print(f"\n检查问题城市是否为新建地级市:")
problem_cities = problem_deflator['city_name'].unique()
print(f"  问题城市数: {len(problem_cities)}")
print(f"  前10个城市: {', '.join(problem_cities[:10])}")

print("\n建议:")
print("  1. 剔除GDP平减指数 < 0.8 的所有观测（可能是基期不一致）")
print("  2. 或者，重新计算这些城市的GDP平减指数（需要原始名义GDP数据）")
print("  3. 或者，在模型中仅使用gdp_real，不控制gdp_deflator")
