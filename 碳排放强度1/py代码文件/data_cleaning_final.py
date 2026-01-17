"""
数据清洗脚本 - 最终版
任务：
1. 筛选2007-2023年均为地级市且无行政区划变更的城市
2. 缺失值线性插值（剔除连续缺失>3年或首尾缺失的城市）
3. 生成变量描述性统计三线表
"""

import pandas as pd
import numpy as np
from pathlib import Path

# 文件路径
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版.xlsx")
OUTPUT_CLEAN = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
OUTPUT_STATS = Path(r"c:\Users\HP\Desktop\毕业论文\描述性统计表.xlsx")

print("=" * 80)
print("数据清洗程序启动")
print("=" * 80)

# 读取数据
print("\n[步骤1/4] 读取数据...")
df = pd.read_excel(INPUT_FILE)
print(f"原始数据: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")
print(f"  年份范围: {df['year'].min()} - {df['year'].max()}")

# ============================================
# 步骤1：筛选连续17年的城市（无行政区划变更）
# ============================================
print("\n" + "=" * 80)
print("[步骤2/4] 筛选2007-2023年连续观测的城市...")

# 统计每个城市的观测数
city_obs = df.groupby('city_name').size()
cities_full = city_obs[city_obs == 17].index.tolist()  # 2007-2023共17年

print(f"\n完整观测17年的城市数: {len(cities_full)}")
print(f"存在缺失年份的城市数: {len(city_obs) - len(cities_full)}")

# 列出有缺失的城市
if len(city_obs) > len(cities_full):
    cities_incomplete = city_obs[city_obs < 17].index.tolist()
    print(f"\n存在年份缺失的城市（前20个）: {cities_incomplete[:20]}")

# 筛选完整城市
df_clean = df[df['city_name'].isin(cities_full)].copy()
print(f"\n筛选后数据: {df_clean.shape}")
print(f"  城市数: {df_clean['city_name'].nunique()}")

# ============================================
# 步骤2：缺失值处理
# ============================================
print("\n" + "=" * 80)
print("[步骤3/4] 处理缺失值...")

# 检查各变量缺失情况
print("\n当前缺失值统计:")
missing_stats = []
for col in df_clean.columns:
    if col not in ['year', 'city_name', 'city_code']:
        missing_count = df_clean[col].isnull().sum()
        if missing_count > 0:
            missing_pct = missing_count / len(df_clean) * 100
            print(f"  {col}: {missing_count} ({missing_pct:.2f}%)")
            missing_stats.append({
                'variable': col,
                'missing_count': missing_count,
                'missing_pct': missing_pct
            })

# 按城市检查连续缺失情况
print("\n检查各城市连续缺失情况...")
cities_to_remove = []

for city in cities_full:
    city_data = df_clean[df_clean['city_name'] == city].sort_values('year')

    # 检查每个变量
    for col in ['gdp_real', 'gdp_deflator', 'carbon_intensity', 'tertiary_share', 'industrial_upgrading']:
        if col in city_data.columns:
            # 找出缺失值的年份
            missing_years = city_data[city_data[col].isnull()]['year'].tolist()

            if len(missing_years) > 0:
                # 检查是否连续缺失超过3年
                missing_years_sorted = sorted(missing_years)
                max_consecutive = 1
                current_consecutive = 1

                for i in range(1, len(missing_years_sorted)):
                    if missing_years_sorted[i] == missing_years_sorted[i-1] + 1:
                        current_consecutive += 1
                        max_consecutive = max(max_consecutive, current_consecutive)
                    else:
                        current_consecutive = 1

                # 检查首尾年份是否缺失
                has_start_missing = 2007 in missing_years
                has_end_missing = 2023 in missing_years

                if max_consecutive > 3 or has_start_missing or has_end_missing:
                    if city not in cities_to_remove:
                        cities_to_remove.append(city)
                        print(f"  剔除城市 {city}: {col}连续缺失{max_consecutive}年, " +
                              f"首尾缺失={has_start_missing or has_end_missing}")
                    break

