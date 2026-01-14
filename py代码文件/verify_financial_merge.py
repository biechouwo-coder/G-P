import pandas as pd

# Read merged dataset
df_merged = pd.read_excel('总数据集_2007-2023_完整版_无缺失FDI_修正pop_density_添加金融发展水平.xlsx')

print(f"[INFO] Merged dataset shape: {df_merged.shape}")
print(f"[INFO] Year range: {df_merged['year'].min()} - {df_merged['year'].max()}")
print(f"[INFO] Unique cities: {df_merged['city_name'].nunique()}")

# Check missing financial_development
missing_fin = df_merged['financial_development'].isnull().sum()
total_obs = len(df_merged)
missing_rate = (missing_fin / total_obs) * 100
print(f"\n[INFO] Missing financial_development: {missing_fin}/{total_obs} ({missing_rate:.2f}%)")

if missing_rate < 5:
    print("[OK] Missing rate is below 5% threshold")
else:
    print(f"[WARNING] Missing rate ({missing_rate:.2f}%) exceeds 5% threshold")

# Check which cities are missing financial data
cities_missing = df_merged[df_merged['financial_development'].isnull()]['city_name'].unique()
print(f"\n[INFO] Cities missing any financial data: {len(cities_missing)}")

if len(cities_missing) > 0:
    print(f"[INFO] Cities with missing financial development data:")
    for city in cities_missing[:20]:  # Show first 20
        city_obs = df_merged[df_merged['city_name'] == city]
        missing_count = city_obs['financial_development'].isnull().sum()
        print(f"  {city}: {missing_count} missing years")

# Check major cities have complete data
major_cities = ['上海市', '北京市', '广州市', '深圳市', '杭州市', '南京市', '成都市', '武汉市']
print(f"\n[INFO] Major cities financial development coverage:")
for city in major_cities:
    city_data = df_merged[df_merged['city_name'] == city]
    total_years = len(city_data)
    valid_years = city_data['financial_development'].notnull().sum()
    if total_years > 0:
        coverage = (valid_years / total_years) * 100
        print(f"  {city}: {valid_years}/{total_years} years ({coverage:.1f}%)")

# Verify key variables are not missing
key_vars = ['ln_carbon_intensity', 'ln_pgdp', 'ln_pop_density', 'ln_fdi', 'financial_development']
print(f"\n[INFO] Missing data in key variables:")
for var in key_vars:
    missing = df_merged[var].isnull().sum()
    rate = (missing / total_obs) * 100
    print(f"  {var}: {missing}/{total_obs} ({rate:.2f}%)")

# Check for duplicates
duplicates = df_merged.duplicated(subset=['city_name', 'year']).sum()
print(f"\n[INFO] Duplicate (city, year) pairs: {duplicates}")
if duplicates > 0:
    print("[WARNING] Found duplicate city-year pairs!")
else:
    print("[OK] No duplicate city-year pairs")

print(f"\n[OK] Merge verification complete!")
