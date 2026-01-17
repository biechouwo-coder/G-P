"""
CEADs数据集倾向得分匹配（PSM）- 缺失值插值版本
使用5个控制变量：人均GDP + 人口集聚程度 + 产业高级化 + 外商投资水平 + 金融发展水平

缺失值处理：线性插值 + 前向/后向填充

匹配策略：
1. 逐年Logit回归估计倾向得分
2. 1:1最近邻匹配，有放回
3. 卡尺：0.02
4. 仅保留政策前的观测用于匹配
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("CEADs数据集倾向得分匹配（PSM）- 缺失值插值版本")
print("=" * 80)
print("\n控制变量：")
print("  1. ln_pgdp - 对数人均GDP")
print("  2. ln_pop_density - 对数人口密度")
print("  3. industrial_advanced - 产业高级化（第三产业/第二产业）")
print("  4. fdi_openness - 外商投资水平（FDI/GDP）")
print("  5. financial_development - 金融发展水平")
print("\n缺失值处理：线性插值 + 前向/后向填充")
print("\n匹配参数：卡径=0.02，有放回，仅使用政策前观测")
print("=" * 80)

# 读取CEADs数据
df = pd.read_excel('CEADs_最终数据集_2007-2019_V2.xlsx')

print(f"\n原始数据集: {df.shape[0]} 行观测")
print(f"年份范围: {df['year'].min()} - {df['year'].max()}")
print(f"城市数量: {df['city_name'].nunique()}")

# 定义协变量（控制变量）
covariates = ['ln_pgdp', 'ln_pop_density', 'industrial_advanced',
              'fdi_openness', 'financial_development']

# 检查缺失值
print("\n各变量缺失值统计（原始数据）:")
vars_to_check = covariates + ['treat', 'ln_carbon_intensity_ceads']
missing_stats = {}
for var in vars_to_check:
    missing = df[var].isnull().sum()
    missing_rate = missing / len(df) * 100
    missing_stats[var] = (missing, missing_rate)
    print(f"  {var}: {missing} 个缺失值 ({missing_rate:.2f}%)")

# 仅保留有效碳排放观测（用于后续回归）
df = df[df['ln_carbon_intensity_ceads'].notna()].copy()
print(f"\n仅保留有效碳排放观测: {df.shape[0]} 行观测")
print(f"涉及城市: {df['city_name'].nunique()} 个")

print("\n" + "=" * 80)
print("缺失值处理：线性插值 + 前向/后向填充")
print("=" * 80)

# 按城市对缺失值进行插值
df_list = []
for city in df['city_name'].unique():
    df_city = df[df['city_name'] == city].copy().sort_values('year')

    # 对协变量进行线性插值
    for var in covariates:
        if var in df_city.columns:
            # 线性插值
            df_city[var] = df_city[var].interpolate(method='linear', limit_direction='both')
            # 前向填充剩余缺失值（针对城市首年）
            df_city[var] = df_city[var].fillna(method='ffill')
            # 后向填充剩余缺失值（针对城市末年）
            df_city[var] = df_city[var].fillna(method='bfill')

    df_list.append(df_city)

df = pd.concat(df_list, axis=0).reset_index(drop=True)

# 再次检查缺失值
print("\n插值后缺失值统计:")
still_missing = {}
for var in covariates + ['treat']:
    missing = df[var].isnull().sum()
    if missing > 0:
        still_missing[var] = missing
        print(f"  {var}: {missing} 个缺失值（无法插值）")

# 如果仍有缺失值，删除这些观测
if still_missing:
    print("\n删除仍有缺失值的观测...")
    df = df.dropna(subset=list(still_missing.keys())).copy()

print(f"\n最终数据集: {df.shape[0]} 行观测")
print(f"城市数: {df['city_name'].nunique()} 个")

# 检查处理组和对照组分布
treat_cities = df[df['treat'] == 1]['city_name'].nunique()
control_cities = df[df['treat'] == 0]['city_name'].nunique()
print(f"\n处理组城市数: {treat_cities}")
print(f"对照组城市数: {control_cities}")

# 仅使用政策前的观测（稳健做法）
df_pre = df[df['post'] == 0].copy()
print(f"\n仅使用政策前观测用于匹配: {df_pre.shape[0]} 行观测")

print("\n" + "=" * 80)
print("第一步：逐年估计倾向得分")
print("=" * 80)

# 为所有观测添加倾向得分列
df['pscore'] = np.nan

years = sorted(df['year'].unique())
pscore_models = {}

for year in years:
    # 提取该年的数据
    df_year = df[df['year'] == year].copy()

    # 提取协变量和处理变量
    X = df_year[covariates].values
    y = df_year['treat'].values

    # 检查是否有足够的处理组和对照组
    if y.sum() < 5 or (len(y) - y.sum()) < 5:
        print(f"\n年份 {year}: 处理组={y.sum()}, 对照组={len(y)-y.sum()}, 样本量不足，跳过")
        continue

    # Logit回归估计倾向得分
    logit_model = LogisticRegression(solver='lbfgs', max_iter=1000)
    logit_model.fit(X, y)
    pscores = logit_model.predict_proba(X)[:, 1]

    # 保存倾向得分
    df.loc[df['year'] == year, 'pscore'] = pscores
    pscore_models[year] = logit_model

    # 输出该年的匹配前统计
    treat_mean = pscores[y == 1].mean()
    control_mean = pscores[y == 0].mean()
    print(f"年份 {year}: 处理组={y.sum()}, 对照组={len(y)-y.sum()}, "
          f"倾向得分 均值: 处理组={treat_mean:.4f}, 对照组={control_mean:.4f}")

print(f"\n倾向得分估计完成，有效观测数: {df['pscore'].notna().sum()}")

print("\n" + "=" * 80)
print("第二步：执行匹配（1:1最近邻，卡径=0.02，有放回）")
print("=" * 80)

class CeadsPSMMatcher:
    """CEADs数据集的倾向得分匹配器"""

    def __init__(self, data, covariates, caliper=0.02):
        """
        参数:
        - data: 包含treat, pscore列的DataFrame
        - covariates: 协变量列表
        - caliper: 卡径范围
        """
        self.data = data.copy()
        self.covariates = covariates
        self.caliper = caliper
        self.matched_pairs = []

    def perform_matching(self):
        """执行匹配"""
        # 分离处理组和对照组
        treat_df = self.data[self.data['treat'] == 1].copy()
        control_df = self.data[self.data['treat'] == 0].copy()

        # 按年份分组匹配
        for year in self.data['year'].unique():
            treat_year = treat_df[treat_df['year'] == year]
            control_year = control_df[control_df['year'] == year]

            if len(treat_year) == 0 or len(control_year) == 0:
                continue

            # 对每个处理组观测找对照组匹配
            for treat_idx, treat_row in treat_year.iterrows():
                treat_pscore = treat_row['pscore']

                # 计算与所有对照组的倾向得分距离
                control_pscores = control_year['pscore'].values
                control_indices = control_year.index.values

                ps_diff = np.abs(control_pscores - treat_pscore)

                # 找到最近的对照组
                min_diff_idx = np.argmin(ps_diff)
                min_diff = ps_diff[min_diff_idx]
                control_idx = control_indices[min_diff_idx]

                # 仅保留在卡径范围内的匹配
                if min_diff <= self.caliper:
                    self.matched_pairs.append({
                        'treat_idx': treat_idx,
                        'control_idx': control_idx,
                        'year': year,
                        'ps_diff': min_diff
                    })

        return self.matched_pairs

    def get_matched_data(self):
        """获取匹配后的数据"""
        if not self.matched_pairs:
            return None

        # 收集所有匹配的索引
        treat_indices = [pair['treat_idx'] for pair in self.matched_pairs]
        control_indices = [pair['control_idx'] for pair in self.matched_pairs]

        # 提取匹配的观测
        matched_treat = self.data.loc[treat_indices].copy()
        matched_control = self.data.loc[control_indices].copy()

        # 合并
        matched_data = pd.concat([matched_treat, matched_control], axis=0)

        return matched_data

    def calculate_balance_stats(self):
        """计算平衡性检验统计量"""
        if not self.matched_pairs:
            return None

        matched_data = self.get_matched_data()
        if matched_data is None:
            return None

        balance_stats = []

        for var in self.covariates:
            # 处理组
            treat_vals = matched_data[matched_data['treat'] == 1][var]
            control_vals = matched_data[matched_data['treat'] == 0][var]

            # 标准化均值差异
            treat_mean = treat_vals.mean()
            control_mean = control_vals.mean()
            pooled_std = np.sqrt((treat_vals.std()**2 + control_vals.std()**2) / 2)

            std_diff = (treat_mean - control_mean) / pooled_std if pooled_std > 0 else 0

            # t检验
            t_stat, p_value = stats.ttest_ind(
                treat_vals.dropna(),
                control_vals.dropna(),
                equal_var=False
            )

            balance_stats.append({
                'variable': var,
                'treat_mean': treat_mean,
                'control_mean': control_mean,
                'std_diff': std_diff,
                't_stat': t_stat,
                'p_value': p_value,
                'n_treat': len(treat_vals),
                'n_control': len(control_vals)
            })

        return pd.DataFrame(balance_stats)

# 执行匹配
matcher = CeadsPSMMatcher(df, covariates, caliper=0.02)
matched_pairs = matcher.perform_matching()

print(f"\n匹配结果:")
print(f"  总匹配对数: {len(matched_pairs)}")
print(f"  匹配率: {len(matched_pairs)/df[df['treat']==1].shape[0]*100:.2f}%")

# 获取匹配后数据
df_matched = matcher.get_matched_data()
print(f"  匹配后总观测数: {df_matched.shape[0]}")
print(f"  匹配后城市数: {df_matched['city_name'].nunique()}")

print("\n" + "=" * 80)
print("第三步：平衡性检验")
print("=" * 80)

# 计算平衡性统计
balance_df = matcher.calculate_balance_stats()

print("\n协变量平衡性检验:")
print("\n变量名 | 处理组均值 | 对照组均值 | 标准化差异 | t值 | p值")
print("-" * 100)

for _, row in balance_df.iterrows():
    var = row['variable']
    treat_mean = row['treat_mean']
    control_mean = row['control_mean']
    std_diff = row['std_diff']
    t_stat = row['t_stat']
    p_value = row['p_value']

    # 判断是否平衡（标准化差异 < 0.1 或 p > 0.05）
    is_balanced = abs(std_diff) < 0.1
    balance_flag = "[OK]" if is_balanced else "[WARNING]"

    print(f"{var:25s} | {treat_mean:10.4f} | {control_mean:10.4f} | "
          f"{std_diff:11.2f} {balance_flag} | {t_stat:6.3f} | {p_value:.4f}")

# 统计平衡性
balanced_vars = (balance_df['std_diff'].abs() < 0.1).sum()
total_vars = len(balance_df)
print(f"\n平衡性总结: {balanced_vars}/{total_vars} 个变量满足平衡性标准（|标准化差异|<0.1）")

if balanced_vars == total_vars:
    print("\n[OK] 所有协变量均通过平衡性检验，匹配质量优秀！")
else:
    print(f"\n[WARNING] {total_vars - balanced_vars} 个变量未通过平衡性检验")

print("\n" + "=" * 80)
print("第四步：倾向得分分布对比")
print("=" * 80)

# 统计倾向得分
treat_pscores = df_matched[df_matched['treat'] == 1]['pscore']
control_pscores = df_matched[df_matched['treat'] == 0]['pscore']

print("\n倾向得分统计（匹配后）:")
print(f"  处理组: 均值={treat_pscores.mean():.4f}, 标准差={treat_pscores.std():.4f}, "
      f"最小值={treat_pscores.min():.4f}, 最大值={treat_pscores.max():.4f}")
print(f"  对照组: 均值={control_pscores.mean():.4f}, 标准差={control_pscores.std():.4f}, "
      f"最小值={control_pscores.min():.4f}, 最大值={control_pscores.max():.4f}")

# 倾向得分的t检验
t_stat, p_value = stats.ttest_ind(treat_pscores, control_pscores)
print(f"\n倾向得分差异检验: t={t_stat:.4f}, p={p_value:.4f}")

if p_value > 0.05:
    print("  [OK] 匹配后倾向得分无显著差异（p>0.05），匹配成功！")
else:
    print("  [WARNING] 匹配后倾向得分仍有显著差异")

print("\n" + "=" * 80)
print("第五步：保存匹配后数据")
print("=" * 80)

# 准备输出数据集
output_cols = ['year', 'city_name', 'city_code', 'ln_carbon_intensity_ceads',
               'ln_pgdp', 'ln_pop_density', 'industrial_advanced', 'fdi_openness',
               'financial_development', 'treat', 'post', 'did', 'pilot_year', 'pscore']

df_output = df_matched[output_cols].copy()

# 保存到Excel
output_file = 'CEADs_PSM_匹配后数据集_五个控制变量_插值版.xlsx'
df_output.to_excel(output_file, index=False)

print(f"\n[OK] 匹配后数据已保存: {output_file}")
print(f"  观测数: {len(df_output)}")
print(f"  城市数: {df_output['city_name'].nunique()}")
print(f"  年份范围: {df_output['year'].min()} - {df_output['year'].max()}")

# 保存平衡性检验结果
balance_output = 'CEADs_PSM_平衡性检验结果_五个控制变量_插值版.xlsx'
balance_df.to_excel(balance_output, index=False)

print(f"\n[OK] 平衡性检验结果已保存: {balance_output}")

print("\n" + "=" * 80)
print("PSM匹配完成！")
print("=" * 80)

print("\n匹配总结:")
print(f"  1. 控制变量: {len(covariates)} 个（人均GDP、人口密度、产业高级化、FDI、金融发展）")
print(f"  2. 缺失值处理: 线性插值 + 前向/后向填充")
print(f"  3. 匹配方法: 1:1最近邻匹配，有放回，卡径=0.02")
print(f"  4. 匹配率: {len(matched_pairs)/df[df['treat']==1].shape[0]*100:.1f}%")
print(f"  5. 匹配后样本: {len(df_matched)} 观测, {df_matched['city_name'].nunique()} 城市")
print(f"  6. 平衡性: {balanced_vars}/{total_vars} 变量通过检验")
print("\n下一步: 使用匹配后样本进行DID回归分析")
