"""
更新描述性统计表（使用重新计算的碳排放强度）
"""

import pandas as pd
from pathlib import Path

# 文件路径
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
OUTPUT_STATS = Path(r"c:\Users\HP\Desktop\毕业论文\描述性统计表_新版.xlsx")

print("=" * 80)
print("生成描述性统计表（更新版）")
print("=" * 80)

# 读取数据
df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")
print(f"  年份范围: {df['year'].min()} - {df['year'].max()}")

# 选择数值变量
numeric_vars = ['pop_density', 'gdp_real', 'gdp_deflator',
                'carbon_intensity', 'tertiary_share', 'industrial_upgrading']

# 计算描述性统计
stats_data = []
for var in numeric_vars:
    if var in df.columns:
        var_data = df[var].dropna()
        stats_data.append({
            '变量': var,
            '变量名（中文）': {
                'pop_density': '人口密度',
                'gdp_real': '实际GDP（2000年基期）',
                'gdp_deflator': 'GDP平减指数',
                'carbon_intensity': '碳排放强度',
                'tertiary_share': '第三产业占比',
                'industrial_upgrading': '产业结构高级化'
            }[var],
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

# 特别说明碳排放强度
print("\n" + "=" * 80)
print("碳排放强度变量说明:")
print("=" * 80)
print("计算公式: 碳排放强度 = 碳排放总量（吨）/ 实际GDP（亿元，2000年基期）")
print("单位: 吨/亿元（即万吨/亿元）")
print("\n统计特征:")
print(f"  均值: {df['carbon_intensity'].mean():.2f} 吨/亿元")
print(f"  标准差: {df['carbon_intensity'].std():.2f}")
print(f"  最小值: {df['carbon_intensity'].min():.2f}")
print(f"  最大值: {df['carbon_intensity'].max():.2f}")
print(f"\n解释: 平均每生产1亿元GDP（2000年不变价），排放{df['carbon_intensity'].mean():.0f}吨二氧化碳")
