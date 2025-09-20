import pandas as pd
import numpy as np

# Set up paths
processed_data_path = '../data/processed/'

def check_and_fix_fips_codes():
    """
    Check all our cleaned files for FIPS code formatting issues
    Ensure all FIPS codes are 5-digit strings with leading zeros
    """
    print("=== CHECKING AND FIXING FIPS CODES ===\n")
    
    # 1. Check counties.csv
    print("1. Checking counties.csv...")
    counties_df = pd.read_csv(f'{processed_data_path}counties.csv')
    print(f"Current FIPS codes sample: {counties_df['fips_code'].head().tolist()}")
    print(f"FIPS code data type: {counties_df['fips_code'].dtype}")
    
    # Fix FIPS codes - convert to string and pad with zeros
    counties_df['fips_code'] = counties_df['fips_code'].astype(str).str.zfill(5)
    print(f"Fixed FIPS codes sample: {counties_df['fips_code'].head().tolist()}")
    
    # Save fixed version
    counties_df.to_csv(f'{processed_data_path}counties.csv', index=False)
    print("✅ Counties FIPS codes fixed\n")
    
    # 2. Check economic_annual.csv
    print("2. Checking economic_annual.csv...")
    economic_df = pd.read_csv(f'{processed_data_path}economic_annual.csv')
    print(f"Current FIPS codes sample: {economic_df['fips_code'].head().tolist()}")
    
    # Fix FIPS codes
    economic_df['fips_code'] = economic_df['fips_code'].astype(str).str.zfill(5)
    print(f"Fixed FIPS codes sample: {economic_df['fips_code'].head().tolist()}")
    
    # Save fixed version
    economic_df.to_csv(f'{processed_data_path}economic_annual.csv', index=False)
    print("✅ Economic FIPS codes fixed\n")
    
    # 3. Check housing data - these use RegionID but we need FIPS mapping
    print("3. Checking housing data structure...")
    housing_monthly = pd.read_csv(f'{processed_data_path}housing_prices_monthly.csv', nrows=1000)  # Sample for speed
    print(f"Housing data columns: {housing_monthly.columns.tolist()}")
    print(f"Sample county names: {housing_monthly['county_name'].head().tolist()}")
    print("Housing data uses RegionID and county names - we'll need to map to FIPS\n")
    
    # 4. Check population data - uses county names
    print("4. Checking population data...")
    population_df = pd.read_csv(f'{processed_data_path}population_annual.csv')
    print(f"Sample county names: {population_df['county_name'].head().tolist()}")
    print("Population data uses county names - we'll need to map to FIPS\n")
    
    return counties_df, economic_df

def create_county_name_to_fips_mapping(counties_df):
    """
    Create a mapping between county names and FIPS codes
    This will help us link housing and population data
    """
    print("5. Creating county name to FIPS mapping...")
    
    # Clean county names for better matching
    counties_df['clean_county_name'] = counties_df['county_name'].str.lower().str.strip()
    
    # Create mapping dictionary
    fips_mapping = dict(zip(counties_df['clean_county_name'], counties_df['fips_code']))
    
    print(f"Created mapping for {len(fips_mapping)} counties")
    print("Sample mappings:")
    for i, (name, fips) in enumerate(list(fips_mapping.items())[:5]):
        print(f"  {name} → {fips}")
    
    # Save mapping as reference file
    mapping_df = counties_df[['fips_code', 'county_name', 'state']].copy()
    mapping_df.to_csv(f'{processed_data_path}county_fips_mapping.csv', index=False)
    print("✅ County-FIPS mapping saved\n")
    
    return fips_mapping

def add_fips_to_housing_data(fips_mapping):
    """
    Add FIPS codes to housing data using county name matching
    """
    print("6. Adding FIPS codes to housing data...")
    
    # Load housing affordability data
    affordability_df = pd.read_csv(f'{processed_data_path}housing_affordability.csv')
    
    # Clean county names for matching
    affordability_df['clean_county_name'] = affordability_df['county_name'].str.lower().str.strip()
    
    # Map FIPS codes
    affordability_df['fips_code'] = affordability_df['clean_county_name'].map(fips_mapping)
    
    # Check mapping success rate
    mapped_count = affordability_df['fips_code'].notna().sum()
    total_count = len(affordability_df)
    print(f"FIPS mapping success: {mapped_count}/{total_count} ({mapped_count/total_count*100:.1f}%)")
    
    # Save updated housing affordability data
    affordability_df.drop('clean_county_name', axis=1).to_csv(f'{processed_data_path}housing_affordability.csv', index=False)
    
    # Do the same for price trends
    trends_df = pd.read_csv(f'{processed_data_path}price_trends_annual.csv')
    trends_df['clean_county_name'] = trends_df['county_name'].str.lower().str.strip()
    trends_df['fips_code'] = trends_df['clean_county_name'].map(fips_mapping)
    trends_df.drop('clean_county_name', axis=1).to_csv(f'{processed_data_path}price_trends_annual.csv', index=False)
    
    print("✅ FIPS codes added to housing data\n")

def add_fips_to_population_data(fips_mapping):
    """
    Add FIPS codes to population data
    """
    print("7. Adding FIPS codes to population data...")
    
    population_df = pd.read_csv(f'{processed_data_path}population_annual.csv')
    
    # Clean county names - remove leading dots and extra spaces
    population_df['clean_county_name'] = (population_df['county_name']
                                        .str.replace('.', '', regex=False)
                                        .str.lower()
                                        .str.strip())
    
    # Map FIPS codes
    population_df['fips_code'] = population_df['clean_county_name'].map(fips_mapping)
    
    # Check mapping success
    mapped_count = population_df['fips_code'].notna().sum()
    total_count = len(population_df)
    print(f"FIPS mapping success: {mapped_count}/{total_count} ({mapped_count/total_count*100:.1f}%)")
    
    # Save updated population data
    population_df.drop('clean_county_name', axis=1).to_csv(f'{processed_data_path}population_annual.csv', index=False)
    print("✅ FIPS codes added to population data\n")

if __name__ == "__main__":
    # Fix FIPS code formatting
    counties_df, economic_df = check_and_fix_fips_codes()
    
    # Create mapping between county names and FIPS codes
    fips_mapping = create_county_name_to_fips_mapping(counties_df)
    
    # Add FIPS codes to housing data
    add_fips_to_housing_data(fips_mapping)
    
    # Add FIPS codes to population data
    add_fips_to_population_data(fips_mapping)
    
    print("=== FIPS CODE FIXING COMPLETE ===")
    print("All datasets now have proper 5-digit FIPS codes!")
    print("\nFiles updated:")
    print("- counties.csv (FIPS codes fixed)")
    print("- economic_annual.csv (FIPS codes fixed)")
    print("- housing_affordability.csv (FIPS codes added)")
    print("- price_trends_annual.csv (FIPS codes added)")
    print("- population_annual.csv (FIPS codes added)")
    print("- county_fips_mapping.csv (new reference file)")
    
    print("\n✅ Ready for SQL database setup!")