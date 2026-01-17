"""
Complete Data Merge Fix
Fix both population and GDP data for 70 cities that were missed in original merge
"""

import pandas as pd
import numpy as np

def load_data():
    """Load all datasets"""
    print("[INFO] Loading datasets...")

    # Total dataset (with missing data)
    df_total = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx')
    print(f"[OK] Total dataset: {len(df_total)} observations")

    # Population data
    df_pop = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')
    df_pop = df_pop.iloc[:, :9].copy()
    df_pop.columns = ['year', 'province', 'city_name', 'city_code', 'city_code_2',
                      'area', 'population', 'population_2', 'pop_density']
    df_pop = df_pop[(df_pop['year'] >= 2007) & (df_pop['year'] <= 2023)]
    print(f"[OK] Population data (2007-2023): {len(df_pop)} observations")

    # GDP data
    df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)
    df_gdp = df_gdp.iloc[:, :7].copy()
    df_gdp.columns = ['province', 'city_name', 'year', 'nominal_gdp', 'gdp_index', 'real_gdp', 'gdp_deflator']
    df_gdp = df_gdp[(df_gdp['year'] >= 2007) & (df_gdp['year'] <= 2023)]
    print(f"[OK] GDP data (2007-2023): {len(df_gdp)} observations")

    return df_total, df_pop, df_gdp

def fix_population_data(df_total, df_pop):
    """Fix missing population data"""
    print("\n[INFO] Fixing population data...")

    missing_before = df_total['population'].isnull().sum()
    print(f"[INFO] Missing population before: {missing_before}")

    # Merge population data
    df_pop_for_merge = df_pop[['year', 'city_name', 'population', 'pop_density']].copy()

    # Update missing population values
    for idx, row in df_total.iterrows():
        if pd.isnull(row['population']) or pd.isnull(row['pop_density']):
            # Find matching record
            match = df_pop_for_merge[
                (df_pop_for_merge['city_name'] == row['city_name']) &
                (df_pop_for_merge['year'] == row['year'])
            ]

            if len(match) > 0:
                df_total.at[idx, 'population'] = match['population'].values[0]
                df_total.at[idx, 'pop_density'] = match['pop_density'].values[0]

    missing_after = df_total['population'].isnull().sum()
    print(f"[OK] Population data updated")
    print(f"[INFO] Missing population after: {missing_after}")
    print(f"[INFO] Fixed: {missing_before - missing_after} observations")

    return df_total

def fix_gdp_data(df_total, df_gdp):
    """Fix missing GDP data and calculate derived variables"""
    print("\n[INFO] Fixing GDP data...")

    missing_gdp_before = df_total['gdp_real'].isnull().sum()
    print(f"[INFO] Missing gdp_real before: {missing_gdp_before}")

    # Merge GDP data
    df_gdp_for_merge = df_gdp[['year', 'city_name', 'real_gdp', 'gdp_deflator', 'nominal_gdp']].copy()

    # Update missing GDP values
    for idx, row in df_total.iterrows():
        if pd.isnull(row['gdp_real']):
            # Find matching record
            match = df_gdp_for_merge[
                (df_gdp_for_merge['city_name'] == row['city_name']) &
                (df_gdp_for_merge['year'] == row['year'])
            ]

            if len(match) > 0:
                df_total.at[idx, 'gdp_real'] = match['real_gdp'].values[0]
                df_total.at[idx, 'gdp_deflator'] = match['gdp_deflator'].values[0]
                df_total.at[idx, 'nominal_gdp'] = match['nominal_gdp'].values[0]

    missing_gdp_after = df_total['gdp_real'].isnull().sum()
    print(f"[OK] GDP data updated")
    print(f"[INFO] Missing gdp_real after: {missing_gdp_after}")
    print(f"[INFO] Fixed: {missing_gdp_before - missing_gdp_after} observations")

    return df_total

