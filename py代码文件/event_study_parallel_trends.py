"""
平行趋势检验（Event Study）- PSM-DID分析
检验多期DID的核心识别假设

Created: 2025-01-08
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 设置中文字体（避免乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 第一步：加载PSM匹配后数据集
# ============================================================================
print('[OK] === 第一步：加载PSM匹配后数据集 ===')

print('[OK] 加载PSM匹配后数据集...')
df = pd.read_excel('倾向得分匹配_匹配后数据集.xlsx')
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
# 第二步：计算相对年份（Relative Year）
# ============================================================================
print('\n[OK] === 第二步：计算相对年份 ===')

# 计算相对年份：年份 - 该城市的试点年份
# 对于对照组（treat=0），相对年份设为0（不生成事件虚拟变量）
df['relative_year'] = df.apply(
    lambda row: (row['year'] - row['pilot_year']) if row['treat'] == 1 else 0,
    axis=1
).astype(int)

print(f'[OK] 相对年份统计:')
print(f'    - 最小值: {df["relative_year"].min()} （政策前）')
print(f'    - 最大值: {df["relative_year"].max()} （政策后）')
print(f'    - 处理组相对年份分布:')
treat_group = df[df['treat'] == 1]
print(treat_group['relative_year'].value_counts().sort_index().head(10))

# ============================================================================
# 第三步：实施缩尾归并（Binning）[-5, +5]窗口
# ============================================================================
print('\n[OK] === 第三步：实施缩尾归并处理 ===')

# 将相对年份归并到[-5, +5]窗口
# 小于-5的归为Pre_-5，大于+5的归为Post_5
def bin_relative_year(rel_year, treat_status):
    """
    缩尾归并处理
    -5及以上：保持原值
    +5及以下：保持原值
    """
    if treat_status == 0:  # 对照组
        return 'control'
    elif rel_year <= -5:
        return 'pre_-5'
    elif rel_year >= 5:
        return 'post_5'
    else:
        return str(rel_year)  # -4, -3, -2, -1, 0, 1, 2, 3, 4

df['binned_relative_year'] = df.apply(
    lambda row: bin_relative_year(row['relative_year'], row['treat']),
    axis=1
)

print(f'[OK] 缩尾归并完成，窗口: [-5, +5]')
print(f'[OK] 归并后分布:')
print(df['binned_relative_year'].value_counts().sort_index())

# ============================================================================
# 第四步：生成事件虚拟变量（Event Dummies）
# ============================================================================
print('\n[OK] === 第四步：生成事件虚拟变量 ===')

# 创建事件虚拟变量（排除对照组和基准期-1）
event_dummies = pd.get_dummies(df['binned_relative_year'], prefix='event')

# 添加到数据集
df = pd.concat([df, event_dummies], axis=1)

# 列出所有事件虚拟变量
event_vars = [col for col in df.columns if col.startswith('event_')]
event_vars_sorted = sorted(event_vars,
                          key=lambda x: (
                              0 if x == 'event_pre_-5' else
                              1 if x == 'event_control' else
                              2 if x == 'event_post_5' else
                              int(x.replace('event_', '')) + 100  # -4 to +4
                          ))

print(f'[OK] 事件虚拟变量总数: {len(event_vars)}')
print(f'[OK] 事件虚拟变量列表（排序后）:')
for var in event_vars_sorted:
    n_obs = (df[var] == 1).sum()
    print(f'    - {var}: {n_obs} 观测值')

# ============================================================================
# 第五步：定义回归变量
# ============================================================================
print('\n[OK] === 第五步：定义回归模型 ===')

# 被解释变量
y_var = 'ln_carbon_intensity'

# 控制变量（6个，与PSM-DID基准回归一致）
control_vars = [
    'ln_pgdp',
    'ln_pop_density',
    'tertiary_share',
    'tertiary_share_sq',
    'ln_fdi',
    'ln_road_area'
]

# 事件虚拟变量（排除基准期event_-1）
event_vars_for_regression = [var for var in event_vars_sorted if var != 'event_-1']

print(f'[OK] 被解释变量: {y_var}')
print(f'[OK] 控制变量: {len(control_vars)} 个（与PSM-DID一致）')
print(f'[OK] 事件虚拟变量: {len(event_vars_for_regression)} 个（排除基准期event_-1）')
print(f'[OK] 基准期: event_-1（政策实施前一年）')

# ============================================================================
# 第六步：执行事件研究回归
# ============================================================================
print('\n[OK] === 第六步：执行事件研究回归 ===')

# 创建固定效应虚拟变量
city_dummies = pd.get_dummies(df['city_entity'], prefix='city', drop_first=True)
year_dummies = pd.get_dummies(df['year_entity'], prefix='year', drop_first=True)

# 准备数据
y = df[y_var].values

# 构建设计矩阵：事件虚拟变量 + 控制变量 + 固定效应
event_data = [df[var].values for var in event_vars_for_regression]
control_data = [df[var].values for var in control_vars]
X = np.column_stack([
    *event_data,
    *control_data,
    city_dummies.values,
    year_dummies.values
])

print(f'[INFO] 总变量数: {X.shape[1]}')
print(f'    - 事件虚拟变量: {len(event_vars_for_regression)}')
print(f'    - 控制变量: {len(control_vars)}')
print(f'    - 城市固定效应: {city_dummies.shape[1]}')
print(f'    - 年份固定效应: {year_dummies.shape[1]}')

# 定义回归函数（聚类标准误）
def ols_regression_clustered(y, X, cluster_var, df):
    """
    OLS回归 + 聚类稳健标准误（城市层面）
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

    # 聚类稳健标准误（城市层面）
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    # 计算夹心估计量
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

    # t统计量和p值
    t_stats = beta / se_cluster
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - k))

    # R2
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum(residuals**2)
    r2 = 1 - ss_res / ss_tot
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)

    return {
        'coefficients': beta,
        'std_errors': se_cluster,
        't_stats': t_stats,
        'p_values': p_values,
        'r2': r2,
        'adj_r2': adj_r2,
        'n_obs': n,
        'n_clusters': n_clusters,
        'n_vars': k
    }

