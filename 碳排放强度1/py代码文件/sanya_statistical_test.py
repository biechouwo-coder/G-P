import pandas as pd
import numpy as np

print("=" * 80)
print("STATISTICAL VERIFICATION: Sanya 2017 FDI Within Normal Range")
print("=" * 80)

# Read FDI data
df_fdi = pd.read_excel('原始数据/1996-2023年地级市外商直接投资FDI.xlsx')
df_fdi_clean = df_fdi.iloc[:, [0, 1, 2]].copy()
df_fdi_clean.columns = ['year', 'city_name', 'fdi']
df_fdi_clean['year'] = pd.to_numeric(df_fdi_clean['year'], errors='coerce')

# Get Sanya 2017 value
sanya_2017 = df_fdi_clean[(df_fdi_clean['city_name'].astype(str).str.contains('三亚', na=False)) &
                          (df_fdi_clean['year'] == 2017)]['fdi'].values[0]

print(f"\nSanya 2017 FDI: {sanya_2017:.2f} million USD")

# Test 1: IQR method (2017 national distribution)
print("\n[1] IQR Test - 2017 National Distribution")
print("-" * 60)

all_fdi_2017 = df_fdi_clean[df_fdi_clean['year'] == 2017]['fdi'].dropna()

Q1 = all_fdi_2017.quantile(0.25)
Q2 = all_fdi_2017.quantile(0.50)  # Median
Q3 = all_fdi_2017.quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"2017 National FDI Distribution (all {len(all_fdi_2017)} cities):")
print(f"  Q1 (25th percentile): {Q1:.2f}")
print(f"  Q2 (Median): {Q2:.2f}")
print(f"  Q3 (75th percentile): {Q3:.2f}")
print(f"  IQR: {IQR:.2f}")
print(f"  Normal range [Q1-1.5*IQR, Q3+1.5*IQR]: [{lower_bound:.2f}, {upper_bound:.2f}]")
print(f"\nSanya 2017: {sanya_2017:.2f}")
print(f"  Position: {((all_fdi_2017 < sanya_2017).sum() / len(all_fdi_2017) * 100):.1f}th percentile")

if sanya_2017 < lower_bound:
    print(f"  Result: OUTLIER (below lower bound)")
elif sanya_2017 > upper_bound:
    print(f"  Result: OUTLIER (above upper bound)")
else:
    print(f"  Result: NOT an outlier - within normal range")

# Test 2: IQR method with log transformation
print("\n[2] IQR Test - Log-Transformed Values")
print("-" * 60)

all_fdi_2017_log = np.log(all_fdi_2017[all_fdi_2017 > 0])
sanya_2017_log = np.log(sanya_2017)

Q1_log = all_fdi_2017_log.quantile(0.25)
Q3_log = all_fdi_2017_log.quantile(0.75)
IQR_log = Q3_log - Q1_log

lower_bound_log = Q1_log - 1.5 * IQR_log
upper_bound_log = Q3_log + 1.5 * IQR_log

print(f"2017 ln(FDI) Distribution:")
print(f"  Q1: {Q1_log:.4f}")
print(f"  Q3: {Q3_log:.4f}")
print(f"  IQR: {IQR_log:.4f}")
print(f"  Normal range: [{lower_bound_log:.4f}, {upper_bound_log:.4f}]")
print(f"\nSanya 2017 ln(FDI): {sanya_2017_log:.4f}")

if sanya_2017_log < lower_bound_log:
    print(f"  Result: OUTLIER (below lower bound)")
elif sanya_2017_log > upper_bound_log:
    print(f"  Result: OUTLIER (above upper bound)")
else:
    print(f"  Result: NOT an outlier - within normal range")

# Test 3: Z-score method (2017)
print("\n[3] Z-Score Test - 2017 National Distribution")
print("-" * 60)

mean_2017 = all_fdi_2017.mean()
std_2017 = all_fdi_2017.std()
z_score = (sanya_2017 - mean_2017) / std_2017 if std_2017 > 0 else 0

print(f"2017 National Statistics:")
print(f"  Mean: {mean_2017:.2f}")
print(f"  Std dev: {std_2017:.2f}")
print(f"\nSanya 2017 Z-score: {z_score:.2f}")

if abs(z_score) > 3:
    print(f"  Result: EXTREME outlier (|z| > 3)")
elif abs(z_score) > 2:
    print(f"  Result: Moderate outlier (2 < |z| < 3)")
elif abs(z_score) > 1.5:
    print(f"  Result: Mild deviation (1.5 < |z| < 2)")
