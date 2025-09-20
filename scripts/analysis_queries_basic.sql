-- Housing Market Analysis - Entry Level SQL Queries
-- Demonstrating basic SQL skills for portfolio

-- 1. BASIC SELECT QUERIES --

-- View all counties in California
SELECT county_name, state, rural_urban_code, metro_status
FROM counties 
WHERE state = 'CA'
ORDER BY county_name;

-- Counties with highest median income in 2022
SELECT 
    c.county_name,
    c.state,
    e.median_household_income_2022
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE e.year = 2022 
  AND e.median_household_income_2022 IS NOT NULL
ORDER BY e.median_household_income_2022 DESC
LIMIT 10;

-- 2. BASIC FILTERING AND WHERE CLAUSES --

-- Rural counties with low unemployment (2022)
SELECT 
    c.county_name,
    c.state,
    e.unemployment_rate,
    c.rural_urban_code
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE e.year = 2022 
  AND c.rural_urban_code >= 4  -- Rural codes are 4+
  AND e.unemployment_rate < 3.0
ORDER BY e.unemployment_rate;

-- Counties where minimum salary needed is over $100k
SELECT 
    c.county_name,
    c.state,
    h.bottom_tier_min_salary,
    h.year
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE h.bottom_tier_min_salary > 100000
  AND h.year = 2022
ORDER BY h.bottom_tier_min_salary DESC;

-- 3. BASIC AGGREGATION (COUNT, AVG, SUM) --

-- Count counties by state
SELECT 
    state,
    COUNT(*) as county_count
FROM counties
GROUP BY state
ORDER BY county_count DESC
LIMIT 10;

-- Average housing prices by year (2020-2024)
SELECT 
    year,
    COUNT(*) as county_count,
    AVG(bottom_tier_price) as avg_bottom_price,
    AVG(top_tier_price) as avg_top_price
FROM price_trends_annual
WHERE year >= 2020
GROUP BY year
ORDER BY year;

-- Average unemployment rate by state (2022)
SELECT 
    c.state,
    COUNT(*) as counties_with_data,
    AVG(e.unemployment_rate) as avg_unemployment_rate
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE e.year = 2022 
  AND e.unemployment_rate IS NOT NULL
GROUP BY c.state
ORDER BY avg_unemployment_rate;

-- 4. BASIC JOINS --

-- Counties with their population and income data
SELECT 
    c.county_name,
    c.state,
    p.population,
    e.median_household_income_2022
FROM counties c
JOIN population_annual p ON c.fips_code = p.fips_code
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE p.year = 2024 
  AND e.year = 2022
ORDER BY p.population DESC
LIMIT 15;

-- Housing affordability with county info
SELECT 
    c.county_name,
    c.state,
    h.bottom_tier_min_salary,
    h.top_tier_min_salary,
    h.year
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE h.year = 2022
  AND c.state IN ('TX', 'FL', 'CA')
ORDER BY h.bottom_tier_min_salary;

-- 5. SORTING AND LIMITING --

-- Most expensive counties for housing (top 15)
SELECT 
    c.county_name,
    c.state,
    h.bottom_tier_min_salary,
    h.top_tier_min_salary
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE h.year = 2022
ORDER BY h.top_tier_min_salary DESC
LIMIT 15;

-- Counties with biggest population (2024)
SELECT 
    c.county_name,
    c.state,
    p.population
FROM counties c
JOIN population_annual p ON c.fips_code = p.fips_code
WHERE p.year = 2024
ORDER BY p.population DESC
LIMIT 20;

-- 6. BASIC CALCULATIONS --

-- How much more income is needed vs actual income
SELECT 
    c.county_name,
    c.state,
    e.median_household_income_2022 as actual_income,
    h.bottom_tier_min_salary as needed_income,
    (h.bottom_tier_min_salary - e.median_household_income_2022) as income_shortfall
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE e.year = 2022 
  AND h.year = 2022
  AND e.median_household_income_2022 IS NOT NULL
ORDER BY income_shortfall DESC
LIMIT 10;

-- 7. USING CASE STATEMENTS (BASIC) --

-- Categorize counties by metro status
SELECT 
    county_name,
    state,
    metro_status,
    CASE 
        WHEN metro_status = 1 THEN 'Metro'
        WHEN metro_status = 0 THEN 'Non-Metro'
        ELSE 'Unknown'
    END as metro_category
FROM counties
WHERE state = 'OH'
ORDER BY metro_category, county_name;

-- Categorize unemployment levels
SELECT 
    c.county_name,
    c.state,
    e.unemployment_rate,
    CASE 
        WHEN e.unemployment_rate < 3 THEN 'Low'
        WHEN e.unemployment_rate < 5 THEN 'Medium' 
        ELSE 'High'
    END as unemployment_level
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE e.year = 2022 
  AND c.state = 'CA'
ORDER BY e.unemployment_rate;

-- 8. BASIC STRING OPERATIONS --

-- Counties with "County" in the name vs others
SELECT 
    county_name,
    state,
    CASE 
        WHEN county_name LIKE '%County%' THEN 'Has County'
        ELSE 'No County'
    END as name_type
FROM counties
WHERE state = 'LA'
ORDER BY county_name;

-- Find counties starting with specific letters
SELECT county_name, state
FROM counties
WHERE county_name LIKE 'San%'
  AND state = 'CA'
ORDER BY county_name;

-- 9. WORKING WITH DATES AND NUMBERS --

-- Recent housing price data (2024)
SELECT 
    c.county_name,
    c.state,
    h.date,
    h.bottom_tier_price,
    h.top_tier_price
FROM counties c
JOIN housing_prices_monthly h ON c.county_name = h.county_name
WHERE h.year = 2024
  AND c.state = 'FL'
  AND h.bottom_tier_price IS NOT NULL
ORDER BY h.date DESC, h.bottom_tier_price DESC
LIMIT 20;

-- 10. PRACTICE QUERIES FOR INTERVIEWS --

-- "Show me the top 5 most affordable counties in Texas"
SELECT 
    c.county_name,
    h.bottom_tier_min_salary
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE c.state = 'TX' 
  AND h.year = 2022
  AND h.bottom_tier_min_salary IS NOT NULL
ORDER BY h.bottom_tier_min_salary
LIMIT 5;

-- "What's the average unemployment rate in metro vs non-metro areas?"
SELECT 
    CASE 
        WHEN c.metro_status = 1 THEN 'Metro'
        ELSE 'Non-Metro'
    END as area_type,
    COUNT(*) as county_count,
    AVG(e.unemployment_rate) as avg_unemployment
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
WHERE e.year = 2022
GROUP BY c.metro_status;

-- "Find counties where housing is most unaffordable"
SELECT 
    c.county_name,
    c.state,
    e.median_household_income_2022,
    h.bottom_tier_min_salary,
    (h.bottom_tier_min_salary / e.median_household_income_2022) as affordability_ratio
FROM counties c
JOIN economic_annual e ON c.fips_code = e.fips_code
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE e.year = 2022 
  AND h.year = 2022
  AND e.median_household_income_2022 > 0
ORDER BY affordability_ratio DESC
LIMIT 10;