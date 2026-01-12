# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Undergraduate thesis studying the impact of China's low-carbon city pilot policies on carbon emission intensity using multi-period Difference-in-Differences (DID) models with panel data from 216 prefecture-level cities spanning 2007-2023.

**Research Focus:** Evaluating whether low-carbon pilot policies (three batches: 2010, 2012, 2017) effectively reduced carbon emission intensity (CEI).

**Core Innovation:** Incorporating high-precision population density data (298 cities × 27 years) into DID models to control for urban agglomeration effects, separating institutional policy effects from morphological urbanization effects.

**Repository:** https://github.com/biechouwo-coder/G-P.git

## Current Status (January 12, 2025 - Updated)

### Completed Work
- ✅ Data collection: 6 datasets merged (population density, GDP, carbon emissions, industrial structure, FDI, road area, exchange rates)
- ✅ Data cleaning: Removed outliers, handled missing values, ensured data quality
- ✅ Variable transformation: All continuous variables log-transformed and winsorized (1% and 99% percentiles)
- ✅ DID variable construction: Three-batch pilot policy (2010, 2012, 2017) implemented
- ✅ FDI processing: Added FDI openness ratio with year-specific exchange rates
- ✅ Foreign investment level: Added `外商投资水平` variable (FDI/GDP ratio using annual exchange rates)
- ✅ Road area: Added prefecture-level road area variable
- ✅ Industrial upgrading: Added `industrial_advanced` (tertiary/secondary ratio) as alternative specification
- ✅ Exchange rate data: Added `原始数据/汇率.xlsx` (2007-2023 annual USD/RMB rates)
- ✅ Baseline DID regression: Two-way fixed effects model completed
- ✅ Final dataset: `总数据集_2007-2023_最终回归版.xlsx` (3,655 obs × 215 cities × 25 variables, 100% complete)
- ✅ **Propensity Score Matching (PSM)**: Year-by-year matching with 5 covariates (caliper=0.02) - **2,830 obs matched**
- ✅ **PSM-DID regression (Alternative specification)**: Double robust estimation using `industrial_advanced` - **2,830 obs**
- ✅ **PSM-DID regression (Tertiary share model)**: Year-by-year matching with 6 covariates (caliper=0.05) - **2,990 obs matched**
- ✅ **Parallel trends test (Event Study)**: Multi-period event study with [-5,+5] window - **PASSED** ✓
- ✅ **Secondary industry share model**: Robustness check with alternative specification
- ✅ **Data quality fixes**: Corrected Shanghai FDI data error (restored original values 2011-2023)

### Key Research Findings

**1. PSM-DID Results (Tertiary Share Model - Main Specification)**
- DID coefficient: 0.0427 (p=0.105, not significant at 10% level)
- Sample: 2,990 obs × 200 cities × 17 years
- Control variables: ln_pgdp***, tertiary_share**, tertiary_share_sq***, ln_road_area** significant
- Parallel trends: ✓ PASSED (pre-period slope p=0.4082)
- **Long-term effect (t≥+5)**: +5.96% increase in emissions (p=0.081*, marginally significant)

**2. Secondary Industry Share Model (Robustness Check)**
- DID coefficient: 0.0332 (p=0.200, less significant than tertiary model)
- Secondary share variables not significant (possible multicollinearity)
- Parallel trends: ✓ PASSED (pre-period slope p=0.3097)
- Long-term effect (t≥+5): +5.03% (p=0.142, not significant)

**3. Policy Interpretation**
- Short-term (0-2 years): No significant effect
- Medium-term (3-4 years): Positive trend but not significant
- **Long-term (≥5 years): Policy may INCREASE emissions by ~6% (p<0.1)**
- Possible mechanisms: "Pollution haven effect" or "Infrastructure expansion effect"
- **Conclusion**: Low-carbon pilot policies show no significant emission reduction effect; may even increase emissions in the long run

### Next Steps
- [ ] Mechanism testing (industrial structure as mediator, not control)
- [ ] Heterogeneity analysis (by batch, region, city size)
- [ ] Additional robustness tests (placebo, exclude concurrent policies)
- [ ] Synthetic control method as alternative identification strategy

## Data Processing Commands

### Python Environment
```bash
# Verify Python version (should be 3.8.1)
py --version

# Install dependencies (if needed)
py -m pip install pandas openpyxl

# Navigate to project directory
cd c:\Users\HP\Desktop\毕业论文

# Run data processing scripts
py py代码文件/fix_data_quality_issues.py  # Final data cleaning
py py代码文件/diagnose_data_issues.py     # Diagnose data quality issues
py py代码文件/verify_final_data.py        # Verify final dataset
```

### Git Workflow
```bash
# Check status
git status

# Add all changes
git add -A

# Commit with descriptive message
git commit -m "type: description"

# Push to GitHub
git push
```

## Research Data Architecture

### Final Dataset
**File:** `总数据集_2007-2023_完整版.xlsx`
- **Observations:** 3,672 city-year pairs
- **Cities:** 216 prefecture-level cities
- **Years:** 2007-2023 (17 years)
- **Variables:** 19 (100% complete, no missing values)

**Quality Checks:**
- ✅ GDP deflator minimum: 0.8410 (>0.8, indicating consistent base year)
- ✅ All variables: 0% missing
- ✅ Outliers removed (48 cities excluded due to data quality issues)

### Key Variables

