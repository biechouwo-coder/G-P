"""
Check industry structure raw data file
"""
import pandas as pd
import numpy as np

# Read the raw industry data
print("[INFO] Reading industry structure data...")
df_raw = pd.read_excel(r'c:\Users\HP\Desktop\毕业论文\原始数据\2000-2023地级市产业结构 .xlsx')

print(f"[INFO] Raw data shape: {df_raw.shape}")
print(f"[INFO] First few rows:")
print(df_raw.head(10))

print(f"\n[INFO] All columns:")
for i, col in enumerate(df_raw.columns):
    print(f"  Column {i}: {col}")

# Try to extract relevant columns by position
# Based on previous patterns, likely: 0=year, 1=city, 2=province, then industry shares
if df_raw.shape[1] >= 5:
    print(f"\n[INFO] Trying column positions 0-5:")
    for i in range(min(10, df_raw.shape[1])):
        print(f"  Column {i} sample values: {df_raw.iloc[:, i].head(3).tolist()}")