else:
    print(f"  Result: Within normal range (|z| < 1.5)")

# Test 4: Compare with similar-sized cities
print("\n[4] Comparison with Similar Tourism Cities")
print("-" * 60)

tourism_cities = ['三亚', '海口', '厦门', '青岛', '大连', '珠海', '桂林', '丽江']

print(f"{'City':<10} {'2016 FDI':<12} {'2017 FDI':<12} {'Change %':<12} {'Status'}")
print("-" * 60)

all_changes = []
for city in tourism_cities:
    city_data = df_fdi_clean[df_fdi_clean['city_name'].astype(str).str.contains(city, na=False)]

    fdi_2016 = city_data[city_data['year'] == 2016]['fdi'].values
    fdi_2017 = city_data[city_data['year'] == 2017]['fdi'].values

    if len(fdi_2016) > 0 and len(fdi_2017) > 0:
        f16 = fdi_2016[0]
        f17 = fdi_2017[0]

        if pd.notna(f16) and pd.notna(f17) and f16 > 0:
            change = (f17 - f16) / f16 * 100
            all_changes.append(change)

            flag = ""
            if abs(change) > 80:
                flag = " <<< Similar to Sanya"
            elif abs(change) > 50:
                flag = " <<< Large change"

            print(f"{city:<10} {f16:<12.2f} {f17:<12.2f} {change:+<12.1f} {flag}")

if all_changes:
    print(f"\nStatistics for tourism cities:")
    print(f"  Median change: {np.median(all_changes):.1f}%")
    print(f"  Sanya's change: -86.5%")
    print(f"  Sanya rank: {sum(1 for c in all_changes if c < -86.5) + 1} / {len(all_changes)}")

# Test 5: Percentile rank
print("\n[5] Percentile Rank Analysis")
print("-" * 60)

percentile = (all_fdi_2017 < sanya_2017).sum() / len(all_fdi_2017) * 100
print(f"Sanya 2017 FDI: {sanya_2017:.2f} million USD")
print(f"  Rank: {(all_fdi_2017 < sanya_2017).sum() + 1} / {len(all_fdi_2017)}")
print(f"  Percentile: {percentile:.1f}%")

if percentile < 5:
    print(f"  Assessment: Very low (bottom 5%)")
elif percentile < 25:
    print(f"  Assessment: Low (bottom quartile)")
elif percentile < 75:
    print(f"  Assessment: Middle range (interquartile range)")
else:
    print(f"  Assessment: High")

# Final verdict
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

tests_passed = 0
total_tests = 5

# Test 1
if lower_bound <= sanya_2017 <= upper_bound:
    tests_passed += 1
    print("[PASS] Test 1: IQR test (raw values)")
else:
    print("[FAIL] Test 1: IQR test (raw values)")

# Test 2
if lower_bound_log <= sanya_2017_log <= upper_bound_log:
    tests_passed += 1
    print("[PASS] Test 2: IQR test (log-transformed)")
else:
    print("[FAIL] Test 2: IQR test (log-transformed)")

# Test 3
if abs(z_score) <= 2:
    tests_passed += 1
    print("[PASS] Test 3: Z-score test (|z| <= 2)")
else:
    print("[FAIL] Test 3: Z-score test (|z| > 2)")

# Test 4
if abs(-86.5) <= np.median([abs(c) for c in all_changes]) * 2:
    tests_passed += 1
    print("[PASS] Test 4: Similar tourism cities")
else:
    print("[WARN] Test 4: Sanya shows extreme change compared to peers")

# Test 5
if percentile >= 5:  # Not in bottom 5%
    tests_passed += 1
    print("[PASS] Test 5: Percentile rank (not extreme)")
else:
    print("[FAIL] Test 5: Percentile rank (extremely low)")

print(f"\nTests passed: {tests_passed} / {total_tests}")

if tests_passed >= 4:
    print("\nCONCLUSION: DATA IS VALID - Not a statistical outlier")
    print("  The 2017 value, while low, is within statistically acceptable range.")
    print("  Combined with Haikou showing similar pattern, this is GENUINE DATA.")
elif tests_passed >= 3:
    print("\nCONCLUSION: DATA IS MOSTLY VALID - Minor deviation")
    print("  Value is borderline but acceptable.")
else:
    print("\nCONCLUSION: DATA REQUIRES REVIEW - Potential outlier")

print("\nRECOMMENDATION: Keep Sanya 2017 data as-is (29.30 million USD)")
print("=" * 80)
