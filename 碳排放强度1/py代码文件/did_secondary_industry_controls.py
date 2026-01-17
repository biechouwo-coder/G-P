"""
Multi-period DID Analysis with Secondary Industry Share as Control

Control variables:
- ln_pgdp: Log GDP per capita
- ln_pop_density: Log population density
- secondary_share: Secondary industry share of GDP (NEW)
- fdi_openness: FDI openness (FDI/GDP)
- ln_road_area: Log road area per capita

Dataset: 总数据集_含第二产业比重/总数据集_2007-2023_含第二产业比重.xlsx
"""

import pandas as pd
import numpy as np
from scipy import stats

def load_and_prepare_data():
    """Load total dataset with secondary industry share"""
    print("[INFO] Loading total dataset with secondary industry share...")

    df = pd.read_excel('总数据集_含第二产业比重/总数据集_2007-2023_含第二产业比重.xlsx')

    print(f"[OK] Total dataset loaded: {len(df)} observations × {len(df.columns)} variables")
    print(f"[INFO] Cities: {df['city_name'].nunique()}")
    print(f"[INFO] Year range: {df['year'].min()}-{df['year'].max()}")

    # Drop rows with missing values in key variables
    print("\n[INFO] Dropping observations with missing values...")

    key_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density',
                'secondary_share', 'fdi_openness', 'ln_road_area',
                'treat', 'post']

    df_clean = df.dropna(subset=key_vars).copy()

    print(f"[OK] Clean dataset: {len(df_clean)} observations × {len(df_clean.columns)} variables")
    print(f"[INFO] Dropped {len(df) - len(df_clean)} observations with missing values")
    print(f"[INFO] Cities in clean data: {df_clean['city_name'].nunique()}")

    # Check secondary_share statistics
    print(f"\n[INFO] Secondary share statistics:")
    print(f"  Mean: {df_clean['secondary_share'].mean():.4f}")
    print(f"  Std: {df_clean['secondary_share'].std():.4f}")
    print(f"  Min: {df_clean['secondary_share'].min():.4f}")
    print(f"  Max: {df_clean['secondary_share'].max():.4f}")

    return df_clean

def create_did_variables(df):
    """Create DID and other necessary variables"""
    print("\n[INFO] Preparing DID variables...")

    # Use existing variables if they exist
    if 'did' in df.columns:
        df['DID'] = df['did']
    else:
        # Create DID interaction term
        df['DID'] = df['treat'] * df['post']

    # Ensure variables are numeric
    df['treat'] = pd.to_numeric(df['treat'], errors='coerce').fillna(0)
    df['post'] = pd.to_numeric(df['post'], errors='coerce').fillna(0)
    df['DID'] = pd.to_numeric(df['DID'], errors='coerce').fillna(0)

    # Create fixed effects dummies
    city_dummies = pd.get_dummies(df['city_name'], prefix='city', drop_first=True)
    year_dummies = pd.get_dummies(df['year'], prefix='year', drop_first=True)

    print(f"[OK] DID variables prepared")
    print(f"[INFO] Treatment group: {df['treat'].sum():.0f} cities")
    print(f"[INFO] Post-policy observations: {df['post'].sum():.0f}")
    print(f"[INFO] DID=1 observations: {df['DID'].sum():.0f}")

    return df, city_dummies, year_dummies

def ols_regression_clustered(y, X, cluster_var, df):
    """
    Manual OLS with cluster-robust standard errors
    """
    n, k = X.shape

    # Add constant
    X_const = np.column_stack([np.ones(n), X])

    # OLS estimation
    XtX = np.dot(X_const.T, X_const)
    Xty = np.dot(X_const.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # Residuals
    residuals = y - np.dot(X_const, beta)

    # Calculate R-squared
    y_mean = np.mean(y)
    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum(residuals ** 2)
    r_squared = 1 - (ss_residual / ss_total)

    # Cluster-robust variance (sandwich estimator)
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)
    n_clusters = len(unique_clusters)

    # Bread matrix
    bread = np.linalg.inv(XtX)

    # Meat matrix (clustered)
    meat = np.zeros((k + 1, k + 1))
    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X_const[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # Small-sample correction
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov_cluster = correction * bread.dot(meat).dot(bread)

    # Standard errors
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    # t-statistics
    t_stats = beta / se_cluster

    # p-values (two-tailed)
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n_clusters - 1))

    # 95% Confidence intervals
    ci_95 = 1.96 * se_cluster

    return {
        'coefficients': beta,
        'std_errors': se_cluster,
        't_stats': t_stats,
        'p_values': p_values,
        'ci_95': ci_95,
        'r_squared': r_squared,
        'n_clusters': n_clusters,
        'n_obs': n
    }

