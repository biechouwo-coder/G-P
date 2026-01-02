# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an undergraduate thesis project studying the impact of low-carbon city pilot policies on industrial structure upgrading in China. The research uses difference-in-differences (DID) econometric models with panel data from 298 prefecture-level cities spanning 1998-2024.

**Research Focus:** Evaluating whether China's low-carbon city pilot policies (implemented in three batches: 2010, 2012, 2017) effectively promoted industrial structure upgrading and carbon emission reduction.

**Key Innovation:** Incorporating high-precision population density data to control for urban agglomeration effects when assessing policy impacts.

## Research Architecture

### Data Ecosystem

The project integrates four primary datasets:

1. **Industrial Structure Data** (`原始数据/2000-2023地级市产业结构 .xlsx`)
   - 330 prefecture-level cities, 2000-2023
   - Contains GDP, three-sector value-added, industrial structure metrics
   - Core outcome variables: industrial upgrading indices
   - Status: Ready to merge (file is .xlsx format, readable by pandas)

2. **Population Density Data** (`原始数据/298个地级市人口密度1998-2024年无缺失.xlsx`)
   - 298 cities, 1998-2024, no missing values (interpolated)
   - Critical control variable for urban agglomeration effects
   - Measured as persons/km² using administrative land area

3. **GDP Deflator Data** (`原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx`)
   - 296 cities, base year 2000
   - Used for real GDP adjustment to eliminate price effects

4. **Carbon Emission Intensity** (`原始数据/地级市碳排放强度.xlsx`)
   - City-level CO₂ per unit GDP
   - Primary dependent variable for policy evaluation

### Empirical Framework

The research employs a **multi-period Difference-in-Differences (DID)** model:

```
CEI_it = α₀ + β₁·DID_it + β₂·ln(PopDen_it) + Σγₖ·Control_kit + μᵢ + νₜ + ε_it
```

Where:
- `DID_it` = Treat_i × Post_it (policy intervention dummy)
- `PopDen_it` = population density (log-transformed)
- `μᵢ` = city fixed effects (controls time-invariant heterogeneity)
- `νₜ` = year fixed effects (controls common temporal shocks)
- Standard errors clustered at city level

**Key Identification Challenge:** Different policy implementation timing (2010/2012/2017) creates a staggered treatment design requiring time-varying DID estimation.

### Variable Construction Logic

**Outcome Variables:**
- Industrial Structure Advancement = Tertiary Industry / Secondary Industry
- Industrial Structure Level = Tertiary Industry / GDP
- Carbon Emission Intensity = CO₂ emissions / Real GDP

**Core Treatment:**
- Three pilot batches (2010, 2012, 2017) → generates time-varying treatment indicator
- Treatment = 1 if city ever designated as pilot (0 otherwise)
- Post = 1 from year of pilot implementation onward

**Critical Controls:**
- ln(Population Density): Captures agglomeration vs. congestion effects
- Economic development: ln(Per capita GDP)
- Industrial structure: Secondary industry share of GDP
- Technical innovation: Tech expenditure / Fiscal expenditure
- FDI, financial development, infrastructure

## Data Cleaning Workflow

Before any empirical analysis, follow the 10-step protocol in `数据清理计划.md`:

1. **Import & Initial Inspection** - Load Excel files, check variable types, missingness
2. **City Code Unification** - Standardize to 6-digit administrative codes (National Bureau of Statistics)
3. **Sample Matching** - Intersect datasets (expected final sample: 290-300 cities)
4. **Time Range Alignment** - Unified period: 2010-2023 (covers all policy windows)
5. **Variable Standardization** - Real GDP (2000 base), log transformations, consistent units
6. **Construct Core Variables** - Treatment dummies, outcome measures, controls
7. **Outlier Treatment** - Winsorize at 1%/99% percentiles
8. **Missing Value Imputation** - Linear interpolation for random gaps, delete if >5% missing
9. **Data Merging** - Merge on "city_code-year" unique identifier
10. **Descriptive Documentation** - Summary statistics, time trends, cleaning logs

**Critical Data Issues:**
- Sample inconsistency: 330 vs. 296 vs. 298 cities across datasets → requires intersection
- Temporal mismatch: 1998-2024 vs. 2000-2023 → align to common period
- No duplicate observations allowed in panel structure

## Robustness Testing Strategy

The `实验思路md` document outlines comprehensive validation:

1. **Parallel Trend Test** - Event study framework to verify pre-treatment trend alignment
2. **PSM-DID** - Propensity score matching to address selection bias (pilot cities not randomly assigned)
3. **Policy Exclusion** - Control for concurrent policies (Smart City, Innovative City, Sponge City pilots)
4. **Alternative Outcomes** - Test with per capita CO₂, total emissions (not just intensity)
5. **Placebo Test** - Monte Carlo simulation with random treatment assignment (500-1000 iterations)
6. **Instrumental Variables** - Address potential reverse causality using geographic or Bartik instruments

## Theoretical Foundation

The empirical model builds on **STIRPAT framework** (Stochastic Impacts by Regression on Population, Affluence, and Technology):

- Traditional STIRPAT uses population **size** → elides spatial distribution
- This study adds population **density** → captures agglomeration externalities
- Hypothesis: High density → shared infrastructure + transit → lower per capita emissions (positive externality)
- Counter-hypothesis: Excessive density → congestion + overload → higher emissions (negative externality)

**Policy Mechanism:** Low-carbon pilots affect emissions through:
1. Administrative mandates (emission caps, energy standards)
2. Market incentives (carbon trading, green finance)
3. Technology promotion (renewable energy, efficiency upgrades)

