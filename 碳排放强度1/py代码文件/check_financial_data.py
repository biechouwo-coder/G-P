import pandas as pd

# Read financial development data
df_fin = pd.read_excel('原始数据/金融发展水平（2003-2023）236缺失.xlsx')

print(f"Shape: {df_fin.shape}")
print(f"\nColumn positions:")
for i, col in enumerate(df_fin.columns):
    print(f"  {i}: {col}")

print(f"\nFirst few rows:")
print(df_fin.head(10))

print(f"\nData types:")
print(df_fin.dtypes)

print(f"\nBasic statistics:")
print(df_fin.describe())