# 执行回归
print('[INFO] 开始回归...')
results = ols_regression_clustered(y, X, 'city_entity', df)
print(f'[OK] 回归完成')
print(f'[INFO] R2: {results["r2"]:.4f}')
print(f'[INFO] 调整R2: {results["adj_r2"]:.4f}')
print(f'[INFO] 样本量: {results["n_obs"]}')
print(f'[INFO] 聚类数: {results["n_clusters"]}')

# ============================================================================
# 第七步：提取事件虚拟变量的系数
# ============================================================================
print('\n[OK] === 第七步：提取事件研究系数 ===')

# 创建结果表格
event_results = []

for var in event_vars_for_regression:
    idx = event_vars_for_regression.index(var) + 1  # +1 for constant

    # 解析相对年份
    var_name = var.replace('event_', '')
    if var_name == 'pre_-5':
        rel_year = -6
        display_name = '≤-5'
    elif var_name == 'post_5':
        rel_year = 6
        display_name = '≥+5'
    elif var_name == 'control':
        continue  # 跳过对照组
    else:
        rel_year = int(var_name)
        display_name = str(rel_year)

    coef = results['coefficients'][idx]
    se = results['std_errors'][idx]
    t_stat = results['t_stats'][idx]
    p_val = results['p_values'][idx]

    # 95%置信区间
    ci_lower = coef - 1.96 * se
    ci_upper = coef + 1.96 * se

    # 显著性标记
    if p_val < 0.01:
        sig = '***'
    elif p_val < 0.05:
        sig = '**'
    elif p_val < 0.1:
        sig = '*'
    else:
        sig = ''

    event_results.append({
        'relative_year': rel_year,
        'display_name': display_name,
        'variable': var,
        'coefficient': coef,
        'std_error': se,
        't_stat': t_stat,
        'p_value': p_val,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'significance': sig
    })

# 添加基准期-1（系数=0，标准误=0）
event_results.append({
    'relative_year': -1,
    'display_name': '-1',
    'variable': 'event_-1 (基准期)',
    'coefficient': 0.0,
    'std_error': 0.0,
    't_stat': np.nan,
    'p_value': np.nan,
    'ci_lower': 0.0,
    'ci_upper': 0.0,
    'significance': '(基准)'
})

# 排序
event_results = sorted(event_results, key=lambda x: x['relative_year'])

# 转换为DataFrame并保存
event_df = pd.DataFrame(event_results)
output_file = '事件研究_平行趋势检验结果.xlsx'
event_df.to_excel(output_file, index=False)
print(f'[OK] 事件研究结果已保存: {output_file}')

# 打印结果表格
print('\n[INFO] Event study coefficients results:')
print('='*80)
print('%-10s %-12s %-10s %-10s %-10s %-8s' % ('Rel Year', 'Coef', 'SE', 't-stat', 'p-value', 'Sig'))
print('-'*80)
for res in event_results:
    if res['relative_year'] == -1:
        print('%-10s %-12.4f %-10.4f %-10s %-10s %-8s' % (
            res["display_name"], res["coefficient"], res["std_error"], "Baseline", "", res["significance"]))
    else:
        print('%-10s %-12.4f %-10.4f %-10.4f %-10.4f %-8s' % (
            res["display_name"], res["coefficient"], res["std_error"], res["t_stat"], res["p_value"], res["significance"]))

# ============================================================================
# 第八步：平行趋势检验
# ============================================================================
print('\n[OK] === 第八步：平行趋势假设检验 ===')

# 提取政策前期的系数（-5, -4, -3, -2）
pre_trend_results = [res for res in event_results if res['relative_year'] < -1]

