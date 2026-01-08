"""
PSM-DID基准回归分析（使用第二产业占比）
基于倾向得分匹配后的样本进行双重差分回归

Created: 2025-01-08
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

# 设置输出目录
output_dir = '二产占比模型_分析结果'
os.makedirs(output_dir, exist_ok=True)

# ============================================================================
# 第一步：加载含二产占比的数据集
# ============================================================================
print('[OK] === 第一步：加载含二产占比的数据集 ===')

data_file = f'{output_dir}/PSM匹配后数据集_含二产占比.xlsx'
print(f'[OK] 加载数据集: {data_file}')
df = pd.read_excel(data_file)
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
# 第二步：定义回归变量（使用二产占比）
# ============================================================================
print('\n[OK] === 第二步：定义回归变量 ===')

# 被解释变量
y_var = 'ln_carbon_intensity'

# 核心解释变量
did_var = 'did'

# 控制变量（6个）- 使用二产占比替代三产占比
control_vars = [
    'ln_pgdp',                # 经济发展水平：人均GDP对数
    'ln_pop_density',         # 人口集聚程度：人口密度对数
    'secondary_share',        # 第二产业占比（替代tertiary_share）
    'secondary_share_sq',     # 第二产业占比平方项
    'ln_fdi',                # 外商直接投资对数
    'ln_road_area'           # 基础设施水平：人均道路面积对数
]

print(f'[OK] 被解释变量: {y_var}')
print(f'[OK] 核心解释变量: {did_var}')
print(f'[OK] 控制变量: {len(control_vars)} 个（使用第二产业占比）')
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
    """
    # 添加常数项
    X = np.column_stack([np.ones(len(y)), X])

    # OLS估计
    XtX = np.dot(X.T, X)
    Xty = np.dot(X.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # 预测值和残差
    y_pred = np.dot(X, beta)
    residuals = y - y_pred

    # 样本量和变量数
    n = len(y)
    k = X.shape[1]

    # === 非聚类标准误 ===
    sigma2 = np.sum(residuals**2) / (n - k)
    vcov_noncluster = sigma2 * np.linalg.inv(XtX)
    se_noncluster = np.sqrt(np.diag(vcov_noncluster))

    # === 聚类稳健标准误（城市层面） ===
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    # 计算聚类稳健的方差协方差矩阵
    meat = np.zeros((k, k))
    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # 校正因子
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov_cluster = correction * np.linalg.inv(XtX).dot(meat).dot(np.linalg.inv(XtX))
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    # t统计量和p值（使用聚类标准误）
    t_stats = beta / se_cluster
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - k))

    # R2
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum(residuals**2)
    r2 = 1 - ss_res / ss_tot
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)

    results = {
        'coefficients': beta,
        'std_errors_noncluster': se_noncluster,
        'std_errors_cluster': se_cluster,
        't_stats': t_stats,
        'p_values': p_values,
        'r2': r2,
        'adj_r2': adj_r2,
        'n_obs': n,
        'n_vars': k,
        'n_clusters': n_clusters
    }

    return results


# ============================================================================
# 第三步：执行PSM-DID回归
# ============================================================================
print('\n[OK] === 第三步：执行PSM-DID基准回归 ===')

# 准备被解释变量
y = df[y_var].values

# ========== 模型(1): 不含控制变量 ==========
print('\n[INFO] --- Model (1): Without control variables ---')

city_dummies1, year_dummies1 = create_fe_dummies(df, 'city_entity', 'year_entity')

X1 = np.column_stack([
    df[did_var].values,
    city_dummies1.values,
    year_dummies1.values
])

print(f'[INFO] Explained variables: {did_var} + City FE + Year FE')
print(f'[INFO] Total variables: {X1.shape[1]} (1 DID + {city_dummies1.shape[1]} city FE + {year_dummies1.shape[1]} year FE)')

results1 = ols_regression_clustered(y, X1, 'city_entity', df)

