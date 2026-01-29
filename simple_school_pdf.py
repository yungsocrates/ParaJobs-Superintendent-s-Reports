"""
NYC DOE School Report PDF Generator
Creates professional PDF reports combining SubCentral and nomination data with NYC DOE styling
"""

import os
from datetime import datetime
import pandas as pd

def format_file_number(file_no):
    """
    Format file number as zero-padded 7-digit string
    """
    if pd.isna(file_no) or file_no == 'N/A' or file_no == '':
        return 'N/A'
    
    try:
        # Convert to int first to remove any decimal places
        file_no_int = int(float(str(file_no)))
        # Format as zero-padded 7-digit string
        return f"{file_no_int:07d}"
    except (ValueError, TypeError):
        return 'N/A'

def load_preferred_list_data(school_code, preferred_csv_path="preferred2026.csv"):
    """
    Load preferred list and DNU data for a specific school
    
    Args:
        school_code: Full school code (e.g., "01M034")
        preferred_csv_path: Path to the preferred2026.csv file
    
    Returns:
        dict: Contains 'preferred' and 'dnu' lists with substitute information
    """
    try:
        # Strip first two characters to get 4-character DBN (e.g., "01M034" -> "M034")
        location_code = school_code[2:] if len(school_code) > 4 else school_code
        
        # Load the preferred list CSV
        preferred_df = pd.read_csv(preferred_csv_path)
        
        # Filter for this school's location code
        school_data = preferred_df[preferred_df['LocationCode'] == location_code].copy()
        
        if school_data.empty:
            return {'preferred': [], 'dnu': []}
        
        preferred_list = []
        dnu_list = []
        
        for _, row in school_data.iterrows():
            # Format names with proper capitalization
            first_name = str(row.get('Substitutes First Name', 'N/A')).title() if pd.notna(row.get('Substitutes First Name')) else 'N/A'
            last_name = str(row.get('Substitutes Last Name', 'N/A')).title() if pd.notna(row.get('Substitutes Last Name')) else 'N/A'
            
            sub_info = {
                'file_no': format_file_number(row.get('Substitutes Access ID', 'N/A')),
                'first_name': first_name,
                'last_name': last_name,
                'list_type': row.get('List', 'N/A')
            }
            
            if row.get('List') == 'Preferred':
                preferred_list.append(sub_info)
            elif row.get('List') == 'Active Do Not Use':
                sub_info['reason'] = row.get('ReasonName', 'N/A')
                dnu_list.append(sub_info)
        
        return {
            'preferred': preferred_list,
            'dnu': dnu_list
        }
        
    except Exception as e:
        print(f"❌ Error loading preferred list data for {school_code}: {e}")
        return {'preferred': [], 'dnu': []}

