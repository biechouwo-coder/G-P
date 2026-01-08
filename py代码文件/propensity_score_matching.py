"""
倾向得分匹配 (Propensity Score Matching, PSM) 分析
用于多期双重差分模型 (Multi-period DID) 的样本选择偏误控制

功能:
1. 逐年Logit回归估计倾向得分
2. 1:1最近邻匹配 (有放回)
3. 平衡性检验 (标准化偏差)
4. 生成匹配后的数据集

作者: Claude Code
日期: 2025-01-08
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve
import warnings
warnings.filterwarnings('ignore')

class PropensityScoreMatcher:
    """
    逐年倾向得分匹配器

    匹配策略:
    - 逐年Logit回归 (而非混合所有年份)
    - 1:1最近邻匹配 (有放回)
    - 卡尺范围: 0.02 (倾向得分差异限制, 更严格的标准)
    """

    def __init__(self, data, covariates, treatment_var='treat', year_var='year',
                 caliper=0.05, random_state=42):
        """
        初始化匹配器

        Parameters:
        -----------
        data : pd.DataFrame
            包含所有变量的面板数据
        covariates : list
            匹配协变量列表 (需要是对数变换后的变量)
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
            print(f"  {var:20s}: {n_miss:4d} ({pct_miss:5.2f}%)")

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
            # 正确计算空模型的对数似然值（仅含截距项的模型）
            p_bar = y.mean()  # 处理组平均比例
            n_treat = y.sum()
            n_control = len(y) - y.sum()

            # 空模型的偏差 (-2倍对数似然值)
            loglike_null = -2 * (n_treat * np.log(p_bar + 1e-10) + n_control * np.log(1 - p_bar + 1e-10))

            # 完整模型的偏差 (-2倍对数似然值)
            loglike_model = -2 * np.sum(y * np.log(pscores + 1e-10) + (1-y) * np.log(1-pscores + 1e-10))

            # McFadden's R2 = 1 - (loglike_model / loglike_null)
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
        print("[STEP 3] 执行1:1最近邻匹配 (有放回, 卡尺=0.02)")
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
                # 超出卡尺的样本不匹配（被剔除）

            # 统计匹配质量
            diffs = [pair[2] for pair in matched_pairs]
            n_within_caliper = sum(1 for d in diffs if d <= self.caliper)
            n_dropped = len(treat_indices) - len(matched_pairs)

            print(f"  匹配结果:")
            print(f"    处理组总数: {len(treat_indices)}")
            print(f"    成功匹配: {len(matched_pairs)} 对")
            print(f"    剔除样本: {n_dropped} 个 ({n_dropped/len(treat_indices)*100:.1f}%)")
            print(f"    卡尺内比例: {n_within_caliper/len(matched_pairs)*100:.1f}% (全部在卡尺内)")
            print(f"    平均PS差异: {np.mean(diffs):.4f}")
            print(f"    最大PS差异: {np.max(diffs):.4f}")
            print(f"    最小PS差异: {np.min(diffs):.4f}")

            # 保存匹配的索引 (原数据中的索引)
            original_indices = year_data.index.tolist()
            for treat_idx, control_idx, _ in matched_pairs:
                matched_indices.append(original_indices[treat_idx])
                matched_indices.append(original_indices[control_idx])

        # 生成匹配后的数据集
        self.matched_data = self.data.loc[matched_indices].copy()

        print(f"\n[OK] 匹配完成")
        print(f"  匹配后样本量: {len(self.matched_data)}")
        print(f"  (每个处理组个体对应1个对照, 共 {len(matched_indices)//2} 对)")

    def check_balance(self):
        """
        平衡性检验 (Standardized Bias)

        计算匹配前后协变量在处理组和对照组之间的标准化偏差
        偏差 < 10% 认为平衡良好
        """
        print("\n" + "="*60)
        print("[STEP 4] 平衡性检验 (标准化偏差)")
        print("="*60)

        balance_results = []

        for var in self.covariates:
            # 匹配前
            treat_before = self.data[self.data[self.treatment_var] == 1][var]
            control_before = self.data[self.data[self.treatment_var] == 0][var]

            mean_treat_before = treat_before.mean()
            mean_control_before = control_before.mean()
            std_pooled_before = np.sqrt((treat_before.var() + control_before.var()) / 2)

            bias_before = 100 * (mean_treat_before - mean_control_before) / std_pooled_before

            # 匹配后
            treat_after = self.matched_data[self.matched_data[self.treatment_var] == 1][var]
            control_after = self.matched_data[self.matched_data[self.treatment_var] == 0][var]

            mean_treat_after = treat_after.mean()
            mean_control_after = control_after.mean()
            std_pooled_after = np.sqrt((treat_after.var() + control_after.var()) / 2)

            bias_after = 100 * (mean_treat_after - mean_control_after) / std_pooled_after

            # 偏差减少比例
            bias_reduction = (bias_before - bias_after) / abs(bias_before) * 100 if bias_before != 0 else 0

            # t检验
            t_stat_before, p_val_before = stats.ttest_ind(treat_before, control_before)
            t_stat_after, p_val_after = stats.ttest_ind(treat_after, control_after)

            balance_results.append({
                '变量': var,
                '匹配前偏差': bias_before,
                '匹配后偏差': bias_after,
                '偏差减少%': bias_reduction,
                '匹配前t值': t_stat_before,
                '匹配前p值': p_val_before,
                '匹配后t值': t_stat_after,
                '匹配后p值': p_val_after,
                '平衡性': 'OK' if abs(bias_after) < 10 else '需检查'
            })

        self.balance_stats = pd.DataFrame(balance_results)

        print("\n平衡性检验结果:")
        print(self.balance_stats.to_string(index=False))

        n_balanced = (self.balance_stats['平衡性'] == 'OK').sum()
        print(f"\n平衡性统计: {n_balanced}/{len(self.covariates)} 个变量偏差 < 10%")

    def save_results(self, output_prefix='倾向得分匹配'):
        """
        保存匹配结果到Excel

        Parameters:
        -----------
        output_prefix : str
            输出文件前缀
        """
        print("\n" + "="*60)
        print("[STEP 5] 保存匹配结果")
        print("="*60)

        # 1. 保存匹配后的数据集
        matched_file = f'{output_prefix}_匹配后数据集.xlsx'
        self.matched_data.to_excel(matched_file, index=False)
        print(f"\n[OK] 已保存匹配后数据集: {matched_file}")

        # 2. 保存平衡性检验结果
        balance_file = f'{output_prefix}_平衡性检验.xlsx'
        self.balance_stats.to_excel(balance_file, index=False)
        print(f"[OK] 已保存平衡性检验: {balance_file}")

        # 3. 保存年度倾向得分统计
        yearly_stats = []
        for year, result in self.yearly_results.items():
            pscores = result['pscores']
            y = result['y']

            yearly_stats.append({
                '年份': year,
                '样本量': len(y),
                '处理组': int(y.sum()),
                '对照组': len(y) - int(y.sum()),
                '伪R²': result['mcfadden_r2'],
                'PS均值': pscores.mean(),
                'PS标准差': pscores.std(),
                'PS最小值': pscores.min(),
                'PS最大值': pscores.max()
            })

        yearly_stats_df = pd.DataFrame(yearly_stats)
        yearly_file = f'{output_prefix}_年度统计.xlsx'
        yearly_stats_df.to_excel(yearly_file, index=False)
        print(f"[OK] 已保存年度统计: {yearly_file}")

        # 4. 创建汇总报告
        summary_file = f'{output_prefix}_汇总报告.xlsx'
        with pd.ExcelWriter(summary_file, engine='openpyxl') as writer:
            self.balance_stats.to_excel(writer, sheet_name='平衡性检验', index=False)
            yearly_stats_df.to_excel(writer, sheet_name='年度统计', index=False)

            # 添加说明sheet
            summary_df = pd.DataFrame({
                '项目': ['匹配方法', '匹配比例', '卡尺值', '协变量数量',
                        '匹配前样本量', '匹配后样本量', '平衡性标准'],
                '数值': ['1:1最近邻匹配(有放回)', '1:1', '0.05', len(self.covariates),
                        len(self.data), len(self.matched_data), '标准化偏差 < 10%']
            })
            summary_df.to_excel(writer, sheet_name='匹配概况', index=False)

        print(f"[OK] 已保存汇总报告: {summary_file}")

    def run_full_matching(self):
        """
        执行完整的PSM流程
        """
        print("\n" + "="*60)
        print("倾向得分匹配 (PSM) 分析流程")
        print("="*60)

        # Step 1: 处理缺失值
        self.handle_missing_values()

        # Step 2: 估计倾向得分
        self.estimate_propensity_scores()

        # Step 3: 执行匹配
        self.perform_matching()

        # Step 4: 平衡性检验
        self.check_balance()

        # Step 5: 保存结果
        self.save_results()

        print("\n" + "="*60)
        print("[OK] PSM分析完成!")
        print("="*60)


