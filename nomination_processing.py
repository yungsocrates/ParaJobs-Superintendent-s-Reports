"""
Nomination and Cancellation Data Processing Module
Processes nomination and cancellation CSV files to calculate school-level metrics
"""

import pandas as pd
import os
import re

def normalize_location_code(location_code):
    """
    Normalize location codes by removing district prefixes
    
    Examples:
        '20KS20' -> 'KS20'
        '30Q445' -> 'Q445' 
        '15K372' -> 'K372'
        'X008' -> 'X008' (already normalized)
        '460000' -> '460000' (no letters, keep as is)
    
    Args:
        location_code (str): Original location code
    
    Returns:
        str: Normalized location code without district prefix
    """
    if pd.isna(location_code) or location_code == '':
        return location_code
    
    location_str = str(location_code).strip()
    
    # If it's all digits, keep as is (like 460000)
    if location_str.isdigit():
        return location_str
    
    # Remove leading digits and return the rest
    # Pattern: digits followed by letter(s) and numbers
    normalized = re.sub(r'^\d+', '', location_str)
    
    # If normalization resulted in empty string, return original
    if not normalized:
        return location_str
        
    return normalized

def load_nomination_data(nominations_file, cancellations_file, srepp_df=None, subcentral_df=None):
    """
    Load and process nomination and cancellation data
    
    Args:
        nominations_file (str): Path to nominations.csv
        cancellations_file (str): Path to cancellations.csv
        srepp_df (pd.DataFrame, optional): SREPP payroll data for job tracking
        subcentral_df (pd.DataFrame, optional): SubCentral data for job tracking
    
    Returns:
        dict: Dictionary with school-level nomination metrics and detailed tracking
    """
    try:
        # Check if files exist before processing
        if not os.path.exists(nominations_file):
            print(f"Warning: Nominations file not found: {nominations_file}")
            return {}
        
        if not os.path.exists(cancellations_file):
            print(f"Warning: Cancellations file not found: {cancellations_file}")
            return {}
        
        print(f"Loading nominations data from {nominations_file}...")
        # Load nominations data
        nominations_df = pd.read_csv(nominations_file)
        print(f"✓ Loaded {len(nominations_df)} nominations records")
        
        print(f"Loading cancellations data from {cancellations_file}...")
        # Load cancellations data  
        cancellations_df = pd.read_csv(cancellations_file)
        print(f"✓ Loaded {len(cancellations_df)} cancellations records")
        
        print("Normalizing location codes...")
        # Normalize location codes in nominations data
        nominations_df['Location_Normalized'] = nominations_df['Location'].apply(normalize_location_code)
        
        # Normalize location codes in cancellations data
        cancellations_df['Location_Normalized'] = cancellations_df['Location'].apply(normalize_location_code)
        
        print("Calculating school metrics...")
        # Process the data by school location
        school_metrics = calculate_school_nomination_metrics(nominations_df, cancellations_df)
        
        # If we have SREPP and SubCentral data, add detailed tracking
        detailed_tracking = {}
        if srepp_df is not None and subcentral_df is not None:
            print("Creating detailed job tracking for nominated individuals...")
            detailed_tracking = create_detailed_nomination_tracking(nominations_df, srepp_df, subcentral_df)
        
        print(f"✓ Nomination processing completed for {len(school_metrics)} schools")
        return {'metrics': school_metrics, 'detailed_tracking': detailed_tracking}
        
    except FileNotFoundError as e:
        print(f"Warning: Could not load nomination files - {e}")
        return {}
    except Exception as e:
        print(f"Error processing nomination data: {e}")
        import traceback
        traceback.print_exc()
        return {}

