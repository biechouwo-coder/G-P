import pandas as pd
import numpy as np
from scipy import stats

def ols_regression_clustered(y, X, cluster_var, df):
    """
    手动实现OLS回归，使用城市层面的聚类稳健标准误
    """
    # 添加常数项
    X = np.column_stack([np.ones(len(y)), X])
    n, k = X.shape

    # 计算系数 beta = (X'X)^(-1)X'y
    XtX = np.dot(X.T, X)
    Xty = np.dot(X.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # 计算残差
    residuals = y - np.dot(X, beta)

    # 计算聚类稳健标准误（sandwich estimator）
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    # Meat matrix (聚类残差外积)
    meat = np.zeros((k, k))
    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # Bread matrix
    bread = np.linalg.inv(XtX)

    # 小样本校正
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov_cluster = correction * bread.dot(meat).dot(bread)

    # 标准误
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    # t统计量和p值
    t_stats = beta / se_cluster
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_clusters - 1))

    # R-squared
    y_mean = np.mean(y)
    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum(residuals ** 2)
    r_squared = 1 - (ss_residual / ss_total)

    return {
        'coefficients': beta,
        'std_errors': se_cluster,
        't_stats': t_stats,
        'p_values': p_values,
        'r_squared': r_squared,
        'n_obs': n,
        'n_clusters': n_clusters
    }

def run_fe_regression(df, cluster_var='city_name'):
    """
    运行固定效应模型（LSDV法）
    """
    # 准备数据
    y = df['ln_carbon_intensity'].values

    # 控制变量
    X_controls = df[['ln_pgdp', 'ln_pop_density', 'industrial_advanced',
                     'ln_road_area', 'financial_development']].values

    # 创建城市固定效应（城市哑变量）
    city_dummies = pd.get_dummies(df['city_name'], drop_first=True)
    print(f"[INFO] 创建了 {city_dummies.shape[1]} 个城市固定效应哑变量")

    # 创建年份固定效应（年份哑变量）
    year_dummies = pd.get_dummies(df['year'], drop_first=True)
    print(f"[INFO] 创建了 {year_dummies.shape[1]} 个年份固定效应哑变量")

    # DID变量
    X_did = df['did'].values.reshape(-1, 1)

    # 合并所有X变量
    X = np.column_stack([X_did, X_controls, city_dummies, year_dummies])

    print(f"\n[INFO] 回归模型:")
    print(f"  因变量: ln_carbon_intensity")
    print(f"  核心变量: DID")
    print(f"  控制变量: ln_pgdp, ln_pop_density, industrial_advanced, ln_road_area, financial_development")
    print(f"  固定效应: 城市FE + 年份FE")

    # 运行回归
    print(f"\n[INFO] 运行OLS回归...")
    results = ols_regression_clustered(y, X, cluster_var, df)

    return results, city_dummies.columns.tolist(), year_dummies.columns.tolist()

# 读取数据
df = pd.read_excel('人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/回归分析数据集.xlsx')
print(f"[INFO] 数据集形状: {df.shape}")
print(f"[INFO] 城市数: {df['city_name'].nunique()}")
print(f"[INFO] 年份范围: {df['year'].min()} - {df['year'].max()}")

# 运行固定效应回归
results, city_fe, year_fe = run_fe_regression(df)

# 提取关键变量的结果（前7个变量：常数项、DID、5个控制变量）
var_names = ['常数项', 'DID', 'ln_pgdp', 'ln_pop_density', 'industrial_advanced', 'ln_road_area', 'financial_development']
n_key_vars = len(var_names)

print(f"\n{'='*80}")
print(f"DID回归结果（含聚类稳健标准误）")
print(f"{'='*80}")
print(f"样本量: {results['n_obs']}")
print(f"城市聚类数: {results['n_clusters']}")
print(f"R-squared: {results['r_squared']:.4f}")
print(f"\n{'变量':<25} {'系数':>12} {'标准误':>12} {'t值':>10} {'p值':>10}")
print(f"{'-'*80}")

for i, name in enumerate(var_names):
    coef = results['coefficients'][i]
    se = results['std_errors'][i]
    t = results['t_stats'][i]
    p = results['p_values'][i]

    # 显著性标记
    sig = ''
    if p < 0.01:
        sig = '***'
    elif p < 0.05:
        sig = '**'
    elif p < 0.1:
        sig = '*'

    print(f"{name:<25} {coef:>12.6f} {se:>12.6f} {t:>10.4f} {p:>10.4f} {sig}")

print(f"{'-'*80}")
print(f"注: 聚类稳健标准误（城市层面）")
print(f"*** p<0.01, ** p<0.05, * p<0.1")

# 保存结果到Excel
output_file = '人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/DID回归结果.xlsx'
results_df = pd.DataFrame({
    '变量': var_names,
    '系数': results['coefficients'][:n_key_vars],
    '标准误': results['std_errors'][:n_key_vars],
    't值': results['t_stats'][:n_key_vars],
    'p值': results['p_values'][:n_key_vars]
})

# 添加显著性标记
results_df['显著性'] = results_df['p值'].apply(
    lambda p: '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else ''))
)

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # 回归结果表
    results_df.to_excel(writer, sheet_name='回归结果', index=False)

    # 模型摘要
    summary_data = {
        '指标': ['样本量', '城市聚类数', 'R-squared', '固定效应'],
        '数值': [results['n_obs'], results['n_clusters'], f"{results['r_squared']:.4f}",
                 f"城市FE ({len(city_fe)}个) + 年份FE ({len(year_fe)}个)"]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='模型摘要', index=False)

print(f"\n[OK] 结果已保存到: {output_file}")

# 解释DID系数
did_coef = results['coefficients'][1]
did_p = results['p_values'][1]
print(f"\n{'='*80}")
print(f"核心发现:")
print(f"{'='*80}")
print(f"DID系数: {did_coef:.6f} (p={did_p:.4f})")

if did_p < 0.05:
    effect_pct = (np.exp(did_coef) - 1) * 100
    print(f"低碳城市试点政策显著影响了碳减排强度（p<0.05）")
    print(f"政策效应: {effect_pct:+.2f}%")
elif did_p < 0.1:
    effect_pct = (np.exp(did_coef) - 1) * 100
    print(f"低碳城市试点政策边际显著影响碳减排强度（p<0.1）")
    print(f"政策效应: {effect_pct:+.2f}%")
else:
    print(f"低碳城市试点政策对碳减排强度无显著影响（p={did_p:.4f}>=0.1）")
    print(f"虽然系数为{did_coef:+.6f}，但统计上不显著")

# 控制变量解释
print(f"\n控制变量解释:")
print(f"  - ln_road_area系数: {results['coefficients'][5]:.6f} (p={results['p_values'][5]:.4f})")
if results['p_values'][5] < 0.1:
    road_effect = (np.exp(results['coefficients'][5]) - 1) * 100
    direction = "增加" if results['coefficients'][5] > 0 else "降低"
    print(f"    人均道路面积显著{direction}碳排放强度")
else:
    print(f"    人均道路面积对碳排放强度无显著影响")

print(f"  - financial_development系数: {results['coefficients'][6]:.6f} (p={results['p_values'][6]:.4f})")
if results['p_values'][6] < 0.1:
    fin_effect = (np.exp(results['coefficients'][6]) - 1) * 100
    direction = "增加" if results['coefficients'][6] > 0 else "降低"
    print(f"    金融发展水平显著{direction}碳排放强度")
else:
    print(f"    金融发展水平对碳排放强度无显著影响")