| Variable | Type | Description | Unit | Notes |
|----------|------|-------------|------|-------|
| `year` | Time | Year | - | 2007-2023 |
| `city_name` | ID | City name | - | Chinese characters |
| `city_code` | ID | 6-digit administrative code | - | National Bureau of Statistics |
| `population` | Control | Total population (permanent residents) | 万人 | Used to calculate per capita GDP |
| `pop_density` | **Core Control** | Population density | 人/平方公里 | Key innovation: captures agglomeration effects |
| `gdp_real` | Control | Real GDP (2000 base) | 亿元 | Eliminates price effects |
| `gdp_per_capita` | Control | Real GDP per capita (2000 base) | 元/人 | Economic development indicator |
| `gdp_deflator` | Control | GDP deflator | - | Base year 2000 = 1.0 |
| `carbon_intensity` | **Dependent Variable** | CO₂ per unit GDP | 吨/亿元（2000年基期） | Primary outcome |
| `tertiary_share` | Control | Tertiary industry share | 比例 | Industrial structure |
| `industrial_upgrading` | Alternative Outcome | Tertiary/Secondary ratio | 比例 | Industrial upgrading measure |
| `did` | **Policy Variable** | DID policy variable | - | Treat × Post (multi-period) |
| `treat` | Policy | Treatment group indicator | - | 1 if pilot city, 0 otherwise |
| `post` | Policy | Post-policy period indicator | - | 1 if year ≥ pilot_year |
| `pilot_year` | Policy | Pilot implementation year | - | 2010, 2012, or 2017 |
| `fdi` | Control | Foreign direct investment | 百万美元 | Original FDI data |
| `外商投资水平` | Control | FDI/GDP ratio | 比例 | Uses nominal GDP + year-specific exchange rates, calculated as (FDI USD × exchange rate / 100) / nominal GDP |
| `road_area` | Control | Road area per capita | 平方米/人 | Prefecture-level data |
| `ln_road_area` | Control | Log road area per capita | - | ln(road_area + 1) |
| `industrial_advanced` | Alternative | Industrial upgrading ratio | 比例 | tertiary/secondary (三产/二产比值), used in alternative specification |

### Data Merge Strategy

**Critical Pattern:** Column position-based extraction (not names) due to Chinese encoding issues:

```python
# Standard pattern used in all merge scripts
df = pd.read_excel('filename.xlsx')

# Extract by column position (indices)
df = df.iloc[:, [col_positions]]

# Rename to standard English variable names
df.columns = ['var1', 'var2', 'var3', ...]

# Outer merge on city_name + year (NOT city_code due to inconsistency)
df_merged = pd.merge(df1, df2, on=['city_name', 'year'], how='outer')
```

**Why this matters:**
- Chinese column names cause encoding errors in Windows console
- City_name matching is more reliable than city_code (inconsistent availability)
- Always use `how='outer'` to preserve all observations, then filter

### Data Quality Issues Fixed

**Issue 1: GDP Deflator Anomalies**
- Problem: 19 cities had gdp_deflator < 0.8 (lowest: 0.407)
- Root cause: Inconsistent base periods in source data (resource-depleted cities, newly established cities)
- Solution: Excluded all observations with gdp_deflator < 0.8
- Cities excluded: Qitaihe, Shuangyashan, Hegang, Yichun, Karamay, Shihezi, Baishan, Anshan, Fuxin, Turpan, Guyuan, Qingyang, Lüliang, Wuhai, Liaoyuan, Tonghua, Baise, Jincheng, Jiayuguan

**Issue 2: Population Missing Data**
- Problem: 167 observations missing population and gdp_per_capita (3.72%)
- Solution:
  - Middle-year gaps: Linear interpolation (Turpan city)
  - Endpoint gaps (2007 or 2023): Exclude entire city (29 cities)

## Empirical Methodology

### Baseline DID Model

```
CEI_it = α₀ + β₁·DID_it + β₂·ln(pop_den_it) + Σγₖ·Control_kit + μᵢ + νₜ + ε_it
```

Where:
- `CEI_it`: Carbon emission intensity (tons/100M yuan, 2000 base)
- `DID_it`: Treat_i × Post_it (policy intervention)
- `pop_den_it`: Population density (log-transformed, persons/km²)
- `μᵢ`: City fixed effects (controls time-invariant heterogeneity)
- `νₜ`: Year fixed effects (controls common temporal shocks)
- `ε_it`: Error term clustered at city level

### DID Variable Construction (COMPLETED)

**Implementation:** See [py代码文件/construct_did_variable.py](py代码文件/construct_did_variable.py)

**Three Pilot Batches:**
- Batch 1 (2010): 5 provinces + 8 cities
  - Provinces: 广东, 辽宁, 湖北, 陕西, 云南 (all prefecture-level cities in these provinces)
  - Cities: 天津市, 重庆市, 深圳市, 厦门市, 杭州市, 南昌市, 贵阳市, 保定市
- Batch 2 (2012): 1 province + 26 cities
  - Province: 海南省
  - Cities: 北京市, 上海市, 石家庄市, 秦皇岛市, etc.
- Batch 3 (2017): 45 cities
  - Cities: 乌海市, 沈阳市, 大连市, 朝阳市, etc.

**Construction Logic:**
```python
# Implemented in construct_did_variable.py
city_to_pilot_year = {}  # Maps city_name to pilot_year (2010, 2012, or 2017)

# For province-level pilots, all cities in that province are included
df['treat'] = df['city_name'].map(city_to_pilot_year).notna().astype(int)
df['pilot_year'] = df['city_name'].map(city_to_pilot_year)
df['post'] = df['year'] >= df['pilot_year']
df['did'] = df['treat'] * df['post']
```

**Key Features:**
- Multi-period DID with different implementation years
- Province-level pilots cover all prefecture cities in that province
- If a city appears in multiple batches, earliest year is used
- DID=1 only when year ≥ pilot_year for that city

### Theoretical Framework