print(f'[OK] Regression completed')
print(f'[INFO] DID coefficient: {results1["coefficients"][1]:.4f}')
print(f'[INFO] Clustered SE: {results1["std_errors_cluster"][1]:.4f}')
print(f'[INFO] t-statistic: {results1["t_stats"][1]:.4f}')
print(f'[INFO] p-value: {results1["p_values"][1]:.4f}')
print(f'[INFO] R2: {results1["r2"]:.4f}')
print(f'[INFO] Adj R2: {results1["adj_r2"]:.4f}')
print(f'[INFO] Clusters: {results1["n_clusters"]}')

# ========== 模型(2): 包含控制变量（使用二产占比） ==========
print('\n[INFO] --- Model (2): With control variables (Secondary Industry Share) ---')

city_dummies2, year_dummies2 = create_fe_dummies(df, 'city_entity', 'year_entity')

# 构建设计矩阵：DID + 6个控制变量 + 固定效应
control_data = [df[var].values for var in control_vars]
X2 = np.column_stack([
    df[did_var].values,
    *control_data,
    city_dummies2.values,
    year_dummies2.values
])

print(f'[INFO] Explained variables: {did_var} + {len(control_vars)} control variables + City FE + Year FE')
print(f'[INFO] Control variables: {", ".join(control_vars)}')
print(f'[INFO] Total variables: {X2.shape[1]} (1 DID + {len(control_vars)} controls + {city_dummies2.shape[1]} city FE + {year_dummies2.shape[1]} year FE)')

results2 = ols_regression_clustered(y, X2, 'city_entity', df)

print(f'[OK] Regression completed')
print(f'[INFO] DID coefficient: {results2["coefficients"][1]:.4f}')
print(f'[INFO] Clustered SE: {results2["std_errors_cluster"][1]:.4f}')
print(f'[INFO] t-statistic: {results2["t_stats"][1]:.4f}')
print(f'[INFO] p-value: {results2["p_values"][1]:.4f}')
print(f'[INFO] R2: {results2["r2"]:.4f}')
print(f'[INFO] Adj R2: {results2["adj_r2"]:.4f}')
print(f'[INFO] Clusters: {results2["n_clusters"]}')

# ============================================================================
# 第四步：生成回归结果表格
# ============================================================================
print('\n[OK] === 第四步：生成回归结果表格 ===')

# 创建结果表格
var_names = ['Constant', did_var] + control_vars

# 准备模型1的结果
model1_coef = [results1['coefficients'][0], results1['coefficients'][1]] + [np.nan] * len(control_vars)
model1_se_cluster = [results1['std_errors_cluster'][0], results1['std_errors_cluster'][1]] + [np.nan] * len(control_vars)
model1_t_stats = [results1['t_stats'][0], results1['t_stats'][1]] + [np.nan] * len(control_vars)
model1_p_values = [results1['p_values'][0], results1['p_values'][1]] + [np.nan] * len(control_vars)

# 准备模型2的结果
model2_coef = [results2['coefficients'][0], results2['coefficients'][1]]
model2_se_cluster = [results2['std_errors_cluster'][0], results2['std_errors_cluster'][1]]
model2_t_stats = [results2['t_stats'][0], results2['t_stats'][1]]
model2_p_values = [results2['p_values'][0], results2['p_values'][1]]

for i in range(len(control_vars)):
    idx = i + 2  # +2 for constant and DID
    model2_coef.append(results2['coefficients'][idx])
    model2_se_cluster.append(results2['std_errors_cluster'][idx])
    model2_t_stats.append(results2['t_stats'][idx])
    model2_p_values.append(results2['p_values'][idx])

# 创建显著性标记
def add_stars(coef, pval):
    """添加显著性星号"""
    if pd.isna(coef) or pd.isna(pval):
        return coef
    if pval < 0.01:
        return f'{coef:.4f}***'
    elif pval < 0.05:
        return f'{coef:.4f}**'
    elif pval < 0.1:
        return f'{coef:.4f}*'
    else:
        return f'{coef:.4f}'

