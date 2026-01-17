"""
Fix GDP Data Merge - Add Real GDP and GDP Deflator

Instead of relying on population data, directly merge real GDP and GDP deflator
from source file. Then we can work with GDP indicators that don't require population.
"""

import pandas as pd
import numpy as np

def load_data():
    """Load datasets"""
    print("[INFO] Loading datasets...")

    # Load total dataset
    df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
    print(f"[OK] Total dataset: {len(df_total)} observations")

    # Load GDP source data
    df_gdp_source = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
    df_gdp_source = df_gdp_source.iloc[:, :7].copy()
    df_gdp_source.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']

    # Filter for 2007-2023
    df_gdp_source = df_gdp_source[(df_gdp_source['year'] >= 2007) & (df_gdp_source['year'] <= 2023)]
    print(f"[OK] GDP source data (2007-2023): {len(df_gdp_source)} observations")

    return df_total, df_gdp_source

def merge_gdp_data(df_total, df_gdp_source):
    """Merge GDP data from source"""
    print("\n[INFO] Merging GDP data...")

    # Check current missing
    print(f"[INFO] Current gdp_real missing: {df_total['gdp_real'].isnull().sum()}")
    print(f"[INFO] Current gdp_deflator missing: {df_total['gdp_deflator'].isnull().sum()}")

    # Prepare GDP data for merge
    df_gdp_for_merge = df_gdp_source[['city_name', 'year', 'real_gdp', 'gdp_deflator', 'nominal_gdp']].copy()

    # Update existing GDP data where missing
    df_total_updated = df_total.copy()

    # For rows with missing gdp_real, fill from source
    for idx, row in df_total_updated.iterrows():
        if pd.isnull(row['gdp_real']) or pd.isnull(row['gdp_deflator']):
            # Find matching record in GDP source
            match = df_gdp_for_merge[
                (df_gdp_for_merge['city_name'] == row['city_name']) &
                (df_gdp_for_merge['year'] == row['year'])
            ]

            if len(match) > 0:
                df_total_updated.at[idx, 'real_gdp'] = match['real_gdp'].values[0]
                df_total_updated.at[idx, 'gdp_deflator'] = match['gdp_deflator'].values[0]
                df_total_updated.at[idx, 'nominal_gdp'] = match['nominal_gdp'].values[0]

    print(f"[OK] GDP data updated")
    print(f"[INFO] gdp_real missing after update: {df_total_updated['gdp_real'].isnull().sum()}")
    print(f"[INFO] gdp_deflator missing after update: {df_total_updated['gdp_deflator'].isnull().sum()}")

    return df_total_updated

def calculate_gdp_per_capita_with_population(df):
    """Calculate GDP per capita where population is available"""
    print("\n[INFO] Calculating GDP per capita (where population available)...")

    # Calculate gdp_per_capita only where population exists
    mask = df['population'].notnull()
    df.loc[mask, 'gdp_per_capita'] = df.loc[mask, 'real_gdp'] * 10000 / df.loc[mask, 'population']

    print(f"[OK] GDP per capita calculated for {mask.sum()} observations")
    print(f"[INFO] GDP per capita missing: {df['gdp_per_capita'].isnull().sum()}")

    return df

def recalculate_log_variables(df):
    """Recalculate log-transformed variables"""
    print("\n[INFO] Recalculating log-transformed variables...")

    # Recalculate ln_pgdp where gdp_per_capita is available
    mask_pgdp = df['gdp_per_capita'].notnull()
    df.loc[mask_pgdp, 'ln_pgdp'] = np.log(df.loc[mask_pgdp, 'gdp_per_capita'])

    print(f"[OK] Log variables recalculated")
    print(f"[INFO] ln_pgdp missing: {df['ln_pgdp'].isnull().sum()}")

    return df

def main():
    """Main execution"""
    print("="*70)
    print("Fix GDP Data Merge - Add Real GDP and GDP Deflator")
    print("="*70)

    # Load data
    df_total, df_gdp_source = load_data()

    # Merge GDP data
    df_updated = merge_gdp_data(df_total, df_gdp_source)

    # Calculate GDP per capita where population exists
    df_updated = calculate_gdp_per_capita_with_population(df_updated)

    # Recalculate log variables
    df_final = recalculate_log_variables(df_updated)

    # Verify results
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)

    print(f"\nData completeness:")
    print(f"  real_gdp missing: {df_final['real_gdp'].isnull().sum()}")
    print(f"  gdp_deflator missing: {df_final['gdp_deflator'].isnull().sum()}")
    print(f"  gdp_per_capita missing: {df_final['gdp_per_capita'].isnull().sum()}")
    print(f"  ln_pgdp missing: {df_final['ln_pgdp'].isnull().sum()}")

    # Check how many cities still can't be used in regression
    key_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density',
                'industrial_advanced', 'fdi_openness', 'ln_road_area']
    df_regression_ready = df_final.dropna(subset=key_vars)

    print(f"\nRegression-ready observations:")
    print(f"  Before fix: 3451 (from previous run)")
    print(f"  After fix: {len(df_regression_ready)}")
    print(f"  Improvement: {len(df_regression_ready) - 3451}")

    # Save
    print("\n[INFO] Saving corrected dataset...")
    output_path = '总数据集_2007-2023_完整版_无缺失FDI_修正GDP.xlsx'
    df_final.to_excel(output_path, index=False)
    print(f"[OK] Saved to: {output_path}")

    print("\n" + "="*70)
    print("[OK] Task completed!")
    print("="*70)

if __name__ == "__main__":
    main()
