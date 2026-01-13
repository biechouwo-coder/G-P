import pandas as pd

df = pd.read_excel('原始数据/2000-2023地级市产业结构 .xlsx', sheet_name=1)
print('All columns:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\nFirst 3 rows:')
print(df.iloc[:3, :])
