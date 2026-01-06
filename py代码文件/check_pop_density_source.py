"""
检查人口密度原始数据的结构
"""

import pandas as pd
from pathlib import Path

POP_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据\298个地级市人口密度1998-2024年无缺失.xlsx")
df_pop = pd.read_excel(POP_FILE)

print("=" * 100)
print("人口密度原始数据结构检查")
print("=" * 100)

print(f"\n数据规模: {df_pop.shape}")
print(f"  行数: {df_pop.shape[0]}")
print(f"  列数: {df_pop.shape[1]}")

print(f"\n前10行数据:")
print(df_pop.head(10))

print(f"\n所有列名:")
for i, col in enumerate(df_pop.columns):
    print(f"[{i}] {col}")

print(f"\n数据类型:")
print(df_pop.dtypes)

# 检查几个典型城市
print("\n典型城市的人口密度数据:")
sample_cities = ['北京市', '上海市', '深圳市']
for city in sample_cities:
    city_data = df_pop[df_pop.iloc[:, 1] == city]  # 假设列1是城市名
    if len(city_data) > 0:
        print(f"\n{city}:")
        # 显示前5年和最后5年
        print("  前5年:")
        for idx, row in city_data.head(5).iterrows():
            year = row.iloc[2]  # 年份列
            pop_den = row.iloc[4]  # 人口密度列
            print(f"    {int(year)}年: {pop_den:.2f} 人/平方公里")