def main():
    """
    主函数: 执行PSM分析
    """
    print("正在加载数据...")

    # 读取最终回归版数据
    df = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')

    print(f"数据集加载成功: {df.shape[0]} 行 × {df.shape[1]} 列")

    # 定义匹配协变量 (按照研究设计)
    covariates = [
        'ln_pgdp',            # 经济发展水平 (人均GDP, 对数)
        'ln_pop_density',     # 人口集聚程度 (人口密度, 对数) - 核心变量
        'tertiary_share',     # 第三产业占比 (产业结构)
        'tertiary_share_sq',  # 第三产业占比平方项 (产业结构非线性效应)
        'ln_fdi',             # 外商直接投资 (对外开放度, 对数)
        'ln_road_area'        # 人均道路面积 (基础设施, 对数)
    ]

    print("\n匹配协变量:")
    for i, var in enumerate(covariates, 1):
        print(f"  {i}. {var}")

    # 创建匹配器
    matcher = PropensityScoreMatcher(
        data=df,
        covariates=covariates,
        treatment_var='treat',
        year_var='year',
        caliper=0.02,  # 卡尺: 倾向得分差异 ≤ 0.02 (更严格的匹配标准)
        random_state=42
    )

    # 执行完整匹配流程
    matcher.run_full_matching()

    print("\n" + "="*60)
    print("后续工作建议:")
    print("="*60)
    print("1. 检查平衡性检验结果, 确保偏差 < 10%")
    print("2. 使用匹配后数据集运行 PSM-DID 回归")
    print("3. 对比匹配前后的DID系数变化")
    print("4. 进行敏感性分析 (检验不可观测混淆变量的影响)")
    print("="*60)

    return matcher


if __name__ == '__main__':
    matcher = main()