print(f"\n需要剔除的城市数: {len(cities_to_remove)}")

# 剔除问题城市
df_clean = df_clean[~df_clean['city_name'].isin(cities_to_remove)].copy()
print(f"剔除后数据: {df_clean.shape}")
print(f"  最终城市数: {df_clean['city_name'].nunique()}")

# 对剩余城市进行线性插值
print("\n对剩余数据进行线性插值...")
df_clean = df_clean.sort_values(['city_name', 'year'])

# 对每个城市分别插值
for city in df_clean['city_name'].unique():
    city_mask = df_clean['city_name'] == city
    for col in ['gdp_real', 'gdp_deflator', 'carbon_intensity', 'tertiary_share', 'industrial_upgrading']:
        if col in df_clean.columns:
            df_clean.loc[city_mask, col] = df_clean.loc[city_mask, col].interpolate(
                method='linear',
                limit_direction='both'
            )

# 检查插值后缺失情况
print("\n插值后缺失值统计:")
for col in df_clean.columns:
    if col not in ['year', 'city_name', 'city_code']:
        missing_count = df_clean[col].isnull().sum()
        if missing_count > 0:
            missing_pct = missing_count / len(df_clean) * 100
            print(f"  {col}: {missing_count} ({missing_pct:.2f}%)")

# ============================================
# 步骤3：生成描述性统计三线表
# ============================================
print("\n" + "=" * 80)
print("[步骤4/4] 生成描述性统计表...")

# 选择数值变量
numeric_vars = ['pop_density', 'gdp_real', 'gdp_deflator',
                'carbon_intensity', 'tertiary_share', 'industrial_upgrading']

# 计算描述性统计
stats_data = []
for var in numeric_vars:
    if var in df_clean.columns:
        var_data = df_clean[var].dropna()
        stats_data.append({
            '变量': var,
            '观测数': len(var_data),
            '均值': f"{var_data.mean():.4f}",
            '标准差': f"{var_data.std():.4f}",
            '最小值': f"{var_data.min():.4f}",
            '最大值': f"{var_data.max():.4f}"
        })

df_stats = pd.DataFrame(stats_data)

print("\n描述性统计:")
print(df_stats.to_string(index=False))

# 保存描述性统计到Excel
with pd.ExcelWriter(OUTPUT_STATS, engine='openpyxl') as writer:
    df_stats.to_excel(writer, sheet_name='描述性统计', index=False)

print(f"\n描述性统计已保存到: {OUTPUT_STATS}")

# ============================================
# 保存清洗后的数据
# ============================================
print("\n" + "=" * 80)
print("保存清洗后的数据...")

with pd.ExcelWriter(OUTPUT_CLEAN, engine='openpyxl') as writer:
    df_clean.to_excel(writer, sheet_name='清洗后数据', index=False)

print(f"清洗后数据已保存到: {OUTPUT_CLEAN}")
print(f"文件大小: {OUTPUT_CLEAN.stat().st_size / 1024:.1f} KB")

# ============================================
# 最终报告
# ============================================
print("\n" + "=" * 80)
print("数据清洗完成！")
print("=" * 80)
print(f"\n原始数据:")
print(f"  观测数: {len(df)}")
print(f"  城市数: {df['city_name'].nunique()}")

print(f"\n清洗后数据:")
print(f"  观测数: {len(df_clean)}")
print(f"  城市数: {df_clean['city_name'].nunique()}")
print(f"  变量数: {len(df_clean.columns)}")

print(f"\n剔除城市数: {len(cities_to_remove)}")
print(f"剔除率: {len(cities_to_remove) / len(cities_full) * 100:.2f}%")

print("\n输出文件:")
print(f"  1. {OUTPUT_CLEAN}")
print(f"  2. {OUTPUT_STATS}")