**Extended STIRPAT Model:**

Traditional STIRPAT: `I = P × A × T`
- I = Environmental impact (carbon emissions)
- P = Population **size**
- A = Affluence (GDP per capita)
- T = Technology level

**This Study's Extension:**
- Add population **density** (spatial distribution)
- Distinguish between:
  - **Agglomeration positive effect**: High density → shared infrastructure → lower per capita emissions
  - **Congestion negative effect**: Overcrowding → traffic congestion → higher per capita emissions

**Contribution:** By controlling for density, separate **institutional policy effects** from **morphological urbanization effects**.

## File Organization

### Raw Data (DO NOT MODIFY)
- `原始数据/298个地级市人口密度1998-2024年无缺失.xlsx` - Core data (298 cities × 27 years, no missing)
- `原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx` - GDP with deflator
- `原始数据/地级市碳排放强度.xlsx` - Carbon emissions
- `原始数据/2000-2023地级市产业结构 .xlsx` - Industrial structure
- `原始数据/1996-2023年地级市外商直接投资FDI.xlsx` - Foreign direct investment
- `原始数据/各省+地级市+县级市人均道路面积.xlsx` - Road area (Sheet 1: prefecture-level)
- `原始数据/汇率.xlsx` - Exchange rates (2007-2023, USD/RMB annual average)
- `原始数据/试点城市名单.xlsx` - List of all pilot cities with implementation years

### Processed Data
- `总数据集_2007-2023_最终回归版.xlsx` - **RECOMMENDED FOR REGRESSION** (3,672 obs × 24 variables, 100% complete, log-transformed and winsorized)
- `倾向得分匹配_匹配后数据集.xlsx` - **PSM-MATCHED SAMPLE** (3,162 obs × 24 variables, matched 1:1 with replacement)
- `倾向得分匹配_平衡性检验.xlsx` - Balance diagnostics (standardized bias before/after matching)
- `倾向得分匹配_年度统计.xlsx` - Yearly Logit regression statistics (pseudo R², PS distribution)
- `倾向得分匹配_汇总报告.xlsx` - Comprehensive PSM summary report
- `总数据集_2007-2023_完整版.xlsx` - Original merged data (3,672 obs × 19 variables)
- `描述性统计表_最终回归版.xlsx` - Descriptive statistics with distribution tests
- `基准回归结果表.xlsx` - Baseline DID regression results
- `缩尾处理报告.xlsx` - Winsorization treatment report
- `试点城市名单.xlsx` - List of all pilot cities with implementation years

### Python Scripts (py代码文件/)

**Data Merging:**
- `merge_final.py` - Initial 3-dataset merge (population + GDP + carbon)
- `merge_industrial_structure.py` - Add industrial structure data
- `data_cleaning_final.py` - 4-step cleaning protocol

**Data Quality:**
- `diagnose_data_issues.py` - Comprehensive diagnostic (GDP deflator anomalies, missing data)
- `fix_data_quality_issues.py` - **MAIN SCRIPT** for final dataset generation
- `verify_final_data.py` - Quality validation

**Variable Construction:**
- `construct_did_variable.py` - **Build DID policy variables** (3 batches: 2010, 2012, 2017)
- `process_fdi_data.py` - Process FDI and calculate FDI openness ratio
- `add_road_area_variable.py` - Add prefecture-level road area data
- `reconstruct_carbon_intensity.py` - Recalculate CEI with correct base period
- `add_population_variables.py` - Add population and per capita GDP
- `generate_final_stats.py` - Generate descriptive statistics table

**Data Transformation (Regression Preparation):**
- `transform_variables_for_regression.py` - Generate log variables (ln_pop_density, ln_pgdp, ln_pop, ln_fdi)
- `winsorize_and_log_transform.py` - **Apply 1%/99% winsorization and ln(carbon_intensity)**
- `generate_regression_ready_stats.py` - Generate descriptive statistics for regression
- `generate_final_winsorized_stats.py` - Generate final regression statistics with distribution tests

**Regression Analysis:**
- `did_baseline_regression.py` - **Baseline DID regression with two-way fixed effects and clustered SE**
  - Implements LSDV (Least Squares Dummy Variable) method manually
  - City and year fixed effects via dummy variables
  - Cluster-robust standard errors at city level
  - Uses pandas, numpy, scipy only (no linearmodels dependency)
  - **Architecture pattern:**
    ```python
    # Standard regression pattern used throughout
    def ols_regression(y, X):
        X = np.column_stack([np.ones(len(y)), X])
        beta = np.linalg.solve(np.dot(X.T, X), np.dot(X.T, y))
        residuals = y - np.dot(X, beta)
        # Calculate clustered SE by city
    ```

**Robustness Testing:**
- `propensity_score_matching.py` - **Propensity Score Matching (PSM) for PSM-DID**
  - Year-by-year Logit regression (not pooled across years)
  - 1:1 nearest neighbor matching with replacement
  - Caliper: 0.05 (propensity score difference threshold)
  - 6 covariates: ln_pgdp, ln_pop_density, tertiary_share, tertiary_share_sq, ln_fdi, ln_road_area
  - Balance diagnostics using standardized bias (< 10% threshold)
  - Uses sklearn.linear_model.LogisticRegression
  - Outputs: matched dataset, balance statistics, yearly summary
  - **Architecture:** Class-based design `PropensityScoreMatcher` with modular methods
    - `handle_missing_values()` - Drop observations with missing covariates
    - `estimate_propensity_scores()` - Year-by-year Logit models
    - `perform_matching()` - 1:1 nearest neighbor with caliper
    - `check_balance()` - Standardized bias calculations
    - `generate_reports()` - Excel outputs for diagnostics

