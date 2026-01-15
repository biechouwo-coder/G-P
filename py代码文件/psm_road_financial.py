import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

class PropensityScoreMatcher:
    def __init__(self, data, covariates, caliper=0.05):
        """
        初始化倾向得分匹配器

        Parameters:
        -----------
        data : DataFrame
            包含处理变量和协变量的数据集
        covariates : list
            协变量列表
        caliper : float
            卡尺范围（倾向得分差异的最大允许值）
        """
        self.data = data.copy()
        self.covariates = covariates
        self.caliper = caliper
        self.propensity_scores = None
        self.matched_pairs = None

    def estimate_propensity_scores(self):
        """
        估计倾向得分（逐年Logit回归，非合并回归）
        """
        print(f"[INFO] 开始估计倾向得分...")
        print(f"[INFO] 协变量: {self.covariates}")
        print(f"[INFO] 卡尺范围: {self.caliper}")

        self.data['pscore'] = np.nan

        # 逐年估计倾向得分
        years = self.data['year'].unique()
        for year in years:
            year_data = self.data[self.data['year'] == year]

            # 检查是否有处理组和控制组
            if year_data['treat'].nunique() < 2:
                print(f"[WARNING] {year}年只有单一组别，跳过")
                continue

            X = year_data[self.covariates].values
            y = year_data['treat'].values

            # 移除缺失值
            mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X_clean = X[mask]
            y_clean = y[mask]

            if len(np.unique(y_clean)) < 2:
                print(f"[WARNING] {year}年处理后只有单一组别，跳过")
                continue

            # Logit回归
            logit_model = LogisticRegression(max_iter=1000, solver='lbfgs')
            logit_model.fit(X_clean, y_clean)

            # 预测倾向得分
            pscores = logit_model.predict_proba(X)[:, 1]
            self.data.loc[self.data['year'] == year, 'pscore'] = pscores

        self.propensity_scores = self.data['pscore'].values
        print(f"[INFO] 倾向得分估计完成")
        print(f"[INFO] 有效倾向得分数量: {self.data['pscore'].notnull().sum()}/{len(self.data)}")

    def perform_matching(self):
        """
        执行1:1最近邻匹配（有放回）
        """
        print(f"\n[INFO] 开始执行匹配...")

        # 分离处理组和控制组
        treat_data = self.data[self.data['treat'] == 1].copy()
        control_data = self.data[self.data['treat'] == 0].copy()

        print(f"[INFO] 处理组观测数: {len(treat_data)}")
        print(f"[INFO] 控制组观测数: {len(control_data)}")

        matched_pairs = []

        # 对每个处理组观测，找到最近的控制组观测
        for idx, treat_row in treat_data.iterrows():
            treat_pscore = treat_row['pscore']
            treat_year = treat_row['year']

            # 在同一年份的控制组中寻找匹配
            control_same_year = control_data[control_data['year'] == treat_year]

            if len(control_same_year) == 0:
                continue

            control_pscores = control_same_year['pscore'].values
            ps_diff = np.abs(control_pscores - treat_pscore)

            # 找到最近的控制组观测
            min_diff_idx = ps_diff.argmin()
            min_diff = ps_diff[min_diff_idx]

            # 检查是否在卡尺范围内
            if min_diff <= self.caliper:
                control_idx = control_same_year.index[min_diff_idx]
                matched_pairs.append({
                    'treat_idx': idx,
                    'control_idx': control_idx,
                    'pscore_diff': min_diff
                })

        self.matched_pairs = pd.DataFrame(matched_pairs)

        match_rate = len(self.matched_pairs) / len(treat_data) * 100
        print(f"[INFO] 匹配完成")
        print(f"[INFO] 成功匹配对数: {len(self.matched_pairs)}")
        print(f"[INFO] 匹配成功率: {match_rate:.2f}%")

        return self.matched_pairs

    def get_matched_dataset(self):
        """
        获取匹配后的数据集
        """
        if self.matched_pairs is None:
            raise ValueError("请先执行匹配（perform_matching方法）")

        # 获取匹配的处理组和控制组索引
        treat_indices = self.matched_pairs['treat_idx'].unique()
        control_indices = self.matched_pairs['control_idx'].unique()

        # 合并匹配的观测
        matched_data = pd.concat([
            self.data.loc[treat_indices],
            self.data.loc[control_indices]
        ]).sort_values(['city_name', 'year']).reset_index(drop=True)

        print(f"[INFO] 匹配后数据集形状: {matched_data.shape}")
        print(f"[INFO] 匹配后城市数: {matched_data['city_name'].nunique()}")

        return matched_data

    def check_balance(self):
        """
        检查匹配后的协变量平衡性
        """
        if self.matched_pairs is None:
            raise ValueError("请先执行匹配")

        matched_data = self.get_matched_dataset()

        print(f"\n[INFO] 协变量平衡性检验:")
        print(f"{'变量':<25} {'处理组均值':>12} {'控制组均值':>12} {'标准化差异':>12}")
        print(f"{'-'*65}")

        for var in self.covariates:
            treat_mean = matched_data[matched_data['treat'] == 1][var].mean()
            control_mean = matched_data[matched_data['treat'] == 0][var].mean()

            # 标准化差异 = (处理组均值 - 控制组均值) / 合并标准差
            treat_std = matched_data[matched_data['treat'] == 1][var].std()
            control_std = matched_data[matched_data['treat'] == 0][var].std()
            pooled_std = np.sqrt((treat_std**2 + control_std**2) / 2)

            std_diff = (treat_mean - control_mean) / pooled_std if pooled_std > 0 else 0

            print(f"{var:<25} {treat_mean:>12.6f} {control_mean:>12.6f} {std_diff:>12.6f}")

        # 检查倾向得分分布
        treat_pscore = matched_data[matched_data['treat'] == 1]['pscore']
        control_pscore = matched_data[matched_data['treat'] == 0]['pscore']

        print(f"\n[INFO] 倾向得分统计:")
        print(f"  处理组: 均值={treat_pscore.mean():.6f}, 标准差={treat_pscore.std():.6f}")
        print(f"  控制组: 均值={control_pscore.mean():.6f}, 标准差={control_pscore.std():.6f}")

        return matched_data

