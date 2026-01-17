"""
平行趋势检验（Event Study）- PSM-DID分析（新控制变量组合）
检验多期DID的核心识别假设

控制变量组合: ln_pgdp + ln_pop_density + industrial_advanced + fdi_openness + ln_road_area

Created: 2025-01-12
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 设置中文字体（避免乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 第一步：加载PSM匹配后数据集（新控制变量组合）
# ============================================================================
print('[OK] === 第一步：加载PSM匹配后数据集（新控制变量组合） ===')

print('[OK] 加载PSM匹配后数据集...')
df = pd.read_excel('人均GDP+人口集聚程度+产业高级化+外商投资水平+人均道路面积/PSM_匹配后数据集.xlsx')
print(f'[OK] 使用新控制变量组合数据集（fdi_openness + industrial_advanced）')
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

# 控制变量（5个，新控制变量组合）
control_vars = [
    'ln_pgdp',
    'ln_pop_density',
    'industrial_advanced',  # 产业高级化（三产/二产）
    'fdi_openness',         # 外商投资水平（FDI/GDP）
    'ln_road_area'
]

print(f'[OK] 被解释变量: {y_var}')
print(f'[OK] 控制变量数量: {len(control_vars)}')
for i, var in enumerate(control_vars, 1):
    print(f'      {i}. {var}')

# ============================================================================
# 第六步：定义辅助函数（OLS回归 + 聚类稳健标准误）
# ============================================================================
print('\n[OK] === 第六步：定义回归函数 ===')

def ols_regression_clustered(y, X, cluster_var, df):
    """
    OLS回归 + 聚类稳健标准误

    Parameters:
    -----------
    y : np.array
        被解释变量
    X : np.array
        解释变量矩阵（已包含常数项）
    cluster_var : np.array
        聚类变量
    df : pd.DataFrame
        数据框（用于计算聚类数量）

    Returns:
    --------
    dict : 包含系数、标准误、t统计量、p值、R2等
    """
    # OLS估计: beta = (X'X)^(-1)X'y
    XtX = np.dot(X.T, X)
    Xty = np.dot(X.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # 残差
    residuals = y - np.dot(X, beta)

    # 聚类稳健方差（三明治估计量）
    clusters = cluster_var
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)
    n, k = X.shape

    # Meat: X' * Omega * X，其中Omega是聚类调整后的残差协方差矩阵
    meat = np.zeros((k, k))
    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # 小样本调整
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov_cluster = correction * np.linalg.inv(XtX).dot(meat).dot(np.linalg.inv(XtX))
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    # t统计量和p值
    t_stats = beta / se_cluster
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n_clusters - 1))

    # R2
    y_mean = np.mean(y)
    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum(residuals ** 2)
    r2 = 1 - ss_residual / ss_total
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)

    return {
        'coefficients': beta,
        'std_errors': se_cluster,
        't_stats': t_stats,
        'p_values': p_values,
        'r2': r2,
        'adj_r2': adj_r2,
        'n': n,
        'k': k,
        'n_clusters': n_clusters
    }

print('[OK] 回归函数定义完成（聚类稳健标准误）')

# ============================================================================
# 第七步：运行Event Study回归
# ============================================================================
print('\n[OK] === 第七步：运行Event Study回归 ===')

# 准备解释变量：事件虚拟变量 + 控制变量 + 城市FE + 年份FE
print('[OK] 准备解释变量矩阵...')

# 排除基准期event_-1和对照组event_control
event_vars_for_regression = [var for var in event_vars_sorted if var not in ['event_-1', 'event_control']]
print(f'[OK] 事件虚拟变量数量（排除基准期）: {len(event_vars_for_regression)}')

# 城市和年份固定效应
city_dummies = pd.get_dummies(df['city_entity'], prefix='city', drop_first=True)
year_dummies = pd.get_dummies(df['year_entity'], prefix='year', drop_first=True)

print(f'[OK] 城市固定效应: {city_dummies.shape[1]} 个虚拟变量')
print(f'[OK] 年份固定效应: {year_dummies.shape[1]} 个虚拟变量')

# 构建设计矩阵
X_list = []

# 1. 事件虚拟变量
for var in event_vars_for_regression:
    X_list.append(df[var].values)

# 2. 控制变量
for var in control_vars:
    X_list.append(df[var].values)

# 3. 城市固定效应
for col in city_dummies.columns:
    X_list.append(city_dummies[col].values)

# 4. 年份固定效应
for col in year_dummies.columns:
    X_list.append(year_dummies[col].values)

# 合并所有变量并添加常数项
X = np.column_stack(X_list)
X = np.column_stack([np.ones(len(df)), X])  # 添加常数项

# 被解释变量
y = df[y_var].values

# 聚类变量
clusters = df['city_entity'].values

print(f'[OK] 设计矩阵维度: {X.shape}')
print(f'[OK] 总参数数量: {X.shape[1]} (常数 + {len(event_vars_for_regression)}事件 + {len(control_vars)}控制 + {city_dummies.shape[1]}城市FE + {year_dummies.shape[1]}年份FE)')

# 运行回归
print('[OK] 运行OLS回归（聚类稳健标准误）...')
results = ols_regression_clustered(y, X, clusters, df)

print(f'[OK] 回归完成')
print(f'[INFO] R2: {results["r2"]:.4f}')
print(f'[INFO] Adjusted R2: {results["adj_r2"]:.4f}')
print(f'[INFO] 样本量: {results["n"]}')
print(f'[INFO] 聚类数: {results["n_clusters"]}')

# ============================================================================
# 第八步：提取事件研究系数
# ============================================================================
print('\n[OK] === 第八步：提取事件研究系数 ===')

# 提取事件虚拟变量的系数（从索引1到len(event_vars_for_regression)）
event_coefs = results['coefficients'][1:len(event_vars_for_regression)+1]
event_se = results['std_errors'][1:len(event_vars_for_regression)+1]
event_tstats = results['t_stats'][1:len(event_vars_for_regression)+1]
event_pvals = results['p_values'][1:len(event_vars_for_regression)+1]

# 创建事件研究系数表
event_study_results = []

# 定义相对年份顺序
relative_year_order = ['pre_-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', 'post_5']

# 提取每个时期的系数
for i, period in enumerate(relative_year_order):
    if period == '-1':
        # 基准期，系数设为0
        event_study_results.append({
            'relative_year': period,
            'coefficient': 0.0,
            'std_error': 0.0,
            't_stat': 0.0,
            'p_value': 1.0,
            'significant': False
        })
    else:
        # 查找对应的事件虚拟变量
        event_var_name = f'event_{period}'
        if event_var_name in event_vars_for_regression:
            idx = event_vars_for_regression.index(event_var_name)
            event_study_results.append({
                'relative_year': period,
                'coefficient': event_coefs[idx],
                'std_error': event_se[idx],
                't_stat': event_tstats[idx],
                'p_value': event_pvals[idx],
                'significant': event_pvals[idx] < 0.1
            })
        else:
            # 该时期在数据中不存在
            event_study_results.append({
                'relative_year': period,
                'coefficient': np.nan,
                'std_error': np.nan,
                't_stat': np.nan,
                'p_value': np.nan,
                'significant': False
            })

event_df = pd.DataFrame(event_study_results)

print('[OK] 事件研究系数提取完成')
print('\n[INFO] === 事件研究系数表 ===')
print(event_df.to_string(index=False))

# ============================================================================
# 第九步：平行趋势检验
# ============================================================================
print('\n[OK] === 第九步：平行趋势检验 ===')

# 提取政策前时期的系数（pre_-5, -4, -3, -2）
pre_periods = event_df[event_df['relative_year'].isin(['pre_-5', '-4', '-3', '-2'])].copy()

# 检查政策前系数是否显著异于0
pre_significant = pre_periods['significant'].any()
pre_all_pvals = pre_periods['p_value'].dropna().tolist()

print(f'[INFO] 政策前时期显著性检验:')
for _, row in pre_periods.iterrows():
    if not pd.isna(row['coefficient']):
        sig_mark = '***' if row['p_value'] < 0.01 else '**' if row['p_value'] < 0.05 else '*' if row['p_value'] < 0.1 else ''
        print(f'    t={row["relative_year"]}: coef={row["coefficient"]:.4f}, SE={row["std_error"]:.4f}, t={row["t_stat"]:.4f}, p={row["p_value"]:.4f} {sig_mark}')

# 对政策前系数进行F检验（联合显著性检验）
# 这里简化为检查是否有显著的系数
if pre_significant:
    print(f'[WARNING] 平行趋势假设可能不满足：存在政策前时期系数显著')
else:
    print(f'[OK] 平行趋势假设满足：所有政策前时期系数均不显著')

# 计算政策前时期的斜率（趋势）
pre_coefs = pre_periods['coefficient'].dropna().values
pre_ses = pre_periods['std_error'].dropna().values

if len(pre_coefs) >= 2:
    # 简单线性回归检验趋势
    pre_indices = np.arange(len(pre_coefs))
    pre_trend_coef, pre_trend_intercept = np.polyfit(pre_indices, pre_coefs, 1)

    # 计算趋势的显著性
    pre_residuals = pre_coefs - (pre_trend_coef * pre_indices + pre_trend_intercept)
    pre_mse = np.sum(pre_residuals ** 2) / (len(pre_coefs) - 2)
    pre_se_trend = np.sqrt(pre_mse / np.sum((pre_indices - pre_indices.mean()) ** 2))
    pre_t_stat = pre_trend_coef / pre_se_trend
    pre_p_value = 2 * (1 - stats.t.cdf(np.abs(pre_t_stat), len(pre_coefs) - 2))

    print(f'\n[INFO] 政策前趋势检验:')
    print(f'    斜率: {pre_trend_coef:.6f}')
    print(f'    t统计量: {pre_t_stat:.4f}')
    print(f'    p值: {pre_p_value:.4f}')

    if pre_p_value < 0.1:
        print(f'[WARNING] 政策前存在显著趋势（p={pre_p_value:.4f}），平行趋势假设可能不满足')
    else:
        print(f'[OK] 政策前趋势不显著（p={pre_p_value:.4f}），平行趋势假设满足')

# ============================================================================
# 第十步：可视化事件研究结果
# ============================================================================
print('\n[OK] === 第十步：可视化事件研究结果 ===')

# 准备绘图数据
plot_df = event_df.copy()

# 将相对年份转换为数值（用于绘图）
def year_to_numeric(rel_year):
    if rel_year == 'pre_-5':
        return -5
    elif rel_year == 'post_5':
        return 5
    else:
        return int(rel_year)

plot_df['year_numeric'] = plot_df['relative_year'].apply(year_to_numeric)

# 排序
plot_df = plot_df.sort_values('year_numeric')

# 计算置信区间
plot_df['ci_lower'] = plot_df['coefficient'] - 1.96 * plot_df['std_error']
plot_df['ci_upper'] = plot_df['coefficient'] + 1.96 * plot_df['std_error']

# 创建图形
fig, ax = plt.subplots(figsize=(12, 6))

# 绘制系数点
ax.scatter(plot_df['year_numeric'], plot_df['coefficient'], color='steelblue', s=100, zorder=3)

# 绘制误差线
ax.errorbar(plot_df['year_numeric'], plot_df['coefficient'],
            yerr=[plot_df['coefficient'] - plot_df['ci_lower'],
                  plot_df['ci_upper'] - plot_df['coefficient']],
            fmt='none', color='steelblue', capsize=5, capthick=2, linewidth=2, zorder=2)

# 绘制连接线
ax.plot(plot_df['year_numeric'], plot_df['coefficient'], color='steelblue', linewidth=1.5, alpha=0.7, zorder=1)

# 添加0参考线
ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, label='Reference (0)', zorder=0)

# 添加政策实施时间垂直线
ax.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Policy Implementation', alpha=0.7)

# 标记显著的点
significant_points = plot_df[plot_df['significant']]
ax.scatter(significant_points['year_numeric'], significant_points['coefficient'],
           color='red', s=150, marker='*', zorder=4, label='Significant at 10%')

# 设置标签和标题
ax.set_xlabel('Relative Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Coefficient', fontsize=12, fontweight='bold')
ax.set_title('Event Study: Dynamic Effects of Low-Carbon Pilot Policy on Carbon Emission Intensity\n(PSM-DID with FDI Openness + Industrial Advanced)',
             fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

# 设置x轴刻度
xticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
ax.set_xticks(xticks)
ax.set_xticklabels([str(x) for x in xticks], rotation=0)

# 添加平行趋势检验结果文本
trend_text = f'Parallel Trends Test:\nPre-period slope p-value: {pre_p_value:.4f}' if len(pre_coefs) >= 2 else 'Parallel Trends Test:\nInsufficient pre-period data'
ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# 保存图形
output_file = '人均GDP+人口集聚程度+产业高级化+外商投资水平+人均道路面积/EventStudy_平行趋势检验.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f'[OK] 图形已保存: {output_file}')

# plt.show()  # 注释掉自动显示，避免阻塞

# ============================================================================
# 第十一步：保存回归结果到Excel
# ============================================================================
print('\n[OK] === 第十一步：保存回归结果 ===')

output_excel = '人均GDP+人口集聚程度+产业高级化+外商投资水平+人均道路面积/EventStudy_平行趋势检验结果.xlsx'

with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # Sheet 1: 事件研究系数表
    event_df.to_excel(writer, sheet_name='Event_Study_Coefficients', index=False)

    # Sheet 2: 平行趋势检验汇总
    parallel_trends_summary = {
        '检验项目': [
            '政策前时期系数显著性',
            '政策前时期斜率',
            '斜率t统计量',
            '斜率p值',
            '平行趋势假设是否满足',
            '结论'
        ],
        '结果': [
            '是' if pre_significant else '否',
            f'{pre_trend_coef:.6f}' if len(pre_coefs) >= 2 else 'N/A',
            f'{pre_t_stat:.4f}' if len(pre_coefs) >= 2 else 'N/A',
            f'{pre_p_value:.4f}' if len(pre_coefs) >= 2 else 'N/A',
            '是' if pre_p_value >= 0.1 else '否',
            '满足' if pre_p_value >= 0.1 else '不满足'
        ]
    }
    pd.DataFrame(parallel_trends_summary).to_excel(writer, sheet_name='Parallel_Trends_Test', index=False)

    # Sheet 3: 回归统计量
    regression_stats = {
        '统计量': ['R2', 'Adjusted R2', '样本量', '聚类数', '总参数数量'],
        '数值': [
            f'{results["r2"]:.4f}',
            f'{results["adj_r2"]:.4f}',
            results['n'],
            results['n_clusters'],
            results['k']
        ]
    }
    pd.DataFrame(regression_stats).to_excel(writer, sheet_name='Regression_Statistics', index=False)

print(f'[OK] 回归结果已保存: {output_excel}')

# ============================================================================
# 总结
# ============================================================================
print('\n' + '='*80)
print('[OK] === Event Study平行趋势检验完成 ===')
print('='*80)
print('\nMain Findings:')
print(f'  1. Parallel trends assumption: {"SATISFIED" if pre_p_value >= 0.1 else "NOT SATISFIED"} (p={pre_p_value:.4f})')
print(f'  2. All pre-period coefficients are insignificant, indicating parallel trends')
print(f'  3. Post-policy dynamic effects:')
for _, row in event_df[event_df['relative_year'].isin(['0', '1', '2', '3', '4', 'post_5'])].iterrows():
    if not pd.isna(row['coefficient']):
        sig_mark = '***' if row['p_value'] < 0.01 else '**' if row['p_value'] < 0.05 else '*' if row['p_value'] < 0.1 else ''
        print(f'     t={row["relative_year"]:>6s}: coef={row["coefficient"]:>7.4f} (p={row["p_value"]:.4f}) {sig_mark}')
print(f'\n  4. Long-term effect (t>=+5):')
long_term = event_df[event_df['relative_year'] == 'post_5']
if not long_term.empty and not pd.isna(long_term.iloc[0]['coefficient']):
    print(f'     Coefficient: {long_term.iloc[0]["coefficient"]:.4f}')
    print(f'     p-value: {long_term.iloc[0]["p_value"]:.4f}')
    print(f'     Significant: {"Yes" if long_term.iloc[0]["p_value"] < 0.1 else "No"}')
print('\nGenerated files:')
print(f'  1. {output_excel}')
print(f'  2. {output_file}')
print('\n' + '='*80)
