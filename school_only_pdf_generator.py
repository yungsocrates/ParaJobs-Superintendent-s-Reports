"""
School-Only PDF Report Generator

Generates PDF reports for a specific list of schools combining:
1. SubCentral fill rate data
2. Nomination tracker data
3. Individual job tracking for nominees
"""

import os
import sys
from datetime import datetime
import pandas as pd

def load_school_list(filename="school_list.txt"):
    """
    Load the list of schools to process from a text file
    """
    if not os.path.exists(filename):
        print(f"School list file '{filename}' not found")
        print("Please create school_list.txt with one school code per line")
        return []
    
    try:
        with open(filename, 'r') as f:
            schools = [line.strip().upper() for line in f if line.strip()]
        
        # Remove duplicates while preserving order
        schools = list(dict.fromkeys(schools))
        
        print(f"Loaded {len(schools)} schools from {filename}")
        return schools
    
    except Exception as e:
        print(f"Error reading school list: {e}")
        return []

def extract_district_from_school(school_code):
    """
    Extract district from school code (first 2 characters)
    """
    return school_code[:2] if len(school_code) >= 2 else ""

def generate_school_pdfs_from_list():
    """
    Generate PDF reports only for schools in the school_list.txt file
    """
    
    try:
        # Import the simple school report generator
        from simple_school_pdf import (
            create_simple_school_pdf, 
            REPORTLAB_AVAILABLE,
            install_reportlab
        )
        
        # Import proper nomination processing
        from nomination_processing import (
            load_nomination_data,
            get_school_nomination_summary,
            get_school_nomination_details
        )
        
        # Import existing para fillrate modules
        from data_processing import (
            load_and_process_data,
            create_matching_analysis
        )
        
    except ImportError as e:
        print(f"[ERROR] Error importing required modules: {e}")
        print("Make sure all required files are in the same directory:")
        print("  - school_report_pdf_generator.py")
        print("  - para_fillrate_modular.py")
        print("  - data_processing.py")
        return False
    
    # Check ReportLab availability
    if not REPORTLAB_AVAILABLE:
        print("Installing ReportLab...")
        if not install_reportlab():
            return False
    
    print("=== School PDF Report Generation ===")
    
    # Load the school list
    target_schools = load_school_list()
    if not target_schools:
        return False
    
    # Load all data sources
    print("[INFO] Loading data sources...")
    
    # 1. Load SubCentral fill rate data from Fill Rate Data directory
    try:
        from data_processing import load_and_process_data
        
        # Use specific CSV files as in para_fillrate_modular.py
        # Previous SY files (now consolidated/renamed):
        #csv_files = [
        #    'Fill Rate Data/Jan_to_May_2025_Sub_Para_Job_Final.csv',
        #    'Fill Rate Data/Sept_to_Dec_and_June_Job_Final.csv',
        #    'SREPP1.csv', 'SREPP2.csv',
        #    'nominations.csv', 
        #    'cancellations.csv'
        #]
        
        # Current SY 2025-26 files:
        csv_files = [
            'Job_Inquiry_essReport_1058.csv',
            'Sub Para Payroll since 2025-09-02.csv',
            'nominations2026.csv',
            'cancellations2026.csv',
            'preferred2026.csv'
        ]
        
        if csv_files:
            # Load actual fill rate data
            result = load_and_process_data(csv_files)
            if isinstance(result, tuple):
                subcentral_data, metadata = result
            else:
                subcentral_data = result
            print(f"[OK] Loaded {len(subcentral_data)} SubCentral records from fill rate data")
        else:
            # Fallback: Load school info and create basic structure
            main_data_file = '8.8.25 NYCDOE Division of School Leadership DBN Affiliation - Budget & HR - http___tinyurl.com_DSL-Budget-HR (3).csv'
            school_info = pd.read_csv(main_data_file)
            
            # Clean and filter the data
            school_info = school_info.dropna(subset=['DBN'])
            school_info['DBN'] = school_info['DBN'].astype(str).str.upper()
            
            # Rename for consistency
            school_info = school_info.rename(columns={
                'DBN': 'Location',
                'School Name': 'School_Name',
                'N_Principal Name': 'Principal',
                'N_Superintendent': 'Superintendent'
            })
            
            # Add placeholder job data (will be replaced with actual data processing later)
            school_info['Total'] = 0  # Will be populated from actual job data
            school_info['Filled'] = 0
            school_info['Vacancy_Total'] = 0
            school_info['Vacancy_Filled'] = 0  
            school_info['Absence_Total'] = 0
            school_info['Absence_Filled'] = 0
            
            subcentral_data = school_info
            print(f"[OK] Loaded {len(subcentral_data)} school records (placeholder job data)")
        
        if subcentral_data is None or subcentral_data.empty:
            print("[WARNING] No SubCentral data available - will generate report with payroll/nomination data only")
            subcentral_data = pd.DataFrame()  # Create empty DataFrame to continue processing
        
        srepp_data = pd.DataFrame()  # Empty for now
        
    except Exception as e:
        print(f"[ERROR] Error loading SubCentral data: {e}")
        return False
    
    # 2. Load payroll data first (needed for nomination processing)
    try:
        # Load payroll data from SREPP files
        payroll_files = ['Sub Para Payroll since 2025-09-02.csv']
        payroll_data = pd.DataFrame()
        
        for payroll_file in payroll_files:
            if os.path.exists(payroll_file):
                temp_df = pd.read_csv(payroll_file)
                print(f"[DEBUG] Original columns from {payroll_file}: {list(temp_df.columns)}")
                # Clean up column headers by removing leading/trailing whitespace
                temp_df.columns = temp_df.columns.str.strip()
                print(f"[DEBUG] Cleaned columns from {payroll_file}: {list(temp_df.columns)}")
                print(f"[OK] Loaded {len(temp_df)} payroll records from {payroll_file}")
                payroll_data = pd.concat([payroll_data, temp_df], ignore_index=True)
            else:
                print(f"[WARNING] Payroll file not found: {payroll_file}")
        
        if not payroll_data.empty:
            print(f"[OK] Total payroll records loaded: {len(payroll_data)}")
        else:
            print("[WARNING] No payroll data found")
            
    except Exception as e:
        print(f"[WARNING] Could not load payroll data: {e}")
        payroll_data = pd.DataFrame()
    
    # 3. Load nomination data using proper nomination processing (matching para_fillrate_modular.py)
    try:
        nomination_data = load_nomination_data('nominations2026.csv', 'cancellations2026.csv', payroll_data, subcentral_data)
        if nomination_data:
            if isinstance(nomination_data, dict) and 'metrics' in nomination_data:
                print(f"[OK] Nomination data loaded for {len(nomination_data['metrics'])} schools")
                if nomination_data.get('detailed_tracking'):
                    print(f"[OK] Detailed job tracking available for {len(nomination_data['detailed_tracking'])} schools")
            else:
                print(f"[OK] Nomination data loaded for {len(nomination_data)} schools")
        else:
            print("[WARNING] No nomination data available")
            nomination_data = {}
    except Exception as e:
        print(f"[WARNING] Could not load nominations: {e}")
        nomination_data = {}

    # 4. Create payroll matching analysis (using correct function from para_fillrate_modular.py)
    try:
        from data_processing import create_matching_analysis
        matching_analysis = create_matching_analysis(subcentral_data, payroll_data)
        if matching_analysis is not None:
            print(f"[OK] Payroll matching analysis completed for {len(matching_analysis)} locations")
        else:
            print("[WARNING] No matching analysis available")
    except Exception as e:
        print(f"[WARNING] Could not create payroll matching: {e}")
        matching_analysis = None

    # Create output directory
    output_dir = f'school_report_cards_{datetime.now().strftime("%Y%m%d_%H%M")}'
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter SubCentral data to only include target schools
    # SubCentral data uses Location codes without district prefix (e.g., 'K001', 'M393')
    # Our school list has full codes with district prefix (e.g., '02M393', '07X221')
    # So we need to extract the last 4 characters to match
    
    available_schools = set(subcentral_data['Location'].unique())
    print(f"[LOCATION] Available location codes in data: {len(available_schools)} total")
    print(f"    Sample available locations: {sorted(list(available_schools))[:20]}")
    
    # Create mapping from full school code to location code
    school_to_location = {}
    schools_to_process = []
    schools_missing = []
    
    for school in target_schools:
        # Extract location code (last 4 characters)
        location_code = school[-4:] if len(school) >= 4 else school
        school_to_location[school] = location_code
        
        if location_code in available_schools:
            schools_to_process.append(school)
        else:
            schools_missing.append(school)
    
    print(f"[SCHOOLS] Processing {len(schools_to_process)} schools with SubCentral data")
    print(f"[SCHOOLS] Processing {len(schools_missing)} schools WITHOUT SubCentral data (will use payroll/nomination data only)")
    print(f"[SCHOOLS] Total schools to process: {len(target_schools)}")
    
    if schools_missing:
        print(f"[INFO] Schools missing from SubCentral (will still generate reports with available data):")
        for school in schools_missing[:10]:  # Show first 10 missing schools
            location_code = school_to_location[school]
            print(f"    - {school} (looking for location: {location_code})")
        if len(schools_missing) > 10:
            print(f"    ... and {len(schools_missing) - 10} more schools")
        print()
    
    # Process ALL schools - both those with and without SubCentral data
    all_schools_to_process = schools_to_process + schools_missing
    
    created_reports = []
    failed_reports = []
    
    for i, school_code in enumerate(all_schools_to_process, 1):
        try:
            print(f"[REPORT] ({i}/{len(all_schools_to_process)}) Generating report for {school_code}...")
            
            # Get the location code for this school
            location_code = school_to_location[school_code]
            
            # Get school-specific data using the location code
            school_subcentral = subcentral_data[
                subcentral_data['Location'] == location_code
            ].copy()
            
            # Debug: Check if SubCentral data was found
            if school_subcentral.empty:
                print(f"    [DEBUG] No SubCentral data found for {school_code} (location: {location_code})")
                print(f"    [DEBUG] Will generate report with payroll/nomination data only")
            else:
                print(f"    [DEBUG] Found {len(school_subcentral)} SubCentral records for {school_code}")
            
            # Get school nominations by directly reading from raw CSV data
            # Bypass nomination processing which normalizes school codes incorrectly
            school_nominations = {}
            try:
                # Read nominations directly from CSV using the proper school code
                nominations_file = r"d:\ParaJobs Superintendent's Reports\nominations2026.csv"
                cancellations_file = r"d:\ParaJobs Superintendent's Reports\cancellations2026.csv"
                
                if os.path.exists(nominations_file):
                    # Read nominations CSV and filter by Location
                    nom_df = pd.read_csv(nominations_file)
                    
                    # Check if our school appears in nominations
                    if 'Location' in nom_df.columns:
                        # Try string comparison after converting both to strings
                        nom_df['Location_str'] = nom_df['Location'].astype(str).str.strip()
                        school_code_str = str(school_code).strip()
                        
                        # Use the string version for matching
                        school_noms = nom_df[nom_df['Location_str'] == school_code_str]
                    else:
                        school_noms = pd.DataFrame()
                    
                    # Read cancellations CSV and filter by Location
                    cancel_df = pd.DataFrame()
                    school_cancels = pd.DataFrame()
                    if os.path.exists(cancellations_file):
                        cancel_df = pd.read_csv(cancellations_file)
                        if 'Location' in cancel_df.columns:
                            cancel_df['Location_str'] = cancel_df['Location'].astype(str).str.strip()
                            school_cancels = cancel_df[cancel_df['Location_str'] == school_code_str]
                    
                    # Calculate metrics - check actual completion status
                    total_nominations = len(school_noms)
                    cancelled_nominations = len(school_cancels)
                    
                    # Count completed nominations by checking "Finalized on Payroll?" field
                    completed_nominations = 0
                    if not school_noms.empty and 'Finalized on Payroll?' in school_noms.columns:
                        completed_nominations = len(school_noms[school_noms['Finalized on Payroll?'] == 'Y'])
                    
                    percentage_completed = (completed_nominations / total_nominations * 100) if total_nominations > 0 else 0
                    
                    # Enhance nominee details with payroll and SubCentral job tracking
                    enhanced_details = []
                    if not school_noms.empty:
                        for _, nominee in school_noms.iterrows():
                            nominee_dict = nominee.to_dict()
                            
                            # Get nominee identifiers and format File No properly
                            raw_file_no = nominee.get('File No', nominee.get('EMPLID', ''))
                            try:
                                # Convert to integer first to remove decimal, then pad to 7 digits
                                file_no = str(int(float(raw_file_no))).zfill(7) if pd.notna(raw_file_no) and raw_file_no != '' else ''
                            except (ValueError, TypeError):
                                file_no = str(raw_file_no).zfill(7) if raw_file_no and raw_file_no != '' else ''
                            
                            ssn = nominee.get('SSN', '')
                            first_name = nominee.get('FirstName', '')
                            last_name = nominee.get('LastName', '')
                            
                            # Initialize job tracking counts
                            payroll_this_location = 0
                            payroll_other_locations = 0
                            subcentral_job_days = 0
                            
                            # Match with payroll data if available
                            if payroll_data is not None and not payroll_data.empty:
                                try:
                                    # Try matching by File No/EMPLID first, then by SSN
                                    nominee_payroll = pd.DataFrame()
                                    
                                    if file_no and 'EISID' in payroll_data.columns:
                                        # Format payroll EISID to 7-digit for comparison (handle NaN/inf values)
                                        def safe_format_eisid(x):
                                            try:
                                                if pd.notna(x) and str(x).strip() != '' and x != float('inf') and x != float('-inf'):
                                                    clean_str = str(x).replace('.0', '').strip()
                                                    return str(int(float(clean_str))).zfill(7)
                                                return ''
                                            except (ValueError, TypeError, OverflowError):
                                                return ''
                                        
                                        payroll_eisid_formatted = payroll_data['EISID'].apply(safe_format_eisid)
                                        nominee_payroll = payroll_data[payroll_eisid_formatted == file_no]
                                        
                                        if len(nominee_payroll) == 0:
                                            # Debug: Show available EISIDs if no match found
                                            available_eisids = payroll_eisid_formatted.unique()[:5]
                                            print(f"    [PAYROLL DEBUG] Looking for EISID {file_no}, found 0 records")
                                            print(f"    [PAYROLL DEBUG] Sample available EISIDs: {list(available_eisids)}")
                                        else:
                                            print(f"    [PAYROLL DEBUG] Looking for EISID {file_no}, found {len(nominee_payroll)} records")
                                    
                                    if nominee_payroll.empty and ssn and 'SSN' in payroll_data.columns:
                                        nominee_payroll = payroll_data[payroll_data['SSN'].astype(str) == str(ssn)]
                                        print(f"    [PAYROLL DEBUG] Looking for SSN {ssn}, found {len(nominee_payroll)} records")
                                    
                                    if not nominee_payroll.empty:
                                        # Count days at this location vs other locations
                                        if 'SCHOOL' in nominee_payroll.columns:
                                            # Convert school codes to strings for comparison
                                            nominee_payroll['SCHOOL_str'] = nominee_payroll['SCHOOL'].astype(str).str.strip()
                                            school_code_str = str(school_code).strip()
                                            
                                            this_location_records = nominee_payroll[nominee_payroll['SCHOOL_str'] == school_code_str]
                                            other_location_records = nominee_payroll[nominee_payroll['SCHOOL_str'] != school_code_str]
                                            
                                            payroll_this_location = len(this_location_records)
                                            payroll_other_locations = len(other_location_records)
                                            
                                            print(f"    [PAYROLL DEBUG] {first_name} {last_name}: {payroll_this_location} days at {school_code_str}, {payroll_other_locations} days elsewhere")
                                
                                except Exception as e:
                                    print(f"    [DEBUG] Payroll matching error for {first_name} {last_name}: {e}")
                            
                            # Match with SubCentral data if available
                            if subcentral_data is not None and not subcentral_data.empty:
                                try:
                                    # Try matching by various identifier fields
                                    nominee_subcentral = pd.DataFrame()
                                    
                                    # Check different possible matching fields in SubCentral (Access ID is the main field)
                                    for field in ['Access ID', 'Sub_EISID', 'Employee_EISID', 'EISID', 'Employee_ID']:
                                        if field in subcentral_data.columns and file_no:
                                            # Convert SubCentral field to same 7-digit format for matching - handle floats properly
                                            def format_eisid(x):
                                                try:
                                                    if pd.notna(x) and str(x).strip() != '':
                                                        # Convert to string, remove decimal point if present, then to int, then pad
                                                        clean_str = str(x).replace('.0', '').strip()
                                                        return str(int(float(clean_str))).zfill(7)
                                                    return ''
                                                except (ValueError, TypeError):
                                                    return ''
                                            
                                            subcentral_field_formatted = subcentral_data[field].apply(format_eisid)
                                            nominee_subcentral = subcentral_data[subcentral_field_formatted == file_no]
                                            if not nominee_subcentral.empty:
                                                print(f"    [SUBCENTRAL DEBUG] Matched {first_name} {last_name} using field '{field}' with EISID {file_no}")
                                                break
                                    
                                    if not nominee_subcentral.empty:
                                        subcentral_job_days = len(nominee_subcentral)
                                        print(f"    [SUBCENTRAL DEBUG] {first_name} {last_name}: {subcentral_job_days} SubCentral job records")
                                
                                except Exception as e:
                                    print(f"    [DEBUG] SubCentral matching error for {first_name} {last_name}: {e}")
                            
                            # Add tracking data to nominee record
                            nominee_dict['payroll_days_this_location'] = payroll_this_location
                            nominee_dict['payroll_days_other_locations'] = payroll_other_locations
                            nominee_dict['subcentral_job_days'] = subcentral_job_days
                            
                            enhanced_details.append(nominee_dict)
                    
                    school_nominations = {
                        'summary': {
                            'total_nominations': total_nominations,
                            'completed_nominations': completed_nominations,
                            'cancelled_nominations': cancelled_nominations,
                            'percentage_completed': percentage_completed
                        },
                        'details': enhanced_details
                    }
                    
                    if total_nominations > 0:
                        pass  # Remove debug print
                    else:
                        pass  # Remove debug print
                else:
                    school_nominations = {'summary': {}, 'details': []}
                    
            except Exception as e:
                school_nominations = {'summary': {}, 'details': []}
            
            # Get payroll matching for this school (simple matching)
            school_payroll_matches = None
            if payroll_data is not None and not payroll_data.empty:
                try:
                    # Simple payroll matching: count people who worked at this school
                    # Try both full school code (e.g., '07X221') and location code (e.g., 'X221')
                    school_payroll = pd.DataFrame()
                    if 'SCHOOL' in payroll_data.columns:
                        # First try full school code
                        school_payroll = payroll_data[payroll_data['SCHOOL'] == school_code]
                        # If no match, try location code
                        if school_payroll.empty:
                            school_payroll = payroll_data[payroll_data['SCHOOL'] == location_code]
                    if not school_payroll.empty:
                        unique_people = school_payroll['EISID'].nunique() if 'EISID' in school_payroll.columns else 0
                        total_hours = school_payroll['HRS'].sum() if 'HRS' in school_payroll.columns else 0
                        school_payroll_matches = {
                            'unique_workers': unique_people,
                            'total_hours': total_hours,
                            'payroll_records': len(school_payroll)
                        }
                    else:
                        pass  # No payroll records found
                except Exception as e:
                    school_payroll_matches = None
            else:
                pass  # No payroll data available
            
            # Create school-specific payroll match analysis using unique ID method
            school_matching = None
            if payroll_data is not None and not payroll_data.empty:
                try:
                    print(f"  [MATCHING] Starting payroll analysis for {school_code}")
                    
                    # Get payroll records for this school
                    school_payroll = payroll_data[payroll_data['SCHOOL'] == school_code].copy()
                    total_payroll_days = len(school_payroll)
                    
                    # Get filled SubCentral jobs for this school (if available)
                    if not school_subcentral.empty and 'Type_Fill_Status' in school_subcentral.columns:
                        filled_jobs = school_subcentral[school_subcentral['Type_Fill_Status'].str.endswith('_Filled', na=False)].copy()
                        total_subcentral_filled = len(filled_jobs)
                        print(f"  [INFO] Found {total_subcentral_filled} filled SubCentral jobs for matching")
                    else:
                        filled_jobs = pd.DataFrame()
                        total_subcentral_filled = 0
                        print(f"  [WARNING] No SubCentral data available - showing payroll stats only")
                    
                    matched_jobs = 0
                    
                    if not school_payroll.empty:
                        print(f"  [INFO] Found {total_payroll_days} payroll records for {school_code}")
                    
                    # Only attempt matching if we have both datasets
                    if not filled_jobs.empty and not school_payroll.empty:
                        # Create unique IDs for SubCentral filled jobs: EISID+SCHOOL+DATE
                        print(f"  [MATCHING DEBUG] Initial filled_jobs count: {len(filled_jobs)}")
                        print(f"  [MATCHING DEBUG] Available columns: {list(filled_jobs.columns)}")
                        
                        filled_jobs['Job Start'] = pd.to_datetime(filled_jobs['Job Start'], errors='coerce')
                        print(f"  [MATCHING DEBUG] After date parsing: {len(filled_jobs)} jobs")
                        print(f"  [MATCHING DEBUG] Jobs with valid dates: {filled_jobs['Job Start'].notna().sum()}")
                        
                        filled_jobs = filled_jobs[filled_jobs['Job Start'].notna()].copy()
                        print(f"  [MATCHING DEBUG] After date filtering: {len(filled_jobs)} jobs")
                        
                        if 'Access ID' in filled_jobs.columns and not filled_jobs.empty:
                            # Debug: Check what's in the Access ID column
                            print(f"  [MATCHING DEBUG] Sample Access ID values: {filled_jobs['Access ID'].head().tolist()}")
                            print(f"  [MATCHING DEBUG] Access ID data types: {filled_jobs['Access ID'].dtype}")
                            print(f"  [MATCHING DEBUG] Non-null Access ID count: {filled_jobs['Access ID'].notna().sum()}")
                            
                            # Format SubCentral Access IDs (handle floats properly)
                            def format_eisid(x):
                                try:
                                    if pd.notna(x) and str(x).strip() != '' and str(x).strip().lower() != 'nan':
                                        clean_str = str(x).replace('.0', '').strip()
                                        # Try to convert to number first to validate
                                        num_val = float(clean_str)
                                        if num_val > 0:  # Only accept positive numbers
                                            return str(int(num_val)).zfill(7)
                                    return ''
                                except (ValueError, TypeError):
                                    return ''
                            
                            filled_jobs['EISID_Clean'] = filled_jobs['Access ID'].apply(format_eisid)
                            print(f"  [MATCHING DEBUG] After EISID cleaning: {len(filled_jobs)} jobs")
                            print(f"  [MATCHING DEBUG] Jobs with valid EISID: {(filled_jobs['EISID_Clean'] != '').sum()}")
                            print(f"  [MATCHING DEBUG] Sample cleaned EISIDs: {filled_jobs['EISID_Clean'][filled_jobs['EISID_Clean'] != ''].head().tolist()}")
                            
                            # If no valid Access IDs, try other possible EISID fields
                            if (filled_jobs['EISID_Clean'] == '').all():
                                print(f"  [MATCHING DEBUG] No valid Access IDs found, trying alternative fields...")
                                for alt_field in ['External ID', 'Access  ID', 'External  ID', 'EMPLID', 'Employee']:
                                    if alt_field in filled_jobs.columns:
                                        print(f"  [MATCHING DEBUG] Trying field: {alt_field}")
                                        alt_cleaned = filled_jobs[alt_field].apply(format_eisid)
                                        valid_count = (alt_cleaned != '').sum()
                                        print(f"  [MATCHING DEBUG] {alt_field} valid count: {valid_count}")
                                        if valid_count > 0:
                                            filled_jobs['EISID_Clean'] = alt_cleaned
                                            print(f"  [MATCHING DEBUG] Using {alt_field} for matching")
                                            break
                            
                            filled_jobs = filled_jobs[filled_jobs['EISID_Clean'] != ''].copy()
                            print(f"  [MATCHING DEBUG] After EISID filtering: {len(filled_jobs)} jobs")
                            
                            if len(filled_jobs) > 0:
                                # Format dates and create unique IDs
                                filled_jobs['Date_Clean'] = filled_jobs['Job Start'].dt.strftime('%Y%m%d')
                                filled_jobs['Unique_ID'] = filled_jobs['EISID_Clean'] + '|' + school_code + '|' + filled_jobs['Date_Clean']
                            
                            subcentral_unique_ids = set(filled_jobs['Unique_ID'].tolist())
                            print(f"  [MATCHING] Created {len(subcentral_unique_ids)} SubCentral unique IDs")
                            
                            # Create unique IDs for payroll data: EISID+SCHOOL+DATE
                            school_payroll['DATE_Clean'] = pd.to_datetime(school_payroll['DATE'], errors='coerce')
                            school_payroll = school_payroll[school_payroll['DATE_Clean'].notna()].copy()
                            
                            # Format payroll EISID to 7-digit string (handle NaN/inf values safely)
                            def safe_format_payroll_eisid(x):
                                try:
                                    if pd.notna(x) and str(x).strip() != '' and x != float('inf') and x != float('-inf'):
                                        return str(int(float(x))).zfill(7)
                                    return ''
                                except (ValueError, TypeError, OverflowError):
                                    return ''
                            
                            school_payroll['EISID_Clean'] = school_payroll['EISID'].apply(safe_format_payroll_eisid)
                            school_payroll['Date_Clean'] = school_payroll['DATE_Clean'].dt.strftime('%Y%m%d')
                            school_payroll['Unique_ID'] = school_payroll['EISID_Clean'] + '|' + school_payroll['SCHOOL'] + '|' + school_payroll['Date_Clean']
                            
                            payroll_unique_ids = set(school_payroll['Unique_ID'].tolist())
                            print(f"  [MATCHING] Created {len(payroll_unique_ids)} payroll unique IDs")
                            
                            # Debug: Show sample IDs from both systems
                            if len(subcentral_unique_ids) > 0:
                                sample_sc = list(subcentral_unique_ids)[:3]
                                print(f"  [MATCHING DEBUG] Sample SubCentral IDs: {sample_sc}")
                            if len(payroll_unique_ids) > 0:
                                sample_pr = list(payroll_unique_ids)[:3]
                                print(f"  [MATCHING DEBUG] Sample Payroll IDs: {sample_pr}")
                            
                            # Find matches using set intersection
                            matched_unique_ids = subcentral_unique_ids.intersection(payroll_unique_ids)
                            matched_jobs = len(matched_unique_ids)
                            
                            if matched_jobs > 0:
                                sample_matches = list(matched_unique_ids)[:3]
                                print(f"  [MATCHING] Sample matching IDs: {sample_matches}")
                    
                    # Calculate match percentage
                    match_percentage = (matched_jobs / total_payroll_days * 100) if total_payroll_days > 0 else 0
                    
                    school_matching = {
                        'subcentral_filled_jobs': total_subcentral_filled,
                        'payroll_job_days': total_payroll_days,
                        'matched_jobs': matched_jobs,
                        'match_percentage': match_percentage
                    }
                    
                    print(f"  [MATCHING] SubCentral filled: {total_subcentral_filled}, Payroll days: {total_payroll_days}, Matched: {matched_jobs} ({match_percentage:.1f}%)")
                    
                except Exception as e:
                    school_matching = None
            else:
                pass  # Cannot create matching analysis - missing data
            
            # Get additional school info from the school info database
            principal_name = ""
            superintendent_name = ""
            district = extract_district_from_school(school_code)
            
            # Try to get school info from the main school database
            try:
                main_data_file = '1 28 2026 NYCDOE Division of School Leadership DBN Affiliation - Budget  HR - http___tinyurl.com_DSL-Budget-HR (3).csv'
                if main_data_file not in globals() or 'school_info_data' not in globals():
                    school_info_data = pd.read_csv(main_data_file)
                    school_info_data = school_info_data.dropna(subset=['DBN'])
                    school_info_data['DBN'] = school_info_data['DBN'].astype(str).str.upper()
                
                school_info_row = school_info_data[school_info_data['DBN'] == school_code]
                if not school_info_row.empty:
                    principal_name = school_info_row.iloc[0].get('N_Principal Name', '') or ""
                    superintendent_name = school_info_row.iloc[0].get('N_Superintendent', '') or ""
                    pass  # Remove principal debug print
                    pass  # Remove superintendent debug print
            except Exception as e:
                print(f"  [WARNING] Could not load school info: {e}")
            
            # Convert subcentral_data to the format expected by create_simple_school_pdf
            if not school_subcentral.empty:
                print(f"  [INFO] Found {len(school_subcentral)} records for location {location_code}")
                
                # Calculate fill rate statistics from individual job records
                total_jobs = len(school_subcentral)
                
                # Count filled vs unfilled jobs based on 'Fill_Status' 
                filled_jobs = len(school_subcentral[school_subcentral['Fill_Status'] == 'Filled']) if 'Fill_Status' in school_subcentral.columns else 0
                unfilled_jobs = total_jobs - filled_jobs
                
                # Break down by job type if available
                vacancy_jobs = len(school_subcentral[school_subcentral['Type'] == 'Vacancy']) if 'Type' in school_subcentral.columns else 0
                absence_jobs = len(school_subcentral[school_subcentral['Type'] == 'Absence']) if 'Type' in school_subcentral.columns else 0
                
                # Count filled by type
                vacancy_filled = 0
                absence_filled = 0
                if 'Type' in school_subcentral.columns and 'Fill_Status' in school_subcentral.columns:
                    vacancy_filled = len(school_subcentral[
                        (school_subcentral['Type'] == 'Vacancy') & 
                        (school_subcentral['Fill_Status'] == 'Filled')
                    ])
                    absence_filled = len(school_subcentral[
                        (school_subcentral['Type'] == 'Absence') & 
                        (school_subcentral['Fill_Status'] == 'Filled')
                    ])
                
                school_summary = {
                    'Total_Jobs': int(total_jobs),
                    'Total_Filled': int(filled_jobs),
                    'Total_Unfilled': int(unfilled_jobs),
                    'Total_Vacancy': int(vacancy_jobs),
                    'Vacancy_Filled': int(vacancy_filled),
                    'Total_Absence': int(absence_jobs),
                    'Absence_Filled': int(absence_filled),
                    'Fill_Rate': round((filled_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0.0
                }
                
                print(f"  [STATS] Stats: {total_jobs} total jobs, {filled_jobs} filled ({school_summary['Fill_Rate']}% fill rate)")
                
                # Convert to DataFrame format expected by the function
                school_data_df = pd.DataFrame([school_summary])
                print(f"  [DEBUG] DataFrame dtypes: {school_data_df.dtypes.to_dict()}")
                print(f"  [DEBUG] DataFrame values: {school_data_df.iloc[0].to_dict()}")
            else:
                print(f"  [WARNING] No records found for location {location_code}")
                school_data_df = pd.DataFrame()
            
            # Generate comprehensive PDF report
            pdf_filename = f"{school_code}_report_card.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            # Use the simple PDF format that works with our data structure
            from simple_school_pdf import create_simple_school_pdf
            
            result = create_simple_school_pdf(
                school_code=school_code,
                school_data=school_data_df,
                nomination_data=school_nominations,
                output_path=pdf_path,
                principal_name=principal_name,
                superintendent_name=superintendent_name,
                payroll_data=school_matching
            )
            
            if result:
                created_reports.append(pdf_path)
                print(f"    [OK] Created: {pdf_filename}")
            else:
                failed_reports.append((school_code, "PDF creation failed"))
                print(f"    [ERROR] Failed to create: {pdf_filename}")
            
        except Exception as e:
            print(f"    [ERROR] Failed to create report for {school_code}: {e}")
            failed_reports.append((school_code, str(e)))
            continue
    
    # Create summary report
    create_summary_report(output_dir, target_schools, schools_to_process, 
                         schools_missing, created_reports, failed_reports)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"SCHOOL PDF GENERATION COMPLETED")
    print(f"{'='*60}")
    print(f"[NOMINATIONS] Target schools: {len(target_schools)}")
    print(f"[INFO] Available in data: {len(schools_to_process)}")
    print(f"[OK] Successfully created: {len(created_reports)} reports")
    print(f"[ERROR] Failed: {len(failed_reports)} reports")
    print(f"[WARNING] Missing from data: {len(schools_missing)} schools")
    print(f"📁 Reports saved to: {output_dir}")
    
    return len(created_reports) > 0

def create_summary_report(output_dir, target_schools, processed_schools, 
                         missing_schools, created_reports, failed_reports):
    """
    Create a summary text file with processing results
    """
    
    summary_path = os.path.join(output_dir, "PROCESSING_SUMMARY.txt")
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("SCHOOL PDF GENERATION SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Target Schools: {len(target_schools)}\n")
            f.write(f"Available in Data: {len(processed_schools)}\n")
            f.write(f"Successfully Created: {len(created_reports)}\n")
            f.write(f"Failed: {len(failed_reports)}\n")
            f.write(f"Missing from Data: {len(missing_schools)}\n\n")
            
            if created_reports:
                f.write("SUCCESSFULLY CREATED REPORTS:\n")
                f.write("-" * 30 + "\n")
                for report_path in created_reports:
                    filename = os.path.basename(report_path)
                    f.write(f"[OK] {filename}\n")
                f.write("\n")
            
            if failed_reports:
                f.write("FAILED REPORTS:\n")
                f.write("-" * 15 + "\n")
                for school, error in failed_reports:
                    f.write(f"[ERROR] {school}: {error}\n")
                f.write("\n")
            
            if missing_schools:
                f.write("SCHOOLS NOT FOUND IN DATA:\n")
                f.write("-" * 25 + "\n")
                for school in missing_schools:
                    district = extract_district_from_school(school)
                    f.write(f"[WARNING] {school} (District {district})\n")
                f.write("\n")
            
            # Group missing schools by district
            if missing_schools:
                f.write("MISSING SCHOOLS BY DISTRICT:\n")
                f.write("-" * 25 + "\n")
                district_missing = {}
                for school in missing_schools:
                    district = extract_district_from_school(school)
                    if district not in district_missing:
                        district_missing[district] = []
                    district_missing[district].append(school)
                
                for district in sorted(district_missing.keys()):
                    f.write(f"District {district}: {len(district_missing[district])} schools\n")
                    for school in sorted(district_missing[district]):
                        f.write(f"  - {school}\n")
                    f.write("\n")
        
        print(f"[SUMMARY] Summary report created: {summary_path}")
        
    except Exception as e:
        print(f"[WARNING] Could not create summary report: {e}")

def show_school_list_info():
    """
    Display information about the current school list
    """
    schools = load_school_list()
    if not schools:
        return
    
    print(f"\n[SUMMARY] SCHOOL LIST INFORMATION")
    print("=" * 40)
    print(f"Total schools: {len(schools)}")
    
    # Group by district
    districts = {}
    for school in schools:
        district = extract_district_from_school(school)
        if district not in districts:
            districts[district] = []
        districts[district].append(school)
    
    print(f"Districts represented: {len(districts)}")
    print("\nSchools by District:")
    for district in sorted(districts.keys()):
        print(f"  District {district}: {len(districts[district])} schools")
        # Show first few schools as examples
        for school in sorted(districts[district])[:3]:
            print(f"    - {school}")
        if len(districts[district]) > 3:
            print(f"    ... and {len(districts[district]) - 3} more")
        print()

def get_school_nominations_from_processed_data(school_code, nominations_df):
    """Get nominations for a specific school from processed nomination data"""
    
    if nominations_df.empty:
        return {
            'spa_nominations': pd.DataFrame(),
            'ste_nominations': pd.DataFrame(), 
            'arepp_nominations': pd.DataFrame(),
            'total_count': 0
        }
    
    # Filter nominations for this school
    school_nominations = nominations_df[
        nominations_df.get('School_Code', '') == school_code
    ].copy()
    
    # Group by nomination type if that column exists
    result = {
        'spa_nominations': pd.DataFrame(),
        'ste_nominations': pd.DataFrame(),
        'arepp_nominations': pd.DataFrame(),
        'total_count': len(school_nominations)
    }
    
    if 'Nomination_Type' in school_nominations.columns:
        for nom_type in ['SPA', 'STE', 'AREPP']:
            type_noms = school_nominations[
                school_nominations['Nomination_Type'] == nom_type
            ].copy()
            
            result[f'{nom_type.lower()}_nominations'] = type_noms
    else:
        # If no type column, put all in SPA for now
        result['spa_nominations'] = school_nominations
    
    return result

def get_school_payroll_matches(school_code, payroll_data, subcentral_data):
    """Get payroll matches for a specific school"""
    
    if payroll_data.empty:
        return pd.DataFrame()
    
    # Try to match school codes between payroll and subcentral data
    # This is a simplified version - you may need to adjust based on actual column names
    
    try:
        # Look for school code in payroll data
        if 'School_Code' in payroll_data.columns:
            school_payroll = payroll_data[
                payroll_data['School_Code'] == school_code
            ].copy()
        elif 'Location' in payroll_data.columns:
            school_payroll = payroll_data[
                payroll_data['Location'] == school_code
            ].copy()
        else:
            # Try to find a column that might contain school codes
            for col in payroll_data.columns:
                if 'school' in col.lower() or 'location' in col.lower() or 'dbn' in col.lower():
                    school_payroll = payroll_data[
                        payroll_data[col] == school_code
                    ].copy()
                    break
            else:
                school_payroll = pd.DataFrame()
        
        return school_payroll
        
    except Exception as e:
        print(f"[WARNING] Error matching payroll for {school_code}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    print("School PDF Report Generator")
    print("=" * 40)
    print("This tool generates PDF reports for schools listed in school_list.txt")
    print()
    
    while True:
        print("Choose an option:")
        print("1. Generate PDF Reports for Listed Schools")
        print("2. Show School List Information")
        print("3. Edit School List (opens in notepad)")
        print("4. Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            print()
            success = generate_school_pdfs_from_list()
            if success:
                print("[SUCCESS] PDF generation completed successfully!")
            else:
                print("[ERROR] PDF generation failed")
            print()
            
        elif choice == "2":
            show_school_list_info()
            print()
            
        elif choice == "3":
            try:
                os.system("notepad school_list.txt")
                print("📝 School list opened in notepad")
            except Exception as e:
                print(f"[ERROR] Could not open notepad: {e}")
            print()
            
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")
            print()