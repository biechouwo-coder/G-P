"""
诊断数据异常问题
1. GDP平减指数异常值（<1）
2. 人口与人均GDP缺失值分析
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("数据异常诊断报告")
print("=" * 80)
print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取数据
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
df = pd.read_excel(INPUT_FILE)

print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")
print(f"  年份范围: {df['year'].min()} - {df['year'].max()}")

# ============ 问题1: GDP平减指数异常值 ============
print("\n" + "=" * 80)
print("问题1: GDP平减指数（gdp_deflator）异常值检查")
print("=" * 80)

gdp_deflator = df['gdp_deflator']
print(f"\nGDP平减指数统计:")
print(f"  均值: {gdp_deflator.mean():.4f}")
print(f"  中位数: {gdp_deflator.median():.4f}")
print(f"  标准差: {gdp_deflator.std():.4f}")
print(f"  最小值: {gdp_deflator.min():.4f} [WARNING]")
print(f"  最大值: {gdp_deflator.max():.4f}")

# 找出GDP平减指数<1的观测
gdp_deflator_low = df[df['gdp_deflator'] < 1.0]
print(f"\nGDP平减指数 < 1.0 的观测数: {len(gdp_deflator_low)} ({len(gdp_deflator_low)/len(df)*100:.2f}%)")

if len(gdp_deflator_low) > 0:
    print("\nGDP平减指数 < 1.0 的城市列表:")
    print("-" * 100)
    gdp_deflator_low_sorted = gdp_deflator_low.sort_values('gdp_deflator').head(20)

    for idx, row in gdp_deflator_low_sorted.iterrows():
        print(f"  {row['city_name']:12s} | {row['year']:4d} | gdp_deflator={row['gdp_deflator']:.4f} | "
              f"gdp_real={row['gdp_real']:.2f}亿元")

    # 统计哪些城市有问题
    cities_with_low_deflator = gdp_deflator_low['city_name'].unique()
    print(f"\n涉及城市数量: {len(cities_with_low_deflator)}")
    print(f"城市列表: {', '.join(cities_with_low_deflator[:10])}{'...' if len(cities_with_low_deflator) > 10 else ''}")

    # 时间分布
    print("\n按年份分布:")
    year_dist = gdp_deflator_low.groupby('year').size()
    for year, count in year_dist.items():
        print(f"  {year}年: {count}个观测")

# ============ 问题2: 人口与人均GDP缺失值 ============
print("\n" + "=" * 80)
print("问题2: 人口与人均GDP缺失值分析")
print("=" * 80)

# 检查缺失值
population_missing = df['population'].isna().sum()
gdp_per_capita_missing = df['gdp_per_capita'].isna().sum()

print(f"\n缺失值统计:")
print(f"  population (总人口): {population_missing} ({population_missing/len(df)*100:.2f}%)")
print(f"  gdp_per_capita (人均GDP): {gdp_per_capita_missing} ({gdp_per_capita_missing/len(df)*100:.2f}%)")

# 找出哪些城市有人口缺失
cities_missing_pop = df[df['population'].isna()]['city_name'].unique()
print(f"\n有人口缺失的城市数量: {len(cities_missing_pop)}")
print(f"占比: {len(cities_missing_pop)/df['city_name'].nunique()*100:.2f}%")

if len(cities_missing_pop) > 0:
    print(f"\n前20个有人口缺失的城市:")
    print("-" * 80)

    # 统计每个城市缺失的年份数
    missing_by_city = df[df['population'].isna()].groupby('city_name').size().sort_values(ascending=False)

    for city, count in missing_by_city.head(20).items():
        city_data = df[df['city_name'] == city]
        total_years = len(city_data)
        missing_years = city_data[city_data['population'].isna()]['year'].tolist()
        print(f"  {city:12s} | 缺失{count}年/共{total_years}年 | 缺失年份: {missing_years[:5]}{'...' if len(missing_years) > 5 else ''}")

    # 分析是否是首尾年份缺失
    print("\n缺失年份分布特征:")
    endpoint_missing = df[(df['population'].isna()) & ((df['year'] == 2007) | (df['year'] == 2023))]
    print(f"  首尾年份（2007或2023）缺失: {len(endpoint_missing)}个观测")

    middle_missing = df[(df['population'].isna()) & (df['year'] > 2007) & (df['year'] < 2023)]
    print(f"  中间年份缺失: {len(middle_missing)}个观测")

# ============ 问题3: 核心变量缺失情况 ============
print("\n" + "=" * 80)
print("问题3: 核心变量完整性检查")
print("=" * 80)

core_vars = ['pop_density', 'gdp_real', 'gdp_deflator', 'carbon_intensity',
             'tertiary_share', 'industrial_upgrading', 'population', 'gdp_per_capita']

print("\n所有变量缺失情况:")
for var in core_vars:
    if var in df.columns:
        missing = df[var].isna().sum()
        missing_rate = missing / len(df) * 100
        status = "[OK]" if missing == 0 else "[WARNING]"
        print(f"  {status} {var:25s}: {missing:5d} ({missing_rate:5.2f}%)")

# ============ 建议措施 ============
print("\n" + "=" * 80)
print("诊断结论与建议")
print("=" * 80)

recommendations = []

# GDP平减指数建议
if len(gdp_deflator_low) > 0:
    recommendations.append({
        '问题': 'GDP平减指数异常值',
        '严重程度': '高',
        '建议': [
            f"发现{len(gdp_deflator_low)}个观测的GDP平减指数<1",
            f"涉及{len(cities_with_low_deflator)}个城市",
            "建议：检查这些城市的原始数据，确认基期是否一致",
            "如果仅少数城市有问题，可考虑剔除这些城市",
            "如果多数城市有问题，需要重新计算平减指数"
        ]
    })

# 人口缺失建议
if population_missing > 0:
    recommendations.append({
        '问题': '人口数据缺失',
        '严重程度': '中' if population_missing/len(df) < 0.05 else '高',
        '建议': [
            f"发现{population_missing}个观测缺失（{population_missing/len(df)*100:.2f}%）",
            f"涉及{len(cities_missing_pop)}个城市",
            "选项1：对缺失值进行线性插值（推荐，如果仅中间年份缺失）",
            "选项2：剔除有人口缺失的城市（会减少样本量）",
            "选项3：在模型中不使用人均GDP，仅用gdp_real控制经济水平"
        ]
    })

for i, rec in enumerate(recommendations, 1):
    print(f"\n【问题{i}】{rec['问题']} ({rec['严重程度']}严重)")
    print("-" * 80)
    for j, suggestion in enumerate(rec['建议'], 1):
        print(f"  {j}. {suggestion}")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)

# 保存详细诊断结果到文件
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\数据诊断报告.txt")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"数据异常诊断报告\n")
    f.write(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")

    if len(gdp_deflator_low) > 0:
        f.write("【问题1】GDP平减指数异常值\n")
        f.write(f"  异常观测数: {len(gdp_deflator_low)} ({len(gdp_deflator_low)/len(df)*100:.2f}%)\n")
        f.write(f"  涉及城市: {len(cities_with_low_deflator)}个\n")
        f.write(f"  城市列表: {', '.join(cities_with_low_deflator)}\n\n")

    if population_missing > 0:
        f.write("【问题2】人口数据缺失\n")
        f.write(f"  缺失观测数: {population_missing} ({population_missing/len(df)*100:.2f}%)\n")
        f.write(f"  涉及城市: {len(cities_missing_pop)}个\n")
        f.write(f"  城市列表: {', '.join(cities_missing_pop[:20])}\n\n")

print(f"\n详细诊断报告已保存到: {OUTPUT_FILE}")
