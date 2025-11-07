"""
NYC DOE School Report PDF Generator with Nomination Data

Creates professional PDF reports for individual schools combining:
- SubCentral fill rate data
- Nomination tracking data
- Individual job tracking for nominees
"""

import os
import time
import pandas as pd
from datetime import datetime

# Check if ReportLab is installed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.platypus.flowables import Flowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not found. Installing...")

def install_reportlab():
    """Install ReportLab if not available"""
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ ReportLab installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install ReportLab: {e}")
        return False

def create_custom_styles():
    """Create custom styles for the PDF reports"""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#004080'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#004080'),
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceBefore=10,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='CenterNormal',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='ItalicStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='AlertStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#d32f2f'),
        fontName='Helvetica-Bold'
    ))
    
    return styles

def draw_school_banner(canvas, doc, school_code, principal_name, superintendent_name, logo_path):
    """Draw banner on first page for school report"""
    if doc.page == 1:  # Only draw on first page
        # Save canvas state
        canvas.saveState()
        
        # Get page dimensions
        page_width, page_height = letter
        
        # Banner dimensions
        banner_height = 1.4 * inch
        
        # Draw blue background across full page width at top
        canvas.setFillColor(colors.HexColor('#004080'))
        canvas.rect(0, page_height - banner_height, page_width, banner_height, fill=1, stroke=0)
        
        # Add logo on the right side if available
        if logo_path and os.path.exists(logo_path):
            try:
                # Scale logo to fit banner height with some padding
                logo_height = banner_height * 0.5
                logo_width = logo_height * 3  # Assuming horizontal logo is roughly 3:1 ratio
                
                # Position logo on the right side with margin
                logo_x = page_width - 0.75*inch - logo_width
                logo_y = page_height - banner_height + (banner_height - logo_height) / 2
                
                canvas.drawImage(logo_path, logo_x, logo_y, 
                               width=logo_width, height=logo_height,
                               preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Add white text on the left side
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        
        # Position title text on the left side with margin
        text_x = 0.7 * inch
        
        # Main title
        canvas.drawString(text_x, page_height - banner_height + 90, "NYC Department of Education")
        
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(text_x, page_height - banner_height + 70, "Substitute Paraprofessional Report")
        
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawString(text_x, page_height - banner_height + 45, f"School: {school_code}")
        
        canvas.setFont('Helvetica', 12)
        if principal_name:
            canvas.drawString(text_x, page_height - banner_height + 25, f"Principal: {principal_name}")
        if superintendent_name:
            canvas.drawString(text_x, page_height - banner_height + 8, f"Superintendent: {superintendent_name}")
            
        # Restore canvas state
        canvas.restoreState()

def create_summary_table(data, title="Summary"):
    """Create a formatted summary table"""
    # Prepare data for table
    table_data = [['Metric', 'Value']]
    
    for key, value in data.items():
        if isinstance(value, (int, float)):
            if 'Pct' in key or 'Rate' in key or '%' in key or 'Percentage' in key:
                if value != 'N/A' and pd.notna(value):
                    formatted_value = f"{value:.1f}%"
                else:
                    formatted_value = "N/A"
            else:
                if value != 'N/A' and pd.notna(value):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = "N/A"
        else:
            formatted_value = str(value) if value != 'N/A' else "N/A"
        
        # Clean up key names
        clean_key = key.replace('_', ' ').title()
        table_data.append([clean_key, formatted_value])
    
    # Create table with repeating headers
    table = Table(table_data, colWidths=[3*inch, 2*inch], repeatRows=1)
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    return table

def create_data_table(df, title="Data Table"):
    """Create a formatted data table from DataFrame"""
    if df.empty:
        return Paragraph("No data available", getSampleStyleSheet()['Normal'])
    
    # Convert DataFrame to list of lists
    table_data = [list(df.columns)]
    
    for _, row in df.iterrows():
        formatted_row = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                formatted_row.append('')
            elif isinstance(value, (int, float)):
                if 'Pct' in col or '%' in col or 'Rate' in col or 'Percentage' in col:
                    formatted_row.append(f"{value:.1f}%")
                else:
                    formatted_row.append(f"{value:,}")
            else:
                formatted_row.append(str(value)[:35])  # Truncate long strings
        table_data.append(formatted_row)
    
    # Calculate column widths
    num_cols = len(df.columns)
    available_width = 6.5 * inch
    
    # Adjust column widths based on content
    if num_cols <= 4:
        col_width = available_width / num_cols
        col_widths = [col_width] * num_cols
    else:
        # For many columns, make some wider/narrower based on content
        col_widths = []
        for col in df.columns:
            if 'Name' in col or 'Location' in col or 'Classification' in col:
                col_widths.append(available_width * 0.3)  # Wider for names
            elif 'Pct' in col or '%' in col:
                col_widths.append(available_width * 0.12)  # Narrower for percentages
            elif 'Date' in col:
                col_widths.append(available_width * 0.15)  # Medium for dates
            else:
                col_widths.append(available_width * 0.15)  # Medium for numbers
        
        # Normalize to fit available width
        total_width = sum(col_widths)
        col_widths = [w * available_width / total_width for w in col_widths]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    return table

def load_nomination_data():
    """Load and process nomination data from CSV files"""
    try:
        # Try to load nomination data
        spa_data = pd.read_csv('spa_nominations.csv') if os.path.exists('spa_nominations.csv') else pd.DataFrame()
        ste_data = pd.read_csv('ste_nominations.csv') if os.path.exists('ste_nominations.csv') else pd.DataFrame()
        
        # Try to load TSN data
        spa_tsn = pd.read_csv('spa_tsn.csv') if os.path.exists('spa_tsn.csv') else pd.DataFrame()
        ste_tsn = pd.read_csv('ste_tsn.csv') if os.path.exists('ste_tsn.csv') else pd.DataFrame()
        
        # Try to load AREPP data
        arepp_data = pd.read_csv('arepp_nominations.csv') if os.path.exists('arepp_nominations.csv') else pd.DataFrame()
        
        return {
            'spa_nominations': spa_data,
            'ste_nominations': ste_data,
            'spa_tsn': spa_tsn,
            'ste_tsn': ste_tsn,
            'arepp_nominations': arepp_data
        }
    except Exception as e:
        print(f"⚠️ Warning: Could not load nomination data: {e}")
        return {
            'spa_nominations': pd.DataFrame(),
            'ste_nominations': pd.DataFrame(),
            'spa_tsn': pd.DataFrame(),
            'ste_tsn': pd.DataFrame(),
            'arepp_nominations': pd.DataFrame()
        }

def get_school_nomination_data(school_code, nomination_data):
    """Extract nomination data for a specific school"""
    school_nominations = {}
    
    # Check SPA nominations
    if not nomination_data['spa_nominations'].empty:
        spa_school = nomination_data['spa_nominations'][
            nomination_data['spa_nominations']['Nominating Location'] == school_code
        ]
        school_nominations['spa'] = spa_school
    else:
        school_nominations['spa'] = pd.DataFrame()
    
    # Check STE nominations  
    if not nomination_data['ste_nominations'].empty:
        ste_school = nomination_data['ste_nominations'][
            nomination_data['ste_nominations']['Nominating Location'] == school_code
        ]
        school_nominations['ste'] = ste_school
    else:
        school_nominations['ste'] = pd.DataFrame()
    
    # Check AREPP nominations
    if not nomination_data['arepp_nominations'].empty:
        arepp_school = nomination_data['arepp_nominations'][
            nomination_data['arepp_nominations']['Location'] == school_code
        ]
        school_nominations['arepp'] = arepp_school
    else:
        school_nominations['arepp'] = pd.DataFrame()
    
    return school_nominations

def create_nomination_summary(school_nominations):
    """Create nomination summary statistics"""
    summary = {
        'SPA Nominations': len(school_nominations.get('spa', pd.DataFrame())),
        'STE Nominations': len(school_nominations.get('ste', pd.DataFrame())),
        'AREPP Nominations': len(school_nominations.get('arepp', pd.DataFrame()))
    }
    
    # Calculate completion rates if status columns exist
    for nom_type, data in [('SPA', 'spa'), ('STE', 'ste'), ('AREPP', 'arepp')]:
        df = school_nominations.get(data, pd.DataFrame())
        if not df.empty:
            if 'Finalized on Payroll' in df.columns:
                completed = len(df[df['Finalized on Payroll'] == 'Y'])
                total = len(df)
                if total > 0:
                    summary[f'{nom_type} Completion Rate'] = (completed / total) * 100
            elif 'Status' in df.columns:
                completed = len(df[df['Status'] == 'Staffed'])
                total = len(df)
                if total > 0:
                    summary[f'{nom_type} Completion Rate'] = (completed / total) * 100
    
    return summary

def create_school_pdf_report(school_code, school_data, nomination_data, output_path, 
                           date_range_info="", principal_name="", superintendent_name=""):
    """Create a professional PDF report for a school with nomination data"""
    
    print(f"🔍 Creating PDF for School {school_code}")
    
    # Title Banner data
    logo_path = os.path.join(os.path.dirname(__file__), "Horizontal_logo_White_PublicSchools.png")
    
    # Create custom page template function
    def first_page(canvas, doc):
        draw_school_banner(canvas, doc, school_code, principal_name, superintendent_name, logo_path)
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=0.75*inch, leftMargin=0.75*inch,
                          topMargin=1.2*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    story = []
    styles = create_custom_styles()
    
    # Add spacing to account for banner
    story.append(Spacer(1, 80))
    
    # Date and range info
    date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    if date_range_info:
        date_text += f"<br/>{date_range_info}"
    
    date_para = Paragraph(date_text, styles['CenterNormal'])
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # School Overview Section
    story.append(Paragraph("School Performance Overview", styles['CustomHeading']))
    
    # SubCentral job data summary
    if not school_data.empty:
        school_row = school_data.iloc[0]  # Get first (should be only) row
        
        # Calculate key metrics
        total_jobs = school_row.get('Total_Jobs', 0)
        total_filled = school_row.get('Total_Filled', 0)
        fill_rate = (total_filled / max(total_jobs, 1)) * 100 if total_jobs > 0 else 0
        
        vacancy_jobs = school_row.get('Total_Vacancy', 0)
        vacancy_filled = school_row.get('Vacancy_Filled', 0)
        vacancy_rate = (vacancy_filled / max(vacancy_jobs, 1)) * 100 if vacancy_jobs > 0 else 0
        
        absence_jobs = school_row.get('Total_Absence', 0)
        absence_filled = school_row.get('Absence_Filled', 0)
        absence_rate = (absence_filled / max(absence_jobs, 1)) * 100 if absence_jobs > 0 else 0
        
        subcentral_summary = {
            'Total SubCentral Jobs': int(total_jobs),
            'Total Jobs Filled': int(total_filled),
            'Overall Fill Rate': fill_rate,
            'Vacancy Jobs': int(vacancy_jobs),
            'Vacancy Fill Rate': vacancy_rate,
            'Absence Jobs': int(absence_jobs),
            'Absence Fill Rate': absence_rate
        }
        
        subcentral_table = create_summary_table(subcentral_summary, "SubCentral Performance")
        story.append(subcentral_table)
        story.append(Spacer(1, 15))
        
        # Performance context
        if fill_rate >= 85:
            performance_text = f"This school has a <strong>strong</strong> fill rate of {fill_rate:.1f}%, indicating effective use of SubCentral."
        elif fill_rate >= 70:
            performance_text = f"This school has a <strong>moderate</strong> fill rate of {fill_rate:.1f}%, with room for improvement."
        else:
            performance_text = f"This school has a <strong>low</strong> fill rate of {fill_rate:.1f}%, requiring attention to improve SubCentral usage."
        
        story.append(Paragraph(performance_text, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Nomination Data Section
    story.append(Paragraph("Nomination Pipeline Analysis", styles['CustomHeading']))
    
    school_nominations = get_school_nomination_data(school_code, nomination_data)
    nomination_summary = create_nomination_summary(school_nominations)
    
    if any(v > 0 for v in nomination_summary.values() if isinstance(v, (int, float))):
        # Create nomination summary table
        nom_table = create_summary_table(nomination_summary, "Nomination Summary")
        story.append(nom_table)
        story.append(Spacer(1, 15))
        
        # Detailed nomination data
        for nom_type, key in [('Substitute Paraprofessionals (SPA)', 'spa'), 
                             ('Substitute Teachers (STE)', 'ste'),
                             ('AREPP Full-Time Paraprofessionals', 'arepp')]:
            
            nom_df = school_nominations.get(key, pd.DataFrame())
            if not nom_df.empty:
                story.append(Paragraph(f"{nom_type} Details", styles['CustomSubheading']))
                
                # Select relevant columns for display
                display_cols = []
                if 'First Name' in nom_df.columns:
                    display_cols.append('First Name')
                if 'Last Name' in nom_df.columns:
                    display_cols.append('Last Name')
                if 'File Number' in nom_df.columns:
                    display_cols.append('File Number')
                elif 'File No' in nom_df.columns:
                    display_cols.append('File No')
                if 'Finalized on Payroll' in nom_df.columns:
                    display_cols.append('Finalized on Payroll')
                elif 'Status' in nom_df.columns:
                    display_cols.append('Status')
                
                if display_cols:
                    display_df = nom_df[display_cols].head(10)  # Limit to first 10 rows
                    nom_detail_table = create_data_table(display_df, f"{nom_type} Details")
                    story.append(nom_detail_table)
                    
                    if len(nom_df) > 10:
                        story.append(Paragraph(f"<i>Showing first 10 of {len(nom_df)} nominations</i>", 
                                             styles['ItalicStyle']))
                    story.append(Spacer(1, 10))
        
        story.append(PageBreak())
    else:
        story.append(Paragraph("No nomination data available for this school.", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Job Classification Analysis
    story.append(Paragraph("Job Classification Breakdown", styles['CustomHeading']))
    story.append(Paragraph("SubCentral job data by classification type", styles['ItalicStyle']))
    story.append(Spacer(1, 10))
    
    if not school_data.empty:
        # Create classification breakdown (this would need to be enhanced based on available data)
        class_data = []
        school_row = school_data.iloc[0]
        
        # For now, show main paraprofessional data - this can be expanded
        class_data.append({
            'Classification': 'Paraprofessional',
            'Total Jobs': int(school_row.get('Total_Jobs', 0)),
            'Jobs Filled': int(school_row.get('Total_Filled', 0)),
            'Fill Rate %': (school_row.get('Total_Filled', 0) / max(school_row.get('Total_Jobs', 1), 1)) * 100
        })
        
        class_df = pd.DataFrame(class_data)
        class_table = create_data_table(class_df, "Classification Analysis")
        story.append(class_table)
        story.append(Spacer(1, 20))
    
    # Recommendations Section
    story.append(Paragraph("Recommendations", styles['CustomHeading']))
    
    recommendations = []
    
    # SubCentral recommendations
    if not school_data.empty:
        school_row = school_data.iloc[0]
        fill_rate = (school_row.get('Total_Filled', 0) / max(school_row.get('Total_Jobs', 1), 1)) * 100
        
        if fill_rate < 70:
            recommendations.append("• Improve SubCentral usage by posting jobs earlier and requesting assistance with hard-to-fill positions")
        
        absence_rate = (school_row.get('Absence_Filled', 0) / max(school_row.get('Total_Absence', 1), 1)) * 100
        if absence_rate < 50:
            recommendations.append("• Consider converting daily absences to vacancy postings for better fill rates")
    
    # Nomination recommendations
    total_nominations = sum(v for v in nomination_summary.values() if isinstance(v, int))
    if total_nominations == 0:
        recommendations.append("• Consider participating in substitute paraprofessional nomination programs to build candidate pipeline")
    elif total_nominations > 0:
        completed_nominations = sum(1 for k, v in nomination_summary.items() 
                                  if 'Completion Rate' in k and isinstance(v, (int, float)) and v < 80)
        if completed_nominations > 0:
            recommendations.append("• Follow up on pending nominations to improve completion rates")
    
    if not recommendations:
        recommendations.append("• Continue current practices - performance metrics are meeting expectations")
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Footer
    footer_text = Paragraph("NYC Department of Education - SubCentral System & HR School Support<br/>For questions: SubCentral@schools.nyc.gov",
                           styles['CenterNormal'])
    story.append(footer_text)
    
    # Build PDF
    doc.build(story, onFirstPage=first_page)
    print(f"✅ Successfully created PDF for School {school_code}")
    return output_path

def main_school_reports():
    """Main function to generate school PDF reports with nomination data"""
    
    # Check if ReportLab is available
    if not REPORTLAB_AVAILABLE:
        if not install_reportlab():
            return
        # Re-import after installation
        global colors, letter, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        global getSampleStyleSheet, ParagraphStyle, inch, canvas, TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    
    try:
        from data_processing import load_and_process_data, create_summary_stats, get_data_date_range
    except ImportError as e:
        print(f"❌ Error importing data processing modules: {e}")
        print("Make sure data_processing.py is in the same directory")
        return
    
    # Configuration
    csv_files = [
        'Fill Rate Data/mayjobs.csv',
        'Fill Rate Data/junejobs.csv', 
        'Fill Rate Data/apriljobs.csv',
        'Fill Rate Data/febmarchjobs.csv',
        'Fill Rate Data/decjanjobs.csv',
        'Fill Rate Data/sepoctnovjobs.csv',
    ]
    
    output_directory = 'school_reports_with_nominations'
    os.makedirs(output_directory, exist_ok=True)
    
    start_time = time.time()
    print("Loading data for School PDF generation with nominations...")
    
    try:
        # Load SubCentral data
        df, _ = load_and_process_data(csv_files)
        
        if df.empty:
            print("❌ No SubCentral data loaded! Check your CSV files.")
            return
        
        print(f"✅ Loaded {len(df)} records from SubCentral data")
        
        # Load nomination data
        nomination_data = load_nomination_data()
        print(f"✅ Loaded nomination data:")
        for key, data in nomination_data.items():
            if not data.empty:
                print(f"  - {key}: {len(data)} records")
            else:
                print(f"  - {key}: No data available")
        
        # Get date range information
        date_range_info = get_data_date_range(df)
        print(f"Data range: {date_range_info}")
        
        # Create summary statistics by school
        summary_stats = create_summary_stats(df, ['Location'])
        if 'Type_Fill_Status' in summary_stats.columns:
            summary_stats = summary_stats.drop(columns=['Type_Fill_Status'])
        
        # Convert to int to avoid float display issues
        int_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Absence_Filled', 'Absence_Unfilled', 
                   'Total_Vacancy', 'Total_Absence', 'Total']
        for col in int_cols:
            if col in summary_stats.columns:
                summary_stats[col] = summary_stats[col].astype(int)
        
        # Add calculated totals
        summary_stats['Total_Jobs'] = summary_stats['Total_Vacancy'] + summary_stats['Total_Absence']
        summary_stats['Total_Filled'] = summary_stats['Vacancy_Filled'] + summary_stats['Absence_Filled']
        
        # Get unique schools - limit to first 10 for testing
        schools = sorted(df['Location'].unique())[:10]  # Remove [:10] to process all schools
        
        created_files = []
        failed_files = []
        
        print(f"Creating PDF reports for {len(schools)} schools...")
        
        for school_code in schools:
            school_data = summary_stats[summary_stats['Location'] == school_code].copy()
            
            if len(school_data) > 0:
                # Try to get principal and superintendent info from original data
                school_info = df[df['Location'] == school_code].iloc[0] if len(df[df['Location'] == school_code]) > 0 else None
                
                principal_name = ""
                superintendent_name = ""
                
                if school_info is not None:
                    principal_name = school_info.get('Principal', '') or ""
                    superintendent_name = school_info.get('Superintendent', '') or ""
                
                pdf_filename = f"School_{school_code}_Report.pdf"
                pdf_path = os.path.join(output_directory, pdf_filename)
                
                try:
                    create_school_pdf_report(
                        school_code, school_data, nomination_data, pdf_path,
                        date_range_info, principal_name, superintendent_name
                    )
                    created_files.append(pdf_path)
                    print(f"✅ Created: {pdf_filename}")
                except Exception as e:
                    failed_files.append((school_code, str(e)))
                    print(f"❌ Failed School {school_code}: {e}")
                    import traceback
                    traceback.print_exc()
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"SCHOOL PDF GENERATION WITH NOMINATIONS COMPLETED")
        print(f"{'='*60}")
        print(f"✅ Created {len(created_files)} PDF reports")
        if failed_files:
            print(f"❌ Failed: {len(failed_files)} reports")
            for school, error in failed_files:
                print(f"  - School {school}: {error}")
        print(f"📁 Output directory: {output_directory}")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find one or more CSV files")
        print("Please make sure all files exist in the specified paths.")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"❌ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_school_reports()