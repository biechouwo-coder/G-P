# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Undergraduate thesis studying the impact of China's low-carbon city pilot policies on carbon emission intensity using multi-period Difference-in-Differences (DID) models with panel data from 216 prefecture-level cities spanning 2007-2023.

**Research Focus:** Evaluating whether low-carbon pilot policies (three batches: 2010, 2012, 2017) effectively reduced carbon emission intensity (CEI).

**Core Innovation:** Incorporating high-precision population density data (298 cities × 27 years) into DID models to control for urban agglomeration effects, separating institutional policy effects from morphological urbanization effects.

**Repository:** https://github.com/biechouwo-coder/G-P.git

## Current Status (January 6, 2025)

### Completed Work
- ✅ Data collection: 6 datasets merged (population density, GDP, carbon emissions, industrial structure, FDI, road area)
- ✅ Data cleaning: Removed outliers, handled missing values, ensured data quality
- ✅ DID variable construction: Three-batch pilot policy (2010, 2012, 2017) implemented
- ✅ FDI processing: Added FDI openness ratio (fdi_rmb/gdp_nominal) with year-specific exchange rates
- ✅ Road area: Added prefecture-level road area variable (ln_road_area)
- ✅ Final dataset: `总数据集_2007-2023_完整版.xlsx` (3,672 obs × 216 cities × 19 variables, 100% complete)
- ✅ Documentation: Complete data cleaning log in `数据清理计划.md`

### Next Steps
- [ ] Baseline DID regression with city and year fixed effects
- [ ] Robustness testing (parallel trends, PSM-DID, placebo tests)
- [ ] Heterogeneity analysis
- [ ] Mechanism testing

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
| `fdi_openness` | Control | FDI/GDP ratio | 比例 | Uses nominal GDP + year-specific exchange rates |
| `road_area` | Control | Road area per capita | 平方米/人 | Prefecture-level data |
| `ln_road_area` | Control | Log road area per capita | - | ln(road_area + 1) |

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

### Processed Data
- `总数据集_2007-2023_完整版.xlsx` - **RECOMMENDED FOR ANALYSIS** (3,672 obs × 19 variables, 100% complete)
- `总数据集_2007-2023_最终版.xlsx` - Previous version (11 variables, before DID/FDI/road_area)
- `描述性统计表_最终版.xlsx` - Descriptive statistics
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

### Documentation
- `数据清理计划.md` - Complete data cleaning log (Chinese, detailed steps)
- `实验思路md` - Research design and methodology (Chinese, 408 lines)
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

### Diagnosing Data Issues
```bash
# Run comprehensive diagnostic
py py代码文件/diagnose_data_issues.py

# Check specific variable
py py代码文件/verify_final_data.py
```

### Updating Documentation
- After any data change: Update `数据清理计划.md` with timestamp
- Commit to Git with descriptive message following convention:
  - `feat:` for new features/variables
  - `fix:` for bug fixes/data quality issues
  - `docs:` for documentation updates
  - `data:` for data updates

## Git Commit History (Key Revisions)

- `aa24ff7` - Delete province-level road area sheet, keep prefecture-level data (Jan 6)
- `99ac6b6` - Fix road area variable to prefecture-level (Jan 6)
- `0a45d06` - Add road area per capita variable (ln_road_area) (Jan 6)
- `e8091f8` - Clean up project files, keep only final complete version (Jan 6)
- `ed78308` - Fix 5 critical errors in FDI data processing (Jan 6)
- `3fa7517` - Add FDI data and calculate FDI openness ratio (Jan 6)
- `8034e8a` - Construct DID policy variables and update dataset (Jan 2)
- `beddacc` - Improve CLAUDE.md documentation and clean up old files (Jan 2)
- `6762728` - Fix GDP deflator anomalies and missing population data (Jan 2)
- `0d75af1` - Rewrite README based on research proposal (Jan 2)
- `108e7f9` - Fix carbon intensity units and add population variables (Jan 2)

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

## Notes for Future Development

1. **Regression Analysis** is the next critical task
   - Use final dataset: `总数据集_2007-2023_完整版.xlsx` (19 variables)
   - Baseline model: `CEI_it = α₀ + β₁·DID_it + β₂·ln(pop_den) + Controls + μᵢ + νₜ + ε_it`
   - Verify DID variable works correctly with multi-period policy

2. **Stata/Python Selection**
   - Can use either Stata or Python for regression
   - Stata: `reghdfe` for fixed effects, `estat ptrends` for parallel trends
   - Python: `linearmodels` package (`PanelOLS` with entity and time effects)

3. **Robustness Tests Priority**
   1. Parallel trends (event study) - CRITICAL for DID validity
   2. PSM-DID (address selection bias)
   3. Placebo test (random treatment assignment)
   4. Excluding concurrent policies (Smart City, Innovative City pilots)

4. **Data Documentation**
   - Always update `数据清理计划.md` after changes
   - Include: timestamp, changes made, rationale, data quality metrics
   - Use Chinese for documentation (maintains consistency)

5. **Variable Additions Completed**
   - DID policy variables: `did`, `treat`, `post`, `pilot_year`
   - FDI openness: `fdi_openness` (correctly calculated with nominal GDP, year-specific rates)
   - Infrastructure: `road_area`, `ln_road_area` (prefecture-level, NOT province-level)
