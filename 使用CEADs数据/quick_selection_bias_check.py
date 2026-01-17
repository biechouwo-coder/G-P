"""
快速检查CEADs样本选择偏差
"""
import pandas as pd
import numpy as np
from scipy import stats

print("=" * 80)
print("CEADs样本选择偏差快速分析")
print("=" * 80)

# 读取数据
df_main = pd.read_excel('../总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')
df_main = df_main[(df_main['year'] >= 2007) & (df_main['year'] <= 2019)].copy()

df_ceads = pd.read_excel('CEADs_最终数据集_2007-2019_V2.xlsx')

# 统计城市
main_cities = set(df_main['city_name'].unique())
ceads_cities = set(df_ceads[df_ceads['emission_million_tons'].notna()]['city_name'].unique())
unmatched_cities = main_cities - ceads_cities

print(f"\n1. 基本统计:")
print(f"   主数据集城市数: {len(main_cities)}")
print(f"   CEADs匹配城市数: {len(ceads_cities)}")
print(f"   未匹配城市数: {len(unmatched_cities)}")
print(f"   匹配率: {len(ceads_cities)/len(main_cities)*100:.2f}%")

# 处理组/对照组分布
df_main_sample = df_main.groupby('city_name').first().reset_index()
treat_all = df_main_sample[df_main_sample['treat'] == 1]['city_name'].nunique()
control_all = df_main_sample[df_main_sample['treat'] == 0]['city_name'].nunique()

treat_ceads = df_main_sample[df_main_sample['city_name'].isin(ceads_cities) & (df_main_sample['treat'] == 1)]['city_name'].nunique()
control_ceads = df_main_sample[df_main_sample['city_name'].isin(ceads_cities) & (df_main_sample['treat'] == 0)]['city_name'].nunique()

print(f"\n2. 处理组/对照组分布:")
print(f"   处理组匹配率: {treat_ceads}/{treat_all} = {treat_ceads/treat_all*100:.1f}%")
print(f"   对照组匹配率: {control_ceads}/{control_all} = {control_ceads/control_all*100:.1f}%")

# 经济特征对比
df_unmatched = df_main[df_main['city_name'].isin(unmatched_cities)]
df_matched = df_main[df_main['city_name'].isin(ceads_cities)]

unmatched_ln_pgdp = df_unmatched.groupby('city_name')['ln_pgdp'].mean()
matched_ln_pgdp = df_matched.groupby('city_name')['ln_pgdp'].mean()

print(f"\n3. 经济特征对比 (对数人均GDP):")
print(f"   未匹配城市均值: {unmatched_ln_pgdp.mean():.4f}")
print(f"   已匹配城市均值: {matched_ln_pgdp.mean():.4f}")
print(f"   差异: {matched_ln_pgdp.mean() - unmatched_ln_pgdp.mean():.4f}")

t_stat, p_value = stats.ttest_ind(matched_ln_pgdp.dropna(), unmatched_ln_pgdp.dropna())
sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.1 else ""
print(f"   t检验: t={t_stat:.3f}, p={p_value:.4f} {sig}")

if p_value < 0.05:
    print(f"   [WARNING] 存在显著差异，可能有样本选择偏差!")
else:
    print(f"   [OK] 差异不显著，样本选择偏差较小")

# 未匹配城市列表
print(f"\n4. 未匹配城市列表 (共{len(unmatched_cities)}个):")
unmatched_list = sorted(list(unmatched_cities))
for i, city in enumerate(unmatched_list, 1):
    print(f"   {i:2d}. {city}")

# 按省份统计
df_unmatched_sample = df_unmatched.groupby('city_name').first().reset_index()
if 'city_name' in df_unmatched_sample.columns:
    df_unmatched_sample['province'] = df_unmatched_sample['city_name'].str[:-1]
    province_counts = df_unmatched_sample['province'].value_counts().sort_values(ascending=False)

    print(f"\n5. 未匹配城市最多的省份:")
    for province, count in province_counts.head(10).items():
        print(f"   {province}: {count}个城市")

print("\n" + "=" * 80)
print("结论:")
print("=" * 80)
print("请根据以上结果评估:")
print("1. 处理组和对照组的匹配率是否相近")
print("2. 未匹配城市的经济特征是否与已匹配城市有显著差异")
print("3. 未匹配城市是否集中在某些特定省份")
print("=" * 80)
