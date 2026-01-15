"""
PSM-DID基准回归分析 (四个控制变量组合)
基于倾向得分匹配后的样本进行双重差分回归
采用双重稳健估计(Double Robust Estimation)

控制变量组合: 人均GDP + 人口集聚程度 + 第三产业占GDP比重 + 外商投资水平
- ln_pgdp: 人均GDP (对数)
- ln_pop_density: 人口密度 (对数)
- tertiary_share: 第三产业占GDP比重 (水平值)
- ln_fdi: 外商直接投资 (对数)

Created: 2025-01-15
"""

import pandas as pd
import numpy as np
from scipy import stats

# ============================================================================
# 第一步：加载PSM匹配后数据集
# ============================================================================
print('[OK] === 第一步：加载PSM匹配后数据集 ===')

print('[OK] 加载PSM匹配后数据集...')
df = pd.read_excel('人均GDP+人口集聚程度+第二产业比重+外商投资水平/PSM_匹配后数据集.xlsx')
print(f'[OK] 数据集加载成功: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# 设置面板标识
df['city_entity'] = df['city_name'].astype('category').cat.codes
df['year_entity'] = df['year'].astype('category').cat.codes

# 确保数据按城市和年份排序
df = df.sort_values(['city_name', 'year']).reset_index(drop=True)

print(f'[OK] 面板数据结构:')
print(f'    - 样本量: {df.shape[0]} 观测值')
print(f'    - 城市数: {df["city_name"].nunique()} 个')
print(f'    - 年份数: {df["year"].nunique()} 年')
print(f'    - 时间范围: {df["year"].min()}-{df["year"].max()}')

# ============================================================================
# 第二步：定义回归变量
# ============================================================================
print('\n[OK] === 第二步：定义回归变量 ===')

# 被解释变量
y_var = 'ln_carbon_intensity'

# 核心解释变量
did_var = 'did'

# 控制变量（4个）- 双重稳健估计
control_vars = [
    'ln_pgdp',             # 经济发展水平：人均GDP对数
    'ln_pop_density',      # 人口集聚程度：人口密度对数
    'tertiary_share',      # 产业结构：第三产业占GDP比重（水平值）
    'ln_fdi'               # 外商投资水平：外商直接投资对数
]

print(f'[OK] 被解释变量: {y_var}')
print(f'[OK] 核心解释变量: {did_var}')
print(f'[OK] 控制变量（双重稳健估计）: {len(control_vars)} 个')
for i, var in enumerate(control_vars, 1):
    print(f'      {i}. {var}')

# ============================================================================
# 辅助函数：OLS回归 + 聚类稳健标准误
# ============================================================================
def create_fe_dummies(df, entity_var, time_var, drop_first=True):
    """创建城市和年份固定效应虚拟变量"""
    city_dummies = pd.get_dummies(df[entity_var], prefix='city', drop_first=drop_first)
    year_dummies = pd.get_dummies(df[time_var], prefix='year', drop_first=drop_first)
    return city_dummies, year_dummies


def ols_regression_clustered(y, X, cluster_var, df):
    """
    手动实现OLS回归 + 聚类稳健标准误
    聚类层面：城市级别

    返回: 系数、标准误(非聚类)、标准误(聚类)、t统计量、p值、R2
    """
    # 添加常数项
    X = np.column_stack([np.ones(len(y)), X])

    # OLS估计: beta = (X'X)^(-1)X'y
    XtX = np.dot(X.T, X)
    Xty = np.dot(X.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # 预测值和残差
    y_pred = np.dot(X, beta)
    residuals = y - y_pred

    # 样本量和变量数
    n = len(y)
    k = X.shape[1]

    # 1. 非聚类标准误 (同方差假设)
    sigma2 = np.sum(residuals**2) / (n - k)
    XtX_inv = np.linalg.inv(XtX)
    vcov_homoskedastic = sigma2 * XtX_inv
    se_homoskedastic = np.sqrt(np.diag(vcov_homoskedastic))

    # 2. 聚类稳健标准误 (城市层面聚类)
    # Meat矩阵: sum(X_j' e_j e_j' X_j), j为聚类单元
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)

    # 初始化meat矩阵
    meat = np.zeros((k, k))

    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # 小样本校正
    n_clusters = len(unique_clusters)
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))

    # 聚类稳健方差矩阵
    vcov_cluster = correction * np.linalg.inv(XtX).dot(meat).dot(np.linalg.inv(XtX))
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    # t统计量和p值 (使用聚类标准误)
    tstats = beta / se_cluster
    pvals = 2 * (1 - stats.t.cdf(np.abs(tstats), df=n_clusters - 1))

    # R2
    ss_total = np.sum((y - np.mean(y))**2)
    ss_residual = np.sum(residuals**2)
    r2 = 1 - ss_residual / ss_total

    # 调整R2
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - k)

    return {
        'coefficients': beta,
        'se_homoskedastic': se_homoskedastic,
        'se_cluster': se_cluster,
        'tstats': tstats,
        'pvals': pvals,
        'r2': r2,
        'r2_adj': r2_adj,
        'n': n,
        'k': k,
        'n_clusters': n_clusters
    }


