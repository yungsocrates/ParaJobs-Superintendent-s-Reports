"""
Enhanced PDF Report Generator Integration

This module adds PDF generation capabilities to the existing para_fillrate_modular.py system
"""

import os
import sys
from datetime import datetime

def generate_enhanced_pdfs_with_nominations():
    """
    Generate PDF reports that combine:
    1. Existing SubCentral fill rate data
    2. Nomination tracker data  
    3. Individual job tracking for nominees
    4. Payroll matching analysis
    """
    
    try:
        # Import the school report generator
        from school_report_pdf_generator import (
            create_school_pdf_report, 
            load_nomination_data,
            get_school_nomination_data,
            create_nomination_summary,
            REPORTLAB_AVAILABLE,
            install_reportlab
        )
        
        # Import existing para fillrate modules
        from para_fillrate_modular import (
            load_and_merge_data,
            generate_fill_rate_analysis,
            create_payroll_matching_analysis
        )
        
    except ImportError as e:
        print(f"❌ Error importing required modules: {e}")
        print("Make sure all required files are in the same directory")
        return False
    
    # Check ReportLab availability
    if not REPORTLAB_AVAILABLE:
        print("Installing ReportLab...")
        if not install_reportlab():
            return False
    
    print("=== Enhanced PDF Report Generation with Nominations ===")
    
    # Load all data sources
    print("📊 Loading data sources...")
    
    # 1. Load SubCentral fill rate data
    try:
        subcentral_data = load_and_merge_data()
        if subcentral_data is None or subcentral_data.empty:
            print("❌ No SubCentral data available")
            return False
        print(f"✅ Loaded {len(subcentral_data)} SubCentral records")
    except Exception as e:
        print(f"❌ Error loading SubCentral data: {e}")
        return False
    
    # 2. Load nomination data
    nomination_data = load_nomination_data()
    print("✅ Loaded nomination data")
    
    # 3. Create payroll matching analysis
    try:
        matching_analysis = create_payroll_matching_analysis(subcentral_data)
        print(f"✅ Created payroll matching analysis")
    except Exception as e:
        print(f"⚠️ Could not create payroll matching: {e}")
        matching_analysis = None
    
    # Create output directory
    output_dir = f'enhanced_school_reports_{datetime.now().strftime("%Y%m%d_%H%M")}'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get unique schools from SubCentral data
    schools = sorted(subcentral_data['Location'].unique())
    
    print(f"🏫 Processing {len(schools)} schools...")
    
    created_reports = []
    failed_reports = []
    
    for i, school_code in enumerate(schools, 1):
        try:
            print(f"📄 ({i}/{len(schools)}) Generating report for {school_code}...")
            
            # Get school-specific data
            school_subcentral = subcentral_data[
                subcentral_data['Location'] == school_code
            ].copy()
            
            # Get school nominations
            school_nominations = get_school_nomination_data(school_code, nomination_data)
            
            # Get school matching data if available
            school_matching = None
            if matching_analysis is not None:
                school_matching_data = matching_analysis[
                    matching_analysis['Location'] == school_code
                ] if 'Location' in matching_analysis.columns else None
                school_matching = school_matching_data
            
            # Get additional school info
            principal_name = ""
            superintendent_name = ""
            
            if not school_subcentral.empty:
                school_row = school_subcentral.iloc[0]
                principal_name = school_row.get('Principal', '') or ""
                superintendent_name = school_row.get('Superintendent', '') or ""
            
            # Generate comprehensive PDF report
            pdf_filename = f"Enhanced_{school_code}_Report.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            create_enhanced_school_report(
                school_code=school_code,
                subcentral_data=school_subcentral,
                nomination_data=school_nominations,
                matching_data=school_matching,
                output_path=pdf_path,
                principal_name=principal_name,
                superintendent_name=superintendent_name
            )
            
            created_reports.append(pdf_path)
            
        except Exception as e:
            print(f"❌ Failed to create report for {school_code}: {e}")
            failed_reports.append((school_code, str(e)))
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print(f"ENHANCED PDF GENERATION COMPLETED")
    print(f"{'='*60}")
    print(f"✅ Successfully created: {len(created_reports)} reports")
    print(f"❌ Failed: {len(failed_reports)} reports")
    
    if failed_reports:
        print("\nFailed Reports:")
        for school, error in failed_reports[:5]:  # Show first 5 failures
            print(f"  - {school}: {error}")
        if len(failed_reports) > 5:
            print(f"  ... and {len(failed_reports) - 5} more")
    
    print(f"📁 Reports saved to: {output_dir}")
    
    return len(created_reports) > 0

