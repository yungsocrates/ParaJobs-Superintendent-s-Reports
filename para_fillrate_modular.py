"""
NYC DOE Paraprofessional Jobs Dashboard - Main Script (Modularized)

This is the main entry point for generating the NYC DOE reports dashboard.
The heavy lifting is now done by imported modules for better maintainability.
"""

import os
import time
import pandas as pd

# Import our custom modules
from data_processing import (
    load_and_process_data, get_data_date_range, create_summary_stats, 
    copy_logo_to_output, create_matching_analysis, load_superintendent_mapping, add_superintendent_info
)
from report_generators import create_district_report, create_borough_report, create_overall_summary, create_superintendent_report
def main():
    """
    Main function to generate static reports
    """
    # Configuration - Updated to use multiple CSV files
    csv_files = [
        'Fill Rate Data/mayjobs.csv',
        'Fill Rate Data/junejobs.csv',
        'Fill Rate Data/apriljobs.csv',
        'Fill Rate Data/febmarchjobs.csv',
        'Fill Rate Data/decjanjobs.csv',
        'Fill Rate Data/sepoctnovjobs.csv',
        'SREPP1.csv',
        'SREPP2.csv',
    ]
    output_directory = 'nycdoe_reports'
    
    # Check for force regeneration flag
    import sys
    force_regenerate = '--force' in sys.argv or '-f' in sys.argv
    if force_regenerate:
        print("🔄 Force regeneration mode: will overwrite existing reports")
    else:
        print("📋 Incremental mode: will skip existing reports (use --force or -f to regenerate all)")
    
    start_time = time.time()
    print("🚀 NYC DOE Paraprofessional Fill Rate Analysis")
    print("=" * 50)
    
    try:
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Copy logo for deployment
        copy_logo_to_output(output_directory)
        
        # Load and process data from multiple files
        print("Loading data sources...")
        df, srepp_df = load_and_process_data(csv_files)
        
        # Handle SREPP data if present
        if not srepp_df.empty:
            print(f"✓ SREPP payroll data: {len(srepp_df)} records")
        else:
            print("⚠ No SREPP payroll data found")
            
        # Show main data info
        if not df.empty:
            print(f"✓ SubCentral data: {len(df)} records")
        else:
            print("✗ No SubCentral data found")
            
        # Create matching analysis between SubCentral and SREPP data
        print("Creating payroll matching analysis...")
        matching_stats = create_matching_analysis(df, srepp_df)
        if not matching_stats.empty:
            print(f"✓ Analysis completed for {len(matching_stats)} locations")
        else:
            print("⚠ No matching analysis available")
        
        # Continue with main data processing
        if df.empty:
            print("✗ Error: No main data loaded. Check your CSV files.")
            return
        
        # Load superintendent mapping and add to main data
        print("Loading superintendent mappings...")
        try:
            mapping_df = load_superintendent_mapping()
            df = add_superintendent_info(df, mapping_df)
        except Exception as e:
            print(f"⚠ Warning: Could not load superintendent mapping: {e}")
            print("Continuing without superintendent information...")
        
        # Get date range information
        date_range_info = get_data_date_range(df)
        print(f"✓ Report period: {date_range_info}")
        
        # OPTIMIZATION: Calculate ALL statistics levels once (like matching analysis)
        print("Creating comprehensive statistics...")
        
        # Create all levels of statistics - now using Superintendent instead of District
        citywide_stats = create_summary_stats(df, [])  # No grouping = citywide
        borough_stats = create_summary_stats(df, ['Borough'])
        superintendent_stats = create_summary_stats(df, ['Superintendent_Name'])  # Changed from District
        school_stats = create_summary_stats(df, ['Superintendent_Name', 'Location'])  # Changed grouping
        
        # Validate statistics were created successfully
        stats_info = [
            ('citywide', citywide_stats),
            ('borough', borough_stats), 
            ('superintendent', superintendent_stats),  # Changed from district
            ('school', school_stats)
        ]
        
        for name, stats in stats_info:
            if stats.empty:
                print(f"⚠ Warning: {name} statistics are empty")
            else:
                print(f"✓ {name.capitalize()} stats: {len(stats)} records, columns: {list(stats.columns)}")
        
        # Clean up any Type_Fill_Status columns
        for stats in [citywide_stats, borough_stats, superintendent_stats, school_stats]:
            if 'Type_Fill_Status' in stats.columns:
                stats.drop(columns=['Type_Fill_Status'], inplace=True)

        # Convert to int to avoid float display issues
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for stats in [citywide_stats, borough_stats, superintendent_stats, school_stats]:
            for col in int_cols:
                if col in stats.columns:
                    stats[col] = stats[col].astype(int)
        
        print(f"✓ Statistics created: citywide, {len(borough_stats)} boroughs, {len(superintendent_stats)} superintendents, {len(school_stats)} schools")
        
        # For backward compatibility, keep summary_stats as superintendent level
        summary_stats = superintendent_stats
        
        # Create reports for each Superintendent
        superintendents = sorted([s for s in df['Superintendent_Name'].unique() if s != 'Unknown'])
        print(f"Generating superintendent reports ({len(superintendents)} superintendents)...")
        report_files = []
        all_school_reports = []
        
        for superintendent in superintendents:
            superintendent_data = summary_stats[summary_stats['Superintendent_Name'] == superintendent].copy()
            if len(superintendent_data) > 0:
                # Check if superintendent has schools in main dataframe
                superintendent_schools = df[df['Superintendent_Name'] == superintendent]
                if superintendent_schools.empty:
                    print(f"⚠ Superintendent {superintendent}: no schools found, skipping...")
                    continue
                
                # Check if report already exists (unless force regeneration)
                safe_superintendent_name = superintendent.replace(" ", "_").replace(",", "").replace(".", "")
                expected_report_file = os.path.join(output_directory, f"Superintendent_{safe_superintendent_name}", f"{safe_superintendent_name}_report.html")
                if not force_regenerate and os.path.exists(expected_report_file):
                    print(f"⚠ Superintendent {superintendent}: report already exists, skipping...")
                    report_files.append(expected_report_file)
                    continue
                
                print(f"✓ Generating report for Superintendent {superintendent}...")
                result = create_superintendent_report(
                    superintendent, superintendent_data, df, output_directory, superintendent_stats, date_range_info, matching_stats, school_stats
                )
                if result is not None:
                    report_file, school_reports = result
                    report_files.append(report_file)
                    all_school_reports.extend(school_reports)
        
        # Create reports for each borough
        boroughs = sorted(df['Borough'].unique())
        print(f"Generating borough reports ({len(boroughs)} boroughs)...")
        borough_report_files = []

        for borough in boroughs:
            if borough != 'Unknown':  # Skip if no valid borough found
                borough_data = borough_stats[borough_stats['Borough'] == borough].copy()
                if len(borough_data) > 0:
                    # Check if report already exists (unless force regeneration)
                    borough_name_clean = borough.replace(" ", "_").replace("/", "_")
                    expected_report_file = os.path.join(output_directory, f"Borough_{borough_name_clean}", f"{borough_name_clean}_report.html")
                    if not force_regenerate and os.path.exists(expected_report_file):
                        print(f"⚠ Borough {borough}: report already exists, skipping...")
                        borough_report_files.append(expected_report_file)
                        continue
                    
                    print(f"✓ Generating report for Borough {borough}...")
                    report_file = create_borough_report(
                        borough, borough_data, df, output_directory, superintendent_stats, date_range_info, matching_stats
                    )
                    borough_report_files.append(report_file)
        
        # Create overall summary
        expected_index_file = os.path.join(output_directory, 'index.html')
        if not force_regenerate and os.path.exists(expected_index_file):
            print("⚠ Overall summary (index.html): report already exists, skipping...")
            index_file = expected_index_file
        else:
            print("✓ Generating overall summary (index.html)...")
            index_file = create_overall_summary(df, citywide_stats, borough_stats, output_directory, date_range_info, matching_stats, superintendent_stats)
        
        print("✓ Reports generated successfully!")
        print(f"  • Main report: {index_file}")
        print(f"  • District reports: {len(report_files)} files")
        print(f"  • Borough reports: {len(borough_report_files)} files")
        print(f"  • School reports: {len(all_school_reports)} files")
        print(f"  • Open '{index_file}' to view the dashboard")
        
        elapsed = time.time() - start_time
        print(f"⏱ Completed in {elapsed:.1f} seconds")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find one or more CSV files: {csv_files}")
        print("Please make sure all files exist in the specified paths.")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