- `psm_new_controls.py` - **Alternative PSM specification with 5 covariates**
  - Uses `industrial_advanced` (tertiary/secondary ratio) instead of tertiary_share + tertiary_share_sq
  - Tighter caliper: 0.02 (stricter matching for higher quality)
  - 5 covariates: ln_pgdp, ln_pop_density, industrial_advanced, ln_fdi, ln_road_area
  - Matched sample: 2,830 observations (198 cities)
  - Outputs saved to: `人均GDP+人口集聚程度+产业高级化+FDI+人均道路面积/` directory
  - All covariates satisfy balance criterion (|bias| < 10%)

**PSM-DID Analysis:**
- `psm_did_regression.py` - **PSM-DID regression with double robust estimation**
  - Loads `倾向得分匹配_匹配后数据集.xlsx` (2,990 obs)
  - Two models: (1) without controls, (2) with 6 controls
  - Double robust estimation: PSM + control variables in regression
  - Control variables: ln_pgdp, ln_pop_density, tertiary_share, tertiary_share_sq, ln_fdi, ln_road_area
  - Uses manual LSDV implementation for two-way fixed effects
  - Cluster-robust standard errors at city level (200 clusters)
  - Outputs: `PSM-DID基准回归结果表.xlsx`

- `psm_did_regression_secondary.py` - **Robustness check with secondary industry share**
  - Alternative specification using secondary_share instead of tertiary_share
  - Loads data from `二产占比模型_分析结果/PSM匹配后数据集_含二产占比.xlsx`
  - Tests sensitivity to industry structure variable choice
  - Outputs: `PSM-DID回归结果表_二产占比.xlsx`

- `psm_did_regression_new_controls.py` - **Alternative specification with industrial_advanced**
  - Loads matched sample from `人均GDP+人口集聚程度+产业高级化+FDI+人均道路面积/PSM_匹配后数据集.xlsx`
  - 5 control variables: ln_pgdp, ln_pop_density, industrial_advanced, ln_fdi, ln_road_area
  - DID coefficient: 0.0346 (p=0.184, not significant)
  - Results consistent with main specification - policy effect remains insignificant
  - Outputs: `人均GDP+人口集聚程度+产业高级化+FDI+人均道路面积/PSM-DID基准回归结果表.xlsx`

**Event Study (Parallel Trends Test):**
- `event_study_parallel_trends.py` - **Multi-period event study for parallel trends verification**
  - Auto-detects data source (tries secondary share, falls back to tertiary share)
  - Calculates relative year: calendar_year - pilot_year
  - Binning: [-5, +5] window with tails collapsed (pre_-5, post_5)
  - Generates 11 event dummies (excludes baseline t=-1)
  - Two-way fixed effects + clustered SE + 6 control variables
  - Tests pre-period slope (parallel trends assumption)
  - Outputs: event study coefficient table + visualization plot
  - **Key pattern:** Automatically adapts control variables based on data source:
    ```python
    if use_secondary:
        control_vars = [ln_pgdp, ln_pop_density, secondary_share,
                       secondary_share_sq, ln_fdi, ln_road_area]
    else:
        control_vars = [ln_pgdp, ln_pop_density, tertiary_share,
                       tertiary_share_sq, ln_fdi, ln_road_area]
    ```

**Data Extraction (Secondary Industry Share):**
- `add_real_secondary_share.py` - **Extract secondary industry share from original source**
  - Reads `原始数据/2000-2023地级市产业结构 .xlsx` (sheet index 1)
  - Extracts column 10: 第二产业占GDP比重
  - Merges on city_code + year
  - Converts from percentage to ratio if max value > 1
  - Cleans anomalies: removes values < 0 or > 1
  - Creates squared term: secondary_share_sq
  - Outputs: `二产占比模型_分析结果/PSM匹配后数据集_含二产占比.xlsx`

### Documentation
- `数据清理计划.md` - Complete data cleaning log (Chinese, detailed steps, 17 sections)
- `实验思路md` - Research design and methodology (Chinese, 408 lines)
- `基础回归记录表.md` - **Baseline DID regression documentation** (model specification, results, interpretation)
- `PSM-DID回归分析记录.md` - **PSM-DID analysis with event study results** (main specification)
- `二产占比模型_分析结果/二产vs三产对比分析.md` - **Model comparison documentation** (robustness check)
- `README.md` - Project overview (bilingual)
- `CLAUDE.md` - This file (guidance for AI assistants)

## Important Constraints

1. **Data Integrity**
   - Never modify files in `原始数据/` (keep originals intact)
   - Always use column positions (indices) not names when reading Excel with Chinese headers
   - Use `city_name` + `year` as merge keys (not `city_code`)

2. **Data Quality Standards**
   - GDP deflator must be > 0.8 (consistent base period)
   - Missing data rate must be < 5% for any variable
   - Prefer deletion over heavy imputation

3. **Encoding Issues**
   - Windows console uses GBK encoding
   - Avoid Chinese characters in console output (use [WARNING], [OK] instead of emojis)
   - If script fails with UnicodeEncodeError, remove special Unicode characters

4. **Sample Selection**
   - Final sample: 216 cities (excluded 48 due to data quality)
   - Must document reasons for excluding any cities
   - Prioritize data quality over sample size

5. **Time Period**
   - Core analysis: 2007-2023 (17 years)
   - Population data available: 1998-2024 (27 years)
   - Align to common period across all datasets