print('[INFO] 政策前期系数（平行趋势检验）:')
for res in pre_trend_results:
    sig_status = '显著' if res['p_value'] < 0.1 else '不显著'
    ci_contains_zero = '包含0' if (res['ci_lower'] < 0 < res['ci_upper']) else '不包含0'
    print(f'  t={res["display_name"]}: 系数={res["coefficient"]:.4f}, 95%CI=[{res["ci_lower"]:.4f}, {res["ci_upper"]:.4f}], {sig_status}, {ci_contains_zero}')

# 统计检验：前期系数是否联合不显著
pre_coeffs = [res['coefficient'] for res in pre_trend_results]
pre_ses = [res['std_error'] for res in pre_trend_results]

# 简单检验：检查是否有显著的趋势
# 计算前期的线性趋势
pre_years = [res['relative_year'] for res in pre_trend_results]
if len(pre_years) > 1:
    # 简单线性回归检验趋势
    from scipy import stats as scipy_stats
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(pre_years, pre_coeffs)
    print(f'\n[INFO] 政策前期线性趋势检验:')
    print(f'  斜率: {slope:.4f} (p={p_value:.4f})')
    if p_value > 0.1:
        print(f'  Conclusion: No significant trend in pre-period, parallel trend assumption supported')
    else:
        print(f'  Conclusion: Significant trend exists in pre-period, parallel trend assumption violated')

# ============================================================================
# 第九步：可视化事件研究图
# ============================================================================
print('\n[OK] === 第九步：生成事件研究图 ===')

# 准备绘图数据
plot_data = [res for res in event_results if res['relative_year'] != -999]
relative_years = [res['relative_year'] for res in plot_data]
coefficients = [res['coefficient'] for res in plot_data]
ci_lower = [res['ci_lower'] for res in plot_data]
ci_upper = [res['ci_upper'] for res in plot_data]

# 创建图形
fig, ax = plt.subplots(figsize=(14, 7))

# 绘制置信区间
ax.vlines(relative_years, ci_lower, ci_upper, colors='gray', linewidth=2, alpha=0.7, label='95%置信区间')

# 绘制系数点
# 根据显著性设置颜色
colors = ['red' if res['p_value'] < 0.05 else 'blue' if res['p_value'] < 0.1 else 'gray' for res in plot_data]
ax.scatter(relative_years, coefficients, s=100, c=colors, zorder=5, edgecolors='black', linewidths=1.5)

# 连接系数线（帮助观察趋势）
ax.plot(relative_years, coefficients, 'o-', color='steelblue', linewidth=1.5, alpha=0.5)

# 添加y=0参考线
ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, label='零线')

# 添加政策实施时间线（在-0.5位置）
ax.axvline(x=-0.5, color='red', linestyle='--', linewidth=2, label='政策实施', alpha=0.7)

# 设置坐标轴
ax.set_xlabel('相对年份（年）', fontsize=14, fontweight='bold')
ax.set_ylabel('系数值（对数变化）', fontsize=14, fontweight='bold')
ax.set_title('事件研究：低碳试点政策的动态效应（含95%置信区间）\n基准期：政策前一年（t=-1）',
             fontsize=16, fontweight='bold', pad=20)

# 设置x轴刻度
ax.set_xticks(relative_years)
ax.set_xticklabels([res['display_name'] for res in plot_data], rotation=45, ha='right')

# 添加网格
ax.grid(True, alpha=0.3, linestyle=':')

# 添加图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='gray', label='不显著'),
    Patch(facecolor='blue', label='* p<0.1'),
    Patch(facecolor='red', label='** p<0.05, *** p<0.01'),
    plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.5, label='零线'),
    plt.Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='政策实施'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

# 添加政策前后区域标注
ax.axvspan(-6, -1, alpha=0.1, color='blue', label='政策前期')
ax.axvspan(0, 6, alpha=0.1, color='red', label='政策后期')

# 标注显著性水平
for i, res in enumerate(plot_data):
    if res['relative_year'] == -1:
        continue
    if res['p_value'] < 0.01:
        ax.text(relative_years[i], coefficients[i], '***', fontsize=12, ha='center', va='bottom', fontweight='bold')
    elif res['p_value'] < 0.05:
        ax.text(relative_years[i], coefficients[i], '**', fontsize=12, ha='center', va='bottom', fontweight='bold')
    elif res['p_value'] < 0.1:
        ax.text(relative_years[i], coefficients[i], '*', fontsize=12, ha='center', va='bottom', fontweight='bold')

plt.tight_layout()

# 保存图形
fig_file = '事件研究_平行趋势检验图.png'
plt.savefig(fig_file, dpi=300, bbox_inches='tight')
print(f'[OK] 事件研究图已保存: {fig_file}')

plt.close()

print('\n' + '='*80)
print('[OK] 平行趋势检验（Event Study）分析完成！')
print('='*80)
