import sqlite3
import pandas as pd
import os

# Set up paths
processed_data_path = '../data/processed/'
database_path = '../data/housing_market.db'

def create_database_connection():
    """
    Create SQLite database connection
    """
    print("Creating SQLite database connection...")
    conn = sqlite3.connect(database_path)
    print(f"✅ Database created: {database_path}")
    return conn

def create_tables_and_import_data(conn):
    """
    Create tables and import all our cleaned CSV data
    """
    print("\n=== CREATING TABLES AND IMPORTING DATA ===\n")
    
    # 1. Counties table (master geographic reference)
    print("1. Creating counties table...")
    counties_df = pd.read_csv(f'{processed_data_path}counties.csv')
    counties_df.to_sql('counties', conn, if_exists='replace', index=False)
    print(f"   ✅ Counties table: {len(counties_df)} records")
    
    # 2. Economic annual data (unemployment + income)
    print("2. Creating economic_annual table...")
    economic_df = pd.read_csv(f'{processed_data_path}economic_annual.csv')
    economic_df.to_sql('economic_annual', conn, if_exists='replace', index=False)
    print(f"   ✅ Economic annual table: {len(economic_df)} records")
    
    # 3. Population data
    print("3. Creating population_annual table...")
    population_df = pd.read_csv(f'{processed_data_path}population_annual.csv')
    population_df.to_sql('population_annual', conn, if_exists='replace', index=False)
    print(f"   ✅ Population annual table: {len(population_df)} records")
    
    # 4. Housing prices monthly (large table)
    print("4. Creating housing_prices_monthly table...")
    print("   (This may take a moment - large dataset)")
    housing_monthly_df = pd.read_csv(f'{processed_data_path}housing_prices_monthly.csv')
    housing_monthly_df.to_sql('housing_prices_monthly', conn, if_exists='replace', index=False)
    print(f"   ✅ Housing prices monthly table: {len(housing_monthly_df)} records")
    
    # 5. Housing affordability (with min salary calculations)
    print("5. Creating housing_affordability table...")
    affordability_df = pd.read_csv(f'{processed_data_path}housing_affordability.csv')
    affordability_df.to_sql('housing_affordability', conn, if_exists='replace', index=False)
    print(f"   ✅ Housing affordability table: {len(affordability_df)} records")
    
    # 6. Price trends annual
    print("6. Creating price_trends_annual table...")
    trends_df = pd.read_csv(f'{processed_data_path}price_trends_annual.csv')
    trends_df.to_sql('price_trends_annual', conn, if_exists='replace', index=False)
    print(f"   ✅ Price trends annual table: {len(trends_df)} records")
    
    return {
        'counties': len(counties_df),
        'economic_annual': len(economic_df),
        'population_annual': len(population_df),
        'housing_prices_monthly': len(housing_monthly_df),
        'housing_affordability': len(affordability_df),
        'price_trends_annual': len(trends_df)
    }

def create_indexes(conn):
    """
    Create indexes for better query performance
    """
    print("\n=== CREATING INDEXES FOR PERFORMANCE ===\n")
    
    cursor = conn.cursor()
    
    # Create indexes on commonly joined/filtered columns
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_counties_fips ON counties(fips_code)",
        "CREATE INDEX IF NOT EXISTS idx_economic_fips ON economic_annual(fips_code)",
        "CREATE INDEX IF NOT EXISTS idx_economic_year ON economic_annual(year)",
        "CREATE INDEX IF NOT EXISTS idx_population_fips ON population_annual(fips_code)",
        "CREATE INDEX IF NOT EXISTS idx_population_year ON population_annual(year)",
        "CREATE INDEX IF NOT EXISTS idx_housing_monthly_region ON housing_prices_monthly(RegionID)",
        "CREATE INDEX IF NOT EXISTS idx_housing_monthly_date ON housing_prices_monthly(date)",
        "CREATE INDEX IF NOT EXISTS idx_affordability_fips ON housing_affordability(fips_code)",
        "CREATE INDEX IF NOT EXISTS idx_affordability_year ON housing_affordability(year)",
        "CREATE INDEX IF NOT EXISTS idx_trends_fips ON price_trends_annual(fips_code)",
        "CREATE INDEX IF NOT EXISTS idx_trends_year ON price_trends_annual(year)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
        print(f"✅ Index created: {index_sql.split()[-1]}")
    
    conn.commit()