6. **FDI Data Processing**
   - CRITICAL: Use correct unit conversion (divide by 100, not 10000)
   - Use nominal GDP (real GDP × deflator), not real GDP
   - Use year-specific exchange rates, not fixed rate
   - Handle city name changes (e.g., 襄樊→襄阳, 思茅→普洱)
   - **Data quality verification**: Check major cities (Shanghai, Beijing, Shenzhen) for constant values
   - Original FDI data source: `原始数据/1996-2023年地级市外商直接投资FDI.xlsx` (column position-based extraction)
   - Always verify that FDI shows realistic year-to-year variation, not repeated values

7. **City-Level Data Granularity**
   - Always use full 6-digit city codes for matching
   - NEVER use `// 10000` operation which converts city codes to province codes
   - This causes data aggregation loss (all cities in same province get same value)
   - Verify uniqueness: each province should have multiple unique values, not just 1

## Common Workflows

### Adding New Variables
1. Extract from raw data using column positions
2. Merge with main dataset on `city_name` + `year`
3. Handle missing values (interpolate or delete)
4. Update descriptive statistics
5. Document in `数据清理计划.md`

### Running DID Regression
```bash
# Run baseline DID regression (two-way fixed effects with clustered SE)
py py代码文件/did_baseline_regression.py

# Output files:
# - 基准回归结果表.xlsx (regression results comparison)
# - Console output with detailed statistics
```

### Running Propensity Score Matching
```bash
# Run PSM analysis (year-by-year matching) - Main specification
py py代码文件/propensity_score_matching.py

# Output files:
# - 倾向得分匹配_匹配后数据集.xlsx (matched dataset for PSM-DID)
# - 倾向得分匹配_平衡性检验.xlsx (balance diagnostics)
# - 倾向得分匹配_年度统计.xlsx (yearly summary)
# - 倾向得分匹配_汇总报告.xlsx (comprehensive report)

# Matching specifications (main):
# - 6 covariates: ln_pgdp, ln_pop_density, tertiary_share, tertiary_share_sq, ln_fdi, ln_road_area
# - Method: 1:1 nearest neighbor matching with replacement
# - Caliper: 0.05 (maximum propensity score difference)
# - Year-by-year estimation (17 separate Logit regressions)
# - Balance criterion: standardized bias < 10%

# Run PSM analysis - Alternative specification (industrial_advanced)
py py代码文件/psm_new_controls.py

# Output files (saved to: 人均GDP+人口集聚程度+产业高级化+FDI+人均道路面积/):
# - PSM_匹配后数据集.xlsx (2,830 obs)
# - PSM_平衡性检验.xlsx
# - PSM_年度统计.xlsx
# - PSM_汇总报告.xlsx

# Matching specifications (alternative):
# - 5 covariates: ln_pgdp, ln_pop_density, industrial_advanced, ln_fdi, ln_road_area
# - Method: 1:1 nearest neighbor matching with replacement
# - Caliper: 0.02 (stricter matching for higher quality)
# - Year-by-year estimation (17 separate Logit regressions)
# - Balance criterion: standardized bias < 10%
```

**Model Specification:**
```
ln(CEI_it) = α₀ + β₁·did_it + β₂·ln_pgdp_it + β₃·ln_pop_density_it
             + β₄·tertiary_share_it + β₅·ln_fdi_it + β₆·ln_road_area_it
             + μᵢ + νₜ + ε_it
```

**Key Points:**
- Dependent variable: `ln_carbon_intensity` (log-transformed, winsorized)
- All controls: log-transformed and winsorized (except tertiary_share)
- Fixed effects: 215 city dummies + 16 year dummies (231 total)
- Standard errors: Clustered at city level (216 clusters)
- Significance: *** p<0.01, ** p<0.05, * p<0.1

### Diagnosing Data Issues
```bash
# Run comprehensive diagnostic
py py代码文件/diagnose_data_issues.py

# Check specific variable
py py代码文件/verify_final_data.py
```

### Extending the Analysis

**Adding new variables to the dataset:**
1. Create new script following pattern: `add_[variable_name].py`
2. Load latest dataset: `总数据集_2007-2023_最终回归版.xlsx`
3. Extract new data using column positions (not names) due to Chinese encoding
4. Merge on `city_name` + `year` with `how='outer'`
5. Handle missing values (delete if <5%, else consider imputation)
6. Save with updated filename suffix
7. Update descriptive statistics

**Adding squared or interaction terms:**
```python
# Pattern from add_squared_term.py
import pandas as pd

df = pd.read_excel('总数据集_2007-2023_最终回归版.xlsx')

# Add squared term
df['ln_pop_density_squared'] = df['ln_pop_density'] ** 2

# Save with new suffix
df.to_excel('总数据集_2007-2023_最终回归版_平方项.xlsx', index=False)
```

**Running new DID specifications:**
1. Copy `did_baseline_regression.py` as template
2. Modify `control_vars` list to include new variables
3. Update model specification in comments
4. Run and save results to new Excel file
5. Document findings in CLAUDE.md status section

## Git Commit History (Key Revisions)

- `515eb83` - Complete baseline DID regression analysis with two-way fixed effects (Jan 6)
- `ca942af` - Log-transform carbon intensity and winsorize continuous variables (Jan 6)
- `c4b62a5` - Generate log variables and descriptive statistics for regression (Jan 6)
- `b40dd4d` - Update CLAUDE.md with latest data processing progress (Jan 6)
- `aa24ff7` - Delete province-level road area sheet, keep prefecture-level data (Jan 6)
- `99ac6b6` - Fix road area variable to prefecture-level (Jan 6)
- `0a45d06` - Add road area per capita variable (ln_road_area) (Jan 6)
- `e8091f8` - Clean up project files, keep only final complete version (Jan 6)
- `ed78308` - Fix 5 critical errors in FDI data processing (Jan 6)
- `3fa7517` - Add FDI data and calculate FDI openness ratio (Jan 6)

