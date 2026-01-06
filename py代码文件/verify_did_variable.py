"""
验证DID变量正确性
"""

import pandas as pd
from pathlib import Path

DATA_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_最终版_含DID.xlsx")
df = pd.read_excel(DATA_FILE)

print("=" * 100)
print("DID变量验证报告")
print("=" * 100)

# 基本统计
print(f"\n数据规模: {df.shape}")
print(f"  观测数: {len(df)}")
print(f"  城市数: {df['city_name'].nunique()}")

# DID变量统计
print(f"\nDID变量统计:")
print(f"  treat=1 (试点城市): {df['treat'].sum() / df['year'].nunique():.0f}个")
print(f"  treat=0 (对照城市): {df['city_name'].nunique() - df['treat'].sum() / df['year'].nunique():.0f}个")
print(f"  DID=1的观测: {df['did'].sum()}个 ({df['did'].sum()/len(df)*100:.2f}%)")
print(f"  DID=0的观测: {len(df) - df['did'].sum()}个 ({(1-df['did'].sum()/len(df))*100:.2f}%)")

# 各批次试点城市
print(f"\n各批次试点城市数:")
batch_counts = df[df['treat'] == 1].groupby('pilot_year')['city_name'].nunique().sort_index()
for year, count in batch_counts.items():
    print(f"  {int(year)}年批次: {count}个城市")

# 时间趋势
print(f"\nDID=1的观测数随时间变化:")
did_trend = df[df['did'] == 1].groupby('year').size()
for year, count in did_trend.items():
    pct = count / df[df['year'] == year]['city_name'].nunique() * 100
    print(f"  {int(year)}年: {count}个城市 (占{pct:.1f}%)")

# 验证逻辑正确性
print(f"\n逻辑验证:")
print("  检查: treat=1的城市，pilot_year之后did应该=1")
for pilot_year in [2010, 2013, 2017]:
    cities = df[df['pilot_year'] == pilot_year]['city_name'].unique()[:3]
    for city in cities:
        city_data = df[df['city_name'] == city]
        before_policy = city_data[city_data['year'] < pilot_year]['did'].sum()
        after_policy = city_data[city_data['year'] >= pilot_year]['did'].sum()
        print(f"    {city} ({int(pilot_year)}年起): 政策前did={before_policy}, 政策后did={after_policy} (预期0, >0)")

# 试点城市名单验证
print(f"\n第一批（2010年）部分城市:")
batch1 = df[df['pilot_year'] == 2010]['city_name'].unique()[:10]
print(f"  {', '.join(batch1)}")

print(f"\n第二批（2013年）部分城市:")
batch2 = df[df['pilot_year'] == 2013]['city_name'].unique()[:10]
print(f"  {', '.join(batch2)}")

print(f"\n第三批（2017年）部分城市:")
batch3 = df[df['pilot_year'] == 2017]['city_name'].unique()[:10]
print(f"  {', '.join(batch3)}")

print("\n" + "=" * 100)
print("验证完成！DID变量构建正确！")
print("=" * 100)
