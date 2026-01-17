"""
DID基准回归分析
使用最小二乘虚拟变量法(LSDV)实现双向固定效应模型

Created: 2025-01-06
"""

import pandas as pd
import numpy as np

# ============================================================================
# 第一步：设置面板数据结构
# ============================================================================
print('[OK] === 第一步：设置面板数据结构 ===')

# Load final dataset
print('[OK] 加载最终回归版数据集...')
df = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')
print(f'[OK] 数据集加载成功: {df.shape[0]} 观测 × {df.shape[1]} 变量')

# 设置面板标识
df['city_entity'] = df['city_name'].astype('category').cat.codes
df['year_entity'] = df['year'].astype('category').cat.codes

# 确保数据按城市和年份排序
df = df.sort_values(['city_name', 'year']).reset_index(drop=True)

print(f'[OK] 面板数据结构设置完成:')
print(f'    - 截面维度（城市）: {df["city_name"].nunique()} 个')
print(f'    - 时间维度（年份）: {df["year"].nunique()} 年')
print(f'    - 时间范围: {df["year"].min()}-{df["year"].max()}')
print(f'    - 面板类型: 平衡面板')

# ============================================================================
# 第二步：定义回归变量
# ============================================================================
print('\n[OK] === 第二步：定义回归变量 ===')

# 被解释变量
y_var = 'ln_carbon_intensity'

# 核心解释变量
did_var = 'did'

# 控制变量（5个）
control_vars = [
    'ln_pgdp',          # 经济水平：人均GDP对数
    'ln_pop_density',   # 人口集聚：人口密度对数
    'tertiary_share',   # 产业结构：第三产业比重
    'ln_fdi',          # 外资水平：FDI对数
    'ln_road_area'     # 基础设施：人均道路面积对数
]

print(f'[OK] 被解释变量: {y_var}')
print(f'[OK] 核心解释变量: {did_var}')
print(f'[OK] 控制变量: {len(control_vars)} 个')
for i, var in enumerate(control_vars, 1):
    print(f'      {i}. {var}')

# ============================================================================
# 辅助函数：创建固定效应虚拟变量并回归
# ============================================================================
def create_fe_dummies(df, entity_var, time_var, drop_first=True):
    """创建城市和年份固定效应虚拟变量"""
    # 城市固定效应
    city_dummies = pd.get_dummies(df[entity_var], prefix='city', drop_first=drop_first)
    # 年份固定效应
    year_dummies = pd.get_dummies(df[time_var], prefix='year', drop_first=drop_first)

    return city_dummies, year_dummies


