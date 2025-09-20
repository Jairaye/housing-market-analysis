import sqlite3

conn = sqlite3.connect('../data/housing_market.db')
cursor = conn.cursor()

# Test 1: Count records
cursor.execute('SELECT COUNT(*) FROM counties')
print('Total counties:', cursor.fetchone()[0])

# Test 2: Sample counties
cursor.execute('SELECT county_name, state FROM counties WHERE state = "TX" LIMIT 3')
print('Sample Texas counties:', cursor.fetchall())

# Test 3: Business query - affordable markets
cursor.execute('''
SELECT c.county_name, c.state, h.bottom_tier_min_salary 
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE h.year = 2022 AND h.bottom_tier_min_salary < 60000
LIMIT 5
''')
print('Affordable markets:', cursor.fetchall())

conn.close()
print('✅ Database working perfectly!')

# Add this to test_db.py or run separately
cursor.execute('''
SELECT c.county_name, c.state, h.bottom_tier_min_salary 
FROM counties c
JOIN housing_affordability h ON c.fips_code = h.fips_code
WHERE h.year = 2022 AND h.bottom_tier_min_salary < 80000
ORDER BY h.bottom_tier_min_salary
LIMIT 5
''')
print('More realistic affordable markets:', cursor.fetchall())