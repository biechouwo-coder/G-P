"""
Prepare dataset with secondary_share variable
Calculate secondary industry share from tertiary share
"""
import pandas as pd
import numpy as np

# Read the main dataset with financial development
print("[INFO] Reading main dataset...")
df = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')

print(f"[INFO] Original data: {len(df)} observations × {len(df.columns)} variables")

# Check if tertiary_share exists
if 'tertiary_share' in df.columns:
    print("[OK] tertiary_share found in dataset")
    print(f"[INFO] tertiary_share range: {df['tertiary_share'].min():.4f} - {df['tertiary_share'].max():.4f}")

    # Calculate secondary_share
    # Assuming primary + secondary + tertiary = 1 (100%)
    # We need to find primary share or calculate secondary directly
    # For now, let's check if there's a pattern: secondary = 1 - tertiary - primary

    # Actually, we should look for raw industry data
    # Let's check if we have industrial_upgrading
    if 'industrial_upgrading' in df.columns:
        print("[OK] industrial_upgrading found")
        print(f"[INFO] industrial_upgrading range: {df['industrial_upgrading'].min():.4f} - {df['industrial_upgrading'].max():.4f}")

    # Check the original data file for industry structure
    print("\n[INFO] Checking original data files for industry shares...")

print("\n[INFO] Available variables:")
for col in sorted(df.columns):
    print(f"  {col}")

# Save for inspection
output_file = r'人均GDP+人口集聚程度+二产占比+人均道路面积+金融发展水平\数据检查.xlsx'
df.to_excel(output_file, index=False)
print(f"\n[OK] Saved data inspection to: {output_file}")
