import pandas as pd

# Read raw pop density data
df_raw = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')

print('=== Column Positions in Raw Pop Density File ===')
print(f'Total columns: {len(df_raw.columns)}\n')

for i in range(min(10, len(df_raw.columns))):
    print(f'Column {i}: {df_raw.columns[i]}')
    # Show sample values
    sample_vals = df_raw.iloc[:3, i].tolist()
    print(f'  Sample values: {sample_vals}')
    print()

# Check Shanghai's data across all columns
print('\n=== Shanghai Data (all numeric columns) ===')
shanghai_mask = df_raw.iloc[:, 2].str.contains('上海', na=False)
shanghai_2013 = df_raw[shanghai_mask & (df_raw.iloc[:, 0] == 2013)]

if len(shanghai_2013) > 0:
    print(f'Found Shanghai 2013 row at index {shanghai_2013.index[0]}')
    print('\nValues in all columns:')
    for i in range(len(df_raw.columns)):
        val = shanghai_2013.iloc[0, i]
        print(f'  Column {i}: {val}')
