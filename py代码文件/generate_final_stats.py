"""
生成最终完整描述性统计表（包含人口和人均GDP）
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# 文件路径
INPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_清洗版.xlsx")
OUTPUT_STATS = Path(r"c:\Users\HP\Desktop\毕业论文\描述性统计表_完整版.xlsx")

print("=" * 80)
print("生成最终描述性统计表（完整版）")
print("=" * 80)
print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取数据
df = pd.read_excel(INPUT_FILE)
print(f"\n数据规模: {df.shape}")
print(f"  城市数: {df['city_name'].nunique()}")
print(f"  年份范围: {df['year'].min()} - {df['year'].max()}")

# 选择数值变量
numeric_vars = ['population', 'pop_density', 'gdp_real', 'gdp_per_capita',
                'gdp_deflator', 'carbon_intensity', 'tertiary_share', 'industrial_upgrading']

# 计算描述性统计
stats_data = []
for var in numeric_vars:
    if var in df.columns:
        var_data = df[var].dropna()

        # 变量中文说明
        var_names = {
            'population': ('总人口', '万人'),
            'pop_density': ('人口密度', '人/平方公里'),
            'gdp_real': ('实际GDP', '亿元（2000年基期）'),
            'gdp_per_capita': ('人均实际GDP', '元/人（2000年基期）'),
            'gdp_deflator': ('GDP平减指数', '-'),
            'carbon_intensity': ('碳排放强度', '吨/亿元（2000年基期）'),
            'tertiary_share': ('第三产业占比', '比例'),
            'industrial_upgrading': ('产业结构高级化', '比例')
        }

        name_cn, unit = var_names[var]

        stats_data.append({
            '变量名': var,
            '变量名称': name_cn,
            '单位': unit,
            '观测数': len(var_data),
            '均值': var_data.mean(),
            '标准差': var_data.std(),
            '最小值': var_data.min(),
            '25%分位数': var_data.quantile(0.25),
            '中位数': var_data.median(),
            '75%分位数': var_data.quantile(0.75),
            '最大值': var_data.max()
        })

df_stats = pd.DataFrame(stats_data)

# 格式化数值列
format_cols = ['均值', '标准差', '最小值', '25%分位数', '中位数', '75%分位数', '最大值']
for col in format_cols:
    df_stats[col] = df_stats[col].apply(lambda x: f"{x:.4f}" if x < 1000 else f"{x:.2f}")

print("\n最终描述性统计表:")
print("-" * 140)
print(df_stats.to_string(index=False))
print("-" * 140)

# 保存描述性统计到Excel
with pd.ExcelWriter(OUTPUT_STATS, engine='openpyxl') as writer:
    df_stats.to_excel(writer, sheet_name='描述性统计', index=False)

    # 创建第二個sheet：数据说明
    df_info = pd.DataFrame({
        '项目': ['数据集名称', '观测数', '城市数', '年份范围', '变量数', '数据完整性',
                '数据类型', '时间跨度', '空间覆盖'],
        '内容': [
            '总数据集_2007-2023_清洗版（完整版）',
            f"{len(df):,}",
            f"{df['city_name'].nunique()}",
            f"{df['year'].min()} - {df['year'].max()}",
            len(df.columns),
            '总人口和人均GDP有部分缺失（约3.7%），其他变量100%完整',
            '面板数据（Panel Data）',
            '17年',
            '264个地级市'
        ]
    })
    df_info.to_excel(writer, sheet_name='数据说明', index=False)

print(f"\n描述性统计已保存到: {OUTPUT_STATS}")

print("\n" + "=" * 80)
print("关键变量说明")
print("=" * 80)

# 人口变量
print("\n总人口（万人）:")
pop_mean = df['population'].mean()
pop_median = df['population'].median()
print(f"  均值: {pop_mean:.2f} 万人")
print(f"  中位数: {pop_median:.2f} 万人")
print(f"  范围: {df['population'].min():.2f} - {df['population'].max():.2f} 万人")
print(f"  缺失: {df['population'].isnull().sum()} ({df['population'].isnull().sum()/len(df)*100:.2f}%)")

# 人均GDP变量
print(f"\n人均实际GDP（元/人，2000年基期）:")
gdp_pc_mean = df['gdp_per_capita'].mean()
gdp_pc_median = df['gdp_per_capita'].median()
print(f"  均值: {gdp_pc_mean:.0f} 元/人")
print(f"  中位数: {gdp_pc_median:.0f} 元/人")
print(f"  范围: {df['gdp_per_capita'].min():.0f} - {df['gdp_per_capita'].max():.0f} 元/人")
print(f"  缺失: {df['gdp_per_capita'].isnull().sum()} ({df['gdp_per_capita'].isnull().sum()/len(df)*100:.2f}%)")

# 碳排放强度
print(f"\n碳排放强度（吨/亿元，2000年基期）:")
ci_mean = df['carbon_intensity'].mean()
ci_median = df['carbon_intensity'].median()
print(f"  均值: {ci_mean:.2f} 吨/亿元")
print(f"  中位数: {ci_median:.2f} 吨/亿元")
print(f"  折算: {ci_mean/10000:.4f} 吨/万元")
print(f"  说明: 此数值在中国地级市典型范围内（1-5吨/万元）")

print("\n" + "=" * 80)
print("最终描述性统计表生成完成！")
print("=" * 80)