def test_database(conn):
    """
    Run test queries to verify everything works
    """
    print("\n=== TESTING DATABASE WITH SAMPLE QUERIES ===\n")
    
    cursor = conn.cursor()
    
    # Test 1: Count records in each table
    print("1. Record counts:")
    tables = ['counties', 'economic_annual', 'population_annual', 
              'housing_prices_monthly', 'housing_affordability', 'price_trends_annual']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count:,} records")
    
    # Test 2: Sample JOIN query
    print("\n2. Sample analysis query:")
    query = """
    SELECT 
        c.county_name,
        c.state,
        e.unemployment_rate,
        e.median_household_income_2022,
        h.bottom_tier_min_salary,
        h.top_tier_min_salary
    FROM counties c
    JOIN economic_annual e ON c.fips_code = e.fips_code AND e.year = 2022
    JOIN housing_affordability h ON c.fips_code = h.fips_code AND h.year = 2022
    WHERE c.state = 'CA'
    ORDER BY h.bottom_tier_min_salary DESC
    LIMIT 5
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("   Top 5 CA counties by minimum salary needed (2022):")
    for row in results:
        county, state, unemployment, income, min_salary_bottom, min_salary_top = row
        print(f"   {county}: ${min_salary_bottom:,.0f} needed (income: ${income:,.0f})")
    
    # Test 3: Time series data
    print("\n3. Housing price trends (sample):")
    trend_query = """
    SELECT 
        county_name,
        year,
        bottom_tier_price,
        bottom_tier_growth
    FROM price_trends_annual 
    WHERE county_name LIKE '%Los Angeles%' AND year >= 2020
    ORDER BY year
    """
    
    cursor.execute(trend_query)
    trend_results = cursor.fetchall()
    
    for row in trend_results:
        county, year, price, growth = row
        growth_str = f"{growth:+.1f}%" if growth else "N/A"
        print(f"   {year}: ${price:,.0f} ({growth_str})")

def create_analysis_queries_file():
    """
    Create a SQL file with sample analysis queries for portfolio
    """
    print("\n=== CREATING SAMPLE ANALYSIS QUERIES FILE ===\n")
    
    sql_queries = """-- Housing Market Analysis SQL Queries
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
"""
    
    # Save SQL queries to file
    with open('../scripts/analysis_queries.sql', 'w') as f:
        f.write(sql_queries)
    
    print("✅ Analysis queries saved to: scripts/analysis_queries.sql")

if __name__ == "__main__":
    print("=== SETTING UP SQL DATABASE ===\n")
    
    # Create database connection
    conn = create_database_connection()
    
    # Import all data
    table_counts = create_tables_and_import_data(conn)
    
    # Create indexes for performance
    create_indexes(conn)
    
    # Test database
    test_database(conn)
    
    # Create sample queries file
    create_analysis_queries_file()
    
    # Close connection
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 SQL DATABASE SETUP COMPLETE! 🎉")
    print("="*60)
    print(f"Database location: {database_path}")
    print(f"Total tables: {len(table_counts)}")
    print(f"Total records: {sum(table_counts.values()):,}")
    
    print("\nTables created:")
    for table, count in table_counts.items():
        print(f"  ✅ {table}: {count:,} records")
    
    print("\nNext steps:")
    print("1. Open database in VS Code SQLite extension")
    print("2. Run queries from analysis_queries.sql")
    print("3. Create visualizations")
    print("4. Write up findings for portfolio")
    
    print(f"\n📁 Database file: {os.path.abspath(database_path)}")