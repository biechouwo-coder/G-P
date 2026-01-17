"""
CEADs数据倾向得分匹配 (Propensity Score Matching, PSM) 分析
控制变量组合: 人均GDP + 人口集聚程度 + 产业高级化 + 外商投资水平 + 金融发展水平

功能:
1. 逐年Logit回归估计倾向得分
2. 1:1最近邻匹配 (有放回)
3. 平衡性检验 (标准化偏差)
4. 生成匹配后的数据集

作者: Claude Code
日期: 2025-01-17
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

class PropensityScoreMatcher:
    """
    逐年倾向得分匹配器

    匹配策略:
    - 逐年Logit回归 (而非混合所有年份)
    - 1:1最近邻匹配 (有放回)
    - 卡尺范围: 0.02 (倾向得分差异限制)

    控制变量组合:
    - ln_pgdp: 人均GDP (对数)
    - ln_pop_density: 人口集聚程度 (对数)
    - industrial_advanced: 产业高级化 (三产/二产, 水平值)
    - fdi_openness: 外商投资水平 (FDI/GDP, 水平值)
    - financial_development: 金融发展水平 (水平值)
    """

    def __init__(self, data, covariates, treatment_var='treat', year_var='year',
                 caliper=0.02, random_state=42):
        """
        初始化匹配器

        Parameters:
        -----------
        data : pd.DataFrame
            包含所有变量的面板数据
        covariates : list
            匹配协变量列表
        treatment_var : str
            处理组标识变量名
        year_var : str
            年份变量名
        caliper : float
            卡尺值 (倾向得分差异上限)
        random_state : int
            随机种子
        """
        self.data = data.copy()
        self.covariates = covariates
        self.treatment_var = treatment_var
        self.year_var = year_var
        self.caliper = caliper
        self.random_state = random_state

        # 存储每年的匹配结果
        self.yearly_results = {}

        # 存储最终匹配结果
        self.matched_data = None

        # 存储平衡性检验结果
        self.balance_stats = None

    def handle_missing_values(self):
        """
        处理协变量中的缺失值

        策略:
        - 删除协变量有缺失的观测
        - 这确保了PSM估计的准确性
        """
        print("\n" + "="*60)
        print("[STEP 1] 处理缺失值")
        print("="*60)

        # 检查协变量缺失情况
        missing_before = self.data[self.covariates].isnull().sum()
        total_obs = len(self.data)

        print(f"\n原始样本量: {total_obs}")
        print("\n协变量缺失值统计:")
        for var in self.covariates:
            n_miss = missing_before[var]
            pct_miss = n_miss / total_obs * 100
            print(f"  {var:25s}: {n_miss:4d} ({pct_miss:5.2f}%)")

        # 删除协变量有缺失的行
        self.data = self.data.dropna(subset=self.covariates)

        missing_after = self.data[self.covariates].isnull().sum()
        total_obs_after = len(self.data)

        print(f"\n删除后样本量: {total_obs_after}")
        print(f"删除观测数: {total_obs - total_obs_after}")
        print(f"删除比例: {(total_obs - total_obs_after) / total_obs * 100:.2f}%")

        # 按年份统计处理组和对照组数量
        print("\n按年份统计处理组/对照组分布 (删除缺失值后):")
        year_treat_counts = self.data.groupby([self.year_var, self.treatment_var]).size().unstack(fill_value=0)
        print(year_treat_counts)

    def estimate_propensity_scores(self):
        """
        逐年估计倾向得分

        对每一年:
        1. 提取该年截面数据
        2. 运行Logit回归: treat ~ covariates
        3. 预测倾向得分
        4. 保存模型系数和预测结果
        """
        print("\n" + "="*60)
        print("[STEP 2] 逐年估计倾向得分 (Logit回归)")
        print("="*60)

        years = sorted(self.data[self.year_var].unique())

        for year in years:
            print(f"\n{'='*60}")
            print(f"年份: {year}")
            print(f"{'='*60}")

            # 提取该年数据
            year_data = self.data[self.data[self.year_var] == year].copy()

            # 准备X和y
            X = year_data[self.covariates].values
            y = year_data[self.treatment_var].values

            n_treat = int(y.sum())
            n_control = len(y) - n_treat

            print(f"  处理组: {n_treat} 个城市")
            print(f"  对照组: {n_control} 个城市")

            # 如果处理组或对照组为空，跳过
            if n_treat == 0:
                print(f"  [WARNING] 该年无处理组城市, 跳过")
                continue
            if n_control == 0:
                print(f"  [WARNING] 该年无对照组城市, 跳过")
                continue

            # 运行Logit回归
            logit_model = LogisticRegression(
                penalty='l2',
                C=1.0,
                solver='lbfgs',
                max_iter=1000,
                random_state=self.random_state
            )

            logit_model.fit(X, y)

            # 预测倾向得分
            pscores = logit_model.predict_proba(X)[:, 1]

            # 计算伪R2 (McFadden's R2)
            p_bar = y.mean()
            n_treat_sum = y.sum()
            n_control_sum = len(y) - y.sum()

            loglike_null = -2 * (n_treat_sum * np.log(p_bar + 1e-10) + n_control_sum * np.log(1 - p_bar + 1e-10))
            loglike_model = -2 * np.sum(y * np.log(pscores + 1e-10) + (1-y) * np.log(1-pscores + 1e-10))
            mcfadden_r2 = 1 - loglike_model / loglike_null if loglike_null != 0 else 0

            print(f"  Logit回归结果:")
            print(f"    伪R2 (McFadden): {mcfadden_r2:.4f}")
            print(f"    处理组平均PS: {pscores[y==1].mean():.4f}")
            print(f"    对照组平均PS: {pscores[y==0].mean():.4f}")
            print(f"    PS标准差: {pscores.std():.4f}")

            # 保存结果
            self.yearly_results[year] = {
                'data': year_data,
                'model': logit_model,
                'pscores': pscores,
                'X': X,
                'y': y,
                'n_treat': n_treat,
                'n_control': n_control,
                'mcfadden_r2': mcfadden_r2
            }

        print(f"\n[OK] 完成 {len(self.yearly_results)} 个年份的倾向得分估计")

    def perform_matching(self):
        """
        执行1:1最近邻匹配 (有放回)

        对每年的每个处理组个体:
        1. 计算与所有对照组的倾向得分差异
        2. 选择差异最小且在卡尺范围内的对照组个体
        3. 允许重复匹配 (有放回)
        """
        print("\n" + "="*60)
        print(f"[STEP 3] 执行1:1最近邻匹配 (有放回, 卡尺={self.caliper})")
        print("="*60)

        matched_indices = []

        for year, result in self.yearly_results.items():
            print(f"\n年份: {year}")

            year_data = result['data']
            pscores = result['pscores']
            y = result['y']

            # 分离处理组和对照组
            treat_indices = np.where(y == 1)[0]
            control_indices = np.where(y == 0)[0]

            print(f"  处理组: {len(treat_indices)} 个城市")
            print(f"  对照组候选: {len(control_indices)} 个城市")

            # 对每个处理组个体寻找匹配
            matched_pairs = []
            for treat_idx in treat_indices:
                treat_ps = pscores[treat_idx]

                # 计算与所有对照组的PS差异
                control_ps = pscores[control_indices]
                ps_diff = np.abs(control_ps - treat_ps)

                # 找到最小差异
                min_diff_idx = np.argmin(ps_diff)
                min_diff = ps_diff[min_diff_idx]

                # 检查是否在卡尺范围内
                if min_diff <= self.caliper:
                    control_idx = control_indices[min_diff_idx]
                    matched_pairs.append((treat_idx, control_idx, min_diff))

            # 统计匹配质量
            diffs = [pair[2] for pair in matched_pairs]
            n_within_caliper = sum(1 for d in diffs if d <= self.caliper)
            n_dropped = len(treat_indices) - len(matched_pairs)

            print(f"  成功匹配: {len(matched_pairs)} / {len(treat_indices)} ({len(matched_pairs)/len(treat_indices)*100:.1f}%)")
            print(f"  剔除样本: {n_dropped} ({n_dropped/len(treat_indices)*100:.1f}%)")

            if len(diffs) > 0:
                print(f"  PS差异统计:")
                print(f"    均值: {np.mean(diffs):.4f}")
                print(f"    中位数: {np.median(diffs):.4f}")
                print(f"    最大值: {np.max(diffs):.4f}")
                print(f"    最小值: {np.min(diffs):.4f}")

            # 收集匹配后的索引 (处理组 + 匹配的对照组)
            for treat_idx, control_idx, ps_diff in matched_pairs:
                matched_indices.append(year_data.index[treat_idx])
                matched_indices.append(year_data.index[control_idx])

        # 提取匹配后的样本
        self.matched_data = self.data.loc[matched_indices].copy()

        print(f"\n[OK] 匹配完成")
        print(f"  匹配后总样本: {len(self.matched_data)} 观测")
        print(f"  预期样本: {len(matched_indices)} 观测 (处理组+对照组)")

    def check_balance(self):
        """
        检查匹配后的平衡性

        计算标准化偏差 (Standardized Bias)
        """
        print("\n" + "="*60)
        print("[STEP 4] 平衡性检验 (标准化偏差)")
        print("="*60)

        balance_results = []

        # 对每个协变量计算匹配前后的标准化偏差
        for var in self.covariates:
            # 匹配前
            treat_mean_before = self.data[self.data[self.treatment_var]==1][var].mean()
            control_mean_before = self.data[self.data[self.treatment_var]==0][var].mean()
            sd_pooled_before = np.sqrt(
                (self.data[self.data[self.treatment_var]==1][var].var() +
                 self.data[self.data[self.treatment_var]==0][var].var()) / 2
            )
            bias_before = 100 * (treat_mean_before - control_mean_before) / sd_pooled_before

            # 匹配后
            treat_mean_after = self.matched_data[self.matched_data[self.treatment_var]==1][var].mean()
            control_mean_after = self.matched_data[self.matched_data[self.treatment_var]==0][var].mean()
            sd_pooled_after = np.sqrt(
                (self.matched_data[self.matched_data[self.treatment_var]==1][var].var() +
                 self.matched_data[self.matched_data[self.treatment_var]==0][var].var()) / 2
            )
            bias_after = 100 * (treat_mean_after - control_mean_after) / sd_pooled_after

            # 检验均值差异的显著性 (t检验)
            before_tstat, before_pval = stats.ttest_ind(
                self.data[self.data[self.treatment_var]==1][var].dropna(),
                self.data[self.data[self.treatment_var]==0][var].dropna(),
                equal_var=False
            )

            after_tstat, after_pval = stats.ttest_ind(
                self.matched_data[self.matched_data[self.treatment_var]==1][var].dropna(),
                self.matched_data[self.matched_data[self.treatment_var]==0][var].dropna(),
                equal_var=False
            )

            balance_results.append({
                'variable': var,
                'treat_mean_before': treat_mean_before,
                'control_mean_before': control_mean_before,
                'bias_before': bias_before,
                'before_pval': before_pval,
                'treat_mean_after': treat_mean_after,
                'control_mean_after': control_mean_after,
                'bias_after': bias_after,
                'after_pval': after_pval,
                'bias_reduction': (bias_before - bias_after) / abs(bias_before) * 100 if abs(bias_before) > 0 else 0
            })

            print(f"\n{var}:")
            print(f"  匹配前: 偏差={bias_before:7.2f}%, p={before_pval:.4f}")
            print(f"  匹配后: 偏差={bias_after:7.2f}%, p={after_pval:.4f}")
            print(f"  偏差减少: {balance_results[-1]['bias_reduction']:5.1f}%")

        self.balance_stats = pd.DataFrame(balance_results)

        # 统计满足平衡性标准的变量数
        n_balanced = (self.balance_stats['bias_after'].abs() < 10).sum()
        print(f"\n[OK] 平衡性检验完成")
        print(f"  满足平衡性标准 (|bias| < 10%): {n_balanced}/{len(self.covariates)}")

        return self.balance_stats

    def generate_reports(self, output_prefix=''):
        """
        生成Excel报告

        Parameters:
        -----------
        output_prefix : str
            输出文件前缀
        """
        print("\n" + "="*60)
        print("[STEP 5] 生成报告")
        print("="*60)

        # 1. 匹配后数据集
        output_file = f"{output_prefix}匹配后数据集.xlsx"
        self.matched_data.to_excel(output_file, index=False)
        print(f"[OK] 已保存: {output_file}")

        # 2. 平衡性检验结果
        balance_file = f"{output_prefix}平衡性检验.xlsx"
        with pd.ExcelWriter(balance_file, engine='openpyxl') as writer:
            # 总体平衡性
            self.balance_stats.to_excel(writer, sheet_name='总体平衡性', index=False)

            # 分年度平衡性
            yearly_balance = []
            for year, result in self.yearly_results.items():
                year_data = result['data']
                pscores = result['pscores']
                y = result['y']

                for var in self.covariates:
                    treat_mask = y == 1
                    control_mask = y == 0

                    if treat_mask.sum() == 0 or control_mask.sum() == 0:
                        continue

                    treat_mean = year_data[treat_mask][var].mean()
                    control_mean = year_data[control_mask][var].mean()
                    sd_pooled = np.sqrt(
                        (year_data[treat_mask][var].var() +
                         year_data[control_mask][var].var()) / 2
                    )
                    bias = 100 * (treat_mean - control_mean) / sd_pooled

                    yearly_balance.append({
                        'year': year,
                        'variable': var,
                        'treat_mean': treat_mean,
                        'control_mean': control_mean,
                        'std_bias': bias
                    })

            pd.DataFrame(yearly_balance).to_excel(writer, sheet_name='分年度平衡性', index=False)

        print(f"[OK] 已保存: {balance_file}")

        # 3. 年度统计
        yearly_stats = []
        for year, result in self.yearly_results.items():
            yearly_stats.append({
                'year': year,
                'n_total': len(result['y']),
                'n_treat': result['n_treat'],
                'n_control': result['n_control'],
                'mcfadden_r2': result['mcfadden_r2'],
                'treat_mean_ps': result['pscores'][result['y']==1].mean(),
                'control_mean_ps': result['pscores'][result['y']==0].mean()
            })

        stats_file = f"{output_prefix}年度统计.xlsx"
        pd.DataFrame(yearly_stats).to_excel(stats_file, index=False)
        print(f"[OK] 已保存: {stats_file}")

        # 4. 汇总报告
        summary_file = f"{output_prefix}汇总报告.xlsx"
        with pd.ExcelWriter(summary_file, engine='openpyxl') as writer:
            # Sheet 1: 概况
            summary_data = {
                '指标': [
                    '原始样本量',
                    '匹配后样本量',
                    '处理组数 (匹配后)',
                    '对照组数 (匹配后)',
                    '匹配年份数',
                    '协变量数',
                    '卡尺值'
                ],
                '数值': [
                    len(self.data),
                    len(self.matched_data),
                    (self.matched_data[self.treatment_var]==1).sum(),
                    (self.matched_data[self.treatment_var]==0).sum(),
                    len(self.yearly_results),
                    len(self.covariates),
                    self.caliper
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='概况', index=False)

            # Sheet 2: 平衡性汇总
            balance_summary = {
                '协变量': self.covariates,
                '匹配前偏差%': ['{:.2f}'.format(v) for v in self.balance_stats['bias_before'].values],
                '匹配后偏差%': ['{:.2f}'.format(v) for v in self.balance_stats['bias_after'].values],
                '偏差减少%': ['{:.1f}'.format(v) for v in self.balance_stats['bias_reduction'].values],
                '匹配后平衡': ['是' if abs(v) < 10 else '否' for v in self.balance_stats['bias_after'].values]
            }
            pd.DataFrame(balance_summary).to_excel(writer, sheet_name='平衡性汇总', index=False)

        print(f"[OK] 已保存: {summary_file}")


def main():
    """
    主函数: 执行完整的PSM流程
    """
    print("="*60)
    print("CEADs数据倾向得分匹配 (PSM) 分析")
    print("="*60)
    print("\n控制变量组合:")
    print("  1. ln_pgdp - 人均GDP (对数)")
    print("  2. ln_pop_density - 人口集聚程度 (对数)")
    print("  3. industrial_advanced - 产业高级化 (三产/二产, 水平值)")
    print("  4. fdi_openness - 外商投资水平 (FDI/GDP, 水平值)")
    print("  5. financial_development - 金融发展水平 (水平值)")
    print("="*60)

    # 读取数据
    print("\n[OK] 读取数据...")
    data = pd.read_excel(r'../CEADs_最终数据集_2007-2019_V2.xlsx')
    print(f"[OK] 原始数据: {len(data)} 观测 × {len(data.columns)} 变量")

    # 定义协变量
    covariates = [
        'ln_pgdp',                    # 人均GDP (对数)
        'ln_pop_density',             # 人口集聚程度 (对数)
        'industrial_advanced',        # 产业高级化 (三产/二产, 水平值)
        'fdi_openness',               # 外商投资水平 (FDI/GDP, 水平值)
        'financial_development'       # 金融发展水平 (水平值)
    ]

    print(f"\n[OK] 协变量数量: {len(covariates)}")
    print("[OK] 协变量列表:")
    for var in covariates:
        print(f"    - {var}")

    # 创建匹配器
    matcher = PropensityScoreMatcher(
        data=data,
        covariates=covariates,
        treatment_var='treat',
        year_var='year',
        caliper=0.02,
        random_state=42
    )

    # 执行匹配流程
    matcher.handle_missing_values()
    matcher.estimate_propensity_scores()
    matcher.perform_matching()
    matcher.check_balance()

    # 生成报告
    output_prefix = 'CEADs_PSM_'
    matcher.generate_reports(output_prefix=output_prefix)

    print("\n" + "="*60)
    print("[OK] CEADs PSM分析完成!")
    print("="*60)
    print("\n生成文件:")
    print(f"  1. {output_prefix}匹配后数据集.xlsx")
    print(f"  2. {output_prefix}平衡性检验.xlsx")
    print(f"  3. {output_prefix}年度统计.xlsx")
    print(f"  4. {output_prefix}汇总报告.xlsx")
    print("\n匹配后数据集可直接用于CEADs PSM-DID回归分析")


if __name__ == "__main__":
    main()
