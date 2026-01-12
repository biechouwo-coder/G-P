import pandas as pd

# Read raw FDI data
df = pd.read_excel('原始数据/1996-2023年地级市外商直接投资FDI.xlsx')

# Get column names by position to avoid encoding issues
print('Column structure (first 3 rows):')
print(df.head(3))
print()

# Extract Sanya data using column positions
# Column structure from inspection: col 0 = year, col 1 = city_name, col 2 = fdi_value, col 3 = unit, col 4 = source
# Need to handle the header row properly

# Check if '三亚市' appears anywhere in the data
print('Searching for Sanya in the data...')
has_sanya = False
for idx, row in df.iterrows():
    city_val = str(row.iloc[1])
    if '三亚' in city_val or 'Sanya' in city_val or 'sanya' in city_val:
        print(f'Found at row {idx}: city={city_val}')
        has_sanya = True
        if idx <= 5:
            print(f'  Full row: year={row.iloc[0]}, fdi={row.iloc[2]}, unit={row.iloc[3]}')

if not has_sanya:
    print('WARNING: Sanya not found in dataset')
    # Let's see what cities ARE in the dataset
    print('\nSample cities in dataset:')
    unique_cities = df.iloc[:, 1].dropna().unique()[:20]
    for city in unique_cities:
        print(f'  - {city}')
else:
    # Now extract Sanya data
    df['is_sanya'] = df.iloc[:, 1].astype(str).str.contains('三亚', na=False)
    sanya_data = df[df['is_sanya']].copy()

# Sort by year
sanya_data = sanya_data.sort_values(sanya_data.columns[0])

# Display 2015-2023 data
print('\n' + '='*60)
print('三亚市 FDI 数据 (2015-2023)')
print('='*60)
print(f"{'Year':<8} {'FDI Value':<15} {'Unit':<12} {'Source'}")
print('-'*60)

for idx, row in sanya_data.iterrows():
    year = row.iloc[0]
    if 2015 <= year <= 2023:
        fdi_val = row.iloc[2]
        unit = row.iloc[3]
        source = row.iloc[4]
        print(f'{int(year):<8} {fdi_val:<15.2f} {unit:<12} {source}')

# Calculate year-over-year changes
print('\n' + '='*60)
print('Year-over-Year Change Analysis')
print('='*60)

sanya_recent = sanya_data[sanya_data.iloc[:, 0].between(2015, 2023)].copy()
sanya_recent = sanya_recent.sort_values(sanya_recent.columns[0])

years = sanya_recent.iloc[:, 0].values
fdi_values = sanya_recent.iloc[:, 2].values

for i in range(1, len(years)):
    prev_year = years[i-1]
    curr_year = years[i]
    prev_fdi = fdi_values[i-1]
    curr_fdi = fdi_values[i]

    if prev_fdi != 0:
        pct_change = ((curr_fdi - prev_fdi) / prev_fdi) * 100
        print(f'{int(prev_year)}→{int(curr_year)}: {prev_fdi:.2f} → {curr_fdi:.2f} ({pct_change:+.1f}%)')
    else:
        print(f'{int(prev_year)}→{int(curr_year)}: {prev_fdi:.2f} → {curr_fdi:.2f} (N/A - prev is zero)')
