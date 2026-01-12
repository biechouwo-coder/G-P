# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

Undergraduate thesis studying the impact of China's low-carbon city pilot policies on carbon emission intensity using multi-period Difference-in-Differences (DID) models with panel data from 216 prefecture-level cities spanning 2007-2023.

**Research Focus:** Evaluating whether low-carbon pilot policies (three batches: 2010, 2012, 2017) effectively reduced carbon emission intensity (CEI).

**Core Innovation:** Incorporating high-precision population density data (298 cities × 27 years) into DID models to control for urban agglomeration effects, separating institutional policy effects from morphological urbanization effects.

**Repository:** https://github.com/biechouwo-coder/G-P.git

## Quick Start

```bash
# Verify Python version
py --version  # Should be 3.8.1

# Install dependencies
py -m pip install pandas openpyxl scipy sklearn matplotlib

# Run PSM analysis (alternative specification with fdi_openness)
py py代码文件/psm_new_controls.py

# Run PSM-DID regression
py py代码文件/psm_did_regression_new_controls.py

# Run event study (parallel trends test)
py py代码文件/event_study_psm_new_controls.py
```

## Current Status (January 12, 2025)

### Analysis Completed
- ✅ **PSM-DID (Alternative spec with fdi_openness, caliper=0.02)**: 2,846 obs × 199 cities
  - DID coefficient: 0.0275 (p=0.329, not significant)
  - Parallel trends: ✓ PASSED (pre-period slope p=0.263)
- ✅ **PSM-DID (Tertiary share model, caliper=0.05)**: 2,990 obs × 200 cities
  - DID coefficient: 0.0427 (p=0.105, not significant)
  - Parallel trends: ✓ PASSED
- ✅ **Event Study**: Dynamic effects with [-5,+5] window
- ✅ **Data quality**: Fixed Shanghai FDI error, documented Sanya anomaly and Ordos 2022 GDP issue

### Key Finding
**Low-carbon pilot policies show no significant emission reduction effect.** Policy effect remains insignificant across all model specifications (caliper 0.01, 0.02, 0.05; different control variables).

## Critical Data Files

### Source Data (DO NOT MODIFY)
- `原始数据/298个地级市人口密度1998-2024年无缺失.xlsx` - Core innovation data (298 cities × 27 years)
- `原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx` - GDP with deflator (use column 3 for nominal GDP)
- `原始数据/地级市碳排放强度.xlsx` - Carbon emissions (contains 2022 GDP error for Ordos, verified not used in final dataset)
- `原始数据/1996-2023年地级市外商直接投资FDI.xlsx` - FDI data
- `原始数据/汇率.xlsx` - USD/RMB annual rates (2007-2023)

### Final Datasets
- `总数据集_2007-2023_完整版_无缺失FDI.xlsx` - **Primary dataset** (4,819 obs × 285 cities, 0% FDI missing)
- `倾向得分匹配_匹配后数据集.xlsx` - PSM-matched sample (2,990 obs, tertiary share model)
- `人均GDP+人口集聚程度+产业高级化+外商投资水平+人均道路面积/PSM_匹配后数据集.xlsx` - PSM-matched sample (2,846 obs, fdi_openness model)

## Essential Code Architecture Patterns

### Pattern 1: Manual OLS with Clustered Standard Errors

All regression scripts use this pattern to avoid `linearmodels` dependency:

```python
def ols_regression_clustered(y, X, cluster_var, df):
    # Add constant and estimate
    X = np.column_stack([np.ones(len(y)), X])
    beta = np.linalg.solve(np.dot(X.T, X), np.dot(X.T, y))
    residuals = y - np.dot(X, beta)

    # Cluster-robust variance (sandwich estimator)
    clusters = df[cluster_var].values
    unique_clusters = np.unique(clusters)
    meat = np.zeros((k, k))
    for cluster in unique_clusters:
        mask = clusters == cluster
        X_cluster = X[mask]
        u_cluster = residuals[mask].reshape(-1, 1)
        meat += np.dot(X_cluster.T, u_cluster).dot(u_cluster.T).dot(X_cluster)

    # Small-sample correction
    n_clusters = len(unique_clusters)
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov_cluster = correction * np.linalg.inv(XtX).dot(meat).dot(np.linalg.inv(XtX))
    se_cluster = np.sqrt(np.diag(vcov_cluster))

    return {'coefficients': beta, 'std_errors': se_cluster, ...}
```

### Pattern 2: Column Position-Based Data Extraction

**CRITICAL:** Always use column positions, not names, due to Chinese encoding issues in Windows console:

