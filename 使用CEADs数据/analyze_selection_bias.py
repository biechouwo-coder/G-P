"""
分析CEADs数据匹配的样本选择偏差
检查未匹配城市是否有系统性特征
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("样本选择偏差分析")
print("=" * 80)

# 读取主数据集
df_main = pd.read_excel('../总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')

# 截取2007-2019年
df_main = df_main[(df_main['year'] >= 2007) & (df_main['year'] <= 2019)].copy()

# 读取CEADs最终数据集
df_ceads = pd.read_excel('CEADs_最终数据集_2007-2019_V2.xlsx')

# 统计主数据集中的城市
main_cities = df_main['city_name'].unique()
print(f"\n主数据集城市数（2007-2019）: {len(main_cities)}")

# 统计CEADs中成功匹配的城市
ceads_cities = df_ceads[df_ceads['emission_million_tons'].notna()]['city_name'].unique()
print(f"CEADs匹配城市数: {len(ceads_cities)}")

# 找出未匹配的城市
unmatched_cities = set(main_cities) - set(ceads_cities)
print(f"未匹配城市数: {len(unmatched_cities)}")

# 提取未匹配城市的观测
df_unmatched = df_main[df_main['city_name'].isin(unmatched_cities)].copy()
df_matched = df_main[df_main['city_name'].isin(ceads_cities)].copy()

print("\n" + "=" * 80)
print("1. 处理组/对照组分布")
print("=" * 80)

# 处理组分布
treat_unmatched = df_unmatched[df_unmatched['treat_post'] == 1]['city_name'].nunique()
control_unmatched = df_unmatched[df_unmatched['treat_post'] == 0]['city_name'].nunique()

treat_matched = df_matched[df_matched['treat_post'] == 1]['city_name'].nunique()
control_matched = df_matched[df_matched['treat_post'] == 0]['city_name'].nunique()

print(f"\n未匹配城市:")
print(f"  处理组城市数: {treat_unmatched}")
print(f"  对照组城市数: {control_unmatched}")

print(f"\n已匹配城市:")
print(f"  处理组城市数: {treat_matched}")
print(f"  对照组城市数: {control_matched}")

# 计算比例
print(f"\n匹配率:")
print(f"  处理组匹配率: {treat_matched}/{treat_matched + treat_unmatched} = {treat_matched/(treat_matched + treat_unmatched)*100:.2f}%")
print(f"  对照组匹配率: {control_matched}/{control_matched + control_unmatched} = {control_matched/(control_matched + control_unmatched)*100:.2f}%")

print("\n" + "=" * 80)
print("2. 未匹配城市名单（按省份分组）")
print("=" * 80)

# 提取省份信息
df_unmatched_sample = df_unmatched.groupby('city_name').first().reset_index()
df_unmatched_sample['province'] = df_unmatched_sample['city_name'].str[:-1]

# 按省份统计
province_counts = df_unmatched_sample['province'].value_counts().sort_values(ascending=False)
print("\n未匹配城市最多的省份:")
print(province_counts.head(15))

print("\n所有未匹配城市:")
unmatched_list = sorted(df_unmatched_sample['city_name'].unique())
for i, city in enumerate(unmatched_list, 1):
    print(f"  {i}. {city}")

print("\n" + "=" * 80)
print("3. 经济特征对比（对数人均GDP）")
print("=" * 80)

# 对比两组的经济特征
unmatched_pgdp = df_unmatched.groupby('city_name')['ln_pgdp'].mean()
matched_pgdp = df_matched.groupby('city_name')['ln_pgdp').mean()

print(f"\n对数人均GDP（均值）:")
print(f"  未匹配城市: {unmatched_pgdp.mean():.4f}")
print(f"  已匹配城市: {matched_pgdp.mean():.4f}")
print(f"  差异: {matched_pgdp.mean() - unmatched_pgdp.mean():.4f}")

# t检验
from scipy import stats
t_stat, p_value = stats.ttest_ind(matched_pgdp.dropna(), unmatched_pgdp.dropna())
print(f"\n差异显著性检验:")
print(f"  t统计量: {t_stat:.4f}")
print(f"  p值: {p_value:.4f}")
if p_value < 0.05:
    print(f"  结论: 差异显著（p<0.05），存在样本选择偏差")
else:
    print(f"  结论: 差异不显著（p>0.05），样本选择偏差较小")

print("\n" + "=" * 80)
print("4. 其他控制变量对比")
print("=" * 80)

variables = ['ln_pop_density', 'ln_fdi', 'ln_road_area_per_capita', 'fin_development']
var_names = ['对数人口密度', '对数FDI', '对数人均道路面积', '金融发展水平']

for var, name in zip(variables, var_names):
    if var in df_unmatched.columns:
        unmatched_mean = df_unmatched.groupby('city_name')[var].mean().mean()
        matched_mean = df_matched.groupby('city_name')[var].mean().mean()

        t_stat, p_value = stats.ttest_ind(
            df_matched.groupby('city_name')[var].mean().dropna(),
            df_unmatched.groupby('city_name')[var].mean().dropna()
        )

        significance = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.1 else ""

        print(f"\n{name}:")
        print(f"  未匹配: {unmatched_mean:.4f}")
        print(f"  已匹配: {matched_mean:.4f}")
        print(f"  差异: {matched_mean - unmatched_mean:.4f} {significance}")

print("\n" + "=" * 80)
print("5. 年份分布")
print("=" * 80)

year_unmatched = df_unmatched.groupby('year')['city_name'].nunique()
year_matched = df_matched.groupby('year')['city_name'].nunique()

print("\n每年未匹配城市数:")
for year in sorted(df_main['year'].unique()):
    n_unmatched = year_unmatched.get(year, 0)
    n_matched = year_matched.get(year, 0)
    total = n_unmatched + n_matched
    print(f"  {year}: {n_unmatched} 个未匹配 ({n_unmatched/total*100:.1f}%)")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)

print("""
样本选择偏差评估：
1. 如果处理组和对照组的匹配率相近 → 选择偏差较小
2. 如果未匹配城市的经济特征与已匹配城市无显著差异 → 选择偏差较小
3. 如果未匹配城市主要是某些特定省份 → 需要在文中说明地理覆盖限制
""")

# 保存结果
output_file = '样本选择偏差分析结果.xlsx'
with pd.ExcelWriter(output_file) as writer:
    # 未匹配城市列表
    df_unmatched_sample[['city_name', 'province']].to_excel(writer, sheet_name='未匹配城市', index=False)

    # 统计汇总
    summary_data = {
        '指标': ['主数据集城市数', 'CEADs匹配城市数', '未匹配城市数',
                '未匹配-处理组', '未匹配-对照组',
                '已匹配-处理组', '已匹配-对照组'],
        '数值': [len(main_cities), len(ceads_cities), len(unmatched_cities),
                treat_unmatched, control_unmatched, treat_matched, control_matched]
    }
    pd.DataFrame(summary_data).to_excel(writer, sheet_name='统计汇总', index=False)

print(f"\n[OK] 分析结果已保存: {output_file}")