## Research Plan Reference

See `实验思路md` (408 lines) for:
- Complete theoretical framework
- Detailed variable definitions
- Robustness testing strategy (parallel trends, PSM-DID, placebo, IV)
- Mechanism analysis approach
- Expected contributions

**Key Sections:**
- Section 1.2: Pilot policy evolution (three batches, quasi-natural experiment)
- Section 2.1: STIRPAT framework + population density extension
- Section 2.2: Variable definitions and measurement logic
- Section 3: Multi-period DID model specification
- Section 4: Robustness testing (6 comprehensive methods)

## Important Constraints

1. **Data Integrity**
   - Never modify files in `原始数据/` (keep originals intact)
   - Always use column positions (indices) not names when reading Excel with Chinese headers
   - Use `city_name` + `year` as merge keys (not `city_code`)

2. **Data Quality Standards**
   - GDP deflator must be > 0.8 (consistent base period)
   - Missing data rate must be < 5% for any variable
   - Prefer deletion over heavy imputation
   - All continuous variables are log-transformed and winsorized (1%/99%)

3. **Encoding Issues**
   - Windows console uses GBK encoding
   - Avoid Chinese characters in console output (use [WARNING], [OK] instead of emojis)
   - If script fails with UnicodeEncodeError, remove special Unicode characters (², ³, etc.)
   - Replace R² with R2 in print statements

4. **Sample Selection**
   - Final sample: 216 cities (excluded 48 due to data quality)
   - Must document reasons for excluding any cities
   - Prioritize data quality over sample size

5. **Time Period**
   - Core analysis: 2007-2023 (17 years)
   - Population data available: 1998-2024 (27 years)
   - Align to common period across all datasets

6. **FDI Data Processing**
   - CRITICAL: Use correct unit conversion (divide by 100, not 10000)
   - Use nominal GDP (real GDP × deflator), not real GDP
   - Use year-specific exchange rates, not fixed rate
   - Handle city name changes (e.g., 襄樊→襄阳, 思茅→普洱)
   - **Data quality verification**: Check major cities (Shanghai, Beijing, Shenzhen) for constant values
   - Original FDI data source: `原始数据/1996-2023年地级市外商直接投资FDI.xlsx` (column position-based extraction)
   - Always verify that FDI shows realistic year-to-year variation, not repeated values

7. **City-Level Data Granularity**
   - Always use full 6-digit city codes for matching
   - NEVER use `// 10000` operation which converts city codes to province codes
   - This causes data aggregation loss (all cities in same province get same value)
   - Verify uniqueness: each province should have multiple unique values, not just 1

8. **Regression Analysis Requirements**
   - **Always use log-transformed dependent variable:** `ln_carbon_intensity`
   - **All continuous control variables are log-transformed and winsorized**
   - **Must include city and year fixed effects** (two-way FE model)
   - **Cluster standard errors at city level** (216 clusters)
   - Report both coefficients with and without clustering for comparison
   - Use LSDV method if linearmodels package unavailable

9. **Package Dependencies**
   - **Core packages:** pandas 2.0.3, numpy 1.24.4
   - **Optional:** scipy (for t-distribution in p-value calculation)
   - **NOT installed:** linearmodels (use manual LSDV implementation instead)
   - If network unavailable, rely on manual OLS implementation (see `did_baseline_regression.py`)

10. **PSM Analysis Requirements**
    - Year-by-year Logit regression (NOT pooled across years)
    - 1:1 nearest neighbor matching WITH replacement
    - Caliper: 0.05 (maximum propensity score difference threshold)
    - Covariates: ln_pgdp, ln_pop_density, tertiary_share, tertiary_share_sq, ln_fdi, ln_road_area
    - Balance criterion: standardized bias < 10% for all covariates
    - McFadden's pseudo R² should be in range [0, 1] (typically 0.06-0.11)
    - Critical bug: Ensure caliper logic actually EXCEEDS samples beyond threshold (lines 234-237 in `propensity_score_matching.py`)

11. **Event Study (Parallel Trends Test) Requirements**
    - Calculate relative year: calendar_year - pilot_year
    - Implement binning: [-5, +5] window with tails collapsed
    - Exclude baseline period t=-1 from regression (set coefficient to 0)
    - Use same control variables as PSM-DID regression
    - Test pre-period slope for significance (should be p > 0.1 for parallel trends)
    - Long-term effect defined as t≥+5 (policy implementation 5+ years ago)
    - Visualization: coefficient plot with 95% CI, vertical line at policy implementation


## Regression Analysis Notes

### Current Baseline Results

**Data:** `总数据集_2007-2023_最终回归版.xlsx`
- 3,672 observations × 216 cities × 17 years
- Dependent variable: `ln_carbon_intensity` (log-transformed, winsorized)
- All continuous controls: log-transformed and winsorized

**Key Findings:**
- Model (1) no controls: DID coef = 0.0186* (p=0.083, significant at 10%)
- Model (2) with controls: DID coef = 0.0204 (p=0.459, clustered SE, not significant)
- Policy effect NOT statistically significant after clustering
- Control variables highly significant (ln_pgdp***, ln_pop_density***, tertiary_share***, ln_road_area***)
- Model fit: R² > 0.97 for both models

**Interpretation:**
- Policy shows small positive effect on emissions (unexpected direction)
- Not statistically distinguishable from zero with clustered SE
- Possible reasons: sample heterogeneity, time lags, implementation variation
- Control variables absorb much of the variation (GDP, density, industrial structure)

### Next Analysis Steps

