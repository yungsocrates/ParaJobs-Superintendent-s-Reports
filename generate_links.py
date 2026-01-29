import pandas as pd
import re
import os


def format_superintendent_name(name):
    """Convert 'Chan, Carry' to 'chan_carry'"""
    if pd.isna(name):
        return ""
    # Remove any extra spaces and convert to lowercase
    name = name.strip().lower()
    # Replace comma and spaces with underscore
    name = re.sub(r'[,\s]+', '_', name)
    # Remove any other special characters
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name


def format_school_code(code):
    """Convert 'M184' to 'm184'"""
    if pd.isna(code):
        return ""
    return str(code).strip().lower()


def normalize_name(name):
    """Normalize names to Title Case (e.g., 'HARRY SHERMAN' -> 'Harry Sherman')"""
    if pd.isna(name):
        return ""
    return name.strip().title()


def generate_superintendent_links(df):
    """Generate superintendent links CSV with emails"""
    # Normalize superintendent names to handle case variations
    df['Superintendent_Normalized'] = df['N_Superintendent'].apply(normalize_name)
    
    # Group by normalized name and get first email for each
    superintendents = df[['Superintendent_Normalized', 'N_Superintendent - Email']].drop_duplicates(subset=['Superintendent_Normalized'])
    
    superintendent_links = []

    for _, row in superintendents.iterrows():
        superintendent = row['Superintendent_Normalized']
        email = row['N_Superintendent - Email']
        
        if pd.isna(superintendent) or superintendent == '':
            continue
            
        formatted_name = format_superintendent_name(superintendent)
        url = f"https://superintendentsparajobs.netlify.app/superintendent_{formatted_name}/{formatted_name}_report"
        
        superintendent_links.append({
            'Superintendent Name': superintendent,
            'Superintendent Email': email if not pd.isna(email) else '',
            'URL': url
        })

    superintendent_df = pd.DataFrame(superintendent_links)
    superintendent_df.to_csv('superintendent_links.csv', index=False)
    print(f"\nGenerated superintendent_links.csv with {len(superintendent_df)} entries")
    print("\nSample Superintendent Links:")
    print(superintendent_df.head())
    
    return superintendent_df


def generate_school_links(df):
    """Generate school links CSV with principal and superintendent emails"""
    # Normalize names to handle case variations
    df['Superintendent_Normalized'] = df['N_Superintendent'].apply(normalize_name)
    df['Principal_Normalized'] = df['N_Principal Name'].apply(normalize_name)
    
    school_links = []

    for idx, row in df.iterrows():
        superintendent = row.get('Superintendent_Normalized', '')
        superintendent_email = row.get('N_Superintendent - Email', '')
        principal = row.get('Principal_Normalized', '')
        principal_email = row.get('N_Principal Email', '')
        dbn = row.get('DBN', '')
        bn = row.get('BN', '')
        school_name = row.get('School Name', '')
        
        # Skip rows without superintendent or BN
        if pd.isna(superintendent) or pd.isna(bn) or superintendent == '' or bn == '':
            continue
        
        formatted_superintendent = format_superintendent_name(superintendent)
        formatted_bn = format_school_code(bn)
        
        url = f"https://superintendentsparajobs.netlify.app/superintendent_{formatted_superintendent}/schools/school_{formatted_bn}/{formatted_bn}_report"
        
        school_links.append({
            'Superintendent': superintendent,
            'Superintendent Email': superintendent_email if not pd.isna(superintendent_email) else '',
            'Principal Name': principal if not pd.isna(principal) else '',
            'Principal Email': principal_email if not pd.isna(principal_email) else '',
            'DBN': dbn,
            'BN': bn,
            'School Name': school_name if not pd.isna(school_name) else '',
            'URL': url
        })

    school_df = pd.DataFrame(school_links)
    school_df.to_csv('school_links.csv', index=False)
    print(f"Generated school_links.csv with {len(school_df)} entries")
    print("\nSample School Links:")
    print(school_df.head())
    
    return school_df


def main():
    """Main function to generate superintendent and school links"""
    # Use the updated file name
    input_file = "1 28 2026 NYCDOE Division of School Leadership DBN Affiliation - Budget  HR - http___tinyurl.com_DSL-Budget-HR (3).csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find file '{input_file}'")
        print("Please make sure the file exists in the current directory.")
        return
    
    df = pd.read_csv(input_file)

    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()

    print(f"Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")

    # Generate both CSV files
    generate_superintendent_links(df)
    generate_school_links(df)


if __name__ == "__main__":
    main()
