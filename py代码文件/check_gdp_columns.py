import pandas as pd

df = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx')

print('Total columns:', len(df.columns))
print('\nFirst row (headers):')
for i, val in enumerate(df.iloc[0]):
    print(f'{i}: {val}')

print('\nSecond row (data sample):')
for i, val in enumerate(df.iloc[1]):
    print(f'{i}: {val}')

print('\nThird row (data sample):')
for i, val in enumerate(df.iloc[2]):
    print(f'{i}: {val}')