1. **PSM-DID Regression** (Next priority - use matched dataset)
   - Run DID regression on `倾向得分匹配_匹配后数据集.xlsx`
   - Compare PSM-DID results with baseline DID
   - Assess whether matching changes policy effect estimates
   - Expected: smaller but more reliable treatment effects

2. **Parallel Trends Test** (CRITICAL for DID validity)
   - Event study to verify pre-trend parallelism
   - Plot DID coefficients by year relative to treatment
   - Essential for DID identification assumption

3. **Heterogeneity Analysis**
   - By pilot batch (2010 vs 2012 vs 2017)
   - By region (East vs Central vs West)
   - By city size/development level

4. **Additional Robustness Tests**
   - Placebo test (random treatment assignment)
   - Exclude concurrent policies (Smart City, Innovative City pilots)

5. **Mechanism Testing**
   - Industrial structure channel (tertiary_share)
   - Technology innovation channel
   - Energy structure optimization channel

### Understanding Regression Output Structure

**Excel output format from `did_baseline_regression.py`:**
- **Sheet 1: Model Comparison** - Side-by-side results
  - Columns: Variable, Coef (no FE), SE (no FE), Coef (FE), SE (FE), t-stat, p-value
  - Rows: All variables + constant
- **Sheet 2: Model Statistics** - R², N, observations
- **Sheet 3: Clustered SE Comparison** - With/without clustering

**Key regression objects to understand:**
```python
# Fixed effects implementation
city_dummies = pd.get_dummies(df['city_name'], prefix='city', drop_first=True)
year_dummies = pd.get_dummies(df['year'], prefix='year', drop_first=True)

# Clustering by city (216 clusters)
clusters = df['city_name']
# Calculate cluster-robust variance matrix
```

**Interpreting clustered vs. non-clustered SE:**
- Non-clustered: Standard OLS assumption (i.i.d. errors)
- Clustered: Allows serial correlation within cities over time
- For panel data, **clustered SE is the correct standard**
- If clustered SE >> non-clustered SE, indicates within-city correlation

## Research Workflow and Dependencies

### Analysis Pipeline (Recommended Order)
1. **Data preparation** → `总数据集_2007-2023_最终回归版.xlsx`
2. **Descriptive statistics** → `描述性统计表_最终回归版.xlsx`
3. **Baseline DID regression** → `基准回归结果表.xlsx`
4. **PSM sample selection** → `倾向得分匹配_匹配后数据集.xlsx` (2,990 obs)
5. **PSM-DID regression** → `PSM-DID基准回归结果表.xlsx`
6. **Parallel trends test** → Event study results table + visualization
7. **Robustness tests** → Secondary industry share model (`二产占比模型_分析结果/`)
8. **Heterogeneity analysis** → By batch, region, city size
9. **Mechanism tests** → Mediation analysis (industrial structure as mediator)

### Script Dependencies
**Bottom-up workflow** (scripts depend on outputs from previous steps):
```
Raw data → merge scripts → cleaning scripts → variable construction
→ transformation → regression → PSM → PSM-DID → Event Study → Robustness checks
```

**Critical dependencies:**
- All regression scripts require `总数据集_2007-2023_最终回归版.xlsx`
- PSM script requires final regression dataset (6 covariates already log-transformed)
- PSM-DID regression script requires `倾向得分匹配_匹配后数据集.xlsx`
- Event study script auto-detects data source (tries secondary, falls back to tertiary)
- Any new variables must be added BEFORE transformation/winsorization
- Always preserve the "final regression version" as the canonical source

### Package Dependencies
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

## Code Architecture Patterns

### Pattern 1: Manual OLS with Clustered Standard Errors
All regression scripts use this pattern (no linearmodels dependency):

```python
def ols_regression_clustered(y, X, cluster_var, df):
    # Add constant
    X = np.column_stack([np.ones(len(y)), X])

    # OLS estimation: beta = (X'X)^(-1)X'y
    XtX = np.dot(X.T, X)
    Xty = np.dot(X.T, y)
    beta = np.linalg.solve(XtX, Xty)

    # Residuals
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

### Pattern 2: Two-Way Fixed Effects via LSDV
```python
# Create city and year dummies
city_dummies = pd.get_dummies(df['city_entity'], prefix='city', drop_first=True)
year_dummies = pd.get_dummies(df['year_entity'], prefix='year', drop_first=True)

# Design matrix: variables + city FE + year FE
X = np.column_stack([
    df[did_var].values,
    *[df[var].values for var in control_vars],
    city_dummies.values,
    year_dummies.values
])
```

### Pattern 3: Event Study with Binning
```python
# Calculate relative year
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

df['binned_relative_year'] = df.apply(
    lambda row: bin_relative_year(row['relative_year'], row['treat']),
    axis=1
)

# Create event dummies (exclude baseline t=-1)
event_dummies = pd.get_dummies(df['binned_relative_year'], prefix='event')
event_vars_for_regression = [var for var in event_dummies.columns if var != 'event_-1']
```

### Pattern 4: Auto-Adapt Control Variables
The event study script demonstrates flexible control variable selection:

```python
import os
data_file = '二产占比模型_分析结果/PSM匹配后数据集_含二产占比.xlsx'
if os.path.exists(data_file):
    df = pd.read_excel(data_file)
    use_secondary = True
else:
    df = pd.read_excel('倾向得分匹配_匹配后数据集.xlsx')
    use_secondary = False

# Adapt control variables based on data source
if use_secondary:
    control_vars = [ln_pgdp, ln_pop_density, secondary_share,
                   secondary_share_sq, ln_fdi, ln_road_area]
else:
    control_vars = [ln_pgdp, ln_pop_density, tertiary_share,
                   tertiary_share_sq, ln_fdi, ln_road_area]