```python
# BAD: df[['年份', '地区名称', '第二产业占GDP比重']]
# GOOD: df.iloc[:, [0, 1, 2, 10]]  # By position

# Standard merge pattern
df = pd.read_excel('filename.xlsx')
df = df.iloc[:, [col_positions]]  # Extract by position
df.columns = ['var1', 'var2', 'var3', ...]  # Rename to English
df_merged = pd.merge(df1, df2, on=['city_name', 'year'], how='outer')
```

### Pattern 3: PSM Matching Strategy

```python
class PropensityScoreMatcher:
    def __init__(self, data, covariates, caliper=0.02):
        self.caliper = caliper  # Propensity score difference threshold

    def estimate_propensity_scores(self):
        # Year-by-year Logit regression (NOT pooled)
        for year in years:
            logit_model = LogisticRegression(...)
            logit_model.fit(X, y)
            pscores = logit_model.predict_proba(X)[:, 1]

    def perform_matching(self):
        # 1:1 nearest neighbor matching with replacement
        for treat_idx in treat_indices:
            ps_diff = np.abs(control_ps - treat_ps)
            min_diff = np.min(ps_diff)
            if min_diff <= self.caliper:  # Exclude if beyond caliper
                matched_pairs.append((treat_idx, control_idx, min_diff))
```

**Key parameters:**
- **Caliper 0.02**: Current setting, 91.3% match rate, 2,846 obs
- **Caliper 0.01**: Stricter matching, 88% match rate, 2,648 obs
- **Caliper 0.05**: More lenient, 95% match rate, 2,990 obs (main specification)

### Pattern 4: Event Study with Binning

```python
# Calculate relative year: calendar_year - pilot_year
df['relative_year'] = df.apply(
    lambda row: (row['year'] - row['pilot_year']) if row['treat'] == 1 else 0,
    axis=1
)

# Binning: collapse tails into [-5, +5] window
def bin_relative_year(rel_year, treat_status):
    if treat_status == 0:
        return 'control'
    elif rel_year <= -5:
        return 'pre_-5'
    elif rel_year >= 5:
        return 'post_5'
    else:
        return str(rel_year)  # -4 to +4

# Exclude baseline t=-1 from regression
event_vars_for_regression = [var for var in event_dummies.columns if var != 'event_-1']
```

## Important Constraints

### Data Quality Rules
1. **GDP deflator must be > 0.8** (consistent base period)
2. **Missing data rate must be < 5%** for any variable
3. **Always use city_name + year as merge keys** (not city_code due to inconsistency)
4. **Use nominal GDP directly from source file** (column 3 of GDP data), NOT calculated as real GDP × deflator

### FDI Processing Rules
- **Correct unit conversion**: Divide by 100, not 10000
- **Use year-specific exchange rates** from `原始数据/汇率.xlsx`
- **Comprehensive interpolation**: Linear interpolation + forward/backward fill for endpoints
- **Data quality verification**: Check major cities (Shanghai, Beijing) for constant values or anomalies
- **Known anomalies**: Sanya 2017 dropped 86.5% (verified as genuine data)

### Regression Requirements
- **Always use log-transformed dependent variable**: `ln_carbon_intensity`
- **All continuous control variables are log-transformed and winsorized** (1%/99%)
- **Must include city and year fixed effects** (two-way FE model)
- **Cluster standard errors at city level** (199-216 clusters)
- **Report both coefficients with and without clustering** for comparison

### Encoding Issues
- Windows console uses GBK encoding
- **Avoid Chinese characters in console output** (use [WARNING], [OK], [INFO] instead of emojis)
- **Avoid Unicode characters** (², ³, ✓) in print statements - replace with ASCII equivalents

## Variable Specifications

### Main Specification (Tertiary Share Model)
```
ln(CEI) = α + β·DID + γ₁·ln(pgdp) + γ₂·ln(pop_density)
          + γ₃·tertiary_share + γ₄·tertiary_share²
          + γ₅·ln(fdi) + γ₆·ln(road_area) + μᵢ + νₜ + ε
```

### Alternative Specification (FDI Openness + Industrial Advanced)
```
ln(CEI) = α + β·DID + γ₁·ln(pgdp) + γ₂·ln(pop_density)
          + γ₃·industrial_advanced + γ₄·fdi_openness
          + γ₅·ln(road_area) + μᵢ + νₜ + ε
```

Where:
- `industrial_advanced = tertiary / secondary` (ratio, not logged)
- `fdi_openness = FDI / nominal_GDP` (ratio, not logged)

## Known Data Issues

### Ordos 2022 GDP Error (Documented, No Impact)
- **File**: `原始数据/地级市碳排放强度.xlsx`
- **Error**: 2022 GDP recorded as 23,158.65 billion yuan (should be 5,613.44)
- **Impact**: None - final dataset uses correct GDP source file
- **Documentation**: `数据质量问题_鄂尔多斯2022年GDP异常.md`

