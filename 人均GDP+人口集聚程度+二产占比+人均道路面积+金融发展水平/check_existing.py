"""
Check existing dataset with secondary share
"""
import pandas as pd
import numpy as np

# Read the existing dataset with secondary share
print("[INFO] Reading existing dataset with secondary share...")
df_existing = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\人均GDP+人口集聚程度+第二产业占GDP比重+外商投资水平+人均道路面积\总数据集_2007-2023_含第二产业比重.xlsx')

print(f"[INFO] Data shape: {df_existing.shape}")
print(f"\n[INFO] Columns:")
for i, col in enumerate(df_existing.columns):
    print(f"  {i}: {col}")

# Check if secondary_share exists
if 'secondary_share' in df_existing.columns or '第二产业占GDP比重' in df_existing.columns:
    print("\n[OK] Found secondary share variable")
    # Get the column name
    sec_col = None
    for col in df_existing.columns:
        if 'secondary' in col.lower() or '第二产业' in str(col):
            sec_col = col
            print(f"[INFO] Column name: {sec_col}")
            print(f"[INFO] Statistics:")
            print(df_existing[sec_col].describe())
            break

# Compare with current dataset
print("\n[INFO] Comparing with current dataset...")
df_current = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')

print(f"[INFO] Current dataset columns:")
for col in sorted(df_current.columns):
    print(f"  {col}")

# Check if we can derive secondary_share from existing variables
print("\n[INFO] Checking if we can calculate secondary_share...")
print(f"  Has tertiary_share: {'tertiary_share' in df_current.columns}")
print(f"  Has industrial_upgrading: {'industrial_upgrading' in df_current.columns}")
print(f"  Has industrial_advanced: {'industrial_advanced' in df_current.columns}")