def create_nominee_details_table_html(school_code, nomination_data):
    """
    Create HTML table showing detailed nominee information with job tracking
    
    Args:
        school_code (str): School location code
        nomination_data (dict): Nomination data with detailed tracking
    
    Returns:
        str: HTML table showing nominee details
    """
    nominees = get_school_nomination_details(school_code, nomination_data)
    
    if not nominees:
        return "<p><em>No completed nominations with detailed tracking data available for this school.</em></p>"
    
    # Create table HTML
    table_html = """
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>File No / EISID</th>
                    <th>Payroll Days<br/>at This Location</th>
                    <th>Payroll Days<br/>at Other Locations</th>
                    <th>SubCentral Job Days<br/>(At This Location)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for nominee in nominees:
        # Format File No as integer with leading zeros (pad to 7 characters)
        file_no = nominee['file_no']
        try:
            # Convert to int first to remove any decimal places, then format with leading zeros
            file_no_int = int(float(file_no))
            file_no_formatted = f"{file_no_int:07d}"
        except (ValueError, TypeError):
            # If conversion fails, use original value
            file_no_formatted = str(file_no)
        
        # Highlight Payroll Days at This Location when it is 0
        payroll_at_loc_style = ' style="background-color: #fff3cd; color: #856404; font-weight: bold;"' if nominee['payroll_days_at_location'] == 0 else ''
        
        table_html += f"""
                <tr>
                    <td>{nominee['first_name']}</td>
                    <td>{nominee['last_name']}</td>
                    <td>{file_no_formatted}</td>
                    <td class="text-center"{payroll_at_loc_style}>{nominee['payroll_days_at_location']}</td>
                    <td class="text-center">{nominee['payroll_days_other_locations']}</td>
                    <td class="text-center">{nominee['subcentral_days']}</td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    return table_html

def calculate_school_nomination_metrics(nominations_df, cancellations_df):
    """
    Calculate nomination metrics by school location
    
    Args:
        nominations_df (pd.DataFrame): Nominations data
        cancellations_df (pd.DataFrame): Cancellations data
    
    Returns:
        dict: School-level metrics {school_code: {metrics}}
    """
    school_metrics = {}
    
    # Get unique school locations from nominations (using normalized codes)
    schools = nominations_df['Location_Normalized'].unique()
    
    for school in schools:
        if pd.isna(school) or school == '':
            continue
            
        # Filter nominations for this school (using normalized codes)
        school_nominations = nominations_df[nominations_df['Location_Normalized'] == school]
        
        # Filter cancellations for this school (using normalized codes)
        school_cancellations = cancellations_df[cancellations_df['Location_Normalized'] == school]
        
        # Calculate metrics
        # Completed nominations: "Finalized on Payroll?" = "Y"
        completed_nominations = len(school_nominations[school_nominations['Finalized on Payroll?'] == 'Y'])
        
        # Cancelled nominations: count from cancellations file
        cancelled_nominations = len(school_cancellations)
        
        # Total nominations = all nominations in nominations file + cancelled
        # (nominations file contains completed + in-progress; cancellations file is separate)
        total_nominations = len(school_nominations) + cancelled_nominations
        
        # In Progress = nominations not yet finalized and not cancelled
        in_progress_nominations = len(school_nominations) - completed_nominations
        
        # Percentage completed = Completed / Total Nominations
        percentage_completed = (completed_nominations / total_nominations * 100) if total_nominations > 0 else 0
        
        school_metrics[school] = {
            'total_nominations': total_nominations,
            'completed_nominations': completed_nominations,
            'in_progress_nominations': in_progress_nominations,
            'cancelled_nominations': cancelled_nominations,
            'percentage_completed': percentage_completed
        }
    
    return school_metrics

