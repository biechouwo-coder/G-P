import pandas as pd
import numpy as np

print("=" * 80)
print("Sanya FDI Anomaly Analysis")
print("=" * 80)

# Read raw FDI data (use column positions)
df_fdi_raw = pd.read_excel('原始数据/1996-2023年地级市外商直接投资FDI.xlsx')

# Extract by column positions to avoid encoding issues
# Structure: [year, city_name, fdi_value, unit, source]
df_fdi = df_fdi_raw.iloc[:, [0, 1, 2]].copy()
df_fdi.columns = ['year', 'city_name', 'fdi']
df_fdi['year'] = pd.to_numeric(df_fdi['year'], errors='coerce')

# Check if 'Sanya' is in the dataset
print("\n[1] Checking if Sanya is in dataset...")
# Use string matching that handles encoding
sanya_data = df_fdi[df_fdi['city_name'].astype(str).str.contains('三亚', na=False)]

if sanya_data.empty:
    print("Sanya NOT found - checking city names...")
    unique_cities = df_fdi['city_name'].dropna().unique()
    print("Sample cities in dataset:")
    for i, city in enumerate(unique_cities[:20]):
        print(f"  {i}: {repr(city)}")
else:
    print(f"Found {len(sanya_data)} observations for Sanya")

    # Get Sanya data 2015-2023
    sanya_recent = sanya_data[sanya_data['year'].between(2015, 2023)].sort_values('year')

    print("\n[2] Sanya FDI Raw Data (2015-2023)")
    print("-" * 50)
    for _, row in sanya_recent.iterrows():
        year = int(row['year'])
        fdi = row['fdi']
        print(f"{year}: {fdi:.2f} million USD")

    # Year-over-year changes
    print("\n[3] Year-over-Year Changes")
    print("-" * 50)
    years = sanya_recent['year'].values
    fdis = sanya_recent['fdi'].values

    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        prev_fdi = fdis[i-1]
        curr_fdi = fdis[i]

        if pd.notna(prev_fdi) and pd.notna(curr_fdi) and prev_fdi != 0:
            pct_change = ((curr_fdi - prev_fdi) / prev_fdi) * 100
            flag = " ***ANOMALY***" if abs(pct_change) > 50 else ""
            print(f"{int(prev_year)}→{int(curr_year)}: {prev_fdi:.2f} → {curr_fdi:.2f} ({pct_change:+.1f}%){flag}")

    # Statistical analysis (IQR method)
    print("\n[4] Statistical Outlier Detection (2017 data)")
    print("-" * 50)

    all_fdi_2017 = df_fdi[df_fdi['year'] == 2017]['fdi'].dropna()
    sanya_2017 = sanya_recent[sanya_recent['year'] == 2017]['fdi'].values

    if len(sanya_2017) > 0:
        sanya_val = sanya_2017[0]

        Q1 = all_fdi_2017.quantile(0.25)
        Q3 = all_fdi_2017.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        print(f"2017 National FDI Distribution (all cities):")
        print(f"  Q1 (25th percentile): {Q1:.2f}")
        print(f"  Q3 (75th percentile): {Q3:.2f}")
        print(f"  IQR: {IQR:.2f}")
        print(f"  Normal range: [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"\nSanya 2017 FDI: {sanya_val:.2f}")

        if sanya_val < lower_bound:
            print(f"  Status: BELOW normal range - Statistical OUTLIER (low)")
        elif sanya_val > upper_bound:
            print(f"  Status: ABOVE normal range - Statistical OUTLIER (high)")
        else:
            print(f"  Status: Within normal range")

    # Compare with similar cities
    print("\n[5] Comparison with Other Cities (2016-2018)")
    print("-" * 50)

    # Try to find similar tourist cities
    target_cities = ['海口', '厦门', '青岛', '大连', '珠海', '汕头']
    comparison_found = False

    for target in target_cities:
        city_data = df_fdi[df_fdi['city_name'].astype(str).str.contains(target, na=False)]
        if not city_data.empty:
            comparison_found = True
            city_2016 = city_data[city_data['year'] == 2016]['fdi'].values
            city_2017 = city_data[city_data['year'] == 2017]['fdi'].values

            if len(city_2016) > 0 and len(city_2017) > 0:
                f16 = city_2016[0]
                f17 = city_2017[0]
                if pd.notna(f16) and pd.notna(f17) and f16 != 0:
                    pct_change = ((f17 - f16) / f16) * 100
                    print(f"{target}: {f16:.2f} → {f17:.2f} ({pct_change:+.1f}%)")

    if not comparison_found:
        print("No comparable cities found in dataset")

    # Check winsorization in final dataset
    print("\n[6] Winsorization Check in Final Dataset")
    print("-" * 50)

    df_final = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')
    sanya_final = df_final[df_final['city_name'].astype(str).str.contains('三亚', na=False) &
                          df_final['year'].between(2015, 2022)].copy()

    if not sanya_final.empty:
        print("Year | Raw FDI | ln_fdi | Exp(ln_fdi) | Winsorized?")
        print("-" * 55)
        for _, row in sanya_final.sort_values('year').iterrows():
            year = int(row['year'])
            raw_fdi = row['fdi']
            ln_fdi = row['ln_fdi']
            exp_ln = np.exp(ln_fdi)
            is_diff = abs(exp_ln - raw_fdi) > 0.01
            flag = "YES" if is_diff else "NO"
            print(f"{year} | {raw_fdi:>7.2f} | {ln_fdi:>6.4f} | {exp_ln:>10.2f} | {flag}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("""
1. DATA VERIFICATION:
   - 86.5% drop in 2017 is HIGHLY SUSPICIOUS
   - Check Sanya Statistical Yearbook 2018 or Hainan Statistical Yearbook 2018
   - Verify if statistical criteria changed (e.g., "actual utilized" vs. "contracted")

2. POSSIBLE REASONS:
   a) Unit error: 2017 value might be missing a digit (29.3 vs 293)
   b) Statistical criteria: Changed from "actual utilized FDI" to "contracted FDI"
   c) Policy effect: 2017 was 30th anniversary of Hainan province, policy transition
   d) Large project: A major FDI project settled in 2016, none in 2017

3. IMPACT ON REGRESSION:
   - ln_fdi in 2017 is 3.41, much lower than adjacent years (5.39-5.57)
   - This creates an outlier that can bias regression coefficients
   - May overestimate FDI effect on carbon emissions

4. RECOMMENDED SOLUTIONS:
   Option A (Conservative): Keep original value, but exclude Sanya in robustness check
   Option B (Moderate): Apply moving average to 2016-2018 (3-year smoothing)
   Option C (Aggressive): Treat 2017 as missing, interpolate using 2016 and 2018
   Option D (Strict): Exclude Sanya 2017-2018 observations entirely

5. ROBUSTNESS CHECK:
   - Re-run regression excluding Sanya city
   - Compare coefficient changes (>10% = substantial impact)
   - Document this anomaly and treatment in thesis methodology
""")
print("=" * 80)
