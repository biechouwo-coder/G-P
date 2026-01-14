import pandas as pd

df = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('数据形状:', df.shape)
print('\n前10行:')
print(df.head(10))

print('\n列名(前25个):')
for i, col in enumerate(df.columns[:25]):
    print(f'{i}: {col}')