# 构建结果DataFrame
results_df = pd.DataFrame({
    'Variable': var_names,
    'Model(1) Coef': [add_stars(model1_coef[i], model1_p_values[i]) for i in range(len(var_names))],
    'Model(1) SE': [f'{model1_se_cluster[i]:.4f}' if not pd.isna(model1_se_cluster[i]) else '' for i in range(len(var_names))],
    'Model(2) Coef': [add_stars(model2_coef[i], model2_p_values[i]) for i in range(len(var_names))],
    'Model(2) SE': [f'{model2_se_cluster[i]:.4f}' for i in range(len(var_names))],
    'Model(2) t-stat': [f'{model2_t_stats[i]:.4f}' for i in range(len(var_names))],
    'Model(2) p-value': [f'{model2_p_values[i]:.4f}' for i in range(len(var_names))]
})

# 添加模型统计信息
model_stats = pd.DataFrame({
    'Variable': ['N', 'Clusters', 'R2', 'Adj R2', 'City FE', 'Year FE', 'Clustered SE'],
    'Model(1) Coef': [results1['n_obs'], results1['n_clusters'], f"{results1['r2']:.4f}",
                   f"{results1['adj_r2']:.4f}", 'Yes', 'Yes', 'Yes'],
    'Model(1) SE': ['', '', '', '', '', '', ''],
    'Model(2) Coef': [results2['n_obs'], results2['n_clusters'], f"{results2['r2']:.4f}",
                   f"{results2['adj_r2']:.4f}", 'Yes', 'Yes', 'Yes'],
    'Model(2) SE': ['', '', '', '', '', '', ''],
    'Model(2) t-stat': ['', '', '', '', '', '', ''],
    'Model(2) p-value': ['', '', '', '', '', '', '']
})

results_df = pd.concat([results_df, model_stats], ignore_index=True)

# 保存到Excel
output_file = f'{output_dir}/PSM-DID回归结果表_二产占比.xlsx'
results_df.to_excel(output_file, index=False)
print(f'[OK] Regression results saved: {output_file}')

# 打印关键结果
print('\n' + '='*80)
print('[OK] PSM-DID Regression Summary (Using Secondary Industry Share)')
print('='*80)
print(f'\n[MODEL 1] Without control variables')
print(f'  DID coefficient: {results1["coefficients"][1]:.4f} (clustered SE: {results1["std_errors_cluster"][1]:.4f}, t: {results1["t_stats"][1]:.4f}, p: {results1["p_values"][1]:.4f})')
sig1 = '***' if results1['p_values'][1] < 0.01 else '**' if results1['p_values'][1] < 0.05 else '*' if results1['p_values'][1] < 0.1 else ''
print(f'  Significance: {sig1 if sig1 else "not significant"}')
print(f'  R2: {results1["r2"]:.4f}, Adj R2: {results1["adj_r2"]:.4f}')
print(f'  N: {results1["n_obs"]}, Clusters: {results1["n_clusters"]}')

print(f'\n[MODEL 2] With control variables (Secondary Industry Share)')
print(f'  DID coefficient: {results2["coefficients"][1]:.4f} (clustered SE: {results2["std_errors_cluster"][1]:.4f}, t: {results2["t_stats"][1]:.4f}, p: {results2["p_values"][1]:.4f})')
sig2 = '***' if results2['p_values'][1] < 0.01 else '**' if results2['p_values'][1] < 0.05 else '*' if results2['p_values'][1] < 0.1 else ''
print(f'  Significance: {sig2 if sig2 else "not significant"}')
print(f'  R2: {results2["r2"]:.4f}, Adj R2: {results2["adj_r2"]:.4f}')
print(f'  N: {results2["n_obs"]}, Clusters: {results2["n_clusters"]}')

print(f'\n[Control Variables Results]')
for i, var in enumerate(control_vars):
    idx = i + 2  # +2 for constant and DID
    coef = results2['coefficients'][idx]
    se = results2['std_errors_cluster'][idx]
    t = results2['t_stats'][idx]
    p = results2['p_values'][idx]
    sig = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
    print(f'  {var}: {coef:.4f}{sig} (SE: {se:.4f}, t: {t:.4f}, p: {p:.4f})')

print('\n' + '='*80)
print('[OK] PSM-DID regression completed!')
print('='*80)