```

This allows the same script to run on different model specifications without modification.

## Key Analysis Results Reference

### PSM-DID Main Specification (Tertiary Share)
- **DID coefficient**: 0.0427 (p=0.105, not significant)
- **Interpretation**: No evidence that low-carbon pilot policy reduced emissions
- **Control variables**:
  - ln_pgdp: -0.3657*** (higher GDP → lower emissions, EKC confirmed)
  - tertiary_share: 1.7389** (positive effect, but with squared term creates U-curve)
  - tertiary_share_sq: -2.6387*** (inflection point at 32.95%)
  - ln_road_area: 0.1031** (more roads → higher emissions, unexpected)
- **Parallel trends**: ✓ PASSED (pre-period slope p=0.4082)
- **Long-term effect (t≥+5)**: +5.96% (p=0.081*, marginally significant)

### Event Study Dynamic Effects
- t=0 (policy year): -0.0028 (p=0.805)
- t=1: 0.0069 (p=0.697)
- t=2: 0.0361 (p=0.112)
- t=3: 0.0296 (p=0.207)
- t=4: 0.0189 (p=0.486)
- t≥+5: 0.0596* (p=0.081) ← **Policy increases emissions in long run**

**Conclusion**: Policy shows no short-term benefit, may increase emissions by ~6% after 5+ years.

### Robustness Check (Secondary Share Model)
- **DID coefficient**: 0.0332 (p=0.200, even less significant)
- **Secondary share variables**: Both NOT significant (possible multicollinearity)
- **Parallel trends**: ✓ PASSED (pre-period slope p=0.3097)
- **Long-term effect (t≥+5)**: 0.0503 (p=0.142, not significant)

**Conclusion**: Results robust - policy effect remains insignificant across specifications.

## Common Issues and Solutions

### Issue 1: PSM Caliper Logic Bug
**Problem**: Lines 234-237 in `propensity_score_matching.py` had else clause that still added samples beyond caliper threshold
**Impact**: 100% match rate (all samples matched regardless of PS difference)
**Solution**: Removed erroneous else clause, now properly excludes samples with PS difference > 0.05
**Result**: Matched sample reduced from 3,162 to 2,990 obs (5.4% reduction)

### Issue 2: McFadden R² Calculation Error
**Problem**: Null model log-likelihood used wrong formula
**Impact**: R² values > 1 (statistically impossible), e.g., 1.1344
**Solution**: Correct formula:
```python
p_bar = y.mean()  # Treatment group proportion
loglike_null = -2 * (n_treat * np.log(p_bar) + n_control * np.log(1 - p_bar))
loglike_model = -2 * np.sum(y * np.log(pscores) + (1-y) * np.log(1-pscores))
mcfadden_r2 = 1 - loglike_model / loglike_null
```
**Result**: R² now in valid range [0,1], typically 0.06-0.11 (8-11% explanatory power)

### Issue 3: Event Study Visualization Encoding
**Problem**: Unicode characters (², ³, ✓) cause UnicodeEncodeError in Windows console
**Solution**: Replace with ASCII equivalents (R2, squared, v) or use English in print statements
**Pattern**: Always avoid special Unicode in console output, use [OK], [WARNING], [INFO] instead of emojis

### Issue 4: Column Position-Based Extraction
**Problem**: Chinese column names cause encoding errors in Windows GBK console
**Solution**: Always use iloc with column indices, not column names:
```python
# BAD: df[['年份', '地区名称', '第二产业占GDP比重']]
# GOOD: industry_df.iloc[:, [0, 1, 2, 10]]  # By position
```

### Issue 5: Shanghai FDI Data Error
**Problem**: Shanghai FDI values were constant at 11,565.46 million USD from 2011-2023
**Root cause**: Data merging error replaced original growing trend with constant value
**Impact**: Severely underestimated Shanghai's FDI growth and foreign investment level
**Solution**: Restored original FDI values from source data
**Before/After**:
- Before: 2011-2023 all showed 11,565.46 million USD (incorrect)
- After: 2011: 12,600.55 → 2023: 24,087.00 million USD (correct 3x growth)
**Verification**: All 17 observations now have unique values (0% repetition rate)
**Lesson**: Always verify major cities' data for unexpected constant values or abnormal patterns

## Git Commit History (Recent Key Revisions)

- `002e7d3` - Correct Shanghai FDI data error - restore original growing values (Jan 12)
- `b3298f7` - Add foreign investment level variable to main dataset (Jan 12)
- `feaf816` - Add PSM-DID regression with new control variable combination (Jan 12)
- `d051b4c` - Tighten PSM caliper from 0.05 to 0.02 for improved matching quality (Jan 12)
- `3e0263c` - Clean up 2012-2017 robustness check files and update raw data (Jan 12)
- `62df061` - Remove log form of industrial upgrading variable (Jan 10)
- `cc2abb7` - Record industrial upgrading variable addition work (Jan 10)
- `6d64ab5` - Add industrial upgrading variable to main dataset (Jan 10)
- `42bdf83` - Add secondary industry share model comparison with tertiary share (Jan 8)
- `b3a617e` - Add parallel trends test (Event Study) for PSM-DID analysis (Jan 8)
- `b231cdb` - Add PSM-DID baseline regression analysis with double robust estimation (Jan 8)
- `3458aef` - Revert PSM caliper from 0.02 back to 0.05 (Jan 8)
- `bf18a0b` - Tighten PSM caliper from 0.05 to 0.02 (Jan 8)
- `1e22d99` - Fix McFadden's R² calculation in PSM Logit regression (Jan 8)
- `060a073` - Fix critical PSM caliper logic error and enhance documentation (Jan 8)