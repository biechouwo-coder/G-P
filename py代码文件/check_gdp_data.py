import pandas as pd

# Read GDP data file
df = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=1)

print('GDP Data Shape:', df.shape)
print('\nColumn indices and names:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\nFirst 3 rows:')
print(df.iloc[:3, :])

print('\nData types:')
print(df.dtypes)

print('\nMissing values by column:')
missing_counts = df.isnull().sum()
for col, count in missing_counts.items():
    if count > 0:
        pct = count / len(df) * 100
        print(f'{col}: {count} ({pct:.2f}%)')