### Shanghai FDI Data Error (Fixed)
- **Issue**: 2011-2023 values were constant at 11,565.46 million USD
- **Fixed**: Restored original growing trend (2011: 12,600.55 → 2023: 24,087.00)
- **Verification**: All 17 observations now have unique values (0% repetition)

### Sanya FDI Anomaly (Verified as Genuine)
- **Issue**: 86.5% drop in 2017 (217.79 → 29.30 million USD)
- **Analysis**: Statistical testing confirms value within normal IQR range
- **Decision**: Keep as genuine data, not an error

## Common Workflows

### Adding New Variables
1. Extract from raw data using **column positions** (not names) due to Chinese encoding
2. Merge with main dataset on `city_name` + `year` with `how='outer'`
3. Handle missing values (interpolate or delete if <5%)
4. Update descriptive statistics
5. Document in `数据清理计划.md`

### Running PSM-DID Analysis
```bash
# Step 1: Run PSM matching
py py代码文件/psm_new_controls.py
# Output: PSM_匹配后数据集.xlsx (caliper=0.02, 2,846 obs)

# Step 2: Run PSM-DID regression
py py代码文件/psm_did_regression_new_controls.py
# Output: PSM-DID基准回归结果表.xlsx

# Step 3: Run parallel trends test
py py代码文件/event_study_psm_new_controls.py
# Output: EventStudy_平行趋势检验结果.xlsx + .png
```

### Modifying PSM Caliper
Edit `py代码文件/psm_new_controls.py`:
- Line 29: Update docstring `卡尺范围: X.XX`
- Line 498: `caliper=X.XX` parameter in `PropensityScoreMatcher()`

Current options:
- **0.01**: Strictest quality, smallest sample (2,648 obs)
- **0.02**: **Current default**, balance (2,846 obs)
- **0.05**: Main specification, largest sample (2,990 obs)

## Git Workflow

```bash
# Check status
git status

# Add changes
git add -A

# Commit with descriptive message
git commit -m "type: description

Details:
- Point 1
- Point 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push
git push
```

Commit types: `feat`, `fix`, `docs`, `refactor`, `chore`

## Research Workflow Dependencies

**Bottom-up workflow** (scripts depend on outputs from previous steps):
```
Raw data → merge scripts → cleaning scripts → variable construction
→ transformation → regression → PSM → PSM-DID → Event Study → Robustness checks
```

**Critical dependencies:**
- All regression scripts require `总数据集_2007-2023_完整版_无缺失FDI.xlsx`
- PSM scripts require final regression dataset (covariates already log-transformed)
- PSM-DID regression scripts require matched PSM output
- Event study script auto-detects data source (tries secondary, falls back to tertiary)

## Package Dependencies

```
pandas==2.0.3        # Data manipulation
numpy==1.24.4        # Numerical operations
openpyxl             # Excel I/O
scipy               # Statistical distributions (t, f)
sklearn             # LogisticRegression (PSM only)
matplotlib          # Visualization (Event Study plots)
```

**NOT installed:**
- `linearmodels` - Use manual LSDV implementation instead
- `statsmodels` - Use scipy.stats + manual calculations

## Research Findings Summary

### Main Conclusion
Low-carbon pilot policies show **no statistically significant effect** on carbon emission intensity across all model specifications and matching strategies.

### Detailed Results

**Alternative Specification (fdi_openness + industrial_advanced, caliper=0.02):**
- Sample: 2,846 obs × 199 cities
- DID coefficient: 0.0275 (p=0.329)
- Parallel trends: ✓ PASSED (p=0.263)
- Long-term effect (t≥+5): +4.0% (p=0.262)

**Main Specification (tertiary share + tertiary_share_sq, caliper=0.05):**
- Sample: 2,990 obs × 200 cities
- DID coefficient: 0.0427 (p=0.105)
- Parallel trends: ✓ PASSED (p=0.408)
- Long-term effect (t≥+5): +5.96% (p=0.081*, marginally significant)

### Consistent Findings Across Specifications
1. Policy effect remains insignificant
2. Control variables behave as expected (ln_pgdp*** negative, industrial_advanced*** negative)
3. Parallel trends assumption satisfied
4. No evidence of emission reduction from pilot policies

## Next Steps (Not Yet Started)

- [ ] Mechanism testing (industrial structure as mediator, not control)
- [ ] Heterogeneity analysis (by batch, region, city size)
- [ ] Additional robustness tests (placebo, exclude concurrent policies)
- [ ] Synthetic control method as alternative identification strategy