def create_custom_styles():
    """Create custom NYC DOE styles for the PDF reports"""
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    styles = getSampleStyleSheet()
    
    # Custom styles with NYC DOE branding (SY 2025-26 Red Theme)
    styles.add(ParagraphStyle(
        name='NYCTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#CC0000"),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='NYCHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#CC0000'),
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='NYCSubheading',
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
    
    return styles

class BlueBanner:
    """Custom flowable for NYC DOE blue banner with white text"""
    
    def __init__(self, title_text, logo_path=None, width=None, height=None):
        from reportlab.platypus.flowables import Flowable
        from reportlab.lib.units import inch
        
        # Set default dimensions using inch after import
        if width is None:
            width = 8.5 * inch
        if height is None:
            height = 1.2 * inch
        
        class BannerFlowable(Flowable):
            def __init__(self, title_text, logo_path, width, height):
                self.title_text = title_text
                self.logo_path = logo_path
                self.width = width
                self.height = height
                
            def wrap(self, availWidth, availHeight):
                return (self.width, self.height)
                
            def draw(self):
                from reportlab.lib import colors
                
                # NYC DOE Red background (SY 2025-26) - draw rectangle extending to page edges
                self.canv.setFillColor(colors.HexColor('#CC0000'))
                self.canv.rect(-1*inch, 0, 9.5*inch, self.height, fill=1, stroke=0)
                
                # Add white text on the left side
                self.canv.setFillColor(colors.white)
                self.canv.setFont('Helvetica-Bold', 16)
                
                # Position title text on the left side with margin
                text_x = -0.75*inch + 0.7 * inch
                
                # Split title into lines and center vertically
                lines = self.title_text.split('<br/>')
                if len(lines) == 1:
                    lines = self.title_text.split('\n')
                
                line_height = 18
                total_text_height = len(lines) * line_height
                start_y = (self.height + total_text_height) / 2 - line_height
                
                for i, line in enumerate(lines):
                    y_pos = start_y - (i * line_height)
                    self.canv.drawString(text_x, y_pos, line.strip())
                
                # Add logo on the right side if available
                if self.logo_path and os.path.exists(self.logo_path):
                    try:
                        # Scale logo to fit banner height with some padding
                        logo_height = self.height * 0.6
                        logo_width = logo_height * 3  # Assuming horizontal logo is roughly 3:1 ratio
                        
                        # Position logo on the right side with margin
                        page_width = 8.5 * inch
                        logo_x = page_width - 0.75*inch - logo_width - 0.5*inch
                        logo_y = (self.height - logo_height) / 2
                        
                        self.canv.drawImage(self.logo_path, logo_x, logo_y, 
                                          width=logo_width, height=logo_height,
                                          preserveAspectRatio=True, mask='auto')
                    except:
                        # If logo fails, just show text
                        pass
        
        self.flowable = BannerFlowable(title_text, logo_path, width, height)
    
    def get_flowable(self):
        return self.flowable

def create_professional_table(data, title="Data Table", use_color_coding=False, match_col_index=None):
    """Create a professional table with NYC DOE styling"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    if not data or len(data) <= 1:
        return None
    
    # Calculate column widths based on content
    num_cols = len(data[0])
    available_width = 6.5 * inch
    
    if num_cols <= 3:
        col_width = available_width / num_cols
        col_widths = [col_width] * num_cols
    else:
        # Smart column width distribution
        col_widths = []
        headers = data[0]
        for i, header in enumerate(headers):
            if any(word in str(header) for word in ['School', 'Name', 'Location', 'Classification']):
                col_widths.append(available_width * 0.35)  # Wider for names
            elif any(word in str(header) for word in ['File', 'No', 'Number']):
                col_widths.append(available_width * 0.15)  # Medium for file numbers
            elif any(word in str(header) for word in ['%', 'Pct', 'Rate', 'Percentage']):
                col_widths.append(available_width * 0.12)  # Narrower for percentages
            else:
                col_widths.append(available_width * 0.18)  # Default for numbers
        
        # Normalize to fit available width
        total_width = sum(col_widths)
        col_widths = [w * available_width / total_width for w in col_widths]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Base professional styling
    table_style = [
        # Header row - NYC DOE Red (SY 2025-26)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CC0000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8e8e8')])
    ]
    
    # Add color coding for match percentages if requested
    if use_color_coding and match_col_index is not None:
        for row_idx in range(1, len(data)):  # Skip header
            try:
                match_value = float(data[row_idx][match_col_index].replace('%', ''))
                if match_value < 70:
                    # Red for poor performance
                    bg_color = colors.HexColor('#ffebee')
                    text_color = colors.HexColor('#c62828')
                elif match_value < 90:
                    # Orange for needs improvement
                    bg_color = colors.HexColor('#fff3e0')
                    text_color = colors.HexColor('#ef6c00')
                else:
                    # Green for meets benchmark
                    bg_color = colors.HexColor('#e8f5e8')
                    text_color = colors.HexColor('#2e7d32')
                
                table_style.append(('BACKGROUND', (match_col_index, row_idx), (match_col_index, row_idx), bg_color))
                table_style.append(('TEXTCOLOR', (match_col_index, row_idx), (match_col_index, row_idx), text_color))
                table_style.append(('FONTNAME', (match_col_index, row_idx), (match_col_index, row_idx), 'Helvetica-Bold'))
            except (ValueError, IndexError):
                continue
    
    table.setStyle(TableStyle(table_style))
    return table

def create_nominee_detail_table(data):
    """Create a specialized table for nominee details with proper column widths"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    if not data or len(data) <= 1:
        return None
    
    # Use same total width as other professional tables for consistency (6.5 inches)
    available_width = 6.5 * inch
    
    # Old column widths with SubCentral Days:
    # col_widths = [
    #     available_width * 0.18,  # First Name
    #     available_width * 0.18,  # Last Name  
    #     available_width * 0.15,  # File No
    #     available_width * 0.16,  # Payroll Days (This School)
    #     available_width * 0.17,  # Payroll Days (Other Schools)
    #     available_width * 0.16   # SubCentral Days
    # ]
    
    # New column widths without SubCentral Days (5 columns):
    col_widths = [
        available_width * 0.22,  # First Name (wider)
        available_width * 0.22,  # Last Name (wider)
        available_width * 0.18,  # File No (wider)
        available_width * 0.19,  # Payroll Days (This School) (wider)
        available_width * 0.19   # Payroll Days (Other Schools) (wider)
    ]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Professional styling for nominee details
    table_style = [
        # Header row - NYC DOE Red (SY 2025-26)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CC0000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Standardized header font size
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8e8e8')])  # Consistent alternating colors
    ]
    
    table.setStyle(TableStyle(table_style))
    return table

def create_dnu_table(data):
    """Create a table specifically for DNU (Do Not Use) substitutes with optimized column widths"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    if not data or len(data) <= 1:
        return None
    
    # Custom column widths for DNU table: File No, First Name, Last Name, Reason
    # Make first/last name smaller and reason column much larger
    available_width = 6.5 * inch  # Same as other tables for consistency
    col_widths = [
        available_width * 0.15,   # File No - narrow 
        available_width * 0.18,   # First Name - smaller than default
        available_width * 0.18,   # Last Name - smaller than default  
        available_width * 0.49    # Reason - much larger for detailed reasons
    ]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    table_style = [
        # Header styling - NYC DOE Red (SY 2025-26)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CC0000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data row styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (2, -1), 'CENTER'),  # Center File No, First Name, Last Name
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Left-align Reason column for better readability
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8e8e8')])
    ]
    
    table.setStyle(TableStyle(table_style))
    return table

def create_school_info_table(data):
    """Create a school information table with merged header cells"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    if not data or len(data) <= 1:
        return None
    
    # Use same total width as other professional tables for consistency
    available_width = 6.5 * inch
    col_widths = [
        available_width * 0.5,   # Label column - equal size
        available_width * 0.5    # Value column - equal size
    ]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Professional styling with merged header cell
    table_style = [
        # Merged header row - spans both columns
        ('SPAN', (0, 0), (1, 0)),  # Merge first row across both columns
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#CC0000')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),  # Standardized header font size
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # Center the merged header
        
        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),  # Standardized data font size
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # Center all content in data rows
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        # Alternating row colors for data rows (skip header)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8e8e8')])
    ]
    
    table.setStyle(TableStyle(table_style))
    return table

def create_simple_school_pdf(school_code, school_data, nomination_data, output_path, 
                           principal_name="", superintendent_name="", payroll_data=None, date_ranges=None):
    """
    Create a professional school PDF report with NYC DOE styling
    """
    
    try:
        # Try to use ReportLab for proper PDF creation
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create the PDF document with normal margins like district reports
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=0.75*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get NYC DOE styles
        styles = create_custom_styles()
        
        # Define banner info for first page template
        logo_path = os.path.join(os.path.dirname(__file__), "Horizontal_logo_White_PublicSchools.png")
        # Define banner info for first page template
        # Format date ranges for display
        date_range_text = "September 2025 - Present"  # Default
        if date_ranges:
            if isinstance(date_ranges, dict):
                # Extract date ranges from different data sources
                ranges = []
                if date_ranges.get('payroll_range'):
                    ranges.append(f"Payroll: {date_ranges['payroll_range']}")
                if date_ranges.get('nomination_range'):
                    ranges.append(f"Nominations: {date_ranges['nomination_range']}")
                if ranges:
                    date_range_text = " | ".join(ranges)
            elif isinstance(date_ranges, str):
                date_range_text = date_ranges
        
        banner_text = f"Office of HR School Support\nSubstitute Paraprofessional Report\nSchool: {school_code}\nReport Data From: {date_range_text}"
        
        # Custom page template function for first page with banner at top edge
        def first_page_template(canvas, doc):
            """Draw banner at the very top edge of the first page only"""
            # This function is called for the first page only due to onFirstPage parameter
            canvas.saveState()
            
            # Get page dimensions
            page_width, page_height = letter
            
            # Banner dimensions - positioned at very top of page (increased height for extra line)
            banner_height = 1.4 * inch
            
            # Draw red background (SY 2025-26) across full page width at top edge
            canvas.setFillColor(colors.HexColor('#CC0000'))
            canvas.rect(0, page_height - banner_height, page_width, banner_height, fill=1, stroke=0)
            
            # Add white text on the left side
            canvas.setFillColor(colors.white)
            canvas.setFont('Helvetica-Bold', 16)
            
            # Position title text on the left side with margin
            text_x = 0.7 * inch
            
            # Split title into lines and center vertically
            lines = banner_text.split('\n')
            line_height = 18
            total_text_height = len(lines) * line_height
            start_y = page_height - banner_height + (banner_height + total_text_height) / 2 - line_height
            
            for i, line in enumerate(lines):
                y_pos = start_y - (i * line_height)
                canvas.drawString(text_x, y_pos, line.strip())
            
            # Add logo on the right side if available
            if logo_path and os.path.exists(logo_path):
                try:
                    # Scale logo to fit banner height with some padding
                    logo_height = banner_height * 0.6
                    logo_width = logo_height * 3  # Assuming horizontal logo is roughly 3:1 ratio
                    
                    # Position logo on the right side with margin
                    logo_x = page_width - 0.75*inch - logo_width
                    logo_y = page_height - banner_height + (banner_height - logo_height) / 2
                    
                    canvas.drawImage(logo_path, logo_x, logo_y, 
                                   width=logo_width, height=logo_height,
                                   preserveAspectRatio=True, mask='auto')
                except:
                    pass  # If logo fails, just show text
                    
            canvas.restoreState()
        
        # Add spacing to account for banner at top of first page
        elements.append(Spacer(1, 80))  # Space for larger banner area on first page
        
        # Old date and school information section (now moved to banner):
        # date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        # date_para = Paragraph(date_text, styles['CenterNormal'])
        # elements.append(date_para)
        # 
        # # Add data date ranges
        # data_ranges_text = "Report Data From: September 2024 - June 2025"
        # data_ranges_para = Paragraph(data_ranges_text, styles['CenterNormal'])
        # elements.append(data_ranges_para)
        # elements.append(Spacer(1, 10))
        
        # Note: Date range now appears in banner for better visibility
        
        # School Information Table
        school_info_data = [
            ['School Information', ''],
            ['School Code:', school_code],
            ['Principal:', principal_name or 'Not Available'],
            ['Superintendent:', superintendent_name or 'Not Available']
        ]
        
        school_info_table = create_school_info_table(school_info_data)
        if school_info_table:
            elements.append(school_info_table)
        elements.append(Spacer(1, 20))
        
        # SubCentral vs Payroll Match Analysis (at top for visibility)
        elements.append(Paragraph("SubCentral vs Payroll Match Analysis", styles['NYCHeading']))
        
        # DEBUG: Print comprehensive payroll analysis
        print(f"  [PAYROLL DEBUG] School {school_code} payroll_data type: {type(payroll_data)}")
        print(f"  [PAYROLL DEBUG] School {school_code} payroll_data is None: {payroll_data is None}")
        print(f"  [PAYROLL DEBUG] School {school_code} payroll_data bool: {bool(payroll_data)}")
        
        if payroll_data:
            print(f"  [PAYROLL DEBUG] payroll_data keys: {list(payroll_data.keys()) if isinstance(payroll_data, dict) else 'not a dict'}")
            if isinstance(payroll_data, dict):
                print(f"  [PAYROLL DEBUG] Dictionary length: {len(payroll_data)}")
                for key, value in payroll_data.items():
                    print(f"  [PAYROLL DEBUG] {key}: {value} (type: {type(value)})")
                
                # Check specific fields used in condition
                payroll_job_days = payroll_data.get('payroll_job_days', 0)
                print(f"  [PAYROLL DEBUG] payroll_job_days value: {payroll_job_days} (type: {type(payroll_job_days)})")
                print(f"  [PAYROLL DEBUG] payroll_job_days > 0: {payroll_job_days > 0}")
        else:
            print(f"  [PAYROLL DEBUG] payroll_data is None or empty")
        
        # Check the condition step by step
        condition_check1 = payroll_data is not None
        condition_check2 = isinstance(payroll_data, dict) if condition_check1 else False
        condition_check3 = payroll_data.get('payroll_job_days', 0) > 0 if condition_check2 else False
        
        print(f"  [PAYROLL DEBUG] Condition checks - payroll_data not None: {condition_check1}, is dict: {condition_check2}, has job days > 0: {condition_check3}")
        
        if payroll_data and isinstance(payroll_data, dict) and payroll_data.get('payroll_job_days', 0) > 0:
            match_data = [
                ['Metric', 'Value'],
                ['SubCentral Filled Jobs', str(int(payroll_data.get('subcentral_filled_jobs', 0)))],
                ['Payroll Job Days', str(int(payroll_data.get('payroll_job_days', 0)))],
                ['Matched Jobs (Both Systems)', str(int(payroll_data.get('matched_jobs', 0)))],
                ['Match Percentage', f"{payroll_data.get('match_percentage', 0):.1f}%"]
            ]
            
            # Check if we need color coding for match percentage
            match_pct = payroll_data.get('match_percentage', 0)
            use_color_coding = True
            match_col_index = 1 if match_pct > 0 else None
            
            match_table = create_professional_table(match_data, "Match Analysis", 
                                                   use_color_coding=use_color_coding, 
                                                   match_col_index=4 if match_pct > 0 else None)
            if match_table:
                elements.append(match_table)
            
            # Add professional explanation
            elements.append(Spacer(1, 10))
            explanation = """
            <b>Analysis Explanation:</b><br/>
            • <b>SubCentral Filled Jobs:</b> Jobs recorded as filled in SubCentral system<br/>
            • <b>Payroll Job Days:</b> Actual work days recorded in payroll system<br/>
            • <b>Matched Jobs:</b> Work days appearing in both SubCentral and payroll systems<br/>
            • <b>Match Percentage:</b> Data consistency rate between systems (Target: ≥90%)
            """
            elements.append(Paragraph(explanation, styles['Normal']))
        else:
            print(f"  [PAYROLL DEBUG] No valid payroll data for {school_code} - showing 'no data available' message")
            elements.append(Paragraph("No payroll matching data available for this school", styles['ItalicStyle']))
        
        elements.append(Spacer(1, 25))
        
        # SubCentral Fill Rate Data Section
        elements.append(Paragraph("SubCentral Fill Rate Data", styles['NYCHeading']))
        elements.append(Paragraph("Data source: SubCentral System", styles['ItalicStyle']))
        elements.append(Spacer(1, 10))
        
        if not school_data.empty:
            # Create professional summary data
            row = school_data.iloc[0]
            total_jobs = row.get('Total_Jobs', 0)
            total_filled = row.get('Total_Filled', 0)
            fill_rate = row.get('Fill_Rate', 0)
            
            # Old version with single table and separator row:
            # summary_data = [
            #     ['Metric', 'Value'],
            #     ['Total Jobs', str(int(total_jobs))],
            #     ['Total Filled', str(int(total_filled))],
            #     ['Total Unfilled', str(int(row.get('Total_Unfilled', 0)))],
            #     ['Fill Rate', f"{fill_rate}%"],
            #     ['', ''],  # Separator row
            #     ['Vacancy Jobs', str(int(row.get('Total_Vacancy', 0)))],
            #     ['Vacancies Filled', str(int(row.get('Vacancy_Filled', 0)))],
            #     ['Absence Jobs', str(int(row.get('Total_Absence', 0)))],
            #     ['Absences Filled', str(int(row.get('Absence_Filled', 0)))]
            # ]
            # 
            # summary_table = create_professional_table(summary_data, "Fill Rate Summary")
            # if summary_table:
            #     elements.append(summary_table)
            
            # New version with two separate tables:
            
            # Table 1: Total Jobs Summary
            elements.append(Paragraph("Total Jobs", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            total_jobs_data = [
                ['Metric', 'Value'],
                ['Total Jobs', str(int(total_jobs))],
                ['Total Filled', str(int(total_filled))],
                ['Total Unfilled', str(int(row.get('Total_Unfilled', 0)))],
                ['Fill Rate', f"{fill_rate}%"]
            ]
            
            total_jobs_table = create_professional_table(total_jobs_data, "Total Jobs")
            if total_jobs_table:
                elements.append(total_jobs_table)
            
            elements.append(Spacer(1, 15))
            
            # Table 2: Vacancy and Absence Breakdown
            elements.append(Paragraph("Vacancy and Absence Breakdown", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            breakdown_data = [
                ['Job Type', 'Total Jobs', 'Filled', 'Unfilled'],
                ['Vacancy Jobs', 
                 str(int(row.get('Total_Vacancy', 0))), 
                 str(int(row.get('Vacancy_Filled', 0))),
                 str(int(row.get('Total_Vacancy', 0)) - int(row.get('Vacancy_Filled', 0)))],
                ['Absence Jobs', 
                 str(int(row.get('Total_Absence', 0))), 
                 str(int(row.get('Absence_Filled', 0))),
                 str(int(row.get('Total_Absence', 0)) - int(row.get('Absence_Filled', 0)))]
            ]
            
            breakdown_table = create_professional_table(breakdown_data, "Vacancy and Absence Breakdown")
            if breakdown_table:
                elements.append(breakdown_table)
            
            # Add vacancy vs absence analysis note
            analysis_note = """
            <b>Note:</b> Absences are historically harder to fill. Schools with a high number of unfilled absences should be encouraged to: either record the absences at their earliest opportunity OR create vacancies to offset the number of daily absences.
            """
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(analysis_note, styles['Normal']))
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("No SubCentral data available for this school", styles['ItalicStyle']))
            elements.append(Spacer(1, 20))
        
        # Nomination Data Section
        elements.append(Paragraph("Nomination Data", styles['NYCHeading']))
        elements.append(Paragraph("This section shows the metrics for substitute paraprofessional nominations for this school.", styles['Normal']))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("Data source: SHM New Hire Report/SHM Cancelled Nominations Report", styles['ItalicStyle']))
        elements.append(Spacer(1, 10))
        
        if nomination_data and nomination_data.get('summary'):
            summary = nomination_data['summary']
            
            # Fix the nomination logic: Total = Completed + Cancelled + In Progress
            completed = summary.get('completed_nominations', 0)
            cancelled = summary.get('cancelled_nominations', 0)
            
            # Count in-progress nominations directly from the data
            # In progress = rows where "Finalized on Payroll?" = "N"
            in_progress = 0
            if nomination_data.get('details'):
                for detail in nomination_data['details']:
                    finalized_status = detail.get('Finalized on Payroll?', '').strip().upper()
                    if finalized_status == 'N':
                        in_progress += 1
            
            actual_total = completed + cancelled + in_progress
            
            # Calculate correct completion rate: Completed / Total Nominations
            if actual_total > 0:
                completion_rate = (completed / actual_total) * 100
            else:
                completion_rate = 0
            
            nom_data = [
                ['Metric', 'Value'],
                ['Total Nominations', str(actual_total)],
                ['Completed Nominations', str(completed)],
                ['In Progress Nominations', str(in_progress)],
                ['Cancelled Nominations', str(cancelled)],
                ['Completion Rate', f"{completion_rate:.1f}%"]
            ]
            
            nom_table = create_professional_table(nom_data, "Nomination Summary")
            if nom_table:
                elements.append(nom_table)
            
            # Add notes explaining the metrics
            notes_text = """
            <b>Notes:</b><br/>
            • <b>Completed Nominations:</b> Nominations that have reached "Finalized on Payroll" status<br/>
            • <b>Cancelled Nominations:</b> Nominations that were cancelled during the process<br/>
            • <b>Completion Rate:</b> Percentage of total nominations that were successfully completed
            """
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(notes_text, styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Nominee Details with Professional Job Tracking - Only show finalized nominees
            finalized_nominees = []
            if nomination_data.get('details'):
                for detail in nomination_data['details']:
                    finalized_status = detail.get('Finalized on Payroll?', '').strip().upper()
                    if finalized_status == 'Y':
                        finalized_nominees.append(detail)
            
            if finalized_nominees and len(finalized_nominees) > 0:
                elements.append(Paragraph("Nominated Individuals - Job Tracking", styles['NYCSubheading']))
                elements.append(Paragraph("This section shows detailed job tracking for individuals who were nominated and finalized for this school.", styles['Normal']))
                elements.append(Spacer(1, 5))
                
                # Better formatted headers that fit in columns
                # Old version with SubCentral Days column:
                # detail_data = [['First Name', 'Last Name', 'File No', 'Payroll Days\n(This School)', 'Payroll Days\n(Other Schools)', 'SubCentral\nDays']]
                
                # New version without SubCentral Days column:
                detail_data = [['First Name', 'Last Name', 'File No', 'Payroll Days\n(This School)', 'Payroll Days\n(Other Schools)']]
                for detail in finalized_nominees[:10]:  # Show first 10 finalized nominees
                    # Format names with proper capitalization (like substitutes)
                    first_name_raw = detail.get('FirstName', detail.get('first_name', 'N/A'))
                    last_name_raw = detail.get('LastName', detail.get('last_name', 'N/A'))
                    
                    first_name = str(first_name_raw).title() if first_name_raw and str(first_name_raw) != 'N/A' else 'N/A'
                    last_name = str(last_name_raw).title() if last_name_raw and str(last_name_raw) != 'N/A' else 'N/A'
                    
                    file_no = detail.get('File No', detail.get('EMPLID', detail.get('file_no', 'N/A')))
                    
                    # These would be populated from actual payroll matching logic
                    payroll_this = detail.get('payroll_days_this_location', 0)
                    payroll_other = detail.get('payroll_days_other_locations', 0)
                    subcentral_days = detail.get('subcentral_job_days', 0)
                    
                    # Old version with SubCentral Days column:
                    # detail_data.append([
                    #     first_name,
                    #     last_name,
                    #     format_file_number(file_no),
                    #     str(payroll_this),
                    #     str(payroll_other),
                    #     str(subcentral_days)
                    # ])
                    
                    # New version without SubCentral Days column:
                    detail_data.append([
                        first_name,
                        last_name,
                        format_file_number(file_no),
                        str(payroll_this),
                        str(payroll_other)
                    ])
                
                # Create custom table with specific column widths for nominee details
                detail_table = create_nominee_detail_table(detail_data)
                if detail_table:
                    elements.append(detail_table)
                
                # Add column definitions
                # Old version with SubCentral Days definition:
                # column_defs_text = """
                # <b>Column Definitions:</b><br/>
                # • <b>Payroll Days at This Location:</b> Number of days this person worked at this school according to payroll records<br/>
                # • <b>Payroll Days at Other Locations:</b> Number of days this person worked at other schools according to payroll records<br/>
                # • <b>SubCentral Job Days:</b> Total number of job days this person was assigned in SubCentral system
                # """
                
                # New version without SubCentral Days definition:
                column_defs_text = """
                <b>Column Definitions:</b><br/>
                • <b>Payroll Days at This Location:</b> Number of days this person worked at this school according to payroll records<br/>
                • <b>Payroll Days at Other Locations:</b> Number of days this person worked at other schools according to payroll records
                """
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(column_defs_text, styles['Normal']))
                
                if len(finalized_nominees) > 10:
                    elements.append(Spacer(1, 10))
                    elements.append(Paragraph(f"... and {len(finalized_nominees) - 10} more finalized nominees", styles['ItalicStyle']))
                    
        else:
            elements.append(Paragraph("No nomination data available for this school", styles['ItalicStyle']))
        
        # Preferred List and DNU Data Section
        elements.append(Paragraph("Substitute Lists", styles['NYCHeading']))
        elements.append(Paragraph("Data source: SubCentral Preferred/DNU Lists", styles['ItalicStyle']))
        elements.append(Spacer(1, 5))
        
        # Add overview explanation
        overview_text = 'The Priority List contains your school\'s "Preferred" and any "Do Not Use" Substitutes.'
        elements.append(Paragraph(overview_text, styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Load preferred list data
        preferred_data = load_preferred_list_data(school_code, 
                                                os.path.join(os.path.dirname(__file__), "preferred2026.csv"))
        
        # Preferred List Section
        if preferred_data['preferred']:
            elements.append(Paragraph("Preferred Substitutes", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            # Add explanation for Preferred Substitutes
            preferred_explanation = "These are substitutes who you nominated or you placed on your Priority List. They will be contacted before the general pool of substitutes."
            elements.append(Paragraph(preferred_explanation, styles['Normal']))
            elements.append(Spacer(1, 10))
            
            # Old version with full table:
            # preferred_table_data = [['File No', 'First Name', 'Last Name']]
            # for sub in preferred_data['preferred'][:15]:  # Show first 15
            #     preferred_table_data.append([
            #         str(sub.get('file_no', 'N/A')),
            #         str(sub.get('first_name', 'N/A')),
            #         str(sub.get('last_name', 'N/A'))
            #     ])
            # 
            # preferred_table = create_professional_table(preferred_table_data, "Preferred Substitutes")
            # if preferred_table:
            #     elements.append(preferred_table)
            # 
            # if len(preferred_data['preferred']) > 15:
            #     elements.append(Paragraph(f"... and {len(preferred_data['preferred']) - 15} more preferred substitutes", styles['ItalicStyle']))
            
            # New version with just count:
            preferred_count = len(preferred_data['preferred'])
            elements.append(Paragraph(f"<b>Total Preferred Substitutes:</b> {preferred_count}", styles['Normal']))
            
            elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("Preferred Substitutes", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            # Add explanation for Preferred Substitutes (even when none exist)
            preferred_explanation = "These are substitutes who you nominated or you placed on your Priority List. They will be contacted before the general pool of substitutes."
            elements.append(Paragraph(preferred_explanation, styles['Normal']))
            elements.append(Spacer(1, 10))
            
            # Old version:
            # elements.append(Paragraph("No preferred substitutes listed for this school", styles['ItalicStyle']))
            
            # New version:
            elements.append(Paragraph("<b>Total Preferred Substitutes:</b> 0", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # DNU (Do Not Use) List Section
        if preferred_data['dnu']:
            elements.append(Paragraph("Do Not Use (DNU) Substitutes", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            # Add explanation for DNU Substitutes
            dnu_explanation = "These are substitutes flagged as not to be sent to your school. Typically, they are flagged based upon your school filing a Do Not Use form."
            elements.append(Paragraph(dnu_explanation, styles['Normal']))
            elements.append(Spacer(1, 10))
            
            dnu_table_data = [['File No', 'First Name', 'Last Name', 'Reason']]
            for sub in preferred_data['dnu'][:10]:  # Show first 10
                dnu_table_data.append([
                    str(sub.get('file_no', 'N/A')),
                    str(sub.get('first_name', 'N/A')),
                    str(sub.get('last_name', 'N/A')),
                    str(sub.get('reason', 'N/A'))
                ])
            
            dnu_table = create_dnu_table(dnu_table_data)
            if dnu_table:
                elements.append(dnu_table)
            
            if len(preferred_data['dnu']) > 10:
                elements.append(Paragraph(f"... and {len(preferred_data['dnu']) - 10} more DNU substitutes", styles['ItalicStyle']))
            
            elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("Do Not Use (DNU) Substitutes", styles['NYCSubheading']))
            elements.append(Spacer(1, 5))
            
            # Add explanation for DNU Substitutes (even when none exist)
            dnu_explanation = "These are substitutes flagged as not to be sent to your school. Typically, they are flagged based upon your school filing a Do Not Use form."
            elements.append(Paragraph(dnu_explanation, styles['Normal']))
            elements.append(Spacer(1, 10))
            
            elements.append(Paragraph("No DNU substitutes listed for this school", styles['ItalicStyle']))
            elements.append(Spacer(1, 10))
        
        # Professional Footer
        elements.append(Spacer(1, 30))
        footer_text = """
        <b>NYC Department of Education - Office of HR School Support</b><br/>
        For questions or support: SubCentral@schools.nyc.gov<br/>
        """
        elements.append(Paragraph(footer_text, styles['CenterNormal']))
        
        # Build PDF with first page template for banner
        doc.build(elements, onFirstPage=first_page_template)
        return True
        
    except ImportError:
        # Fallback to simple text file if ReportLab not available
        print(f"⚠️ ReportLab not available, creating text report instead")
        return create_text_report(school_code, school_data, nomination_data, output_path.replace('.pdf', '.txt'),
                                principal_name, superintendent_name)
    
    except Exception as e:
        print(f"❌ Error creating PDF for {school_code}: {e}")
        return False

def create_text_report(school_code, school_data, nomination_data, output_path,
                      principal_name="", superintendent_name=""):
    """
    Create a simple text report as fallback
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"SCHOOL REPORT CARD: {school_code}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"School Code: {school_code}\n")
            f.write(f"Principal: {principal_name or 'Not Available'}\n")
            f.write(f"Superintendent: {superintendent_name or 'Not Available'}\n")
            f.write(f"Report Date: {datetime.now().strftime('%B %d, %Y')}\n")
            f.write("Report Data From: September 2025 - Present\n")
            f.write("Nomination Data: Current as of report date\n\n")
            
            f.write("SUBCENTRAL FILL RATE DATA\n")
            f.write("-" * 30 + "\n")
            if not school_data.empty:
                row = school_data.iloc[0]
                f.write(f"Total Jobs: {row.get('Total_Jobs', 'N/A')}\n")
                f.write(f"Total Filled: {row.get('Total_Filled', 'N/A')}\n")
                f.write(f"Total Vacancies: {row.get('Total_Vacancy', 'N/A')}\n")
                f.write(f"Vacancies Filled: {row.get('Vacancy_Filled', 'N/A')}\n")
                f.write(f"Total Absences: {row.get('Total_Absence', 'N/A')}\n")
                f.write(f"Absences Filled: {row.get('Absence_Filled', 'N/A')}\n")
            else:
                f.write("No SubCentral data available\n")
            
            f.write("\nNOMINATION DATA\n")
            f.write("-" * 15 + "\n")
            if nomination_data and nomination_data.get('summary'):
                summary = nomination_data['summary']
                
                # Fix the nomination logic: Total = Completed + Cancelled
                completed = summary.get('completed_nominations', 0)
                cancelled = summary.get('cancelled_nominations', 0)
                actual_total = completed + cancelled
                
                # Calculate correct completion rate
                if actual_total > 0:
                    completion_rate = (completed / actual_total) * 100
                else:
                    completion_rate = 0
                
                f.write(f"Total Nominations: {actual_total}\n")
                f.write(f"Completed Nominations: {completed}\n")
                f.write(f"Cancelled Nominations: {cancelled}\n")
                f.write(f"Completion Rate: {completion_rate:.1f}%\n")
                
                if nomination_data.get('details'):
                    f.write(f"\nNominee Details ({len(nomination_data['details'])} total):\n")
                    for i, detail in enumerate(nomination_data['details'][:10], 1):
                        name = f"{detail.get('first_name', '')} {detail.get('last_name', '')}"
                        file_no = detail.get('File No', detail.get('EMPLID', detail.get('file_no', 'N/A')))
                        formatted_file_no = format_file_number(file_no)
                        f.write(f"{i}. {name} (File: {formatted_file_no})\n")
                    
                    if len(nomination_data['details']) > 10:
                        f.write(f"... and {len(nomination_data['details']) - 10} more\n")
            else:
                f.write("No nomination data available\n")
        
        # Preferred List and DNU Data Section
        f.write("\nSUBSTITUTE LISTS\n")
        f.write("-" * 20 + "\n")
        
        # Load preferred list data
        preferred_data = load_preferred_list_data(school_code, 
                                                os.path.join(os.path.dirname(__file__), "preferred2026.csv"))
        
        # Preferred List Section
        f.write("\nPreferred Substitutes:\n")
        if preferred_data['preferred']:
            f.write(f"Total Preferred: {len(preferred_data['preferred'])}\n")
            for i, sub in enumerate(preferred_data['preferred'][:15], 1):  # Show first 15
                name = f"{sub.get('first_name', '')} {sub.get('last_name', '')}"
                file_no = sub.get('file_no', 'N/A')
                f.write(f"{i}. {name} (File No: {file_no})\n")
            
            if len(preferred_data['preferred']) > 15:
                f.write(f"... and {len(preferred_data['preferred']) - 15} more\n")
        else:
            f.write("No preferred substitutes listed for this school\n")
        
        # DNU List Section
        f.write("\nDo Not Use (DNU) Substitutes:\n")
        if preferred_data['dnu']:
            f.write(f"Total DNU: {len(preferred_data['dnu'])}\n")
            for i, sub in enumerate(preferred_data['dnu'][:10], 1):  # Show first 10
                name = f"{sub.get('first_name', '')} {sub.get('last_name', '')}"
                file_no = sub.get('file_no', 'N/A')
                reason = sub.get('reason', 'N/A')
                f.write(f"{i}. {name} (File No: {file_no}) - Reason: {reason}\n")
            
            if len(preferred_data['dnu']) > 10:
                f.write(f"... and {len(preferred_data['dnu']) - 10} more\n")
        else:
            f.write("No DNU substitutes listed for this school\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating text report for {school_code}: {e}")
        return False

def install_reportlab():
    """
    Install ReportLab if not available
    """
    try:
        import subprocess
        import sys
        
        print("Installing ReportLab...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ ReportLab installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install ReportLab: {e}")
        return False

# Check if ReportLab is available
try:
    import reportlab
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False