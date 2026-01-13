"""
Descriptive Statistics for Total Dataset
Variables related to low-carbon pilot policy experiment
"""

import pandas as pd
import numpy as np

def load_data():
    """Load total dataset"""
    print("[INFO] Loading total dataset...")
    df = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
    print(f"[OK] Dataset loaded: {len(df)} observations × {len(df.columns)} variables")
    return df

def calculate_descriptive_stats(df, variables, var_labels):
    """Calculate descriptive statistics for specified variables"""
    print("\n[INFO] Calculating descriptive statistics...")

    stats_list = []

    for var, label in zip(variables, var_labels):
        data = df[var].dropna()

        stats_dict = {
            'Variable': label,
            'Variable_Name': var,
            'N': len(data),
            'Mean': data.mean(),
            'Std_Dev': data.std(),
            'Min': data.min(),
            '25%': data.quantile(0.25),
            '50%': data.quantile(0.50),
            '75%': data.quantile(0.75),
            'Max': data.max()
        }

        stats_list.append(stats_dict)

    stats_df = pd.DataFrame(stats_list)
    return stats_df

def stats_by_group(df, var, var_label, group_var='treat'):
    """Calculate statistics by treatment/control group"""
    print(f"\n[INFO] Calculating statistics by {group_var}...")

    results = []

    for group in [0, 1]:
        group_label = 'Treatment Group' if group == 1 else 'Control Group'
        data = df[df[group_var] == group][var].dropna()

        results.append({
            'Group': group_label,
            'N': len(data),
            'Mean': data.mean(),
            'Std_Dev': data.std(),
            'Min': data.min(),
            'Max': data.max()
        })

    return pd.DataFrame(results)

def policy_adoption_stats(df):
    """Calculate policy adoption statistics"""
    print("\n[INFO] Calculating policy adoption statistics...")

    # Pilot cities by batch
    pilot_cities = df[df['pilot_year'] > 0].groupby('city_name')['pilot_year'].first()

    batch_counts = pilot_cities.value_counts().sort_index()

    print("\n[INFO] Pilot cities by batch:")
    for year, count in batch_counts.items():
        batch_name = {2010: 'First Batch (2010)',
                     2012: 'Second Batch (2012)',
                     2017: 'Third Batch (2017)'}.get(year, f'Batch {year}')
        print(f"  {batch_name}: {count} cities")

    return batch_counts

def year_distribution(df):
    """Show year distribution of observations"""
    print("\n[INFO] Calculating year distribution...")

    year_counts = df['year'].value_counts().sort_index()

    year_stats = []
    for year, count in year_counts.items():
        pilot_count = df[(df['year'] == year) & (df['treat'] == 1) &
                        (df['year'] >= df['pilot_year'])].shape[0]

        year_stats.append({
            'Year': year,
            'Total_Obs': count,
            'Cities_Under_Policy': pilot_count
        })

    return pd.DataFrame(year_stats)

