import pandas as pd
import numpy as np
import os
from datetime import datetime

# Set up paths
raw_data_path = '../data/raw/'
processed_data_path = '../data/processed/'

def clean_population_data():
    """
    Clean the population data - extract county-level annual population
    """
    print("Cleaning population data...")
    
    # Read population file, skipping the header rows we saw earlier
    df = pd.read_excel(f'{raw_data_path}2024_pop_county.xlsx', 
                       sheet_name='CO-EST2024-POP',
                       skiprows=3)
    
    print(f"Original population data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # The first column should be geographic area, let's examine the structure
    # From our earlier analysis, it looks like:
    # - Column 0: Geographic Area (county names)
    # - Columns 2-6: Population estimates for 2020-2024
    
    # Clean up column names
    df.columns = [str(col).strip() for col in df.columns]
    
    # Filter to county-level data only (exclude state/national totals)
    # County rows typically contain "County" in the name
    county_mask = df.iloc[:, 0].astype(str).str.contains('County', na=False)
    county_df = df[county_mask].copy()
    
    print(f"Counties identified: {len(county_df)}")
    
    # Extract county names and create FIPS mapping
    # We'll need to match these to our existing counties table
    county_df['clean_county_name'] = county_df.iloc[:, 0].astype(str)
    
    # Reshape population data from wide to long
    population_data = []
    
    # Get the year columns (should be 2020, 2021, 2022, 2023, 2024)
    year_columns = [col for col in county_df.columns if str(col).isdigit()]
    print(f"Year columns found: {year_columns}")
    
    for _, row in county_df.iterrows():
        county_name = row['clean_county_name']
        
        for year_col in year_columns:
            if pd.notna(row[year_col]) and str(year_col).isdigit():
                population_data.append({
                    'county_name': county_name,
                    'year': int(year_col),
                    'population': row[year_col]
                })
    
    population_df = pd.DataFrame(population_data)
    
    # Save population data (we'll merge with FIPS codes later)
    population_df.to_csv(f'{processed_data_path}population_annual.csv', index=False)
    print(f"Population annual table saved: {population_df.shape}")
    
    return population_df

def reshape_housing_data():
    """
    Reshape housing price data from wide (300+ date columns) to long format
    """
    print("\nReshaping housing price data...")
    
    # Read both housing price files
    bottom_df = pd.read_csv(f'{raw_data_path}bottom_tier_prices_county.csv')
    top_df = pd.read_csv(f'{raw_data_path}top_tier_prices_county.csv')
    
    print(f"Bottom tier shape: {bottom_df.shape}")
    print(f"Top tier shape: {top_df.shape}")
    
    # Get date columns (all columns that look like dates: YYYY-MM-DD)
    bottom_date_cols = [col for col in bottom_df.columns if '-' in str(col) and len(str(col)) == 10]
    top_date_cols = [col for col in top_df.columns if '-' in str(col) and len(str(col)) == 10]
    
    print(f"Date columns found: {len(bottom_date_cols)} bottom, {len(top_date_cols)} top")
    print(f"Date range: {bottom_date_cols[0]} to {bottom_date_cols[-1]}")
    
    # Reshape bottom tier prices
    bottom_melted = bottom_df.melt(
        id_vars=['RegionID', 'RegionName', 'StateName', 'State'],
        value_vars=bottom_date_cols,
        var_name='date',
        value_name='bottom_tier_price'
    )
    
    # Reshape top tier prices
    top_melted = top_df.melt(
        id_vars=['RegionID', 'RegionName', 'StateName', 'State'],
        value_vars=top_date_cols,
        var_name='date',
        value_name='top_tier_price'
    )
    
    # Merge bottom and top tier data
    housing_prices = bottom_melted.merge(
        top_melted[['RegionID', 'date', 'top_tier_price']], 
        on=['RegionID', 'date'], 
        how='outer'
    )
    
    # Convert date column to datetime
    housing_prices['date'] = pd.to_datetime(housing_prices['date'])
    housing_prices['year'] = housing_prices['date'].dt.year
    housing_prices['month'] = housing_prices['date'].dt.month
    
    # Clean up region names and create FIPS mapping
    # RegionName should be county names that match our counties table
    housing_prices['county_name'] = housing_prices['RegionName']
    
    # Remove rows with no price data
    housing_prices = housing_prices.dropna(subset=['bottom_tier_price', 'top_tier_price'], how='all')
    
    print(f"Housing prices reshaped: {housing_prices.shape}")
    
    # Save monthly housing prices
    housing_prices.to_csv(f'{processed_data_path}housing_prices_monthly.csv', index=False)
    print("Housing prices monthly table saved")
    
    return housing_prices

def calculate_affordability_metrics(housing_df):
    """
    Calculate minimum salary needed and affordability metrics
    """
    print("\nCalculating affordability metrics...")
    
    # Load our economic data to get median incomes
    economic_df = pd.read_csv(f'{processed_data_path}economic_annual.csv')
    
    # Create annual averages for housing prices
    annual_housing = housing_df.groupby(['RegionID', 'county_name', 'year']).agg({
        'bottom_tier_price': 'mean',
        'top_tier_price': 'mean'
    }).reset_index()
    
    # Calculate minimum salary needed (using 30% rule: housing shouldn't exceed 30% of income)
    # Assuming 5% annual housing cost (mortgage + taxes + insurance as % of home value)
    annual_housing['bottom_tier_annual_cost'] = annual_housing['bottom_tier_price'] * 0.05
    annual_housing['top_tier_annual_cost'] = annual_housing['top_tier_price'] * 0.05
    
    annual_housing['bottom_tier_min_salary'] = annual_housing['bottom_tier_annual_cost'] / 0.30
    annual_housing['top_tier_min_salary'] = annual_housing['top_tier_annual_cost'] / 0.30
    
    # Merge with actual median incomes (for 2022 where we have data)
    income_2022 = economic_df[economic_df['year'] == 2022][['fips_code', 'median_household_income_2022']].copy()
    
    # We'll need to create a mapping between county names and FIPS codes
    counties_df = pd.read_csv(f'{processed_data_path}counties.csv')
    
    # For now, save the affordability data and we'll join later
    annual_housing.to_csv(f'{processed_data_path}housing_affordability.csv', index=False)
    print(f"Housing affordability table saved: {annual_housing.shape}")
    
    return annual_housing

def create_annual_price_trends(housing_df):
    """
    Create annual price trends and growth rates
    """
    print("\nCreating price trends...")
    
    # Calculate annual averages and year-over-year growth
    annual_trends = housing_df.groupby(['RegionID', 'county_name', 'year']).agg({
        'bottom_tier_price': 'mean',
        'top_tier_price': 'mean'
    }).reset_index()
    
    # Calculate year-over-year growth rates
    annual_trends = annual_trends.sort_values(['RegionID', 'year'])
    annual_trends['bottom_tier_growth'] = annual_trends.groupby('RegionID')['bottom_tier_price'].pct_change() * 100
    annual_trends['top_tier_growth'] = annual_trends.groupby('RegionID')['top_tier_price'].pct_change() * 100
    
    # Save price trends
    annual_trends.to_csv(f'{processed_data_path}price_trends_annual.csv', index=False)
    print(f"Price trends table saved: {annual_trends.shape}")
    
    return annual_trends

if __name__ == "__main__":
    print("=== CLEANING HOUSING AND POPULATION DATA ===\n")
    
    # Clean population data
    population_df = clean_population_data()
    
    # Reshape housing price data
    housing_df = reshape_housing_data()
    
    # Calculate affordability metrics
    affordability_df = calculate_affordability_metrics(housing_df)
    
    # Create price trends
    trends_df = create_annual_price_trends(housing_df)
    
    print("\n=== CLEANING COMPLETE ===")
    print("Files created:")
    print("- population_annual.csv")
    print("- housing_prices_monthly.csv") 
    print("- housing_affordability.csv")
    print("- price_trends_annual.csv")
    
    print(f"\nData summary:")
    print(f"- Population data: {len(population_df)} records")
    print(f"- Monthly housing prices: {len(housing_df)} records") 
    print(f"- Annual affordability: {len(affordability_df)} records")
    print(f"- Annual trends: {len(trends_df)} records")
    
    print("\nNext steps:")
    print("- Create FIPS code mappings between datasets")
    print("- Set up SQL database and import tables")
    print("- Write analysis queries")