def calculate_derived_variables(df_total):
    """Calculate GDP per capita and log variables"""
    print("\n[INFO] Calculating derived variables...")

    # Calculate gdp_per_capita where population is available
    mask = df_total['population'].notnull() & df_total['gdp_real'].notnull()
    df_total.loc[mask, 'gdp_per_capita'] = df_total.loc[mask, 'gdp_real'] * 10000 / df_total.loc[mask, 'population']

    print(f"[OK] GDP per capita calculated for {mask.sum()} observations")
    print(f"[INFO] Missing gdp_per_capita: {df_total['gdp_per_capita'].isnull().sum()}")

    # Recalculate log variables
    # ln_pop_density
    mask_pop = df_total['pop_density'].notnull()
    df_total.loc[mask_pop, 'ln_pop_density'] = np.log(df_total.loc[mask_pop, 'pop_density'])

    # ln_pgdp
    mask_pgdp = df_total['gdp_per_capita'].notnull()
    df_total.loc[mask_pgdp, 'ln_pgdp'] = np.log(df_total.loc[mask_pgdp, 'gdp_per_capita'])

    print(f"[OK] Log variables recalculated")
    print(f"[INFO] Missing ln_pop_density: {df_total['ln_pop_density'].isnull().sum()}")
    print(f"[INFO] Missing ln_pgdp: {df_total['ln_pgdp'].isnull().sum()}")

    return df_total

def verify_results(df_original, df_fixed):
    """Verify fix results"""
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)

    # Check completeness
    print("\nData completeness:")

    key_vars = {
        'population': df_fixed['population'].isnull().sum(),
        'pop_density': df_fixed['pop_density'].isnull().sum(),
        'gdp_real': df_fixed['gdp_real'].isnull().sum(),
        'gdp_per_capita': df_fixed['gdp_per_capita'].isnull().sum(),
        'ln_pop_density': df_fixed['ln_pop_density'].isnull().sum(),
        'ln_pgdp': df_fixed['ln_pgdp'].isnull().sum()
    }

    for var, missing in key_vars.items():
        print(f"  {var}: {missing} missing")

    # Check regression-ready observations
    regression_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density',
                      'industrial_advanced', 'fdi_openness', 'ln_road_area']
    df_regression = df_fixed.dropna(subset=regression_vars)

    print(f"\nRegression-ready observations:")
    print(f"  Before fix: 3451")
    print(f"  After fix: {len(df_regression)}")
    print(f"  Improvement: {len(df_regression) - 3451} observations")

    # Cities added
    original_cities = df_original[df_original['ln_pgdp'].notnull()]['city_name'].nunique()
    fixed_cities = df_fixed[df_fixed['ln_pgdp'].notnull()]['city_name'].nunique()

    print(f"\nCities with complete data:")
    print(f"  Before fix: {original_cities}")
    print(f"  After fix: {fixed_cities}")
    print(f"  Cities added: {fixed_cities - original_cities}")

    return df_regression

def main():
    """Main execution"""
    print("="*70)
    print("Complete Data Merge Fix")
    print("Fix population and GDP data for 70 cities")
    print("="*70)

    # Load data
    df_total, df_pop, df_gdp = load_data()

    # Fix population
    df_total = fix_population_data(df_total, df_pop)

    # Fix GDP
    df_total = fix_gdp_data(df_total, df_gdp)

    # Calculate derived variables
    df_final = calculate_derived_variables(df_total)

    # Verify
    df_regression = verify_results(pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI.xlsx'), df_final)

    # Save
    print("\n[INFO] Saving corrected dataset...")
    output_path = '总数据集_2007-2023_完整版_无缺失FDI_完整版.xlsx'
    df_final.to_excel(output_path, index=False)
    print(f"[OK] Saved to: {output_path}")

    print("\n" + "="*70)
    print("[SUCCESS] Data merge fix completed!")
    print("="*70)

if __name__ == "__main__":
    main()
