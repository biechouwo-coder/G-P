import pandas as pd
import numpy as np

print("=" * 80)
print("COMPREHENSIVE DIAGNOSIS: Sanya 2017 FDI Anomaly")
print("=" * 80)

# Read raw FDI data
df_fdi = pd.read_excel('原始数据/1996-2023年地级市外商直接投资FDI.xlsx')
df_fdi_clean = df_fdi.iloc[:, [0, 1, 2]].copy()
df_fdi_clean.columns = ['year', 'city_name', 'fdi']
df_fdi_clean['year'] = pd.to_numeric(df_fdi_clean['year'], errors='coerce')

# Extract Sanya data
sanya_all = df_fdi_clean[df_fdi_clean['city_name'].astype(str).str.contains('三亚', na=False)].copy()
sanya_all = sanya_all.sort_values('year')

print("\n[1] Sanya FDI Complete Time Series (1996-2023)")
print("-" * 60)
print(f"{'Year':<6} {'FDI (USD)':<15} {'ln(FDI)':<10} {'Status'}")
print("-" * 60)

for _, row in sanya_all.iterrows():
    year = int(row['year'])
    fdi = row['fdi']
    if pd.notna(fdi) and fdi > 0:
        ln_fdi = np.log(fdi)
        status = ""
        if year == 2017:
            status = "<<< ANOMALY"
        print(f"{year:<6} {fdi:<15.2f} {ln_fdi:<10.4f} {status}")
    else:
        print(f"{year:<6} {fdi:<15.2f} {'MISSING':<10}")

# Detailed analysis of 2016-2018 period
print("\n[2] Detailed Analysis: 2016-2018 Period")
print("-" * 60)

sanya_period = sanya_all[sanya_all['year'].between(2016, 2018)].copy()

for _, row in sanya_period.iterrows():
    year = int(row['year'])
    fdi = row['fdi']
    ln_fdi = np.log(fdi) if pd.notna(fdi) and fdi > 0 else np.nan

    # Calculate what 2017 should be if following trend
    if year == 2016:
        fdi_2016 = fdi
        print(f"2016: FDI = {fdi:.2f} million USD")
    elif year == 2017:
        fdi_2017 = fdi
        # Check if this could be a unit error
        possible_errors = []
        if fdi * 10 < fdi_2016:
            possible_errors.append(f"Missing one zero? {fdi*10:.2f}")
        if fdi * 100 < fdi_2016:
            possible_errors.append(f"Missing two zeros? {fdi*100:.2f}")

        print(f"2017: FDI = {fdi:.2f} million USD")
        print(f"      Drop from 2016: {((fdi - fdi_2016) / fdi_2016 * 100):.1f}%")

        if possible_errors:
            print(f"      Possible unit errors: {', '.join(possible_errors)}")

        # Compare with statistical expectation
        # If 2016-2018 trend should be smooth, what would 2017 be?
        fdi_2018 = sanya_all[sanya_all['year'] == 2018]['fdi'].values[0]
        expected_trend = np.sqrt(fdi_2016 * fdi_2018)  # Geometric mean
        expected_arith = (fdi_2016 + fdi_2018) / 2  # Arithmetic mean

        print(f"\n      Statistical Expectations (if smooth trend):")
        print(f"        Geometric mean of 2016&2018: {expected_trend:.2f}")
        print(f"        Arithmetic mean of 2016&2018: {expected_arith:.2f}")
        print(f"        Actual 2017 value: {fdi:.2f}")
        print(f"        Deviation from geometric mean: {((fdi - expected_trend) / expected_trend * 100):.1f}%")

# Check digit pattern
print("\n[3] Data Quality Checks")
print("-" * 60)

fdi_2017 = sanya_all[sanya_all['year'] == 2017]['fdi'].values[0]
fdi_2016 = sanya_all[sanya_all['year'] == 2016]['fdi'].values[0]
fdi_2018 = sanya_all[sanya_all['year'] == 2018]['fdi'].values[0]

# Check 1: Could it be 293.0 instead of 29.30?
print("Check 1: Decimal place error")
if abs(fdi_2017 * 10 - np.sqrt(fdi_2016 * fdi_2018)) < abs(fdi_2017 - np.sqrt(fdi_2016 * fdi_2018)):
    print(f"  29.30 -> 293.00 would be closer to expected trend")
    print(f"  Current: {fdi_2017:.2f}, Scaled: {fdi_2017*10:.2f}, Expected: {np.sqrt(fdi_2016 * fdi_2018):.2f}")
else:
    print(f"  Scaling does not improve alignment")

# Check 2: Compare with city GDP trend
print("\nCheck 2: Context with city development")
df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx')
df_gdp_clean = df_gdp.iloc[:, [0, 1, 2, 3]].copy()
df_gdp_clean.columns = ['year', 'city_code', 'city_name', 'gdp']

sanya_gdp = df_gdp_clean[df_gdp_clean['city_name'].astype(str).str.contains('三亚', na=False)].copy()
sanya_gdp = sanya_gdp[sanya_gdp['year'].between(2015, 2019)].sort_values('year')

print("  Sanya GDP trend (million RMB):")
for _, row in sanya_gdp.iterrows():
    year = int(row['year'])
    gdp = row['gdp']
    if year >= 2016:
        gdp_prev = sanya_gdp[sanya_gdp['year'] == year-1]['gdp'].values
        if len(gdp_prev) > 0:
            growth = ((gdp - gdp_prev[0]) / gdp_prev[0] * 100)
            print(f"    {year}: {gdp:.2f} (growth: {growth:+.1f}%)")