def run_did_regression(df, city_dummies, year_dummies):
    """Run multi-period DID regression"""
    print("\n[INFO] Running multi-period DID regression...")
    print("[INFO] Model: ln(CEI) = α + β·DID + controls + city FE + year FE")
    print("[INFO] Controls: ln_pgdp + ln_pop_density + secondary_share + fdi_openness + ln_road_area")

    # Define variables
    dependent_var = 'ln_carbon_intensity'

    # Control variables
    control_vars = ['ln_pgdp', 'ln_pop_density', 'secondary_share',
                   'fdi_openness', 'ln_road_area']

    # Prepare design matrix
    print(f"[INFO] Preparing design matrix...")

    X_did = df[['DID']].values
    X_controls = df[control_vars].values
    X_city_fe = city_dummies.values
    X_year_fe = year_dummies.values

    X = np.column_stack([X_did, X_controls, X_city_fe, X_year_fe])

    # Dependent variable
    y = df[dependent_var].values

    # Check for inf or nan
    print(f"[INFO] Checking for invalid values...")
    print(f"[INFO] NaN in X: {np.isnan(X).sum()}")
    print(f"[INFO] Inf in X: {np.isinf(X).sum()}")
    print(f"[INFO] NaN in y: {np.isnan(y).sum()}")
    print(f"[INFO] Inf in y: {np.isinf(y).sum()}")

    # Replace inf with nan, then drop rows with any nan
    X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
    y = np.nan_to_num(y, nan=0, posinf=0, neginf=0)

    # Run OLS with clustered SE
    results = ols_regression_clustered(y, X, 'city_name', df)

    # Extract coefficient names
    var_names = ['DID'] + control_vars + \
                [f'city_{c}' for c in city_dummies.columns] + \
                [f'year_{y}' for y in year_dummies.columns]

    print(f"\n[OK] Regression completed")
    print(f"[INFO] R-squared: {results['r_squared']:.4f}")
    print(f"[INFO] Observations: {results['n_obs']}")
    print(f"[INFO] Clusters (cities): {results['n_clusters']}")

    return results, var_names

def format_results_table(results, var_names):
    """Format results into summary table"""
    print("\n[INFO] Formatting results table...")

    # Create summary for main variables only
    main_vars = ['DID', 'ln_pgdp', 'ln_pop_density', 'secondary_share',
                'fdi_openness', 'ln_road_area']

    summary_data = []
    for var in main_vars:
        idx = var_names.index(var) + 1  # +1 for constant

        coef = results['coefficients'][idx]
        se = results['std_errors'][idx]
        t_stat = results['t_stats'][idx]
        p_val = results['p_values'][idx]

        # Significance stars
        if p_val < 0.01:
            stars = '***'
        elif p_val < 0.05:
            stars = '**'
        elif p_val < 0.1:
            stars = '*'
        else:
            stars = ''

        summary_data.append({
            'Variable': var,
            'Coefficient': coef,
            'Std_Error': se,
            't_Statistic': t_stat,
            'p_Value': p_val,
            'Significance': stars
        })

    summary_df = pd.DataFrame(summary_data)

    return summary_df

def save_results(summary_df, results):
    """Save regression results to Excel"""
    print("\n[INFO] Saving results...")

    output_path = '总数据集_含第二产业比重/DID_回归结果_第二产业控制.xlsx'

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main results
        summary_df.to_excel(writer, sheet_name='回归结果', index=False)

        # Model fit statistics
        fit_stats = pd.DataFrame({
            '指标': ['R-squared', 'Observations', 'Clusters (Cities)'],
            '数值': [f"{results['r_squared']:.4f}",
                   f"{results['n_obs']:.0f}",
                   f"{results['n_clusters']:.0f}"]
        })
        fit_stats.to_excel(writer, sheet_name='模型拟合', index=False)

    print(f"[OK] Results saved to: {output_path}")

def main():
    """Main execution"""
    print("="*70)
    print("Multi-period DID Analysis - With Secondary Industry Share")
    print("Control Variables: ln_pgdp + ln_pop_density + secondary_share +")
    print("                  fdi_openness + ln_road_area")
    print("="*70)

    # Load data
    df = load_and_prepare_data()

    # Create variables
    df, city_dummies, year_dummies = create_did_variables(df)

    # Run regression
    results, var_names = run_did_regression(df, city_dummies, year_dummies)

    # Format results
    summary_df = format_results_table(results, var_names)

    # Save results
    save_results(summary_df, results)

    # Print main results
    print("\n" + "="*70)
    print("MAIN RESULTS - DID COEFFICIENT")
    print("="*70)

    did_idx = var_names.index('DID') + 1  # +1 for constant
    did_coef = results['coefficients'][did_idx]
    did_se = results['std_errors'][did_idx]
    did_t = results['t_stats'][did_idx]
    did_p = results['p_values'][did_idx]

    print(f"\nDID Coefficient: {did_coef:.4f}")
    print(f"Std. Error: {did_se:.4f}")
    print(f"t-statistic: {did_t:.4f}")
    print(f"p-value: {did_p:.4f}")

    if did_p < 0.01:
        sig = '*** (p < 0.01)'
    elif did_p < 0.05:
        sig = '** (p < 0.05)'
    elif did_p < 0.1:
        sig = '* (p < 0.1)'
    else:
        sig = 'not significant'

    print(f"Significance: {sig}")
    print("\nInterpretation:")
    if did_p < 0.1:
        effect_pct = (np.exp(did_coef) - 1) * 100
        print(f"Low-carbon pilot policy has a {sig} effect on CEI")
        print(f"Estimated effect: {effect_pct:.2f}% change")
    else:
        print("Low-carbon pilot policy has NO statistically significant effect on CEI")

    # Print control variables results
    print("\n" + "="*70)
    print("CONTROL VARIABLES RESULTS")
    print("="*70)

    control_vars = ['ln_pgdp', 'ln_pop_density', 'secondary_share',
                   'fdi_openness', 'ln_road_area']

    for var in control_vars:
        idx = var_names.index(var) + 1
        coef = results['coefficients'][idx]
        p_val = results['p_values'][idx]

        if p_val < 0.01:
            sig = '***'
        elif p_val < 0.05:
            sig = '**'
        elif p_val < 0.1:
            sig = '*'
        else:
            sig = ''

        print(f"{var:20s}: {coef:8.4f} ({sig})")

    print("\n" + "="*70)
    print("[OK] Analysis complete!")
    print("="*70)

if __name__ == "__main__":
    main()
