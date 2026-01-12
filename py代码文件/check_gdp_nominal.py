import pandas as pd

df = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx')

print('Column positions:')
for i in range(min(11, len(df.columns))):
    sample_val = df.iloc[0, i]
    print(f'Col {i}: {sample_val}')

print('\n' + '='*60)
print('Sample data (Beijing):')
beijing = df[df.iloc[:, 1] == '北京市']
print(beijing.head(5))
