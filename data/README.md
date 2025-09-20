# Housing Market Analysis Project

**A comprehensive SQL-based analysis of U.S. housing affordability using county-level data from 2000-2025**

## 🎯 Project Overview

This project analyzes the relationship between housing costs, income levels, and economic indicators across U.S. counties to identify investment opportunities and affordability trends. Using data from Zillow, U.S. Census, and Bureau of Labor Statistics, I built a normalized database to answer key business questions about the housing market.

## 🔍 Key Business Questions Answered

- **Where are the best markets for real estate investment?** (Growing population + affordable housing)
- **Which counties face the most severe affordability crisis?** (Income gap analysis)
- **How do metro vs. rural markets compare for investment opportunities?**
- **Which markets experienced the fastest price appreciation?** (2020-2025 trends)
- **What salary is needed to afford housing in different markets?** (30% rule calculations)

## 📊 Key Findings

- **Housing affordability crisis confirmed**: Many counties require salaries significantly higher than median income
- **Geographic patterns**: Coastal areas generally less affordable than inland regions  
- **Economic correlation**: Metro areas show different affordability patterns than rural counties
- **Minimum salary calculator**: Automated calculation showing income needed for housing affordability

## 🛠️ Technical Skills Demonstrated

### Data Engineering
- **Python data cleaning** with pandas and NumPy
- **Data normalization** from wide to long format
- **FIPS code standardization** and geographic data handling
- **Multi-source data integration** (housing prices + demographics + economic data)

### Database Design
- **SQLite database creation** with 6 normalized tables
- **Proper foreign key relationships** using FIPS codes
- **Index optimization** for query performance
- **Data integrity** validation and testing

### SQL Analysis
- **Complex multi-table JOINs** 
- **Aggregate functions** and GROUP BY operations
- **Business logic implementation** (affordability calculations)
- **Time series analysis** queries
- **Geographic comparisons** and market segmentation

### Tools & Technologies
- **Python**: pandas, NumPy, sqlite3
- **SQL**: SQLite database design and querying
- **Git/GitHub**: Version control and project documentation
- **VS Code**: Development environment and SQLite extension

## 📁 Project Structure

```
housing-market-analysis/
├── data/
│   ├── raw/                    # Original datasets
│   ├── processed/              # Cleaned CSV files
│   └── housing_market.db       # Final SQLite database
├── scripts/
│   ├── 02_data_cleaning.py     # Clean unemployment/demographic data
│   ├── 03_housing_and_population_cleaning.py  # Process housing prices
│   ├── 04_fix_fips_codes.py    # Standardize geographic codes
│   ├── 05_create_sql_database.py  # Build final database
│   └── analysis_queries_basic.sql  # Business analysis queries
└── README.md
```

## 🗃️ Database Schema

**6 Normalized Tables:**

1. **Counties** (3,233 records) - Master geographic reference
2. **Economic_Annual** (77,148 records) - Unemployment rates and median income by county/year
3. **Population_Annual** (14,995 records) - County population estimates 2020-2024
4. **Housing_Prices_Monthly** (900k+ records) - Monthly price data 2000-2025
5. **Housing_Affordability** (57,237 records) - Calculated minimum salary requirements
6. **Price_Trends_Annual** (57,237 records) - Annual averages and growth rates

## 📈 Sample Business Analysis

### Most Unaffordable Markets (2022)
Counties where median income cannot afford bottom-tier housing:

```sql
SELECT 
    c.county_name,
    c.state,
    e.median_household_income_2022 as actual_income,
    h.bottom_tier_min_salary as income_needed,
    (h.bottom_tier_min_salary - e.median_household_income_2022) as income_gap
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE e.year = 2022 AND h.year = 2022
ORDER BY income_gap DESC;
```

### Investment Opportunities
Affordable markets with stable economies and growing populations:

```sql
SELECT 
    c.county_name, c.state, p.population,
    h.bottom_tier_min_salary, e.unemployment_rate
FROM counties c
JOIN population_annual p ON c.fips_code = p.fips_code
JOIN housing_affordability h ON c.fips_code = h.fips_code  
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE p.year = 2024 AND h.year = 2022 AND e.year = 2022
  AND h.bottom_tier_min_salary < 75000
  AND e.unemployment_rate < 5
ORDER BY p.population DESC;
```

## 🚀 How to Run This Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jairaye/housing-market-analysis
   cd housing-market-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install pandas numpy openpyxl
   ```

3. **Run data pipeline** (if recreating from raw data)
   ```bash
   cd scripts
   python 02_data_cleaning.py
   python 03_housing_and_population_cleaning.py
   python 04_fix_fips_codes.py
   python 05_create_sql_database.py
   ```

4. **Analyze data**
   - Open `data/housing_market.db` in SQLite browser
   - Run queries from `scripts/analysis_queries_basic.sql`

## 💼 Business Impact

This analysis framework could support:
- **Real estate investment decisions** - Identify undervalued markets
- **Policy development** - Target housing affordability programs
- **Economic research** - Understand regional market dynamics
- **Financial planning** - Salary requirements for geographic moves

## 📝 Data Sources

- **Housing Prices**: Zillow Home Value Index (county-level, 2000-2025)
- **Population**: U.S. Census Bureau County Population Estimates (2020-2024)  
- **Economic Data**: Bureau of Labor Statistics, Local Area Unemployment Statistics
- **Demographics**: Census Bureau Small Area Income and Poverty Estimates

## 🔗 Connect With Me

- **LinkedIn**: https://www.linkedin.com/in/jradams11/
- - **Email**: ada.jos@outlook.com

---

*This project demonstrates end-to-end data analysis capabilities from raw data collection through database design to business intelligence insights.*