import pandas as pd
from pathlib import Path

# 数据路径
DATA_DIR = Path(r"c:\Users\HP\Desktop\毕业论文\原始数据")
OUTPUT_FILE = Path(r"c:\Users\HP\Desktop\毕业论文\总数据集.xlsx")

print("Starting data merge...")

# 读取数据
df_pop = pd.read_excel(DATA_DIR / "298个地级市人口密度1998-2024年无缺失.xlsx")
df_gdp = pd.read_excel(DATA_DIR / "296个地级市GDP相关数据（以2000年为基期）.xlsx")
df_carbon = pd.read_excel(DATA_DIR / "地级市碳排放强度.xlsx")

# 显示列名（便于调试）
print("\nPopulation columns:", list(df_pop.columns))
print("\nGDP columns:", list(df_gdp.columns))
print("\nCarbon columns:", list(df_carbon.columns))

# 标准化：查找关键列（按位置）
# 人口密度：年份[0], 城市[2], 代码[4], 密度[9]
df_pop = df_pop.iloc[:, [0, 2, 4, 9]]
df_pop.columns = ['year', 'city_name', 'city_code', 'pop_density']

# GDP：省份[0], 城市[1], 年份[2], 实际GDP[5], 平减指数[6]
df_gdp = df_gdp.iloc[:, [1, 2, 5, 6]]
df_gdp.columns = ['city_name', 'year', 'gdp_real', 'gdp_deflator']

# 碳排放：年份[0], 代码[1], 城市[3], 碳强度[8]
df_carbon = df_carbon.iloc[:, [0, 1, 3, 8]]
df_carbon.columns = ['year', 'city_code', 'city_name', 'carbon_intensity']

print("\nAfter standardization:")
print(f"Population: {df_pop.shape}")
print(f"GDP: {df_gdp.shape}")
print(f"Carbon: {df_carbon.shape}")

# 第一步：合并人口密度和GDP（用城市名+年份）
df_merged = pd.merge(df_pop, df_gdp, on=['city_name', 'year'], how='left', indicator='gdp_src')
print(f"\nAfter pop+gdp merge: {df_merged.shape}")
print(f"  Both: {(df_merged[\"gdp_src\"] == \"both\").sum()}")
print(f"  Left only: {(df_merged[\"gdp_src\"] == \"left_only\").sum()}")

# 第二步：添加城市代码（从人口数据）
# 第三步：合并碳排放（用城市名+年份）
df_merged = pd.merge(df_merged, df_carbon, on=['city_name', 'year'], how='left', indicator='carbon_src')
print(f"\nAfter adding carbon: {df_merged.shape}")
print(f"  Carbon matched: {(df_merged[\"carbon_src\"] == \"both\").sum()}")

# 删除indicator列
df_merged = df_merged.drop(columns=['gdp_src', 'carbon_src'], errors='ignore')

# 数据质量检查
print("\nData quality check:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Total columns: {len(df_merged.columns)}")
print(f"  Unique cities: {df_merged['city_name'].nunique()}")
print(f"  Year range: {df_merged['year'].min()} - {df_merged['year'].max()}")

# 缺失值统计
print("\nMissing values:")
for col in df_merged.columns:
    missing = df_merged[col].isnull().sum()
    if missing > 0:
        pct = missing / len(df_merged) * 100
        print(f"  {col}: {missing} ({pct:.1f}%)")

# 保存Excel
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_merged.to_excel(writer, sheet_name='总数据集', index=False)

print(f"\nSaved to: {OUTPUT_FILE}")
print("Merge complete!")
