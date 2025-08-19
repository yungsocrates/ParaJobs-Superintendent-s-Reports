"""
Superintendent Mapping Module for NYC DOE Reports
Maps schools to their respective superintendents based on DBN codes
"""

import pandas as pd
import os
from typing import Dict, List, Tuple
import re

def load_superintendent_mapping(csv_path: str) -> Dict[str, List[str]]:
    """
    Load superintendent-to-schools mapping from the CSV file
    
    Args:
        csv_path: Path to the superintendent CSV file
        
    Returns:
        Dictionary mapping superintendent names to lists of school DBNs
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_path)
        
        # Clean up column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Create superintendent to schools mapping
        superintendent_mapping = {}
        
        for _, row in df.iterrows():
            dbn = str(row['DBN']).strip()
            superintendent = str(row['Superintendent']).strip()
            
            # Skip rows with missing data
            if pd.isna(superintendent) or pd.isna(dbn) or superintendent == '' or dbn == '':
                continue
                
            # Initialize list if superintendent not seen before
            if superintendent not in superintendent_mapping:
                superintendent_mapping[superintendent] = []
                
            # Add school to superintendent's list
            if dbn not in superintendent_mapping[superintendent]:
                superintendent_mapping[superintendent].append(dbn)
        
        print(f"✅ Loaded mapping for {len(superintendent_mapping)} superintendents")
        print(f"📊 Total schools mapped: {sum(len(schools) for schools in superintendent_mapping.values())}")
        
        return superintendent_mapping
        
    except Exception as e:
        print(f"❌ Error loading superintendent mapping: {e}")
        return {}

def get_school_location_code(dbn: str) -> str:
    """
    Extract school location code by removing first 2 characters from DBN
    
    Args:
        dbn: School DBN code (e.g., "01M015")
        
    Returns:
        School location code (e.g., "M015")
    """
    if len(dbn) >= 3:
        return dbn[2:]
    return dbn

def get_superintendent_for_school(dbn: str, superintendent_mapping: Dict[str, List[str]]) -> str:
    """
    Find which superintendent oversees a given school
    
    Args:
        dbn: School DBN code
        superintendent_mapping: Mapping from superintendents to school lists
        
    Returns:
        Superintendent name or "Unknown" if not found
    """
    for superintendent, schools in superintendent_mapping.items():
        if dbn in schools:
            return superintendent
    return "Unknown"

def get_schools_for_superintendent(superintendent: str, superintendent_mapping: Dict[str, List[str]]) -> List[str]:
    """
    Get list of schools for a specific superintendent
    
    Args:
        superintendent: Superintendent name
        superintendent_mapping: Mapping from superintendents to school lists
        
    Returns:
        List of school DBN codes
    """
    return superintendent_mapping.get(superintendent, [])

def create_superintendent_summary(superintendent_mapping: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Create a summary DataFrame of superintendents and their school counts
    
    Args:
        superintendent_mapping: Mapping from superintendents to school lists
        
    Returns:
        DataFrame with superintendent summary statistics
    """
    summary_data = []
    
    for superintendent, schools in superintendent_mapping.items():
        # Extract borough information from school DBNs
        boroughs = set()
        districts = set()
        
        for school in schools:
            if len(school) >= 3:
                district_code = school[:2]
                borough_code = school[2:3]
                
                districts.add(district_code)
                
                # Map borough codes to names
                borough_map = {
                    'M': 'Manhattan',
                    'X': 'Bronx', 
                    'K': 'Brooklyn',
                    'Q': 'Queens',
                    'R': 'Staten Island'
                }
                borough_name = borough_map.get(borough_code, 'Unknown')
                boroughs.add(borough_name)
        
        summary_data.append({
            'Superintendent': superintendent,
            'School_Count': len(schools),
            'Districts': ', '.join(sorted(districts)),
            'Boroughs': ', '.join(sorted(boroughs)),
            'Schools': ', '.join(schools)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('School_Count', ascending=False)
    
    return summary_df

def clean_superintendent_name(superintendent: str) -> str:
    """
    Clean superintendent name for use in file names and URLs
    
    Args:
        superintendent: Raw superintendent name
        
    Returns:
        Cleaned name suitable for file names
    """
    # Remove special characters and spaces, replace with underscores
    cleaned = re.sub(r'[^\w\s-]', '', superintendent)
    cleaned = re.sub(r'\s+', '_', cleaned.strip())
    return cleaned

def find_superintendent_csv() -> str:
    """
    Find the superintendent CSV file in the current directory
    
    Returns:
        Path to the CSV file or empty string if not found
    """
    current_dir = os.getcwd()
    
    # Look for CSV files starting with "8.8.25"
    for file in os.listdir(current_dir):
        if file.startswith("8.8.25") and file.endswith(".csv"):
            return os.path.join(current_dir, file)
    
    return ""

# Test the mapping functionality
if __name__ == "__main__":
    # Find and load the superintendent mapping
    csv_path = find_superintendent_csv()
    
    if csv_path:
        print(f"📁 Found superintendent CSV: {os.path.basename(csv_path)}")
        mapping = load_superintendent_mapping(csv_path)
        
        if mapping:
            # Create and display summary
            summary = create_superintendent_summary(mapping)
            print("\n📊 SUPERINTENDENT SUMMARY:")
            print("="*60)
            print(summary[['Superintendent', 'School_Count', 'Boroughs']].head(10).to_string(index=False))
            
            # Show example mapping
            first_superintendent = list(mapping.keys())[0]
            schools = mapping[first_superintendent]
            print(f"\n🏫 Example - {first_superintendent}:")
            print(f"   Schools: {schools[:5]}{'...' if len(schools) > 5 else ''}")
            
        else:
            print("❌ Failed to load superintendent mapping")
    else:
        print("❌ Superintendent CSV file not found")