def create_detailed_nomination_tracking(nominations_df, srepp_df, subcentral_df):
    """
    Create detailed job tracking for nominated individuals (optimized version)
    
    Args:
        nominations_df (pd.DataFrame): Nominations data with normalized location codes
        srepp_df (pd.DataFrame): SREPP payroll data
        subcentral_df (pd.DataFrame): SubCentral job data
    
    Returns:
        dict: School-level tracking {school_code: [list of nominee details]}
    """
    detailed_tracking = {}
    
    # Pre-process SREPP data for faster lookups
    srepp_lookup = {}
    if not srepp_df.empty and 'EISID' in srepp_df.columns and 'SCHOOL' in srepp_df.columns:
        print("Preprocessing SREPP data for faster lookups...")
        # Clean and index SREPP data once
        srepp_clean = srepp_df.copy()
        # FIXED: Convert EISID to integer string (remove decimals)
        srepp_clean['EISID_clean'] = srepp_clean['EISID'].fillna(0).astype(int).astype(str).str.strip()
        srepp_clean['SCHOOL_clean'] = srepp_clean['SCHOOL'].astype(str).str.strip()
        
        # Also normalize SREPP school codes for matching
        srepp_clean['SCHOOL_normalized'] = srepp_clean['SCHOOL_clean'].apply(normalize_location_code)
        
        # FIXED: Convert DATE column to datetime for proper matching
        if 'DATE' in srepp_clean.columns:
            srepp_clean['DATE'] = pd.to_datetime(srepp_clean['DATE'], format='%m/%d/%Y', errors='coerce')
        
        # Debug: Show sample SREPP school codes
        sample_schools = srepp_clean['SCHOOL_clean'].unique()[:10]
        sample_normalized = srepp_clean['SCHOOL_normalized'].unique()[:10]
        print(f"Sample SREPP school codes: {list(sample_schools)}")
        print(f"Sample SREPP normalized: {list(sample_normalized)}")
        
        # Group by EISID for faster lookups
        for eisid, group in srepp_clean.groupby('EISID_clean'):
            if eisid and eisid != 'nan' and eisid != '0':
                srepp_lookup[eisid] = group
    
    # Pre-process SubCentral data for faster lookups  
    subcentral_lookup = {}
    if not subcentral_df.empty and 'Access ID' in subcentral_df.columns:
        print("Preprocessing SubCentral data for faster lookups...")
        # Clean and index SubCentral data once
        subcentral_clean = subcentral_df.copy()
        # FIXED: Convert Access ID to integer string (remove decimals from float values like 869184.0)
        subcentral_clean['Access_ID_clean'] = subcentral_clean['Access ID'].fillna(0).astype(int).astype(str).str.strip()
        
        # FIXED: Normalize location codes in SubCentral for matching
        subcentral_clean['Location_normalized'] = subcentral_clean['Location'].apply(normalize_location_code)
        
        # Count jobs by Access ID AND location
        for (access_id, location), group in subcentral_clean.groupby(['Access_ID_clean', 'Location_normalized']):
            if access_id and access_id != 'nan' and access_id != '0':
                if access_id not in subcentral_lookup:
                    subcentral_lookup[access_id] = {}
                subcentral_lookup[access_id][location] = len(group)
    
    # Group nominations by school (normalized location)
    schools = nominations_df['Location_Normalized'].unique()
    
    # Debug: Show sample normalized school codes
    sample_schools = [s for s in schools if s and s != ''][:10]
    print(f"Sample normalized nomination school codes: {list(sample_schools)}")
    
    print(f"Processing detailed tracking for {len(schools)} schools...")
    
    # Debug counter
    debug_matches = 0
    
    for school in schools:
        if pd.isna(school) or school == '':
            continue
            
        school_nominations = nominations_df[nominations_df['Location_Normalized'] == school]
        
        # Only include completed nominations (finalized on payroll)
        completed_nominations = school_nominations[school_nominations['Finalized on Payroll?'] == 'Y']
        
        nominees_details = []
        
        for _, nominee in completed_nominations.iterrows():
            # FIXED: Convert File No to integer string to match EISID format
            try:
                file_no = str(int(float(nominee['File No']))).strip()
            except (ValueError, TypeError):
                continue
            
            first_name = nominee.get('FirstName', 'N/A')
            last_name = nominee.get('LastName', 'N/A')
            
            # Skip if no valid file number
            if pd.isna(file_no) or file_no == '' or file_no == 'nan' or file_no == '0':
                continue
            
            # Calculate job days from SREPP data using pre-processed lookup
            payroll_at_location = 0
            payroll_at_other_locations = 0
            
            if file_no in srepp_lookup:
                person_srepp = srepp_lookup[file_no]
                
                # Count payroll days at this location (using normalized school codes for matching)
                school_srepp = person_srepp[person_srepp['SCHOOL_normalized'] == school]
                payroll_at_location = len(school_srepp)
                
                # Count payroll days at other locations  
                other_srepp = person_srepp[person_srepp['SCHOOL_normalized'] != school]
                payroll_at_other_locations = len(other_srepp)
                
                # Debug: Log matches for first few cases
                if debug_matches < 5:
                    print(f"Debug: File {file_no} at school {school}: {payroll_at_location} days here, {payroll_at_other_locations} days elsewhere")
                    if len(person_srepp) > 0:
                        print(f"  SREPP normalized schools for this person: {list(person_srepp['SCHOOL_normalized'].unique())[:5]}")
                        print(f"  Looking for school: {school}")
                    debug_matches += 1
            
            # Calculate job days from SubCentral data using pre-processed lookup
            subcentral_days = 0
            if file_no in subcentral_lookup:
                # Get total days at this specific location
                subcentral_days = subcentral_lookup[file_no].get(school, 0)
            
            # Add to nominees details
            nominees_details.append({
                'first_name': first_name,
                'last_name': last_name,
                'file_no': file_no,
                'payroll_days_at_location': payroll_at_location,
                'payroll_days_other_locations': payroll_at_other_locations,
                'subcentral_days': subcentral_days
            })
        
        if nominees_details:
            detailed_tracking[school] = nominees_details
    
    print(f"✓ Detailed job tracking available for {len(detailed_tracking)} schools")
    return detailed_tracking