**Contribution:** Separating **institutional policy effects** from **morphological urbanization effects** by controlling for density.

## Common Tasks

### Data Preparation
```stata
* Typical Stata workflow (if using Stata)
import excel "原始数据/2000-2023地级市产业结构 - 面板.xls", firstrow clear
merge 1:1 city_code year using "population_density_data"
winsor2 all_vars, replace cuts(1 99)
```

### DID Regression
```stata
* Multi-period DID with city and year FEs
reghdfe ce_inseity did ln_popden controls, absorb(city_id year) vce(cluster city_id)
```

### Event Study (Parallel Trends)
```stata
* Generate lead/lag dummies relative to treatment
forvalues k = -5/5 {
    gen lead_lag_`k' = (year == treatment_year + `k')
}
reghdfe ce_inseity lead_lag_* , absorb(city_id year)
```

## File Organization Conventions

- `原始数据/` - Raw data files (Excel format). Do not modify originals.
- `数据清理计划.md` - 10-step cleaning protocol, variable definitions
- `实验思路md` - Complete research design, model specifications, robustness strategy
- `README.md` - Project overview (note: outdated file structure, refer to actual directory)

## Important Constraints

1. **No Large File Uploads** - Files >100MB blocked by GitHub (CFPS .dta files excluded)
2. **City Code Standard** - Always use 6-digit National Bureau of Statistics codes
3. **Time Period** - Core analysis: 2010-2023 (policy windows); population data available 1998-2024
4. **Sample Selection** - Must document reasons for excluding any cities from final sample
5. **Missing Data** - Never impute >5% of any variable; prefer deletion over heavy imputation

## Theoretical References

Key citations (see `中文参考/` and `英文参考/`):
- Cai Haiya & Xu Yingzhi (2017) - Trade liberalization & industrial upgrading
- Gan Chunhui et al. (2011) - Industrial structure change & economic growth
- Cao Xiang - Low-carbon pilots & green lifestyle formation
- Zhao Zhenzhi - Low-carbon strategy & total factor productivity

## Current Data Processing Status

As of January 2, 2025:

**Completed:**
- ✅ Literature review & theoretical analysis
- ✅ Data collection & compilation
- ✅ Proposal completed
- ✅ Partial data merge (GDP, population density, carbon emissions → 8,065 obs, 7 variables)
- ✅ Time period filtering (2007-2023 subset created → 5,066 obs)

**In Progress:**
- ⏳ Industrial structure data merge (file exists as .xlsx but needs to be integrated)

**Pending:**
- ⏳ Full data merge completion
- ⏳ Construct treatment variable (DID: pilot city × post-policy period)
- ⏳ Empirical model estimation
- ⏳ Robustness testing
- ⏳ Thesis writing

## Data Processing Commands

### Python Environment
```bash
# Activate Python environment
py --version  # Should be 3.8.1

# Install required packages (if needed)
py -m pip install pandas openpyxl

# Run data merge scripts
cd c:\Users\HP\Desktop\毕业论文
py merge_final.py  # Merge 3 datasets (already done)
py filter_2007_2023.py  # Filter to 2007-2023 period
```

### Current Data Files
- `总数据集.xlsx` - Merged dataset (8,065 rows × 7 columns, 1998-2024)
- `总数据集_2007-2023.xlsx` - Time-filtered dataset (5,066 rows × 7 columns)
- `原始数据/2000-2023地级市产业结构 .xlsx` - Industrial structure data (ready to merge)

### Data Merge Process
The merge uses pandas with city_name + year as matching keys:

```python
# Standard approach used in merge_final.py
import pandas as pd

df_pop = pd.read_excel('原始数据/298个地级市人口密度1998-2024年无缺失.xlsx')
df_gdp = pd.read_excel('原始数据/296个地级市GDP相关数据（以2000年为基期）.xlsx')
df_carbon = pd.read_excel('原始数据/地级市碳排放强度.xlsx')

# Extract columns by position (not name) to avoid encoding issues
df_pop = df_pop.iloc[:, [0, 2, 4, 8]]  # year, city_name, city_code, pop_density
df_pop.columns = ['year', 'city_name', 'city_code', 'pop_density']

df_gdp = df_gdp.iloc[:, [1, 2, 5, 6]]  # city_name, year, gdp_real, gdp_deflator
df_gdp.columns = ['city_name', 'year', 'gdp_real', 'gdp_deflator']

df_carbon = df_carbon.iloc[:, [0, 1, 3, 8]]  # year, city_code, city_name, carbon_intensity
df_carbon.columns = ['year', 'city_code', 'city_name', 'carbon_intensity']

# Outer merge on city_name + year
df_merged = pd.merge(df_pop, df_gdp, on=['city_name', 'year'], how='outer')
df_merged = pd.merge(df_merged, df_carbon, on=['city_name', 'year'], how='outer')

# Save
df_merged.to_excel('总数据集.xlsx', index=False, engine='openpyxl')
```

**Critical Notes:**
- Column positions (indices) are used instead of names due to Chinese character encoding issues
- City name matching is used instead of city_code due to inconsistent city_code availability
- Industrial structure data file exists but needs to be merged into the main dataset

## Research Status

- ✅ Literature review & theoretical analysis
- ✅ Data collection & compilation
- ✅ Proposal completed
- ⏳ Full data merge (3 of 4 sources merged, industrial structure pending)
- ⏳ Empirical model construction
- ⏳ Data analysis & results
- ⏳ Thesis writing
- ⏳ Defense preparation
