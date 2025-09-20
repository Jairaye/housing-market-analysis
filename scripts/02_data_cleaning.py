import pandas as pd
import numpy as np
import os

# Set up paths
raw_data_path = '../data/raw/'
processed_data_path = '../data/processed/'

# Create processed directory if it doesn't exist
os.makedirs(processed_data_path, exist_ok=True)

def clean_unemployment_data():
    """
    Clean the unemployment and income data
    Skip header rows, standardize FIPS codes, reshape data
    """
    print("Cleaning unemployment data...")
    
    # Read the unemployment file, skipping the header rows
    df = pd.read_excel(f'{raw_data_path}Unemployment2023.xlsx', 
                       sheet_name='Unemployment Med HH Income',
                       skiprows=4)  # Skip the caption rows
    
    # Display basic info
    print(f"Original shape: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
    
    # Clean up - remove any completely empty rows
    df = df.dropna(subset=['FIPS_Code'])
    
    # Convert FIPS to string and pad with zeros (some may be missing leading zeros)
    df['FIPS_Code'] = df['FIPS_Code'].astype(str).str.zfill(5)
    
    # Keep only county-level data (exclude state and national totals)
    # County FIPS codes are 5 digits, state codes end in 000
    df = df[~df['FIPS_Code'].str.endswith('000')]
    
    print(f"After filtering to counties only: {df.shape}")
    
    # Extract key columns for our base tables
    county_cols = ['FIPS_Code', 'State', 'Area_Name', 'Rural_Urban_Continuum_Code_2023', 
                   'Urban_Influence_Code_2013', 'Metro_2023']
    
    # Create counties table
    counties_df = df[county_cols].copy()
    counties_df.columns = ['fips_code', 'state', 'county_name', 'rural_urban_code', 
                          'urban_influence_code', 'metro_status']
    
    # Save counties table
    counties_df.to_csv(f'{processed_data_path}counties.csv', index=False)
    print(f"Counties table saved: {counties_df.shape}")
    
    # Create economic data table (reshape unemployment and income data)
    economic_data = []
    
    # Extract unemployment data for each year (2000-2023)
    for year in range(2000, 2024):
        year_data = df[['FIPS_Code', f'Unemployment_rate_{year}']].copy()
        year_data['year'] = year
        year_data.columns = ['fips_code', 'unemployment_rate', 'year']
        year_data = year_data.dropna(subset=['unemployment_rate'])
        economic_data.append(year_data)
    
    # Combine all years
    economic_df = pd.concat(economic_data, ignore_index=True)
    
    # Add median household income (2022 data available)
    income_data = df[['FIPS_Code', 'Median_Household_Income_2022']].copy()
    income_data.columns = ['fips_code', 'median_household_income_2022']
    income_data = income_data.dropna(subset=['median_household_income_2022'])
    
    # Merge income data with 2022 economic data
    economic_df = economic_df.merge(income_data, on='fips_code', how='left')
    
    # Save economic data
    economic_df.to_csv(f'{processed_data_path}economic_annual.csv', index=False)
    print(f"Economic annual table saved: {economic_df.shape}")
    
    return counties_df, economic_df

def clean_population_data():
    """
    Clean the population data
    """
    print("\nCleaning population data...")
    
    # Read population file
    df = pd.read_excel(f'{raw_data_path}2024_pop_county.xlsx', 
                       sheet_name='CO-EST2024-POP',
                       skiprows=3)  # Skip header rows
    
    print(f"Population data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # This will need adjustment based on actual structure
    # We'll examine the data first and then clean
    
    return df

def preview_housing_data():
    """
    Preview the housing data structure (already clean CSVs)
    """
    print("\nPreviewing housing data...")
    
    # Read a sample of the housing data
    bottom_df = pd.read_csv(f'{raw_data_path}bottom_tier_prices_county.csv', nrows=5)
    top_df = pd.read_csv(f'{raw_data_path}top_tier_prices_county.csv', nrows=5)
    
    print(f"Bottom tier shape: {bottom_df.shape}")
    print(f"Top tier shape: {top_df.shape}")
    print(f"Sample columns: {list(bottom_df.columns)[:10]}")
    
    return bottom_df, top_df

if __name__ == "__main__":
    print("=== STARTING DATA CLEANING ===\n")
    
    # Clean unemployment data first
    counties_df, economic_df = clean_unemployment_data()
    
    # Preview population data
    pop_df = clean_population_data()
    
    # Preview housing data
    bottom_sample, top_sample = preview_housing_data()
    
    print("\n=== CLEANING COMPLETE ===")
    print("Files created:")
    print("- counties.csv")
    print("- economic_annual.csv")
    print("\nNext steps:")
    print("- Clean population data") 
    print("- Reshape housing price data")
    print("- Calculate affordability metrics")