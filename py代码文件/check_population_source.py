import pandas as pd

df = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('Shape:', df.shape)
print('Columns:', df.columns.tolist()[:10])

city = '七台河市'
if city in df.columns:
    print(f'\n{city} exists!')
else:
    print(f'\n{city} not found')
    print('\nSample cities:', df.columns[2:12].tolist())
    print('\nSearching for cities with 七台河:')
    for col in df.columns:
        if '七台河' in str(col):
            print(f'  Found: {col}')
