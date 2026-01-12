import pandas as pd

df = pd.read_excel('总数据集_2007-2023_修正FDI.xlsx')

print('Dataset shape:', df.shape)
print('\nAll columns:')
for i, col in enumerate(df.columns, 1):
    print(f'{i:2d}. {col}')

# Check for industrial_upgrading variable
print('\n' + '='*60)
print('Checking for industrial_upgrading variable...')
if 'industrial_upgrading' in df.columns:
    print('[OK] industrial_upgrading EXISTS in the dataset')
    print('\nSample values:')
    print(df[['city_name', 'year', 'industrial_upgrading']].head(10).to_string(index=False))
else:
    print('[WARNING] industrial_upgrading NOT FOUND in the dataset')