def create_enhanced_school_report(school_code, subcentral_data, nomination_data, 
                                matching_data, output_path, principal_name="", 
                                superintendent_name=""):
    """
    Create an enhanced school report that combines all data sources
    """
    
    try:
        from school_report_pdf_generator import (
            create_school_pdf_report,
            create_nomination_summary
        )
    except ImportError:
        print("❌ Could not import PDF generator functions")
        return False
    
    # Convert subcentral_data to the format expected by create_school_pdf_report
    if not subcentral_data.empty:
        # Aggregate SubCentral data for this school
        school_summary = {
            'Total_Jobs': subcentral_data['Total'].sum() if 'Total' in subcentral_data.columns else 0,
            'Total_Filled': subcentral_data['Filled'].sum() if 'Filled' in subcentral_data.columns else 0,
            'Total_Vacancy': subcentral_data['Vacancy_Total'].sum() if 'Vacancy_Total' in subcentral_data.columns else 0,
            'Vacancy_Filled': subcentral_data['Vacancy_Filled'].sum() if 'Vacancy_Filled' in subcentral_data.columns else 0,
            'Total_Absence': subcentral_data['Absence_Total'].sum() if 'Absence_Total' in subcentral_data.columns else 0,
            'Absence_Filled': subcentral_data['Absence_Filled'].sum() if 'Absence_Filled' in subcentral_data.columns else 0,
        }
        
        # Convert to DataFrame format expected by the function
        import pandas as pd
        school_data_df = pd.DataFrame([school_summary])
    else:
        import pandas as pd
        school_data_df = pd.DataFrame()
    
    # Create the enhanced report
    result = create_school_pdf_report(
        school_code=school_code,
        school_data=school_data_df,
        nomination_data=nomination_data,
        output_path=output_path,
        date_range_info=f"Data as of {datetime.now().strftime('%B %Y')}",
        principal_name=principal_name,
        superintendent_name=superintendent_name
    )
    
    return result

def create_superintendent_reports_with_nominations():
    """
    Create superintendent-level reports that include nomination data
    """
    print("🏛️ Creating Superintendent Reports with Nomination Data...")
    
    try:
        from para_fillrate_modular import (
            load_and_merge_data,
            get_superintendent_data,
            create_payroll_matching_analysis
        )
        from school_report_pdf_generator import load_nomination_data
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        return False
    
    # Load data
    subcentral_data = load_and_merge_data()
    nomination_data = load_nomination_data()
    
    if subcentral_data is None or subcentral_data.empty:
        print("❌ No SubCentral data available")
        return False
    
    # Get unique superintendents
    superintendents = sorted(subcentral_data['Superintendent'].dropna().unique())
    
    output_dir = f'superintendent_reports_with_nominations_{datetime.now().strftime("%Y%m%d_%H%M")}'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"👥 Processing {len(superintendents)} superintendents...")
    
    created_reports = []
    
    for superintendent in superintendents:
        try:
            # Get superintendent's schools
            super_data = subcentral_data[
                subcentral_data['Superintendent'] == superintendent
            ].copy()
            
            schools_in_district = super_data['Location'].unique()
            
            # Aggregate nomination data for this superintendent's schools
            super_nominations = {
                'spa': [],
                'ste': [],  
                'arepp': []
            }
            
            for school in schools_in_district:
                school_noms = get_school_nomination_data(school, nomination_data)
                for nom_type in ['spa', 'ste', 'arepp']:
                    if not school_noms.get(nom_type, pd.DataFrame()).empty:
                        super_nominations[nom_type].append(school_noms[nom_type])
            
            # Combine nomination data
            import pandas as pd
            for nom_type in super_nominations:
                if super_nominations[nom_type]:
                    super_nominations[nom_type] = pd.concat(super_nominations[nom_type], ignore_index=True)
                else:
                    super_nominations[nom_type] = pd.DataFrame()
            
            # Create superintendent PDF report
            pdf_filename = f"Superintendent_{superintendent.replace(',', '').replace(' ', '_')}_Enhanced.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            create_superintendent_pdf_with_nominations(
                superintendent_name=superintendent,
                schools_data=super_data,
                nomination_data=super_nominations,
                output_path=pdf_path
            )
            
            created_reports.append(pdf_path)
            print(f"✅ Created: {pdf_filename}")
            
        except Exception as e:
            print(f"❌ Failed superintendent {superintendent}: {e}")
            continue
    
    print(f"✅ Created {len(created_reports)} superintendent reports")
    print(f"📁 Reports saved to: {output_dir}")
    
    return len(created_reports) > 0

def create_superintendent_pdf_with_nominations(superintendent_name, schools_data, 
                                             nomination_data, output_path):
    """
    Create a superintendent-level PDF report with nomination data
    This is a placeholder - full implementation would be similar to school reports
    but aggregated across multiple schools
    """
    
    # This would be implemented similar to create_school_pdf_report
    # but with superintendent-level aggregation
    
    print(f"📊 Creating superintendent report for {superintendent_name}")
    print(f"  - {len(schools_data['Location'].unique())} schools")
    print(f"  - SPA nominations: {len(nomination_data.get('spa', []))}")
    print(f"  - STE nominations: {len(nomination_data.get('ste', []))}")
    print(f"  - AREPP nominations: {len(nomination_data.get('arepp', []))}")
    
    # For now, create a simple placeholder file
    with open(output_path, 'w') as f:
        f.write(f"Superintendent Report for {superintendent_name} - Enhanced Version Coming Soon")
    
    return output_path

if __name__ == "__main__":
    print("Enhanced PDF Report Generator")
    print("Choose an option:")
    print("1. Generate School Reports with Nominations")
    print("2. Generate Superintendent Reports with Nominations") 
    print("3. Generate Both")
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        success = generate_enhanced_pdfs_with_nominations()
    elif choice == "2":
        success = create_superintendent_reports_with_nominations()
    elif choice == "3":
        success1 = generate_enhanced_pdfs_with_nominations()
        success2 = create_superintendent_reports_with_nominations()
        success = success1 or success2
    else:
        print("Invalid choice")
        success = False
    
    if success:
        print("🎉 PDF generation completed successfully!")
    else:
        print("❌ PDF generation failed")