# ============================================================================
# 第三步：构建回归矩阵
# ============================================================================
print('\n[OK] === 第三步：构建回归矩阵 ===')

# 被解释变量
y = df[y_var].values

# 核心解释变量：DID交互项
did = df[did_var].values

# 控制变量矩阵
X_controls = df[control_vars].values

# 检查缺失值
print(f'[OK] 检查数据完整性:')
print(f'    - 被解释变量缺失: {np.isnan(y).sum()}')
print(f'    - DID变量缺失: {np.isnan(did).sum()}')
for var in control_vars:
    missing = df[var].isnull().sum()
    print(f'    - {var}缺失: {missing}')

# 删除有任何缺失的观测
valid_mask = ~np.isnan(y) & ~np.isnan(did)
for var in control_vars:
    valid_mask &= ~np.isnan(df[var].values)

if valid_mask.sum() < len(y):
    print(f'\n[WARNING] 删除 {len(y) - valid_mask.sum()} 个含缺失值的观测')
    y = y[valid_mask]
    did = did[valid_mask]
    X_controls = X_controls[valid_mask]
    df = df[valid_mask].reset_index(drop=True)

    # 重新创建实体编码
    df['city_entity'] = df['city_name'].astype('category').cat.codes
    df['year_entity'] = df['year'].astype('category').cat.codes

print(f'\n[OK] 最终回归样本: {len(y)} 观测')
print(f'    - 城市数: {df["city_name"].nunique()}')
print(f'    - 年份数: {df["year"].nunique()}')

# ============================================================================
# 第四步：构建城市和年份固定效应
# ============================================================================
print('\n[OK] === 第四步：构建固定效应 ===')

city_dummies, year_dummies = create_fe_dummies(
    df,
    entity_var='city_entity',
    time_var='year_entity',
    drop_first=True  # 删除基准类避免完全共线性
)

print(f'[OK] 城市固定效应: {city_dummies.shape[1]} 个虚拟变量')
print(f'[OK] 年份固定效应: {year_dummies.shape[1]} 个虚拟变量')

# ============================================================================
# 第五步：PSM-DID回归 (加入城市和年份固定效应)
# ============================================================================
print('\n[OK] === 第五步：PSM-DID回归 (固定效应模型) ===')

# 构建完整的设计矩阵 (DID + 控制变量 + 城市FE + 年份FE)
X_fe = np.column_stack([did, X_controls, city_dummies, year_dummies])

print(f'[OK] 设计矩阵维度: {X_fe.shape}')
print(f'    - 解释变量数: {X_fe.shape[1]}')
print(f'    - DID系数 + 控制变量: {1 + len(control_vars)}')
print(f'    - 城市固定效应: {city_dummies.shape[1]}')
print(f'    - 年份固定效应: {year_dummies.shape[1]}')

# 执行回归 (聚类稳健标准误)
results_fe = ols_regression_clustered(
    y=y,
    X=X_fe,
    cluster_var='city_entity',
    df=df
)

print(f'\n[OK] 回归结果 (固定效应 + 聚类标准误):')
print(f'    - R2: {results_fe["r2"]:.4f}')
print(f'    - 调整R2: {results_fe["r2_adj"]:.4f}')
print(f'    - 样本量: {results_fe["n"]}')
print(f'    - 聚类数: {results_fe["n_clusters"]}')

# ============================================================================
# 第六步：结果整理与输出
# ============================================================================
print('\n[OK] === 第六步：结果整理 ===')

# 创建变量名列表
var_names = ['const', 'DID'] + control_vars + \
             [f'city_FE_{i}' for i in range(city_dummies.shape[1])] + \
             [f'year_FE_{i}' for i in range(year_dummies.shape[1])]

# 构建结果表格
results_table = pd.DataFrame({
    'Variable': var_names,
    'Coefficient': results_fe['coefficients'],
    'SE_Cluster': results_fe['se_cluster'],
    'SE_Homoskedastic': results_fe['se_homoskedastic'],
    't_stat': results_fe['tstats'],
    'p_value': results_fe['pvals']
})

# 添加显著性标记
results_table['Significance'] = ''
results_table.loc[results_table['p_value'] < 0.01, 'Significance'] = '***'
results_table.loc[(results_table['p_value'] >= 0.01) & (results_table['p_value'] < 0.05), 'Significance'] = '**'
results_table.loc[(results_table['p_value'] >= 0.05) & (results_table['p_value'] < 0.1), 'Significance'] = '*'

# 格式化输出
results_table['Coefficient_fmt'] = results_table['Coefficient'].apply(lambda x: f'{x:.4f}')
results_table['SE_Cluster_fmt'] = results_table['SE_Cluster'].apply(lambda x: f'{x:.4f}')
results_table['t_stat_fmt'] = results_table['t_stat'].apply(lambda x: f'{x:.4f}')
results_table['p_value_fmt'] = results_table['p_value'].apply(
    lambda x: f'{x:.4f}' if x >= 0.001 else '<0.001'
)

# 核心结果
print('\n' + '='*80)
print('[OK] PSM-DID回归核心结果 (基于PSM匹配样本)')
print('='*80)

