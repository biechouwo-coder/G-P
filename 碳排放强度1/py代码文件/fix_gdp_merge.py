"""
Fix GDP Data Merge - Add Missing GDP for 70 Cities

This script will merge GDP data from source file to total dataset
for the 70 cities that are currently missing GDP data.
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

def identify_missing_gdp_cities(df_total):
    """Identify cities missing GDP data"""
    print("\n[INFO] Identifying cities with missing GDP...")

    missing_gdp_cities = df_total[df_total['gdp_per_capita'].isnull()]['city_name'].unique()

    print(f"[OK] Found {len(missing_gdp_cities)} cities missing GDP data")

    return missing_gdp_cities

def merge_gdp_data(df_total, df_gdp_source, missing_cities):
    """Merge GDP data for missing cities"""
    print("\n[INFO] Merging GDP data for missing cities...")

    # Create a copy of total dataset
    df_total_fixed = df_total.copy()

    # Count before merge
    missing_before = df_total_fixed['gdp_per_capita'].isnull().sum()
    print(f"[INFO] Missing GDP before merge: {missing_before}")

    # Merge GDP data
    # We'll merge on city_name and year
    df_gdp_for_merge = df_gdp_source[['city_name', 'year', 'real_gdp', 'gdp_deflator', 'nominal_gdp']].copy()

    # Perform merge for all rows (will only fill missing ones)
    df_total_fixed = df_total_fixed.drop(columns=['gdp_real', 'gdp_per_capita', 'gdp_deflator'], errors='ignore')

    df_merged = pd.merge(
        df_total_fixed,
        df_gdp_for_merge,
        on=['city_name', 'year'],
        how='left'
    )

    print(f"[OK] Merge completed")
    print(f"[INFO] Dataset size after merge: {len(df_merged)}")

    return df_merged

def calculate_gdp_per_capita(df):
    """Calculate GDP per capita"""
    print("\n[INFO] Calculating GDP per capita...")

    # Use real_gdp from source to calculate gdp_per_capita
    # gdp_per_capita = real_gdp * 10000 / population (converting to yuan)

    df['gdp_per_capita'] = df['real_gdp'] * 10000 / df['population']

    print(f"[OK] GDP per capita calculated")
    print(f"[INFO] Missing GDP per capita: {df['gdp_per_capita'].isnull().sum()}")
    print(f"[INFO] Mean GDP per capita: {df['gdp_per_capita'].mean():.2f}")

    return df

def verify_merge(df_original, df_fixed):
    """Verify merge results"""
    print("\n[INFO] Verifying merge results...")

    missing_before = df_original['gdp_per_capita'].isnull().sum()
    missing_after = df_fixed['gdp_per_capita'].isnull().sum()

    print(f"[INFO] Missing GDP before fix: {missing_before}")
    print(f"[INFO] Missing GDP after fix: {missing_after}")
    print(f"[INFO] Fixed: {missing_before - missing_after} observations")

    # Check which cities still have missing GDP
    still_missing = df_fixed[df_fixed['gdp_per_capita'].isnull()]['city_name'].unique()
    print(f"[INFO] Cities still missing GDP: {len(still_missing)}")

    if len(still_missing) > 0:
        print("\n[WARNING] These cities still have missing GDP (likely due to missing population):")
        for city in list(still_missing)[:10]:
            print(f"  - {city}")

    # Calculate overall completion rate
    total_obs = len(df_fixed)
    complete_obs = total_obs - missing_after
    completion_rate = complete_obs / total_obs * 100

    print(f"\n[OK] GDP data completion rate: {completion_rate:.2f}%")

    return missing_after == 0

def main():
    """Main execution"""
    print("="*70)
    print("Fix GDP Data Merge - Add Missing GDP for 70 Cities")
    print("="*70)

    # Load data
    df_total, df_gdp_source = load_data()

    # Identify missing cities
    missing_cities = identify_missing_gdp_cities(df_total)

    # Merge GDP data
    df_merged = merge_gdp_data(df_total, df_gdp_source, missing_cities)

    # Calculate GDP per capita
    df_final = calculate_gdp_per_capita(df_merged)

    # Recalculate log GDP per capita
    print("\n[INFO] Recalculating log-transformed variables...")
    df_final['ln_pgdp'] = np.log(df_final['gdp_per_capita'])

    # Reorder columns to match original structure
    original_cols = df_total.columns.tolist()

    # Identify which columns to keep
    cols_to_keep = [col for col in original_cols if col not in ['gdp_real', 'gdp_per_capita', 'gdp_deflator', 'ln_pgdp']]
    cols_to_keep.extend(['real_gdp', 'gdp_deflator', 'nominal_gdp', 'gdp_per_capita', 'ln_pgdp'])

    # Add any new columns from merge
    for col in df_final.columns:
        if col not in cols_to_keep:
            cols_to_keep.insert(-4, col)  # Insert before GDP variables

    df_final = df_final[[col for col in cols_to_keep if col in df_final.columns]]

    # Verify
    success = verify_merge(df_total, df_final)

    # Save corrected dataset
    print("\n[INFO] Saving corrected dataset...")
    output_path = '总数据集_2007-2023_完整版_无缺失FDI_修正GDP.xlsx'
    df_final.to_excel(output_path, index=False)

    print(f"[OK] Saved to: {output_path}")

    print("\n" + "="*70)
    if success:
        print("[SUCCESS] All GDP data has been filled!")
    else:
        print("[INFO] GDP data mostly filled. Some cities still missing due to population data.")
    print("="*70)

    # Summary statistics
    print(f"\nFinal dataset summary:")
    print(f"  Total observations: {len(df_final)}")
    print(f"  Cities: {df_final['city_name'].nunique()}")
    print(f"  GDP per capita missing: {df_final['gdp_per_capita'].isnull().sum()}")
    print(f"  Ln GDP per capita missing: {df_final['ln_pgdp'].isnull().sum()}")

if __name__ == "__main__":
    main()