def get_school_nomination_summary(school_code, nomination_data):
    """
    Get nomination summary for a specific school
    
    Args:
        school_code (str): School location code
        nomination_data (dict): Nomination data (can be old format or new format with metrics/detailed_tracking)
    
    Returns:
        dict: Nomination metrics for the school
    """
    # Handle backward compatibility - check if it's the old format or new format
    if isinstance(nomination_data, dict) and 'metrics' in nomination_data:
        # New format with separate metrics and detailed tracking
        school_metrics = nomination_data['metrics']
    else:
        # Old format - nomination_data is the metrics directly
        school_metrics = nomination_data
    
    if school_code not in school_metrics:
        return {
            'total_nominations': 0,
            'completed_nominations': 0,
            'in_progress_nominations': 0,
            'cancelled_nominations': 0,
            'percentage_completed': 0
        }
    
    return school_metrics[school_code]

def get_school_nomination_details(school_code, nomination_data):
    """
    Get detailed nomination tracking for a specific school
    
    Args:
        school_code (str): School location code  
        nomination_data (dict): Nomination data with detailed tracking
    
    Returns:
        list: List of nominee details with job tracking
    """
    # Handle backward compatibility
    if isinstance(nomination_data, dict) and 'detailed_tracking' in nomination_data:
        detailed_tracking = nomination_data['detailed_tracking']
        return detailed_tracking.get(school_code, [])
    else:
        # Old format - no detailed tracking available
        return []
    """
    Get nomination summary for a specific school
    
    Args:
        school_code (str): School location code
        school_metrics (dict): School metrics dictionary
    
    Returns:
        dict: Nomination metrics for the school
    """
    if school_code not in school_metrics:
        return {
            'total_nominations': 0,
            'completed_nominations': 0,
            'cancelled_nominations': 0,
            'percentage_completed': 0
        }
    
    return school_metrics[school_code]

def format_nomination_metrics(metrics):
    """
    Format nomination metrics for display
    
    Args:
        metrics (dict): Nomination metrics
    
    Returns:
        dict: Formatted metrics
    """
    in_progress = metrics.get('in_progress_nominations',
        metrics['total_nominations'] - metrics['completed_nominations'] - metrics['cancelled_nominations'])
    return {
        'Total Nominations': f"{metrics['total_nominations']:,}",
        'Nominations Completed': f"{metrics['completed_nominations']:,}",
        'In Progress Nominations': f"{in_progress:,}",
        'Cancelled Nominations': f"{metrics['cancelled_nominations']:,}",
        'Percentage of Nominations Completed': f"{metrics['percentage_completed']:.1f}%"
    }

