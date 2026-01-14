import pandas as pd
import numpy as np

# Read financial development data (use corrected version with pop_density fix)
df_main = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_修正pop_density.xlsx')
print(f"[INFO] Main dataset shape: {df_main.shape}")
print(f"[INFO] Main dataset columns: {list(df_main.columns)}")
print(f"[INFO] Year range: {df_main['year'].min()} - {df_main['year'].max()}")
print(f"[INFO] Unique cities: {df_main['city_name'].nunique()}")

# Read financial development data
df_fin = pd.read_excel('原始数据/金融发展水平（2003-2023）236缺失.xlsx')
print(f"\n[INFO] Financial data shape: {df_fin.shape}")

# Extract relevant columns by position (avoid Chinese encoding issues)
# Column 0: Year, Column 2: City, Column 9: Financial development level
df_fin_extracted = df_fin.iloc[:, [0, 2, 9]]
df_fin_extracted.columns = ['year', 'city_name', 'financial_development']

print(f"[INFO] Extracted financial data shape: {df_fin_extracted.shape}")
print(f"[INFO] Financial data year range: {df_fin_extracted['year'].min()} - {df_fin_extracted['year'].max()}")
print(f"[INFO] Unique cities in financial data: {df_fin_extracted['city_name'].nunique()}")

# Check for missing values in financial development
missing_count = df_fin_extracted['financial_development'].isnull().sum()
total_count = len(df_fin_extracted)
missing_rate = (missing_count / total_count) * 100
print(f"\n[INFO] Missing financial_development values: {missing_count}/{total_count} ({missing_rate:.2f}%)")

# Merge with main dataset using left join (preserve only main dataset observations)
df_merged = pd.merge(df_main, df_fin_extracted, on=['city_name', 'year'], how='left')

print(f"\n[INFO] Merged dataset shape: {df_merged.shape}")
print(f"[INFO] New columns added: {[col for col in df_merged.columns if col not in df_main.columns]}")

# Check merge quality
print(f"\n[INFO] Checking merge quality...")
print(f"  - Cities in main only: {df_main[~df_main['city_name'].isin(df_fin_extracted['city_name'])]['city_name'].nunique()}")
print(f"  - Cities in financial only: {df_fin_extracted[~df_fin_extracted['city_name'].isin(df_main['city_name'])]['city_name'].nunique()}")

# Check missing financial_development in merged dataset
missing_after_merge = df_merged['financial_development'].isnull().sum()
print(f"\n[INFO] Missing financial_development after merge: {missing_after_merge}/{len(df_merged)}")

# Check if main dataset observations are preserved
main_obs_before = len(df_main)
main_obs_after = df_merged.dropna(subset=df_main.columns).shape[0]
print(f"\n[INFO] Main dataset observations preserved: {main_obs_after}/{main_obs_before}")

if main_obs_after != main_obs_before:
    print("[WARNING] Some observations from main dataset were lost during merge!")
else:
    print("[OK] All main dataset observations preserved")

# Show sample of merged data
print(f"\n[INFO] Sample of merged data (first 10 rows):")
print(df_merged[['city_name', 'year', 'financial_development']].head(10))

# Check for major cities
major_cities = ['上海市', '北京市', '广州市', '深圳市']
print(f"\n[INFO] Major cities financial development data:")
for city in major_cities:
    city_data = df_merged[df_merged['city_name'] == city][['year', 'financial_development']].dropna()
    if len(city_data) > 0:
        print(f"  {city}: {len(city_data)} observations, range {city_data['financial_development'].min():.4f} - {city_data['financial_development'].max():.4f}")
    else:
        print(f"  {city}: NO DATA")

# Save merged dataset
output_file = '总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx'
df_merged.to_excel(output_file, index=False)
print(f"\n[OK] Merged dataset saved to: {output_file}")
