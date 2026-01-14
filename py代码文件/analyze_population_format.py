import pandas as pd

df = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('完整列名:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\n数据类型和非空数量:')
print(df.info())

print('\n前3行所有列:')
pd.set_option('display.max_columns', None)
print(df.head(3))

# Check how many unique cities
print(f'\n唯一城市数: {df.iloc[:, 2].nunique()}')
print('城市示例:')
print(df.iloc[:, 2].unique()[:20])
