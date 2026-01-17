"""
Merge secondary_share from existing dataset into current dataset
"""
import pandas as pd
import numpy as np

print("="*60)
print("Merge secondary_share variable")
print("="*60)

# Read current dataset (with financial_development)
print("\n[INFO] Reading current dataset (with financial_development)...")
df_current = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')
print(f"[OK] Current data: {len(df_current)} observations × {len(df_current.columns)} variables")

# Read existing dataset (with secondary_share)
print("\n[INFO] Reading existing dataset (with secondary_share)...")
df_existing = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\人均GDP+人口集聚程度+第二产业占GDP比重+外商投资水平+人均道路面积\总数据集_2007-2023_含第二产业比重.xlsx')
print(f"[OK] Existing data: {len(df_existing)} observations × {len(df_existing.columns)} variables")

# Extract secondary_share
print("\n[INFO] Extracting secondary_share from existing dataset...")
df_secondary = df_existing[['city_name', 'year', 'secondary_share']].copy()
print(f"[INFO] secondary_share statistics:")
print(f"  Count: {df_secondary['secondary_share'].notna().sum()}")
print(f"  Mean: {df_secondary['secondary_share'].mean():.4f}")
print(f"  Min: {df_secondary['secondary_share'].min():.4f}")
print(f"  Max: {df_secondary['secondary_share'].max():.4f}")

# Merge into current dataset
print("\n[INFO] Merging secondary_share into current dataset...")
df_merged = pd.merge(
    df_current,
    df_secondary,
    on=['city_name', 'year'],
    how='left'
)

print(f"[OK] Merged data: {len(df_merged)} observations × {len(df_merged.columns)} variables")

# Check merge quality
print("\n[INFO] Checking merge quality...")
missing_secondary = df_merged['secondary_share'].isnull().sum()
print(f"  Missing secondary_share: {missing_secondary} ({missing_secondary/len(df_merged)*100:.2f}%)")

if missing_secondary > 0:
    print(f"\n[WARNING] Some observations have missing secondary_share")
    print(f"[INFO] These will be handled by PSM missing value handler")

# Save merged dataset
output_file = r'c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_含二产占比_含金融发展水平.xlsx'
df_merged.to_excel(output_file, index=False)
print(f"\n[OK] Saved merged dataset to: {output_file}")

# Summary
print("\n" + "="*60)
print("Summary")
print("="*60)
print(f"Final dataset: {len(df_merged)} observations × {len(df_merged.columns)} variables")
print(f"\nVariables for PSM:")
print(f"  1. ln_pgdp -人均GDP (对数)")
print(f"  2. ln_pop_density - 人口集聚程度 (对数)")
print(f"  3. secondary_share - 二产占比 (水平值)")
print(f"  4. ln_road_area - 人均道路面积 (对数)")
print(f"  5. financial_development - 金融发展水平 (水平值)")
print(f"\nReady for PSM analysis!")