# 读取数据
df = pd.read_excel('人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/回归分析数据集.xlsx')
print(f"[INFO] 原始数据集形状: {df.shape}")
print(f"[INFO] 城市数: {df['city_name'].nunique()}")
print(f"[INFO] 年份范围: {df['year'].min()} - {df['year'].max()}")

# 定义协变量（控制变量）
covariates = ['ln_pgdp', 'ln_pop_density', 'industrial_advanced', 'ln_road_area', 'financial_development']

# 创建PSM匹配器（使用caliper=0.05，与主要规格一致）
psm_matcher = PropensityScoreMatcher(df, covariates=covariates, caliper=0.05)

# 估计倾向得分
psm_matcher.estimate_propensity_scores()

# 执行匹配
psm_matcher.perform_matching()

# 获取匹配后数据集
matched_data = psm_matcher.check_balance()

# 保存匹配后数据集
output_file = '人均GDP+人口集聚程度+产业高级化+人均道路面积+金融发展水平/PSM_匹配后数据集.xlsx'
matched_data.to_excel(output_file, index=False)
print(f"\n[OK] 匹配后数据集已保存到: {output_file}")

# 输出匹配统计信息
treat_cities = matched_data[matched_data['treat'] == 1]['city_name'].nunique()
control_cities = matched_data[matched_data['treat'] == 0]['city_name'].nunique()
print(f"\n[INFO] 匹配后样本统计:")
print(f"  总观测数: {len(matched_data)}")
print(f"  处理组城市数: {treat_cities}")
print(f"  控制组城市数: {control_cities}")
print(f"  总城市数: {matched_data['city_name'].nunique()}")
