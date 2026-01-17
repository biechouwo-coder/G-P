"""
第五步：生成描述性统计报告
"""
import pandas as pd
import numpy as np

print("=" * 80)
print("CEADs数据集描述性统计报告")
print("=" * 80)

# 读取数据
df = pd.read_excel('CEADs_最终数据集_2007-2019.xlsx')

# 1. 数据集基本信息
print("\n【一、数据集基本信息】")
print("-" * 80)

# 总观测数
total_obs = len(df)
print(f"总观测数: {total_obs}")

# 有CEADs碳排放数据的观测数
ceads_valid = df['carbon_intensity_ceads_winsor'].notnull().sum()
print(f"有CEADs碳排放数据的观测数: {ceads_valid} ({ceads_valid/total_obs*100:.2f}%)")

# 年份范围
print(f"年份范围: {df['year'].min()} - {df['year'].max()}")

# 城市数量
total_cities = df['city_name'].nunique()
ceads_cities = df[df['carbon_intensity_ceads_winsor'].notnull()]['city_name'].nunique()
print(f"总城市数: {total_cities}")
print(f"有CEADs数据的城市数: {ceads_cities} ({ceads_cities/total_cities*100:.2f}%)")

# 2. 核心变量描述性统计
print("\n【二、核心变量描述性统计】")
print("-" * 80)

core_vars = ['carbon_intensity_ceads_winsor', 'ln_carbon_intensity_ceads',
             'emission_million_tons', 'real_gdp_100m_yuan',
             'ln_pgdp', 'ln_pop_density', 'pop_density',
             'tertiary_share', 'industrial_advanced',
             'fdi_openness', 'ln_road_area', 'financial_development']

# 为有CEADs数据的子集计算统计量
df_ceads = df[df['carbon_intensity_ceads_winsor'].notnull()].copy()

stats_data = []
for var in core_vars:
    if var in df_ceads.columns:
        var_data = df_ceads[var].dropna()
        stats_data.append({
            '变量': var,
            '观测数': len(var_data),
            '均值': f"{var_data.mean():.4f}",
            '标准差': f"{var_data.std():.4f}",
            '最小值': f"{var_data.min():.4f}",
            '中位数': f"{var_data.median():.4f}",
            '最大值': f"{var_data.max():.4f}",
            '缺失数': df_ceads[var].isnull().sum(),
            '缺失率': f"{df_ceads[var].isnull().sum()/len(df_ceads)*100:.2f}%"
        })

stats_df = pd.DataFrame(stats_data)
print(stats_df.to_string(index=False))

# 3. 处理组与对照组对比（基于有CEADs数据的样本）
print("\n【三、处理组与对照组均值对比（CEADs样本）】")
print("-" * 80)

comparison_vars = ['ln_carbon_intensity_ceads', 'ln_pgdp', 'ln_pop_density',
                   'industrial_advanced', 'fdi_openness', 'ln_road_area', 'financial_development']

comparison_data = []
for var in comparison_vars:
    if var in df_ceads.columns:
        treat_mean = df_ceads[df_ceads['treat'] == 1][var].mean()
        control_mean = df_ceads[df_ceads['treat'] == 0][var].mean()
        diff = treat_mean - control_mean
        diff_pct = (diff / control_mean) * 100 if control_mean != 0 else 0

        comparison_data.append({
            '变量': var,
            '处理组均值': f"{treat_mean:.4f}",
            '对照组均值': f"{control_mean:.4f}",
            '差异': f"{diff:.4f}",
            '差异(%)': f"{diff_pct:.2f}%"
        })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

# 4. 年份分布
print("\n【四、各年份观测数分布（CEADs样本）】")
print("-" * 80)
year_counts = df_ceads['year'].value_counts().sort_index()
for year, count in year_counts.items():
    print(f"{year}: {count} 个观测")

# 5. 碳排放强度分位数
print("\n【五、碳排放强度分位数分布（CEADs样本）】")
print("-" * 80)
ci_quantiles = df_ceads['carbon_intensity_ceads_winsor'].quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
print("分位数          值（吨/万元）")
for q, val in ci_quantiles.items():
    print(f"{q*100:.0f}%        {val:.4f}")

# 6. 省份分布（如果能提取的话）
print("\n【六、数据质量检查】")
print("-" * 80)
print("各变量缺失情况（CEADs样本）:")
missing_stats = df_ceads.isnull().sum()
missing_stats = missing_stats[missing_stats > 0].sort_values(ascending=False)
if len(missing_stats) > 0:
    for var, count in missing_stats.items():
        print(f"  {var}: {count} ({count/len(df_ceads)*100:.2f}%)")
else:
    print("  [OK] 所有核心变量均无缺失值")

# 7. 导出详细统计表
print("\n【七、导出描述性统计表】")
print("-" * 80)

# 创建详细的描述性统计表（按处理组分组）
descriptive_table = []
for var in core_vars:
    if var in df_ceads.columns:
        # 全样本
        all_mean = df_ceads[var].mean()
        all_std = df_ceads[var].std()

        # 处理组
        treat_data = df_ceads[df_ceads['treat'] == 1][var].dropna()
        treat_mean = treat_data.mean() if len(treat_data) > 0 else np.nan
        treat_std = treat_data.std() if len(treat_data) > 0 else np.nan

        # 对照组
        control_data = df_ceads[df_ceads['treat'] == 0][var].dropna()
        control_mean = control_data.mean() if len(control_data) > 0 else np.nan
        control_std = control_data.std() if len(control_data) > 0 else np.nan

        descriptive_table.append({
            '变量': var,
            '全样本均值': all_mean,
            '全样本标准差': all_std,
            '处理组均值': treat_mean,
            '处理组标准差': treat_std,
            '对照组均值': control_mean,
            '对照组标准差': control_std
        })

descriptive_df = pd.DataFrame(descriptive_table)
output_file = 'CEADs_描述性统计表.xlsx'
descriptive_df.to_excel(output_file, index=False)
print(f"[OK] 详细统计表已保存至: {output_file}")

# 8. 生成核心发现总结
print("\n" + "=" * 80)
print("核心发现总结")
print("=" * 80)

print(f"\n1. 数据覆盖情况:")
print(f"   - 总观测数: {total_obs}")
print(f"   - CEADs有效观测数: {ceads_valid} ({ceads_valid/total_obs*100:.1f}%)")
print(f"   - 涉及城市数: {ceads_cities}/{total_cities} ({ceads_cities/total_cities*100:.1f}%)")

print(f"\n2. 碳排放强度水平:")
print(f"   - 均值: {df_ceads['carbon_intensity_ceads_winsor'].mean():.2f} 吨/万元")
print(f"   - 中位数: {df_ceads['carbon_intensity_ceads_winsor'].median():.2f} 吨/万元")
print(f"   - 标准差: {df_ceads['carbon_intensity_ceads_winsor'].std():.2f} 吨/万元")

print(f"\n3. 处理组与对照组差异:")
if 'ln_carbon_intensity_ceads' in df_ceads.columns:
    treat_ci = df_ceads[df_ceads['treat'] == 1]['ln_carbon_intensity_ceads'].mean()
    control_ci = df_ceads[df_ceads['treat'] == 0]['ln_carbon_intensity_ceads'].mean()
    print(f"   - 对数碳排放强度: 处理组{treat_ci:.4f} vs 对照组{control_ci:.4f}")
    print(f"   - 差异: {treat_ci - control_ci:.4f} ({(treat_ci/control_ci - 1)*100:.2f}%)")

print("\n" + "=" * 80)
print("描述性统计完成！")
print("=" * 80)