def create_nomination_section_html(school_code, school_metrics):
    """
    Create HTML section for nomination metrics
    
    Args:
        school_code (str): School location code
        school_metrics (dict): School metrics dictionary
    
    Returns:
        str: HTML section for nomination metrics
    """
    metrics = get_school_nomination_summary(school_code, school_metrics)
    formatted_metrics = format_nomination_metrics(metrics)
    
    # Create color coding based on completion percentage
    completion_pct = metrics['percentage_completed']
    if completion_pct >= 90:
        status_class = "status-excellent"
        status_text = "Excellent"
    elif completion_pct >= 75:
        status_class = "status-good" 
        status_text = "Good"
    elif completion_pct >= 50:
        status_class = "status-fair"
        status_text = "Fair"
    else:
        status_class = "status-poor"
        status_text = "Needs Attention"
    
    html = f"""
    <div class="section nomination-section">
        <h3>Substitute Paraprofessional Nomination Metrics</h3>
        <p><em>This section shows the metrics for substitute paraprofessional nominations for this school.</em></p>
        
        <div class="nomination-summary">
            <div class="nomination-card">
                <h4>Nomination Metrics Overview</h4>
                <div class="metric-grid">
                    <div class="metric-item">
                        <span class="metric-label">Total Nominations:</span>
                        <span class="metric-value">{formatted_metrics['Total Nominations']}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Nominations Completed:</span>
                        <span class="metric-value">{formatted_metrics['Nominations Completed']}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Cancelled Nominations:</span>
                        <span class="metric-value">{formatted_metrics['Cancelled Nominations']}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Completion Rate:</span>
                        <span class="metric-value {status_class}">{formatted_metrics['Percentage of Nominations Completed']}</span>
                    </div>
                </div>
                
                <div class="status-indicator {status_class}">
                    <strong>Status: {status_text}</strong>
                </div>
            </div>
        </div>
        
        <div class="nomination-notes">
            <h4>Notes:</h4>
            <ul>
                <li><strong>Completed Nominations:</strong> Nominations that have reached "Finalized on Payroll" status</li>
                <li><strong>Cancelled Nominations:</strong> Nominations that were cancelled during the process</li>
                <li><strong>Completion Rate:</strong> Percentage of total nominations that were successfully completed</li>
            </ul>
        </div>
    </div>
    
    <style>
    .nomination-section {{
        margin: 20px 0;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }}
    
    .nomination-card {{
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 15px 0;
    }}
    
    .metric-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
    }}
    
    .metric-label {{
        font-weight: bold;
        color: #495057;
    }}
    
    .metric-value {{
        font-size: 1.1em;
        font-weight: bold;
    }}
    
    .status-indicator {{
        text-align: center;
        padding: 10px;
        border-radius: 4px;
        margin-top: 15px;
    }}
    
    .status-excellent {{
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }}
    
    .status-good {{
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }}
    
    .status-fair {{
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }}
    
    .status-poor {{
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }}
    
    .nomination-notes {{
        margin-top: 15px;
        padding: 15px;
        background-color: #e9ecef;
        border-radius: 4px;
    }}
    
    .nomination-notes ul {{
        margin: 10px 0;
        padding-left: 20px;
    }}
    
    .nomination-notes li {{
        margin: 5px 0;
    }}
    </style>
    """
    
    return html

# Test function to verify data loading
def test_nomination_processing():
    """Test function to verify nomination data processing"""
    nominations_file = "nominations2026.csv"
    cancellations_file = "cancellations2026.csv"
    
    if os.path.exists(nominations_file) and os.path.exists(cancellations_file):
        school_metrics = load_nomination_data(nominations_file, cancellations_file)
        
        # Print sample results
        print(f"\nProcessed nomination data for {len(school_metrics)} schools")
        
        # Show top 5 schools by total nominations
        sorted_schools = sorted(school_metrics.items(), 
                              key=lambda x: x[1]['total_nominations'], 
                              reverse=True)[:5]
        
        print("\nTop 5 schools by total nominations (normalized location codes):")
        for school, metrics in sorted_schools:
            print(f"{school}: {metrics['total_nominations']} total, "
                  f"{metrics['completed_nominations']} completed "
                  f"({metrics['percentage_completed']:.1f}%), "
                  f"{metrics['cancelled_nominations']} cancelled")
        
        return school_metrics
    else:
        print("Nomination files not found for testing")
        return {}

if __name__ == "__main__":
    test_nomination_processing()