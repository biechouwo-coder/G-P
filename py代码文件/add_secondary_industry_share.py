"""
Add Secondary Industry Share to Total Dataset

Secondary industry share data source: 原始数据/2000-2023地级市产业结构 .xlsx
Column: 第二产业占GDP比重 (column index 10)
"""

import pandas as pd
import numpy as np

def load_data():
    """Load both datasets"""
    print("[INFO] Loading datasets...")

    # Load total dataset
    df_total = pd.read_excel('总数据集_含第二产业比重/总数据集_2007-2023_含第二产业比重.xlsx')
    print(f"[OK] Total dataset loaded: {len(df_total)} observations")

    # Load industrial structure data
    df_industry = pd.read_excel('原始数据/2000-2023地级市产业结构 .xlsx', sheet_name=1)
    print(f"[OK] Industrial structure data loaded: {len(df_industry)} observations")

    return df_total, df_industry

def extract_secondary_share(df_industry):
    """Extract secondary industry share by column positions"""
    print("\n[INFO] Extracting secondary industry share...")

    # Extract relevant columns by position
    # Column 0: 年份, 1: 地级市, 10: 第二产业占GDP比重
    df_extracted = df_industry.iloc[:, [0, 1, 10]].copy()

    # Rename columns to English
    df_extracted.columns = ['year', 'city_name', 'secondary_share']

    # Filter for 2007-2023
    df_extracted = df_extracted[
        (df_extracted['year'] >= 2007) &
        (df_extracted['year'] <= 2023)
    ]

    print(f"[OK] Extracted {len(df_extracted)} observations (2007-2023)")
    print(f"[INFO] Cities: {df_extracted['city_name'].nunique()}")
    print(f"[INFO] Missing values: {df_extracted['secondary_share'].isnull().sum()}")
    print(f"[INFO] Missing rate: {df_extracted['secondary_share'].isnull().sum() / len(df_extracted) * 100:.2f}%")

    # Check data quality
    print(f"\n[INFO] Secondary share statistics:")
    print(f"  Mean: {df_extracted['secondary_share'].mean():.4f}")
    print(f"  Min: {df_extracted['secondary_share'].min():.4f}")
    print(f"  Max: {df_extracted['secondary_share'].max():.4f}")
    print(f"  Std: {df_extracted['secondary_share'].std():.4f}")

    return df_extracted

def merge_and_save(df_total, df_secondary):
    """Merge secondary share into total dataset and save"""
    print("\n[INFO] Merging datasets...")

    # Check original dataset
    print(f"[INFO] Original dataset columns: {len(df_total.columns)}")
    print(f"[INFO] Original observations: {len(df_total)}")

    # Merge on city_name and year
    df_merged = pd.merge(
        df_total,
        df_secondary[['city_name', 'year', 'secondary_share']],
        on=['city_name', 'year'],
        how='left'
    )

    print(f"[OK] Merged dataset: {len(df_merged)} observations")
    print(f"[INFO] Added column: secondary_share")
    print(f"[INFO] Missing values in secondary_share: {df_merged['secondary_share'].isnull().sum()}")
    print(f"[INFO] Missing rate: {df_merged['secondary_share'].isnull().sum() / len(df_merged) * 100:.2f}%")

    # Compare with existing tertiary_share
    if 'tertiary_share' in df_merged.columns:
        correlation = df_merged[['secondary_share', 'tertiary_share']].corr().iloc[0, 1]
        print(f"\n[INFO] Correlation between secondary_share and tertiary_share: {correlation:.4f}")

    # Show a few examples
    print(f"\n[INFO] Sample data with secondary_share:")
    sample = df_merged[df_merged['secondary_share'].notnull()][['city_name', 'year', 'secondary_share', 'tertiary_share']].head(5)
    print(sample.to_string(index=False))

    # Save updated dataset
    output_path = '总数据集_含第二产业比重/总数据集_2007-2023_含第二产业比重.xlsx'
    print(f"\n[INFO] Saving updated dataset...")

    df_merged.to_excel(output_path, index=False)

    print(f"[OK] Saved to: {output_path}")
    print(f"[INFO] Final dataset: {len(df_merged)} obs × {len(df_merged.columns)} variables")

    return df_merged

def main():
    """Main execution"""
    print("="*70)
    print("Add Secondary Industry Share to Total Dataset")
    print("="*70)

    # Load data
    df_total, df_industry = load_data()

    # Extract secondary share
    df_secondary = extract_secondary_share(df_industry)

    # Merge and save
    df_final = merge_and_save(df_total, df_secondary)

    print("\n" + "="*70)
    print("[OK] Task completed successfully!")
    print("="*70)
    print(f"\nFinal dataset columns: {len(df_final.columns)}")
    print(f"New variable added: secondary_share (第二产业占GDP比重)")

if __name__ == "__main__":
    main()