def main():
    """Main execution"""
    print("="*70)
    print("Descriptive Statistics - Total Dataset")
    print("Low-Carbon Pilot Policy Experiment Variables")
    print("="*70)

    # Load data
    df = load_data()

    print(f"\n[INFO] Dataset Overview:")
    print(f"  Total observations: {len(df)}")
    print(f"  Total cities: {df['city_name'].nunique()}")
    print(f"  Year range: {df['year'].min()}-{df['year'].max()}")

    # Key variables for experiment
    key_variables = [
        'carbon_intensity',      # Carbon emission intensity
        'ln_carbon_intensity',   # Log-transformed CEI
        'pgdp',                  # GDP per capita
        'ln_pgdp',              # Log GDP per capita
        'pop_density',          # Population density
        'ln_pop_density',       # Log population density
        'industrial_advanced',  # Industrial advancement
        'fdi_openness',         # FDI openness
        'road_area',            # Road area per capita
        'ln_road_area'          # Log road area
    ]

    var_labels = [
        'Carbon Emission Intensity (CEI)',
        'Log CEI',
        'GDP Per Capita',
        'Log GDP Per Capita',
        'Population Density',
        'Log Population Density',
        'Industrial Advancement (Tertiary/Secondary)',
        'FDI Openness (FDI/GDP)',
        'Road Area Per Capita',
        'Log Road Area Per Capita'
    ]

    # Overall descriptive statistics
    print("\n" + "="*70)
    print("1. OVERALL DESCRIPTIVE STATISTICS")
    print("="*70)

    # Check which variables exist
    available_vars = [v for v in key_variables if v in df.columns]
    available_labels = [var_labels[key_variables.index(v)] for v in available_vars]

    overall_stats = calculate_descriptive_stats(df, available_vars, available_labels)

    # Print summary
    print("\n[INFO] Key variables summary:")
    for idx, row in overall_stats.iterrows():
        print(f"\n{row['Variable']} ({row['Variable_Name']}):")
        print(f"  N = {row['N']:.0f}")
        print(f"  Mean = {row['Mean']:.4f}")
        print(f"  Std. Dev. = {row['Std_Dev']:.4f}")
        print(f"  Min = {row['Min']:.4f}, Max = {row['Max']:.4f}")
        print(f"  Median = {row['50%']:.4f}")

    # Treatment vs Control comparison
    print("\n" + "="*70)
    print("2. TREATMENT VS CONTROL GROUP COMPARISON")
    print("="*70)

    dep_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density',
                'industrial_advanced', 'fdi_openness', 'ln_road_area']

    dep_labels = ['Log CEI', 'Log GDP Per Capita', 'Log Pop Density',
                  'Industrial Advancement', 'FDI Openness', 'Log Road Area']

    comparison_results = []

    for var, label in zip(dep_vars, dep_labels):
        if var in df.columns:
            group_stats = stats_by_group(df, var, label)

            treatment_mean = group_stats[group_stats['Group'] == 'Treatment Group']['Mean'].values[0]
            control_mean = group_stats[group_stats['Group'] == 'Control Group']['Mean'].values[0]

            print(f"\n{label}:")
            print(f"  Control Group: Mean = {control_mean:.4f}")
            print(f"  Treatment Group: Mean = {treatment_mean:.4f}")
            print(f"  Difference: {treatment_mean - control_mean:.4f}")

            comparison_results.append({
                'Variable': label,
                'Control_Mean': control_mean,
                'Treatment_Mean': treatment_mean,
                'Difference': treatment_mean - control_mean
            })

    comparison_df = pd.DataFrame(comparison_results)

    # Policy adoption statistics
    print("\n" + "="*70)
    print("3. POLICY ADOPTION STATISTICS")
    print("="*70)

    batch_counts = policy_adoption_stats(df)

    # Year distribution
    print("\n" + "="*70)
    print("4. YEAR DISTRIBUTION")
    print("="*70)

    year_dist = year_distribution(df)
    print(year_dist.to_string(index=False))

    # DID variable statistics
    print("\n" + "="*70)
    print("5. DID VARIABLE STATISTICS")
    print("="*70)

    if 'did' in df.columns:
        did_var = 'did'
    elif 'DID' in df.columns:
        did_var = 'DID'
    else:
        df['DID'] = df['treat'] * df['post']
        did_var = 'DID'

    did_count = (df[did_var] == 1).sum()
    post_count = (df['post'] == 1).sum()
    treat_count = (df['treat'] == 1).sum()

    print(f"\nDID Variable ({did_var}):")
    print(f"  Treatment group cities (treat=1): {treat_count:.0f} observations")
    print(f"  Post-policy period obs (post=1): {post_count:.0f} observations")
    print(f"  DID=1 observations: {did_count:.0f}")
    print(f"  Policy implementation rate: {(did_count/len(df)*100):.2f}%")

    # Save all results
    print("\n" + "="*70)
    print("6. SAVING RESULTS")
    print("="*70)

    output_file = '多时点DID_总数据集分析/描述性统计_总数据集.xlsx'

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Overall stats
        overall_stats.to_excel(writer, sheet_name='总体描述性统计', index=False)

        # Treatment vs Control
        comparison_df.to_excel(writer, sheet_name='处理组vs对照组', index=False)

        # Year distribution
        year_dist.to_excel(writer, sheet_name='年份分布', index=False)

        # Batch distribution
        batch_df = pd.DataFrame({
            'Batch': ['First Batch (2010)', 'Second Batch (2012)', 'Third Batch (2017)'],
            'Year': [2010, 2012, 2017],
            'Cities': [batch_counts.get(2010, 0),
                      batch_counts.get(2012, 0),
                      batch_counts.get(2017, 0)]
        })
        batch_df.to_excel(writer, sheet_name='批次分布', index=False)

        # Missing data summary
        missing_vars = [v for v in key_variables + ['treat', 'post', 'pilot_year']
                       if v in df.columns]
        missing_summary = pd.DataFrame({
            'Variable': missing_vars,
            'Missing_Count': [df[v].isnull().sum() for v in missing_vars],
            'Missing_Percentage': [df[v].isnull().sum() / len(df) * 100
                                   for v in missing_vars]
        })
        missing_summary.to_excel(writer, sheet_name='缺失值统计', index=False)

    print(f"\n[OK] All results saved to: {output_file}")

    print("\n" + "="*70)
    print("[OK] Descriptive statistics complete!")
    print("="*70)

if __name__ == "__main__":
    main()
