import pandas as pd

# Read first sheet
df = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx', sheet_name=0)

print('GDP Data Shape:', df.shape)
print('\nFirst 10 columns:')
for i, col in enumerate(df.columns[:10]):
    print(f'{i}: {col}')

print('\nFirst 5 rows, first 10 columns:')
print(df.iloc[:5, :10])

print('\nTotal rows:', len(df))
print('Unique cities:', df.iloc[:, 1].nunique() if len(df.columns) > 1 else 'N/A')
print('Year range:', f'{df.iloc[:, 2].min()} - {df.iloc[:, 2].max()}' if len(df.columns) > 2 else 'N/A')

print('\nMissing values in each column (first 15 columns):')
for i in range(min(15, len(df.columns))):
    missing = df.iloc[:, i].isnull().sum()
    if missing > 0:
        pct = missing / len(df) * 100
        print(f'Column {i}: {missing} ({pct:.2f}%)')
