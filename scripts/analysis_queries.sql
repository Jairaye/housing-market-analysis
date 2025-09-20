-- Housing Market Analysis SQL Queries
-- Portfolio project demonstrating SQL skills with housing, economic, and population data

-- 1. BASIC QUERIES --

-- Counties with highest housing costs relative to income (2022)
SELECT 
    c.county_name,
    c.state,
    e.median_household_income_2022,
    h.bottom_tier_min_salary,
    ROUND((h.bottom_tier_min_salary / e.median_household_income_2022 - 1) * 100, 1) as income_gap_percent
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code AND e.year = 2022
JOIN housing_affordability h ON c.fips_code = h.fips_code AND h.year = 2022
WHERE e.median_household_income_2022 IS NOT NULL 
  AND h.bottom_tier_min_salary IS NOT NULL
ORDER BY income_gap_percent DESC
LIMIT 10;

-- 2. TIME SERIES ANALYSIS --

-- Housing price growth by year (national averages)
SELECT 
    year,
    ROUND(AVG(bottom_tier_price), 0) as avg_bottom_tier_price,
    ROUND(AVG(top_tier_price), 0) as avg_top_tier_price,
    ROUND(AVG(bottom_tier_growth), 2) as avg_bottom_growth_rate,
    ROUND(AVG(top_tier_growth), 2) as avg_top_growth_rate
FROM price_trends_annual 
WHERE year >= 2010
GROUP BY year
ORDER BY year;

-- 3. GEOGRAPHIC ANALYSIS --

-- State-level housing affordability comparison (2022)
SELECT 
    c.state,
    COUNT(*) as county_count,
    ROUND(AVG(e.median_household_income_2022), 0) as avg_income,
    ROUND(AVG(h.bottom_tier_min_salary), 0) as avg_min_salary_needed,
    ROUND(AVG(e.unemployment_rate), 1) as avg_unemployment_rate
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code AND e.year = 2022
JOIN housing_affordability h ON c.fips_code = h.fips_code AND h.year = 2022
GROUP BY c.state
HAVING COUNT(*) >= 5  -- States with at least 5 counties
ORDER BY avg_min_salary_needed DESC
LIMIT 15;

-- 4. ADVANCED QUERIES --

-- Counties where housing became less affordable during COVID (2019 vs 2022)
WITH affordability_change AS (
  SELECT 
    c.county_name,
    c.state,
    h2019.bottom_tier_min_salary as min_salary_2019,
    h2022.bottom_tier_min_salary as min_salary_2022,
    e.median_household_income_2022,
    ((h2022.bottom_tier_min_salary - h2019.bottom_tier_min_salary) / h2019.bottom_tier_min_salary * 100) as salary_increase_needed
  FROM counties c
  JOIN housing_affordability h2019 ON c.fips_code = h2019.fips_code AND h2019.year = 2019
  JOIN housing_affordability h2022 ON c.fips_code = h2022.fips_code AND h2022.year = 2022  
  JOIN economic_annual e ON c.fips_code = e.fips_code AND e.year = 2022
  WHERE h2019.bottom_tier_min_salary IS NOT NULL 
    AND h2022.bottom_tier_min_salary IS NOT NULL
)
SELECT 
  county_name,
  state,
  ROUND(min_salary_2019, 0) as min_salary_2019,
  ROUND(min_salary_2022, 0) as min_salary_2022,
  ROUND(median_household_income_2022, 0) as actual_income,
  ROUND(salary_increase_needed, 1) as salary_increase_needed_percent
FROM affordability_change
WHERE salary_increase_needed > 20  -- 20%+ increase needed
ORDER BY salary_increase_needed DESC
LIMIT 20;

-- 5. CORRELATION ANALYSIS --

-- Relationship between unemployment and housing costs
SELECT 
    CASE 
        WHEN e.unemployment_rate < 3 THEN 'Low (< 3%)'
        WHEN e.unemployment_rate < 5 THEN 'Medium (3-5%)'
        ELSE 'High (> 5%)'
    END as unemployment_category,
    COUNT(*) as county_count,
    ROUND(AVG(h.bottom_tier_min_salary), 0) as avg_min_salary,
    ROUND(AVG(e.median_household_income_2022), 0) as avg_income
FROM economic_annual e
JOIN housing_affordability h ON e.fips_code = h.fips_code AND e.year = h.year
WHERE e.year = 2022 AND e.unemployment_rate IS NOT NULL
GROUP BY unemployment_category
ORDER BY avg_min_salary;

-- 6. POPULATION GROWTH VS HOUSING PRICES --

-- Counties with highest population growth and housing price changes
SELECT 
    c.county_name,
    c.state,
    p2020.population as pop_2020,
    p2024.population as pop_2024,
    ROUND(((p2024.population - p2020.population) / p2020.population * 100), 1) as pop_growth_percent,
    ROUND(t2020.bottom_tier_price, 0) as price_2020,
    ROUND(t2024.bottom_tier_price, 0) as price_2024,
    ROUND(((t2024.bottom_tier_price - t2020.bottom_tier_price) / t2020.bottom_tier_price * 100), 1) as price_growth_percent
FROM counties c
JOIN population_annual p2020 ON c.fips_code = p2020.fips_code AND p2020.year = 2020
JOIN population_annual p2024 ON c.fips_code = p2024.fips_code AND p2024.year = 2024
JOIN price_trends_annual t2020 ON c.fips_code = t2020.fips_code AND t2020.year = 2020
JOIN price_trends_annual t2024 ON c.fips_code = t2024.fips_code AND t2024.year = 2024
WHERE p2020.population > 50000  -- Larger counties only
ORDER BY pop_growth_percent DESC
LIMIT 15;