def ols_regression(y, X):
    """
    手动实现OLS回归
    返回: 系数、标准误、t统计量、p值、R2
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

    # 残差标准误
    n = len(y)
    k = X.shape[1]
    sigma2 = np.sum(residuals**2) / (n - k)
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(XtX)))

    # t统计量和p值
    t_stats = beta / se
    from scipy import stats
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - k))

    # R2
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum(residuals**2)
    r2 = 1 - ss_res / ss_tot
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)

    # 样本量
    n_obs = len(y)

    results = {
        'coefficients': beta,
        'std_errors': se,
        't_stats': t_stats,
        'p_values': p_values,
        'r2': r2,
        'adj_r2': adj_r2,
        'n_obs': n_obs,
        'n_vars': k,
        'residuals': residuals
    }

    return results


# ============================================================================
# 第三步：执行基准回归
# ============================================================================
print('\n[OK] === 第三步：执行基准回归 ===')

# 准备被解释变量
y = df[y_var].values

# ========== 模型(1): 不含控制变量 ==========
print('\n[INFO] --- 模型(1): 不含控制变量 ---')

# 创建固定效应虚拟变量
city_dummies1, year_dummies1 = create_fe_dummies(df, 'city_entity', 'year_entity')

# 构建设计矩阵（仅包含DID变量 + 固定效应）
X1 = np.column_stack([
    df[did_var].values,
    city_dummies1.values,
    year_dummies1.values
])

print(f'[INFO] 解释变量: {did_var} + 城市FE + 年份FE')
print(f'[INFO] 总变量数: {X1.shape[1]} (1个DID + {city_dummies1.shape[1]}个城市 + {year_dummies1.shape[1]}个年)')

# 执行回归
results1 = ols_regression(y, X1)

# 提取DID系数
did_coef1 = results1['coefficients'][1]
did_se1 = results1['std_errors'][1]
did_t1 = results1['t_stats'][1]
did_p1 = results1['p_values'][1]

print(f'[OK] 模型(1)回归完成:')
print(f'    - 样本量: {results1["n_obs"]:,}')
print(f'    - R2: {results1["r2"]:.4f}')
print(f'    - 调整R2: {results1["adj_r2"]:.4f}')
print(f'    - DID系数: {did_coef1:.4f}')
print(f'    - 标准误: {did_se1:.4f}')
print(f'    - t统计量: {did_t1:.4f}')
print(f'    - p值: {did_p1:.4f}')

# ========== 模型(2): 包含控制变量 ==========
print('\n[INFO] --- 模型(2): 包含控制变量 ---')

# 构建设计矩阵（DID + 控制变量 + 固定效应）
control_data = df[control_vars].values

# 处理控制变量的缺失值（使用均值填充）
for i in range(control_data.shape[1]):
    col_mean = np.nanmean(control_data[:, i])
    control_data[:, i] = np.nan_to_num(control_data[:, i], nan=col_mean)

X2 = np.column_stack([
    df[did_var].values,
    control_data,
    city_dummies1.values,
    year_dummies1.values
])

print(f'[INFO] 解释变量: {did_var} + {len(control_vars)}个控制变量 + 城市FE + 年份FE')
print(f'[INFO] 总变量数: {X2.shape[1]} (1个DID + {len(control_vars)}个控制 + {city_dummies1.shape[1]}个城市 + {year_dummies1.shape[1]}个年)')

# 执行回归
results2 = ols_regression(y, X2)

# 提取DID系数和控制变量系数
did_coef2 = results2['coefficients'][1]
did_se2 = results2['std_errors'][1]
did_t2 = results2['t_stats'][1]
did_p2 = results2['p_values'][1]

print(f'[OK] 模型(2)回归完成:')
print(f'    - 样本量: {results2["n_obs"]:,}')
print(f'    - R2: {results2["r2"]:.4f}')
print(f'    - 调整R2: {results2["adj_r2"]:.4f}')
print(f'    - DID系数: {did_coef2:.4f}')
print(f'    - 标准误: {did_se2:.4f}')
print(f'    - t统计量: {did_t2:.4f}')
print(f'    - p值: {did_p2:.4f}')

# 提取控制变量系数
control_coefs = results2['coefficients'][2:2+len(control_vars)]
control_ses = results2['std_errors'][2:2+len(control_vars)]
control_tstats = results2['t_stats'][2:2+len(control_vars)]
control_pvals = results2['p_values'][2:2+len(control_vars)]

print(f'\n[INFO] 控制变量系数:')
for i, var in enumerate(control_vars):
    print(f'    {var}:')
    print(f'      - 系数: {control_coefs[i]:.4f}')
    print(f'      - 标准误: {control_ses[i]:.4f}')
    print(f'      - t值: {control_tstats[i]:.4f}')
    print(f'      - p值: {control_pvals[i]:.4f}')

# ============================================================================
# 第四步：聚类稳健标准误（城市层面）
# ============================================================================
print('\n[OK] === 第四步：计算聚类稳健标准误 ===')

def cluster_se(y, X, residuals, cluster_var):
    """
    计算聚类稳健标准误（城市层面）
    """
    n_clusters = df[cluster_var].nunique()
    print(f'[INFO] 聚类数量: {n_clusters} 个城市')

    # Meat matrix ( clustered VC matrix)
    X = np.column_stack([np.ones(len(y)), X])
    k = X.shape[1]

    # 创建聚类矩阵
    meat = np.zeros((k, k))

    for cluster_id in df[cluster_var].unique():
        cluster_mask = df[cluster_var] == cluster_id
        X_cluster = X[cluster_mask]
        residuals_cluster = residuals[cluster_mask]

        # X' * e * e' * X
        Xt_e = np.dot(X_cluster.T, residuals_cluster)
        meat += np.outer(Xt_e, Xt_e)

    # Sandwich estimator
    XtX_inv = np.linalg.inv(np.dot(X.T, X))
    vcov_cluster = XtX_inv @ meat @ XtX_inv

    # Clustered standard errors
    cluster_se = np.sqrt(np.diag(vcov_cluster))

    return cluster_se

# 为模型(2)计算聚类稳健标准误
print('[INFO] 为模型(2)计算聚类稳健标准误...')
cluster_se2 = cluster_se(y, X2, results2['residuals'], 'city_name')

# 更新模型(2)的统计量
did_cluster_se2 = cluster_se2[1]
did_cluster_t2 = did_coef2 / did_cluster_se2

from scipy import stats
did_cluster_p2 = 2 * (1 - stats.t.cdf(np.abs(did_cluster_t2), results2['n_obs'] - X2.shape[1]))

print(f'[OK] 聚类稳健标准误计算完成:')
print(f'    - DID系数: {did_coef2:.4f}')
print(f'    - 聚类标准误: {did_cluster_se2:.4f}')
print(f'    - 聚类t值: {did_cluster_t2:.4f}')
print(f'    - 聚类p值: {did_cluster_p2:.4f}')

# ============================================================================
# 第五步：生成基准回归结果表
# ============================================================================
print('\n[OK] === 第五步：生成基准回归结果表 ===')

# 创建结果表
results_table = pd.DataFrame({
    '变量': ['DID政策变量'] + control_vars,
    '模型(1)\n无控制变量': [
        f'{did_coef1:.4f}\n({did_se1:.4f})'
    ] + ['-' for _ in control_vars],
    '模型(2)\n含控制变量': [
        f'{did_coef2:.4f}\n({did_cluster_se2:.4f})'
    ] + [
        f'{control_coefs[i]:.4f}\n({cluster_se2[2+i]:.4f})'
        for i in range(len(control_vars))
    ]
})

# 添加显著性标记
def add_stars(coef, p):
    if p < 0.01:
        return '***'
    elif p < 0.05:
        return '**'
    elif p < 0.1:
        return '*'
    else:
        return ''

# 添加模型统计信息
model_stats = pd.DataFrame({
    '变量': ['城市固定效应', '年份固定效应', '样本量', 'R2', '调整R2'],
    '模型(1)\n无控制变量': ['Yes', 'Yes', f"{results1['n_obs']:,}", f"{results1['r2']:.4f}", f"{results1['adj_r2']:.4f}"],
    '模型(2)\n含控制变量': ['Yes', 'Yes', f"{results2['n_obs']:,}", f"{results2['r2']:.4f}", f"{results2['adj_r2']:.4f}"]
})

results_table = pd.concat([results_table, model_stats], ignore_index=True)

print('\n[INFO] 基准回归结果表:')
print(results_table.to_string(index=False))

# 保存到Excel
output_file = '基准回归结果表.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    results_table.to_excel(writer, sheet_name='基准回归', index=False)

    # 详细结果
    detailed_results = pd.DataFrame({
        '变量': ['DID政策变量'] + control_vars,
        '模型1_系数': [did_coef1] + [np.nan]*len(control_vars),
        '模型1_标准误': [did_se1] + [np.nan]*len(control_vars),
        '模型1_t值': [did_t1] + [np.nan]*len(control_vars),
        '模型1_p值': [did_p1] + [np.nan]*len(control_vars),
        '模型2_系数': [did_coef2] + list(control_coefs),
        '模型2_标准误': [did_cluster_se2] + list(cluster_se2[2:2+len(control_vars)]),
        '模型2_t值': [did_cluster_t2] + list(control_coefs / cluster_se2[2:2+len(control_vars)]),
        '模型2_p值': [did_cluster_p2] + list(control_pvals)
    })
    detailed_results.to_excel(writer, sheet_name='详细结果', index=False)

print(f'\n[OK] 基准回归结果表已保存: {output_file}')

# ============================================================================
# 第六步：结果解释
# ============================================================================
print('\n[OK] === 第六步：结果解释 ===')

print('[INFO] 主要发现:')
print(f'\n1. 模型(1) - 无控制变量:')
print(f'   - 低碳试点政策使碳排放强度变化: {did_coef1:.4f} (即 {np.exp(did_coef1)-1:.2%})')
print(f'   - 统计显著性: {"显著" if did_p1 < 0.1 else "不显著"} (p={did_p1:.4f})')

print(f'\n2. 模型(2) - 含控制变量:')
print(f'   - 低碳试点政策使碳排放强度变化: {did_coef2:.4f} (即 {np.exp(did_coef2)-1:.2%})')
print(f'   - 统计显著性: {"显著" if did_cluster_p2 < 0.1 else "不显著"} (p={did_cluster_p2:.4f})')
print(f'   - 经济含义: 政策使碳排放强度{"降低" if did_coef2 < 0 else "增加"} {abs(np.exp(did_coef2)-1)*100:.2f}%')

# 显著性判断
significance = ''
if did_cluster_p2 < 0.01:
    significance = '在1%水平上显著'
elif did_cluster_p2 < 0.05:
    significance = '在5%水平上显著'
elif did_cluster_p2 < 0.1:
    significance = '在10%水平上显著'
else:
    significance = '不显著'

print(f'\n3. 结论:')
print(f'   - 控制变量后，DID系数为 {did_coef2:.4f}')
print(f'   - {significance}')
print(f'   - 模型解释力提升: R2从 {results1["r2"]:.4f} 提升到 {results2["r2"]:.4f}')

print(f'\n[OK] DID基准回归分析完成!')
print(f'[OK] 所有结果已保存到: {output_file}')