print(f'\n被解释变量: {y_var}')
print(f'回归方法: OLS + 城市和年份固定效应 + 聚类稳健标准误 (城市层面)')
print(f'控制变量: {len(control_vars)} 个 (双重稳健估计)')
print(f'样本量: {results_fe["n"]} 观测')
print(f'聚类数: {results_fe["n_clusters"]} 个城市')
print(f'R2: {results_fe["r2"]:.4f}')
print(f'调整R2: {results_fe["r2_adj"]:.4f}')

print('\n' + '-'*80)
print('{:<25} {:>12} {:>10} {:>10} {:>10} {:>8}'.format('变量', '系数', '聚类SE', 't值', 'p值', '显著性'))
print('-'*80)

# 核心变量 (DID + 控制变量)
core_vars = ['DID'] + control_vars
for var in core_vars:
    row = results_table[results_table['Variable'] == var].iloc[0]
    print(f'{var:<25} {row["Coefficient_fmt"]:>12} {row["SE_Cluster_fmt"]:>10} '
          f'{row["t_stat_fmt"]:>10} {row["p_value_fmt"]:>10} {row["Significance"]:>8}')

print('-'*80)
print('注: 聚类稳健标准误 (城市层面)')
print('    *** p<0.01, ** p<0.05, * p<0.1')
print('='*80 + '\n')

# ============================================================================
# 第七步：保存结果到Excel
# ============================================================================
print('[OK] === 第七步：保存结果 ===')

output_file = '人均GDP+人口集聚程度+第二产业比重+外商投资水平/PSM-DID回归结果.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Sheet 1: 完整结果
    results_table.to_excel(writer, sheet_name='完整结果', index=False)

    # Sheet 2: 核心结果 (仅DID和控制变量)
    core_results = results_table[results_table['Variable'].isin(['const', 'DID'] + control_vars)].copy()
    core_results.to_excel(writer, sheet_name='核心变量', index=False)

    # Sheet 3: 格式化汇报表
    report_table = pd.DataFrame({
        '变量': ['常数项', 'DID (政策效应)'] + [v for v in control_vars],
        '系数': results_table[results_table['Variable'].isin(['const', 'DID'] + control_vars)]['Coefficient'].values,
        '聚类稳健标准误': results_table[results_table['Variable'].isin(['const', 'DID'] + control_vars)]['SE_Cluster'].values,
        't统计量': results_table[results_table['Variable'].isin(['const', 'DID'] + control_vars)]['t_stat'].values,
        'p值': results_table[results_table['Variable'].isin(['const', 'DID'] + control_vars)]['p_value'].values,
    })
    report_table['显著性'] = report_table['p值'].apply(
        lambda x: '***' if x < 0.01 else ('**' if x < 0.05 else ('*' if x < 0.1 else ''))
    )
    report_table.to_excel(writer, sheet_name='汇报表', index=False)

    # Sheet 4: 回归统计量
    stats_df = pd.DataFrame({
        '统计量': ['样本量', '聚类数', 'R2', '调整R2', '解释变量数',
                  '被解释变量', '回归方法', '固定效应', '聚类层面'],
        '数值': [
            f'{results_fe["n"]:,}',
            f'{results_fe["n_clusters"]}',
            f'{results_fe["r2"]:.4f}',
            f'{results_fe["r2_adj"]:.4f}',
            results_fe['k'],
            y_var,
            'OLS + 聚类稳健标准误',
            '城市FE + 年份FE',
            '城市层面'
        ]
    })
    stats_df.to_excel(writer, sheet_name='回归统计量', index=False)

print(f'[OK] 结果已保存: {output_file}')

print('\n' + '='*80)
print('[OK] PSM-DID回归分析完成!')
print('='*80)

# 政策效应解读
did_coef = results_table[results_table['Variable'] == 'DID']['Coefficient'].values[0]
did_pval = results_table[results_table['Variable'] == 'DID']['p_value'].values[0]

print(f'\n政策效应解读:')
print(f'  - DID系数: {did_coef:.4f}')
print(f'  - 系数含义: 低碳试点政策使碳排放强度变化了 {did_coef*100:.2f}%')
print(f'  - 统计显著性: p = {did_pval:.4f}')

if did_pval < 0.01:
    sig_level = '1%水平显著'
elif did_pval < 0.05:
    sig_level = '5%水平显著'
elif did_pval < 0.1:
    sig_level = '10%水平显著'
else:
    sig_level = '不显著'

print(f'  - 结论: 政策效应{sig_level}')

if did_pval >= 0.1:
    print(f'  - 经济含义: 低碳试点政策对碳排放强度没有显著的因果效应')
else:
    effect_dir = '增加' if did_coef > 0 else '降低'
    print(f'  - 经济含义: 低碳试点政策显著{effect_dir}了碳排放强度')

print(f'\n模型设定:')
print(f'  - 基于PSM匹配后的样本 (减少选择偏差)')
print(f'  - 双重稳健估计 (PSM + 回归控制)')
print(f'  - 城市和年份双向固定效应 (控制不可观测因素)')
print(f'  - 聚类稳健标准误 (允许城市内序列相关)')