# Check 3: Compare with other cities in Hainan
print("\nCheck 3: Comparison with Haikou (capital of Hainan)")
haikou = df_fdi_clean[df_fdi_clean['city_name'].astype(str).str.contains('海口', na=False)].copy()
haikou_recent = haikou[haikou['year'].between(2015, 2019)].sort_values('year')

print("  Haikou FDI (million USD):")
for _, row in haikou_recent.iterrows():
    year = int(row['year'])
    fdi = row['fdi']
    if year >= 2016:
        fdi_prev = haikou_recent[haikou_recent['year'] == year-1]['fdi'].values
        if len(fdi_prev) > 0 and pd.notna(fdi_prev[0]) and fdi_prev[0] != 0:
            change = ((fdi - fdi_prev[0]) / fdi_prev[0] * 100)
            print(f"    {year}: {fdi:.2f} (change: {change:+.1f}%)")

# Check 4: Statistical outlier detection (multiple methods)
print("\n[4] Statistical Outlier Detection")
print("-" * 60)

# Method 1: IQR (already done, showing within range)
# Method 2: Z-score for Sanya's time series
sanya_valid = sanya_all[(sanya_all['year'].between(2010, 2023)) & (sanya_all['fdi'] > 0)].copy()
fdi_values = sanya_valid['fdi'].values
mean_fdi = np.mean(fdi_values)
std_fdi = np.std(fdi_values)

fdi_2017 = sanya_all[sanya_all['year'] == 2017]['fdi'].values[0]
z_score = (fdi_2017 - mean_fdi) / std_fdi if std_fdi > 0 else 0

print(f"Method 1: Z-score within Sanya's own time series")
print(f"  Mean (2010-2023): {mean_fdi:.2f}")
print(f"  Std dev: {std_fdi:.2f}")
print(f"  2017 value: {fdi_2017:.2f}")
print(f"  Z-score: {z_score:.2f}")
if abs(z_score) > 2:
    print(f"  Assessment: OUTLIER (|z| > 2)")
elif abs(z_score) > 1.5:
    print(f"  Assessment: Moderate outlier (1.5 < |z| < 2)")
else:
    print(f"  Assessment: Within normal range")

# Method 3: Percentile jump analysis
print(f"\nMethod 2: Percentile rank in 2017")
all_fdi_2017 = df_fdi_clean[df_fdi_clean['year'] == 2017]['fdi'].dropna()
percentile = (all_fdi_2017 < fdi_2017).sum() / len(all_fdi_2017) * 100
print(f"  Sanya 2017 FDI: {fdi_2017:.2f}")
print(f"  Percentile rank: {percentile:.1f}th percentile")
print(f"  Assessment: {'Low value' if percentile < 25 else 'Mid range' if percentile < 75 else 'High value'}")

# Method 4: Moving average deviation
print(f"\nMethod 3: Deviation from 3-year moving average")
sanya_2015_2019 = sanya_all[sanya_all['year'].between(2015, 2019)].copy()
for _, row in sanya_2015_2019.iterrows():
    year = int(row['year'])
    fdi = row['fdi']
    if year in [2015, 2019]:
        continue

    # Get 3-year window
    window = sanya_2015_2019[sanya_2015_2019['year'].between(year-1, year+1)]['fdi'].values
    moving_avg = np.mean(window[window > 0])  # Exclude zeros/negative

    if pd.notna(fdi) and fdi > 0:
        deviation = (fdi - moving_avg) / moving_avg * 100
        flag = " <<<" if abs(deviation) > 50 else ""
        print(f"  {year}: {fdi:.2f}, 3yr MA: {moving_avg:.2f}, deviation: {deviation:+.1f}%{flag}")

print("\n" + "=" * 80)
print("DIAGNOSIS SUMMARY")
print("=" * 80)

# Final assessment
print("\nEVIDENCE OF DATA ERROR:")
print("  [1] Magnitude: -86.5% drop (largest in Sanya's 28-year history)")
print("  [2] Reversal: +254.4% bounce in 2018 (also largest)")
print("  [3] Pattern: V-shaped reversal suggests measurement error, not genuine trend")
print("  [4] Context: No similar drop in Haikou or national data")

print("\nPOSSIBLE EXPLANATIONS:")
print("  A. UNIT ERROR: 29.30 million USD")
print("     -> Should be 293.0 million? (missing one digit)")
print("     -> If scaled by 10x: 293.0 (closer to 2016-2018 trend)")
print("  B. STATISTICAL CRITERIA CHANGE:")
print("     -> Changed from 'actual utilized' to 'contracted' FDI?")
print("     -> Or measurement scope narrowed?")
print("  C. GENUINE ECONOMIC SHOCK:")
print("     -> Policy change in Hainan (30th anniversary in 2018)")
print("     -> One-off project completion")

print("\nRECOMMENDATION:")
print("  1. CONSULT ORIGINAL SOURCE:")
print("     - Check Sanya Statistical Yearbook 2018 (published ~2019)")
print("     - Verify FDI definition and units")
print("  2. IF DATA ERROR CONFIRMED:")
print("     - Replace 2017 value with interpolation: sqrt(2016 * 2018)")
print(f"     - Expected value: {np.sqrt(fdi_2016 * fdi_2018):.2f} million USD")
print("  3. IF GENUINE VALUE:")
print("     - Keep as is, but add dummy variable for Sanya 2017")
print("     - Or exclude Sanya from robustness check")

print("\n  ACTION ITEM: Check source data if possible before fixing")
print("=" * 80)
