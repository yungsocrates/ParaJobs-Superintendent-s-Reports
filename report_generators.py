"""
Report generation functions for NYC DOE Reports
"""

import os
import re
import numpy as np
from templates import (
    get_html_template, get_header_html, get_professional_footer,
    get_navigation_html, get_comparison_card_html, create_classification_tabbed_tables, create_school_tabbed_tables,
    create_district_tabbed_tables, create_borough_tabbed_tables,
    create_conditional_formatted_table
)
from chart_utils import (
    create_bar_chart, create_pie_charts_for_data, create_overall_bar_chart
)
from data_processing import (
    format_pct, format_int, create_summary_stats, calculate_fill_rates, get_totals_from_data, copy_logo_to_output
)

def create_school_report(district, location, location_clean, school_data, df, summary_stats, output_dir, date_range_info, matching_stats=None):
    """
    Create a comprehensive report for a single school
    """
    # Create subfolder for school if it doesn't exist
    school_dir = os.path.join(output_dir, f"District_{int(float(district))}", "Schools", f"School_{location_clean}")
    os.makedirs(school_dir, exist_ok=True)
    
    # Sanitize location name for files - more robust for Windows
    safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location_clean)).strip()
    safe_location_name = re.sub(r'_+', '_', safe_location_name).strip('_')
    safe_location_name = safe_location_name.replace('.', '_')
    if len(safe_location_name) > 200:
        safe_location_name = safe_location_name[:200].rstrip('._')
    
    # Create tabbed summary tables - use all required columns for school classification data
    # For school reports, the data should be aggregated by classification
    school_classification_data = school_data.groupby('Classification').agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    }).reset_index()
    
    # Return placeholder for now - this function needs full implementation
    return os.path.join(school_dir, f'{safe_location_name}_report.html')


def create_superintendent_school_report(superintendent, location, location_clean, school_data, df, summary_stats, superintendent_dir, date_range_info, matching_stats=None):
    """
    Create a comprehensive report for a single school under a superintendent
    """
    import pandas as pd
    import numpy as np
    
    # Create subfolder for school directly under the superintendent directory
    school_dir = os.path.join(superintendent_dir, "Schools", f"School_{location_clean}")
    os.makedirs(school_dir, exist_ok=True)
    
    # Sanitize location name for files - more robust for Windows
    safe_location_name = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location_clean)).strip()
    safe_location_name = re.sub(r'_+', '_', safe_location_name).strip('_')
    safe_location_name = safe_location_name.replace('.', '_')
    if len(safe_location_name) > 200:
        safe_location_name = safe_location_name[:200].rstrip('._')
    
    # Create tabbed summary tables - handle both Series and DataFrame input
    # For school reports, check what type of data we received
    if isinstance(school_data, pd.Series):
        # Convert Series to DataFrame and add Classification column
        school_classification_data = pd.DataFrame([school_data])
        school_classification_data['Classification'] = 'All Classifications'
    elif hasattr(school_data, 'columns') and 'Classification' in school_data.columns:
        # Data has Classification column, aggregate by it
        school_classification_data = school_data.groupby('Classification').agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
            'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        }).reset_index()
    else:
        # Data is already aggregated or missing Classification, create it
        if hasattr(school_data, 'to_frame'):
            # Series - convert to DataFrame
            school_classification_data = school_data.to_frame().T
        else:
            # Already a DataFrame
            school_classification_data = school_data.copy()
        school_classification_data['Classification'] = 'All Classifications'
    
    # Calculate percentages for the aggregated data
    school_classification_data['Vacancy_Fill_Pct'] = np.where(
        school_classification_data['Total_Vacancy'] > 0,
        (school_classification_data['Vacancy_Filled'] / school_classification_data['Total_Vacancy'] * 100).round(1), 0
    )
    school_classification_data['Absence_Fill_Pct'] = np.where(
        school_classification_data['Total_Absence'] > 0,
        (school_classification_data['Absence_Filled'] / school_classification_data['Total_Absence'] * 100).round(1), 0
    )
    school_classification_data['Total_Filled'] = school_classification_data['Vacancy_Filled'] + school_classification_data['Absence_Filled']
    school_classification_data['Total_Unfilled'] = school_classification_data['Vacancy_Unfilled'] + school_classification_data['Absence_Unfilled']
    school_classification_data['Overall_Fill_Pct'] = np.where(
        school_classification_data['Total'] > 0,
        ((school_classification_data['Vacancy_Filled'] + school_classification_data['Absence_Filled']) / school_classification_data['Total'] * 100).round(1), 0
    )
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_cols = [col for col in required_cols if col in school_classification_data.columns]
    
    # Sort by Total jobs descending (highest to lowest)
    school_classification_data = school_classification_data.sort_values('Total', ascending=False)
    
    # Create formatters for all the columns
    formatters = {}
    for col in existing_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str
    
    table_html = create_classification_tabbed_tables(school_classification_data[existing_cols], formatters)
    
    # Create bar chart with sorted data (highest to lowest total jobs)
    bar_chart_file = os.path.join(school_dir, f'{safe_location_name}_bar_chart.html')
    create_bar_chart(
        school_classification_data,  # Use sorted classification data instead of raw school_data
        f'Jobs by Classification and Type - {location}',
        bar_chart_file,
        f"{safe_location_name}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(school_data, location_clean, school_dir)
    
    # Get comparison data
    school_borough = df[df['Location'] == location]['Borough'].iloc[0]
    school_superintendent = df[df['Location'] == location]['Superintendent_Name'].iloc[0]
    safe_superintendent_name = school_superintendent.replace(',', '').replace(' ', '_').replace('.', '').replace("'", "")
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    borough_data = create_summary_stats(df[df['Borough'] == school_borough], ['Borough'])
    superintendent_data = create_summary_stats(df[df['Superintendent_Name'] == school_superintendent], ['Superintendent_Name'])
    
    borough_totals = get_totals_from_data(borough_data)
    superintendent_totals = get_totals_from_data(superintendent_data)
    school_totals = get_totals_from_data(school_data)
    
    # Calculate fill rates
    school_rates = calculate_fill_rates(school_totals)
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    superintendent_rates = calculate_fill_rates(superintendent_totals)
    
    # Calculate average match percentages from pre-calculated matching stats
    citywide_match_pct = 0
    borough_match_pct = 0
    district_match_pct = 0
    
    if matching_stats is not None and not matching_stats.empty:
        # Find match percentage column
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Calculate averages by filtering the pre-calculated data
            citywide_match_pct = matching_stats[match_col].mean()
            
            # Borough average
            borough_schools = df[df['Borough'] == school_borough]['Location'].unique()
            borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)]
            if not borough_matching.empty:
                borough_match_pct = borough_matching[match_col].mean()
            
            # Superintendent average
            superintendent_schools = df[df['Superintendent_Name'] == school_superintendent]['Location'].unique()
            superintendent_matching = matching_stats[matching_stats['Location'].isin(superintendent_schools)]
            if not superintendent_matching.empty:
                district_match_pct = superintendent_matching[match_col].mean()
    
    # Create comparison cards
    comparison_cards = []
    
    # Citywide card
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Total Vacancies": f"{overall_stats['Total_Vacancy']:,} ({(overall_stats['Total_Vacancy'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{overall_stats['Total_Absence']:,} ({(overall_stats['Total_Absence'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_match_pct:.1f}%" if citywide_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Total Vacancies": f"{borough_totals['Total_Vacancy']:,} ({(borough_totals['Total_Vacancy'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{borough_totals['Total_Absence']:,} ({(borough_totals['Total_Absence'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_match_pct:.1f}%" if borough_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == school_borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"{school_borough} Statistics", borough_stats, "borough"))
    
    # Superintendent card
    superintendent_stats = {
        "Total Jobs": f"{superintendent_totals['Total']:,}",
        "Total Vacancies": f"{superintendent_totals['Total_Vacancy']:,} ({(superintendent_totals['Total_Vacancy'] / superintendent_totals['Total'] * 100) if superintendent_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{superintendent_totals['Total_Absence']:,} ({(superintendent_totals['Total_Absence'] / superintendent_totals['Total'] * 100) if superintendent_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{superintendent_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{superintendent_rates[1]:.1f}%",
        "Absence Fill Rate": f"{superintendent_rates[2]:.1f}%",
        "Average Match %": f"{district_match_pct:.1f}%" if district_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df[df['Superintendent_Name'] == school_superintendent]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"Superintendent {school_superintendent}", superintendent_stats, "superintendent"))
    
    # School card
    school_stats = {
        "Total Jobs": f"{school_totals['Total']:,}",
        "Total Vacancies": f"{school_totals['Total_Vacancy']:,} ({(school_totals['Total_Vacancy'] / school_totals['Total'] * 100) if school_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{school_totals['Total_Absence']:,} ({(school_totals['Total_Absence'] / school_totals['Total'] * 100) if school_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{school_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{school_rates[1]:.1f}%",
        "Absence Fill Rate": f"{school_rates[2]:.1f}%",
        "Classifications": ", ".join(school_data['Classification'].unique())
    }
    comparison_cards.append(get_comparison_card_html(f"This School ({location})", school_stats, "school"))
    
    comparison_html = f'<div class="comparison-grid-four">{"".join(comparison_cards)}</div>'
    
    # Build content with new structure
    content = f"""
        {get_header_html("../../../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"School: {location} (Superintendent: {school_superintendent})", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([
                (f"../../{safe_superintendent_name}_report.html", f"← Back to Superintendent {school_superintendent}")
            ])}
            
            <div class="section">
                <h3>Comparison Statistics</h3>
                <p><em>This comparison shows how this school performs relative to schools under the same
                stuperintendent, the borough, and citywide averages.</em></p>
                {comparison_html}
            </div>
            
            <div class="section">
                <h3>Fill Rate Analysis by Classification</h3>
                <p><em><strong>Note:</strong> This data is based on SubCentral data only. Use the tabs below to switch
                between different views of the classification data. Data is sorted from highest to lowest number of
                total jobs.</em></p>
                {table_html}
            </div>

            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{safe_location_name}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h3>Breakdown by Classification</h3>
                <div class="pie-container">{pie_charts_html}</div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - {location}", "../../../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(school_dir, f'{safe_location_name}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file

def create_district_report(district, district_data, df, output_dir, summary_stats, date_range_info, matching_stats=None, school_stats=None):
    """
    Create a comprehensive report for a single District following the new structure:
    1. Comparison cards (Citywide vs Borough vs District)
    2. SubCentral vs Payroll Analysis
    3. Classification Information
    4. School Level Fill Rates
    """
    # Create subfolder for District
    district_dir = os.path.join(output_dir, f"District_{int(float(district))}")
    os.makedirs(district_dir, exist_ok=True)
    
    # Get the borough for this district with error handling
    district_schools = df[df['District'] == district]
    if district_schools.empty:
        print(f"Warning: No schools found for district {district}")
        return None, []
    
    district_borough = district_schools['Borough'].iloc[0]
    borough_name_clean = district_borough.replace(' ', '_').replace('/', '_')
    borough_data = create_summary_stats(df[df['Borough'] == district_borough], ['Borough'])
    
    # Get comparison data for Section 1
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    borough_totals = get_totals_from_data(borough_data)
    district_totals = get_totals_from_data(district_data)
    
    # Calculate fill rates
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    district_rates = calculate_fill_rates(district_totals)
    
    # Calculate average match percentage for each level
    citywide_match_pct = 0
    borough_match_pct = 0
    district_match_pct = 0
    
    if matching_stats is not None and not matching_stats.empty:
        # Calculate citywide average
        match_col = 'Match_Percentage'
        if match_col not in matching_stats.columns:
            for col in matching_stats.columns:
                if 'Match' in col and ('Percentage' in col or '%' in col):
                    match_col = col
                    break
        
        if match_col in matching_stats.columns:
            citywide_match_pct = matching_stats[match_col].mean()
            
            # Borough average
            borough_schools = df[df['Borough'] == district_borough]['Location'].unique()
            borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)]
            if not borough_matching.empty:
                borough_match_pct = borough_matching[match_col].mean()
            
            # District average
            district_school_list = df[df['District'] == district]['Location'].unique()
            district_matching = matching_stats[matching_stats['Location'].isin(district_school_list)]
            if not district_matching.empty:
                district_match_pct = district_matching[match_col].mean()
    
    # Section 1: Comparison Cards
    comparison_cards = []
    
    # Citywide card with match percentage
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%", 
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Districts": f"{len(df['District'].unique())}",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card with match percentage
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == district_borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"{district_borough} Statistics", borough_stats, "borough"))
    
    # District card with match percentage
    district_stats = {
        "Total Jobs": f"{district_totals['Total']:,}",
        "Overall Fill Rate": f"{district_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{district_rates[1]:.1f}%",
        "Absence Fill Rate": f"{district_rates[2]:.1f}%",
        "Average Match %": f"{district_match_pct:.1f}%" if matching_stats is not None and not matching_stats.empty else "N/A",
        "Number of Schools": f"{len(df[df['District'] == district]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This District ({int(float(district))})", district_stats, "district"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Section 2: SubCentral vs Payroll Analysis (simple table, no tabs)
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty and not district_matching.empty:
        # Sort by Match Percentage (lowest to highest)
        district_matching_sorted = district_matching.sort_values(match_col, ascending=True)
        
        # Rename Match_Percentage column for display (remove underscore)
        district_matching_display = district_matching_sorted.rename(columns={'Match_Percentage': 'Match Percentage'})
        
        # Create summary stats
        subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in district_matching.columns else 'SubCentral_Count'
        payroll_col = 'Payroll Job Days' if 'Payroll Job Days' in district_matching.columns else 'Payroll_Count'
        matched_col = None
        for col in district_matching.columns:
            if 'Matched' in col and 'Job' in col:
                matched_col = col
                break
        
        total_subcentral = district_matching[subcentral_col].sum() if subcentral_col in district_matching.columns else 0
        total_payroll = district_matching[payroll_col].sum() if payroll_col in district_matching.columns else 0
        total_matched = district_matching[matched_col].sum() if matched_col and matched_col in district_matching.columns else 0
        
        # Create formatters for matching table
        match_formatters = {
            col: format_pct if 'Match' in col and ('Percentage' in col or '%' in col) else format_int
            for col in district_matching_display.columns
        }
        
        payroll_analysis_html = f"""
        <div class="section">
            <h3>SubCentral vs Payroll Analysis</h3>
            <p><em>This analysis matches individual jobs using Location + EIS ID + Date between SubCentral and SREPP payroll systems.</em></p>
            
            <div class="summary-box">
                <h4>District Matching Summary</h4>
                <ul>
                    <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                    <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                    <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                    <li><strong>Average Match Rate:</strong> {district_match_pct:.1f}%</li>
                </ul>
            </div>
            
            <div class="table-responsive">
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify schools needing attention.</em></p>
                {create_conditional_formatted_table(district_matching_display, match_formatters, 'Match Percentage')}
            </div>
        </div>
        """
    
    # Section 3: Classification Information (sorted by total jobs - highest to lowest)
    district_data_sorted = district_data.sort_values('Total', ascending=False)
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    available_display_cols = [col for col in required_cols if col in district_data_sorted.columns]
    
    # Create formatters for all the columns
    formatters = {}
    for col in available_display_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str
    
    table_html = create_classification_tabbed_tables(district_data_sorted[available_display_cols], formatters, debug_district=True)
    
    # Create bar chart (use full data for chart)
    bar_chart_file = os.path.join(district_dir, f'{int(float(district))}_bar_chart.html')
    create_bar_chart(
        district_data_sorted,
        f'Jobs by Classification and Type - District {int(float(district))}',
        bar_chart_file,
        f"district_{int(float(district))}_bar_chart"
    )
    
    # Create pie charts (use full data for chart)
    pie_charts_html = create_pie_charts_for_data(district_data_sorted, f"District_{int(float(district))}", district_dir)
    
    # Generate school reports and create summary table
    df_district = df[df['District'] == district]
    
    # Use pre-calculated school stats if available, otherwise calculate
    if school_stats is not None:
        # Filter school stats for this district and aggregate by location
        district_schools_data = school_stats[school_stats['District'] == district]
        summary_by_school = district_schools_data.groupby('Location', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
    else:
        # Fallback: calculate school stats
        summary_by_school = create_summary_stats(df_district, ['Location'])
        summary_by_school = summary_by_school.groupby('Location', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
    
    # Calculate percentages for schools
    summary_by_school['Vacancy_Fill_Pct'] = (summary_by_school['Vacancy_Filled'] / summary_by_school['Total_Vacancy'] * 100).fillna(0).round(1)
    summary_by_school['Absence_Fill_Pct'] = (summary_by_school['Absence_Filled'] / summary_by_school['Total_Absence'] * 100).fillna(0).round(1)
    
    # Calculate combined totals for schools
    summary_by_school['Total_Filled'] = summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']
    summary_by_school['Total_Unfilled'] = summary_by_school['Vacancy_Unfilled'] + summary_by_school['Absence_Unfilled']
    
    summary_by_school['Overall_Fill_Pct'] = ((summary_by_school['Vacancy_Filled'] + summary_by_school['Absence_Filled']) / summary_by_school['Total'] * 100).fillna(0).round(1)
    
    # Generate school reports and links
    district_schools = df[df['District'] == district]['Location'].unique()
    school_links = ""
    school_reports = []
    
    for location in sorted(district_schools):
        # More robust sanitization for Windows filenames
        location_clean = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location)).strip()
        location_clean = re.sub(r'_+', '_', location_clean).strip('_')
        location_clean = location_clean.replace('.', '_')
        if len(location_clean) > 200:
            location_clean = location_clean[:200].rstrip('._')
        
        school_df = df[(df['District'] == district) & (df['Location'] == location)]
        school_summary = create_summary_stats(school_df, ['District', 'Location'])
        
        if len(school_summary) > 0:
            school_report = create_school_report(
                district, location, location_clean, school_summary, 
                df, summary_stats, output_dir, date_range_info, matching_stats
            )
            school_reports.append(school_report)
            
            total_jobs = int(school_summary['Total'].sum())
            school_links += f'<li><a href="Schools/School_{location_clean}/{location_clean}_report.html">{location}</a> - {total_jobs:,} total jobs</li>\n'
    
    # Create school summary table HTML using tabbed interface
    school_formatters = {
        'School': str,
        'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
        'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
        'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total Filled': format_int, 
        'Total Unfilled': format_int, 'Total': format_int, 'Overall Fill %': format_pct
    }
    summary_by_school_html = create_school_tabbed_tables(
        summary_by_school.rename(columns={'Location': 'School'}), 
        school_formatters
    )
    
    # Build content with new structure
    content = f"""
        {get_header_html("../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"District: {int(float(district))}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([
                ("../index.html", "← Back to Overall Summary"),
                (f"../Borough_{borough_name_clean}/{borough_name_clean}_report.html", f"← Back to {district_borough} Report")
            ])}
            
            <div class="section">
                <h3>District Overview: Comparison</h3>
                {comparison_html}
            </div>

            {payroll_analysis_html}

            <div class="section">
                <h3>Classification Information</h3>
                <p><em><strong>Note:</strong> Use the tabs below to switch between different views of the data. Data sorted by highest to lowest total jobs.</em></p>
                {table_html}
            </div>

            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{int(float(district))}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h3>Breakdown by Classification</h3>
                <div class="pie-container">{pie_charts_html}</div>
            </div>
            
            <div class="section">
                <h3>School Level Fill Rates</h3>
                <p><em><strong>Note:</strong> This data is based on SubCentral data only. Data is sorted from lowest to highest overall fill rate to identify schools needing attention. Use the tabs below to switch between different views. Click on school codes for detailed reports.</em></p>
                {summary_by_school_html}
                
                <h4>Individual School Reports</h4>
                <div class="district-links"><ul>{school_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - District {int(float(district))}", "../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(district_dir, f'{int(float(district))}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports


def create_superintendent_report(superintendent, superintendent_data, df, output_dir, summary_stats, date_range_info, matching_stats=None, school_stats=None):
    """
    Create a comprehensive report for a single Superintendent following the same structure as district reports
    """
    # Create subfolder for Superintendent (safe filename)
    safe_superintendent_name = superintendent.replace(',', '').replace(' ', '_').replace('.', '').replace("'", "")
    superintendent_dir = os.path.join(output_dir, f"Superintendent_{safe_superintendent_name}")
    os.makedirs(superintendent_dir, exist_ok=True)
    
    # Copy logo to superintendent directory
    copy_logo_to_output(superintendent_dir)
    
    # Get the schools for this superintendent
    superintendent_schools = df[df['Superintendent_Name'] == superintendent]
    if superintendent_schools.empty:
        print(f"Warning: No schools found for superintendent {superintendent}")
        return None, []
    
    # Get the most common borough for this superintendent
    superintendent_borough = superintendent_schools['Borough'].mode().iloc[0] if not superintendent_schools['Borough'].empty else 'Unknown'
    
    # Get comparison data - similar to district report
    overall_totals = summary_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    
    # Calculate comparison statistics
    citywide_rates = calculate_fill_rates(overall_stats)
    superintendent_totals = get_totals_from_data(superintendent_data)
    superintendent_rates = calculate_fill_rates(superintendent_totals)
    
    # Create main content using templates (similar to district approach)
    header_html = get_header_html(f"Superintendent Report: {superintendent}", date_range_info)
    
    # Create comparison cards for citywide vs borough vs superintendent
    # Get schools for this superintendent from the full dataframe
    superintendent_schools_list = df[df['Superintendent_Name'] == superintendent]['Location'].unique()
    
    # Calculate borough stats
    borough_data = create_summary_stats(df[df['Borough'] == superintendent_borough], ['Borough'])
    borough_totals = get_totals_from_data(borough_data)
    borough_rates = calculate_fill_rates(borough_totals)
    borough_schools_list = df[df['Borough'] == superintendent_borough]['Location'].unique()
    
    # Calculate match percentages for each level
    citywide_match_pct = 0
    borough_match_pct = 0
    superintendent_match_pct = 0
    
    if matching_stats is not None and not matching_stats.empty:
        # Find match percentage column
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Citywide average
            citywide_match_pct = matching_stats[match_col].mean()
            
            # Borough average
            borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools_list)]
            if not borough_matching.empty:
                borough_match_pct = borough_matching[match_col].mean()
            
            # Superintendent average
            superintendent_matching = matching_stats[matching_stats['Location'].isin(superintendent_schools_list)]
            if not superintendent_matching.empty:
                superintendent_match_pct = superintendent_matching[match_col].mean()
    
    comparison_cards = []
    
    # Citywide card
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Total Vacancies": f"{overall_stats['Total_Vacancy']:,} ({(overall_stats['Total_Vacancy'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{overall_stats['Total_Absence']:,} ({(overall_stats['Total_Absence'] / overall_stats['Total'] * 100) if overall_stats['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_match_pct:.1f}%" if citywide_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Total Vacancies": f"{borough_totals['Total_Vacancy']:,} ({(borough_totals['Total_Vacancy'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{borough_totals['Total_Absence']:,} ({(borough_totals['Total_Absence'] / borough_totals['Total'] * 100) if borough_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_match_pct:.1f}%" if borough_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(borough_schools_list)}"
    }
    comparison_cards.append(get_comparison_card_html(f"{superintendent_borough} Statistics", borough_stats, "borough"))
    
    # Superintendent card
    superintendent_stats = {
        "Total Jobs": f"{superintendent_totals['Total']:,}",
        "Total Vacancies": f"{superintendent_totals['Total_Vacancy']:,} ({(superintendent_totals['Total_Vacancy'] / superintendent_totals['Total'] * 100) if superintendent_totals['Total'] > 0 else 0:.1f}%)",
        "Total Absences": f"{superintendent_totals['Total_Absence']:,} ({(superintendent_totals['Total_Absence'] / superintendent_totals['Total'] * 100) if superintendent_totals['Total'] > 0 else 0:.1f}%)",
        "Overall Fill Rate": f"{superintendent_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{superintendent_rates[1]:.1f}%",
        "Absence Fill Rate": f"{superintendent_rates[2]:.1f}%",
        "Average Match %": f"{superintendent_match_pct:.1f}%" if superintendent_match_pct > 0 else "N/A",
        "Number of Schools": f"{len(superintendent_schools_list)}"
    }
    comparison_cards.append(get_comparison_card_html(f"Superintendent {superintendent}", superintendent_stats, "superintendent"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # Create classification analysis table
    # Create formatters for all the columns
    available_display_cols = [col for col in superintendent_data.columns if col in [
        'Classification', 'Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
        'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 'Total_Filled', 'Total_Unfilled', 'Overall_Fill_Pct'
    ]]
    
    formatters = {}
    for col in available_display_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str
    
    # Sort by Total jobs descending (highest to lowest) for both tables and charts
    superintendent_data_sorted = superintendent_data.sort_values('Total', ascending=False)
    
    classification_html = create_classification_tabbed_tables(superintendent_data_sorted[available_display_cols], formatters)
    
    # Create bar chart for classification analysis
    bar_chart_file = os.path.join(superintendent_dir, f'{safe_superintendent_name}_bar_chart.html')
    create_bar_chart(
        superintendent_data_sorted,
        f'Jobs by Classification and Type - Superintendent {superintendent}',
        bar_chart_file,
        f"superintendent_{safe_superintendent_name}_bar_chart"
    )
    
    # Create school level analysis if available
    summary_by_school_html = ""
    school_links = ""
    school_reports = []
    
    if school_stats is not None and not school_stats.empty:
        superintendent_school_data = school_stats[school_stats['Superintendent_Name'] == superintendent]
        if not superintendent_school_data.empty:
            # FIRST aggregate the school data by Location to prevent duplicates
            school_aggregated_for_display = superintendent_school_data.groupby(['Location']).agg({
                'Vacancy_Filled': 'sum',
                'Vacancy_Unfilled': 'sum', 
                'Total_Vacancy': 'sum',
                'Absence_Filled': 'sum',
                'Absence_Unfilled': 'sum',
                'Total_Absence': 'sum',
                'Total': 'sum'
            }).reset_index()
            
            # Calculate fill rates for the aggregated data
            school_aggregated_for_display['Vacancy_Fill_Pct'] = (
                school_aggregated_for_display['Vacancy_Filled'] / 
                school_aggregated_for_display['Total_Vacancy'].replace(0, 1) * 100
            ).round(1)
            school_aggregated_for_display['Absence_Fill_Pct'] = (
                school_aggregated_for_display['Absence_Filled'] / 
                school_aggregated_for_display['Total_Absence'].replace(0, 1) * 100
            ).round(1)
            school_aggregated_for_display['Total_Filled'] = (
                school_aggregated_for_display['Vacancy_Filled'] + 
                school_aggregated_for_display['Absence_Filled']
            )
            school_aggregated_for_display['Total_Unfilled'] = (
                school_aggregated_for_display['Vacancy_Unfilled'] + 
                school_aggregated_for_display['Absence_Unfilled']
            )
            school_aggregated_for_display['Overall_Fill_Pct'] = (
                school_aggregated_for_display['Total_Filled'] / 
                school_aggregated_for_display['Total'].replace(0, 1) * 100
            ).round(1)
            
            summary_by_school_html = create_school_tabbed_tables(
                school_aggregated_for_display.rename(columns={'Location': 'School'}), 
                formatters
            )
            
            # Create school links with actual reports (prevent duplicates)
            unique_schools = school_aggregated_for_display['Location'].unique()  # Get unique schools only
            
            # Use the same aggregated data for links
            school_aggregated = school_aggregated_for_display.copy()
            # Don't rename 'Total' to 'Total_Jobs' here since school reports expect 'Total'
            
            # Generate school reports and track successful ones
            school_reports = []
            for location in unique_schools:
                # Get data for this specific school
                location_data = school_aggregated[school_aggregated['Location'] == location]
                if not location_data.empty:
                    # Create safe filename for school
                    location_clean = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location)).strip()
                    location_clean = re.sub(r'_+', '_', location_clean).strip('_')
                    location_clean = location_clean.replace('.', '_')
                    if len(location_clean) > 200:
                        location_clean = location_clean[:200].rstrip('._')
                    
                    # Get school data for this location from school_stats (pre-calculated)
                    if school_stats is not None:
                        school_data = school_stats[
                            (school_stats['Superintendent_Name'] == superintendent) & 
                            (school_stats['Location'] == location)
                        ]
                        if not school_data.empty:
                            # Create school report using the superintendent school report function
                            try:
                                school_report = create_superintendent_school_report(
                                    superintendent, location, location_clean, school_data, 
                                    df, summary_stats, superintendent_dir, date_range_info, matching_stats
                                )
                                if school_report:
                                    school_reports.append(school_report)
                            except Exception as e:
                                print(f"Warning: Could not create school report for {location}: {e}")
                        else:
                            print(f"Warning: No school stats found for {location} under {superintendent}")
                    else:
                        print(f"Warning: No school_stats provided for {location}")
            
            # Create school links with styling matching district reports
            school_links_list = []
            for _, school in school_aggregated.iterrows():
                location = school['Location']
                total_jobs = school['Total']  # Use 'Total' instead of 'Total_Jobs'
                # Create clean location name for file path
                location_clean = re.sub(r'[<>:"/\\|?*\n\r\t\s]', '_', str(location)).strip()
                location_clean = re.sub(r'_+', '_', location_clean).strip('_')
                location_clean = location_clean.replace('.', '_')
                if len(location_clean) > 200:
                    location_clean = location_clean[:200].rstrip('._')
                
                school_links_list.append(f'<li><a href="Schools/School_{location_clean}/{location_clean}_report.html">{location} ({total_jobs:,} jobs)</a></li>')
            
            school_links = f'''
            <div class="superintendent-links">
                <h3> Schools under Superintendent {superintendent}</h3>
                <ul>
                    {''.join(school_links_list)}
                </ul>
            </div>'''
    
    # Create SubCentral vs Payroll analysis if matching data available
    matching_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty:
        # Get schools for this superintendent first
        superintendent_schools_for_matching = df[df['Superintendent_Name'] == superintendent]['Location'].unique()
        # Filter matching stats by schools in this superintendent's jurisdiction
        superintendent_matching = matching_stats[matching_stats['Location'].isin(superintendent_schools_for_matching)]
        if not superintendent_matching.empty:
            # Sort by Match Percentage (lowest to highest)
            match_col = None
            for col in superintendent_matching.columns:
                if 'Match' in col and ('Percentage' in col or '%' in col):
                    match_col = col
                    break
            
            if match_col:
                superintendent_matching_sorted = superintendent_matching.sort_values(match_col, ascending=True)
                
                # Create formatters for matching table
                match_formatters = {
                    col: format_pct if 'Match' in col and ('Percentage' in col or '%' in col) else format_int
                    for col in superintendent_matching_sorted.columns
                }
                
                # Calculate summary stats
                subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in superintendent_matching.columns else 'SubCentral_Count'
                payroll_col = 'Payroll Job Days' if 'Payroll Job Days' in superintendent_matching.columns else 'Payroll_Count'
                matched_col = None
                for col in superintendent_matching.columns:
                    if 'Matched' in col and 'Job' in col:
                        matched_col = col
                        break
                
                total_subcentral = superintendent_matching[subcentral_col].sum() if subcentral_col in superintendent_matching.columns else 0
                total_payroll = superintendent_matching[payroll_col].sum() if payroll_col in superintendent_matching.columns else 0
                total_matched = superintendent_matching[matched_col].sum() if matched_col and matched_col in superintendent_matching.columns else 0
                
                matching_analysis_html = f"""
                <div class="section">
                    <h3>SubCentral vs Payroll Analysis</h3>
                    <p><em>This analysis matches individual jobs using Location + EIS ID + Date between SubCentral and SREPP payroll systems to identify discrepancies and data quality issues.</em></p>
                    
                    <div class="summary-box">
                        <h4>Superintendent Matching Summary</h4>
                        <ul>
                            <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                            <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                            <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                            <li><strong>Average Match Rate:</strong> {superintendent_match_pct:.1f}%</li>
                        </ul>
                    </div>
                    
                    <div class="table-responsive">
                        <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify schools needing attention.</em></p>
                        {create_conditional_formatted_table(superintendent_matching_sorted, match_formatters, match_col)}
                    </div>
                </div>
                """
    
    # Combine content
    content = f"""
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"Superintendent: {superintendent}", 
                        date_range_info)}
        
        <div class="content">
            <div class="section">
                <h3>Comparison Statistics</h3>
                <p><em>This comparison shows how schools under this superintendent perform relative to the borough and citywide averages.</em></p>
                {comparison_html}
            </div>
            
            {matching_analysis_html}
            
            <div class="section">
                <h3>Fill Rate Analysis by Classification</h3>
                <p><em><strong>Note:</strong> Data is based on SubCentral records. Use the tabs below to switch between
                different views. Data is sorted from highest to lowest number of total jobs.</em></p>
                {classification_html}
            </div>
            
            <div class="section">
                <h3>Jobs by Classification and Type</h3>
                <div class="chart-container">
                    <iframe src="{safe_superintendent_name}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>
            
            <div class="section">
                <h3>School Level Fill Rates</h3>
                <p><em><strong>Note:</strong> This data is based on SubCentral data only. Data is sorted from lowest to highest overall fill rate to identify schools needing attention. Use the tabs below to switch between different views.</em></p>
                {summary_by_school_html}
                
                {school_links}
            </div>
        </div>
        
        <style>
        .school-links {{
            margin: 20px 0;
        }}
        
        .links-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .school-link-item {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .school-link-item:hover {{
            border-color: #007bff;
            box-shadow: 0 2px 8px rgba(0,123,255,0.1);
            transform: translateY(-2px);
        }}
        
        .school-link {{
            display: block;
            padding: 15px;
            text-decoration: none;
            color: inherit;
        }}
        
        .school-link:hover {{
            text-decoration: none;
            color: inherit;
        }}
        
        .school-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .school-name {{
            font-weight: bold;
            color: #007bff;
            font-size: 16px;
        }}
        
        .school-stats {{
            color: #666;
            font-size: 14px;
            font-style: italic;
        }}
        </style>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML using template
    html_content = get_html_template(f"Jobs Report - Superintendent {superintendent}", "Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(superintendent_dir, f'{safe_superintendent_name}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file, school_reports


def create_borough_report(borough, borough_data, df, output_dir, district_stats, date_range_info, matching_stats=None):
    """
    Create a comprehensive report for a single borough with restructured sections per feedback:
    1. Overall Summary (Borough vs Citywide) with Average Match %
    2. Match Payroll Analysis (sorted lowest to highest Match %)
    3. Classification Information (sorted highest to lowest total jobs)
    4. Individual Schools (with helpful notes)
    """
    import pandas as pd
    # Create subfolder for borough
    borough_clean = borough.replace(' ', '_').replace('/', '_')
    borough_dir = os.path.join(output_dir, f"Borough_{borough_clean}")
    os.makedirs(borough_dir, exist_ok=True)
    
    # Get borough data
    df_borough = df[df['Borough'] == borough]
    
    # === SECTION 1: OVERALL SUMMARY (Borough vs Citywide) ===
    # Get comparison data
    overall_totals = district_stats.agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
        'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    overall_stats = {k: int(v) for k, v in overall_totals.items()}
    borough_totals = get_totals_from_data(borough_data)
    
    # Calculate fill rates
    citywide_rates = calculate_fill_rates(overall_stats)
    borough_rates = calculate_fill_rates(borough_totals)
    
    # Filter matching analysis data for this borough and calculate average match percentage
    citywide_avg_match = 0
    borough_avg_match = 0
    borough_matching = pd.DataFrame()
    
    if matching_stats is not None and not matching_stats.empty:
        # Get borough schools from the district-level matching data
        borough_schools = df[df['Borough'] == borough]['Location'].unique()
        borough_matching = matching_stats[matching_stats['Location'].isin(borough_schools)].copy()
        
        # Calculate average match percentages
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Citywide average
            citywide_avg_match = matching_stats[match_col].mean()
            
            # Borough average
            if not borough_matching.empty:
                borough_avg_match = borough_matching[match_col].mean()
    
    # Create comparison cards with match percentage
    comparison_cards = []
    
    # Citywide card with match percentage
    citywide_stats = {
        "Total Jobs": f"{overall_stats['Total']:,}",
        "Overall Fill Rate": f"{citywide_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{citywide_rates[1]:.1f}%",
        "Absence Fill Rate": f"{citywide_rates[2]:.1f}%",
        "Average Match %": f"{citywide_avg_match:.1f}%" if citywide_avg_match > 0 else "N/A",
        "Number of Schools": f"{len(df['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html("Citywide Statistics", citywide_stats, "citywide"))
    
    # Borough card with match percentage  
    borough_stats = {
        "Total Jobs": f"{borough_totals['Total']:,}",
        "Overall Fill Rate": f"{borough_rates[0]:.1f}%",
        "Vacancy Fill Rate": f"{borough_rates[1]:.1f}%",
        "Absence Fill Rate": f"{borough_rates[2]:.1f}%",
        "Average Match %": f"{borough_avg_match:.1f}%" if borough_avg_match > 0 else "N/A",
        "Number of Schools": f"{len(df[df['Borough'] == borough]['Location'].unique())}"
    }
    comparison_cards.append(get_comparison_card_html(f"This Borough", borough_stats, "borough"))
    
    comparison_html = f'<div class="comparison-grid">{"".join(comparison_cards)}</div>'
    
    # === SECTION 2: MATCH PAYROLL ANALYSIS (for districts in this borough) ===
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty and not borough_matching.empty:
        # Find the match percentage column
        match_col = None
        for col in borough_matching.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Add district information to borough matching data
            district_info = df[['Location', 'District']].drop_duplicates()
            borough_matching_with_district = borough_matching.merge(district_info, on='Location', how='left')
            
            # Aggregate by district to show district-level analysis
            district_analysis = borough_matching_with_district.groupby('District').agg({
                'SubCentral Job Days' if 'SubCentral Job Days' in borough_matching.columns else 'SubCentral_Count': 'sum',
                'Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count': 'sum'
            }).reset_index()
            
            # Find matched column and add it
            matched_col = None
            for col in borough_matching.columns:
                if 'Matched' in col and 'Job' in col:
                    matched_col = col
                    break
            
            if matched_col:
                district_matched = borough_matching_with_district.groupby('District')[matched_col].sum().reset_index()
                district_analysis = district_analysis.merge(district_matched, on='District', how='left')
                
                # Calculate district-level match percentages
                subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in borough_matching.columns else 'SubCentral_Count'
                district_analysis['Match_Percentage'] = (
                    district_analysis[matched_col] / district_analysis[subcentral_col] * 100
                ).round(1)
                
                # Sort by Match Percentage (lowest to highest per feedback)
                district_analysis = district_analysis.sort_values('Match_Percentage', ascending=True)
                
                # Rename column for display (remove underscore)
                district_analysis_display = district_analysis.rename(columns={'Match_Percentage': 'Match Percentage'})
                
                # Calculate totals
                total_subcentral = district_analysis[subcentral_col].sum()
                total_payroll = district_analysis['Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count'].sum()
                total_matched = district_analysis[matched_col].sum()
                
                # Create formatters for district analysis table
                district_formatters = {
                    'District': lambda x: f"District {int(x)}",
                    subcentral_col: format_int,
                    'Payroll Job Days' if 'Payroll Job Days' in borough_matching.columns else 'Payroll_Count': format_int,
                    matched_col: format_int,
                    'Match Percentage': format_pct
                }
                
                payroll_analysis_html = f"""
                <div class="section">
                    <h3>SubCentral vs Payroll Analysis (District Level)</h3>
                    <p><em>This analysis shows district-level matching within {borough} borough.</em></p>
                    
                    <div class="summary-box">
                        <h4>Borough Matching Summary</h4>
                        <ul>
                            <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                            <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                            <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                            <li><strong>Average Match Rate:</strong> {borough_avg_match:.1f}%</li>
                        </ul>
                    </div>
                    
                    <div class="table-responsive">
                        <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify districts needing attention.</em></p>
                        {create_conditional_formatted_table(district_analysis_display, district_formatters, 'Match Percentage')}
                    </div>
                </div>
                """
    
    # === SECTION 3: CLASSIFICATION INFORMATION ===
    # Sort by total jobs (highest to lowest per feedback)
    borough_data_sorted = borough_data.sort_values('Total', ascending=False)
    
    # Use all the columns needed for tabbed tables
    required_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                     'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_cols = [col for col in required_cols if col in borough_data_sorted.columns]
    
    # Create formatters for all the columns
    formatters = {}
    for col in existing_cols:
        if 'Pct' in col:
            formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            formatters[col] = format_int
        else:
            formatters[col] = str  # For Classification
    
    classification_table_html = create_classification_tabbed_tables(borough_data_sorted[existing_cols], formatters)
    
    # Create bar chart
    bar_chart_file = os.path.join(borough_dir, f'{borough_clean}_bar_chart.html')
    create_bar_chart(
        borough_data_sorted,
        f'Jobs by Classification and Type - {borough}',
        bar_chart_file,
        f"borough_{borough_clean}_bar_chart"
    )
    
    # Create pie charts
    pie_charts_html = create_pie_charts_for_data(borough_data_sorted, borough_clean, borough_dir)
    
    # === SECTION 4: DISTRICT LEVEL FILL RATES ===
    # Create summary by district within this borough
    district_summary = create_summary_stats(df_borough, ['District'])
    district_summary = district_summary.groupby('District', as_index=False).agg({
        'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
        'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
    })
    
    # Calculate percentages
    district_summary['Vacancy_Fill_Pct'] = (district_summary['Vacancy_Filled'] / district_summary['Total_Vacancy'] * 100).fillna(0).round(1)
    district_summary['Absence_Fill_Pct'] = (district_summary['Absence_Filled'] / district_summary['Total_Absence'] * 100).fillna(0).round(1)
    district_summary['Total_Filled'] = district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']
    district_summary['Total_Unfilled'] = district_summary['Vacancy_Unfilled'] + district_summary['Absence_Unfilled']
    district_summary['Overall_Fill_Pct'] = ((district_summary['Vacancy_Filled'] + district_summary['Absence_Filled']) / district_summary['Total'] * 100).fillna(0).round(1)
    
    # Create formatters for district summary
    district_formatters = {
        'District': lambda x: f"District {int(x)}" if pd.notna(x) else x,
        'Vacancy Filled': format_int, 'Vacancy Unfilled': format_int, 'Total Vacancy': format_int,
        'Vacancy Fill %': format_pct, 'Absence Filled': format_int, 'Absence Unfilled': format_int,
        'Total Absence': format_int, 'Absence Fill %': format_pct, 'Total Filled': format_int, 
        'Total Unfilled': format_int, 'Total': format_int, 'Overall Fill %': format_pct
    }
    district_summary_html = create_district_tabbed_tables(
        district_summary.rename(columns={
            'District': 'District',
            'Vacancy_Filled': 'Vacancy_Filled', 'Vacancy_Unfilled': 'Vacancy_Unfilled', 'Total_Vacancy': 'Total_Vacancy',
            'Vacancy_Fill_Pct': 'Vacancy_Fill_Pct', 'Absence_Filled': 'Absence_Filled', 'Absence_Unfilled': 'Absence_Unfilled',
            'Total_Absence': 'Total_Absence', 'Absence_Fill_Pct': 'Absence_Fill_Pct', 'Total_Filled': 'Total_Filled', 
            'Total_Unfilled': 'Total_Unfilled', 'Total': 'Total', 'Overall_Fill_Pct': 'Overall_Fill_Pct'
        }), 
        district_formatters
    )
    
    # Get districts in this borough and create links
    borough_districts = sorted(df[df['Borough'] == borough]['District'].unique())
    district_links = ""
    for district in borough_districts:
        total_jobs = district_summary[district_summary['District'] == district]['Total'].iloc[0]
        district_links += f'<li><a href="../District_{int(float(district))}/{int(float(district))}_report.html">District {int(float(district))} Report</a> - {int(total_jobs):,} total jobs</li>\n'
    
    # Build content with new structure
    content = f"""
        {get_header_html("../Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Report", 
                        f"Borough: {borough}", 
                        date_range_info)}
        
        <div class="content">
            {get_navigation_html([("../index.html", "← Back to Overall Summary")])}
            
            <!-- SECTION 1: Overall Summary (Borough vs Citywide) -->
            <div class="section">
                <h3>1. Overall Summary - {borough} vs. Citywide</h3>
                <p><em>Comparison frames everything else you will see on this page</em></p>
                {comparison_html}
            </div>

            <!-- SECTION 2: Match Payroll Analysis -->
            {payroll_analysis_html}

            <!-- SECTION 3: Classification Information -->
            <div class="section">
                <h3>3. Classification Information (Borough Level)</h3>
                <h4>Summary Statistics</h4>
                <p><em>Data sorted from highest to lowest total jobs</em></p>
                {classification_table_html}
            </div>

            <div class="section">
                <h4>Jobs by Classification Type</h4>
                <div class="chart-container">
                    <iframe src="{borough_clean}_bar_chart.html" width="1220" height="520" frameborder="0"></iframe>
                </div>
            </div>

            <div class="section">
                <h4>Breakdown by Classification</h4>
                <div class="pie-container">{pie_charts_html}</div>
            </div>

            <!-- SECTION 4: District Level Fill Rates -->
            <div class="section">
                <h3>4. District Level Fill Rates</h3>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify districts needing attention. This data is based on SubCentral data only. Use the tabs below to switch between different views. Click on district links for detailed reports.</em></p>
                {district_summary_html}
                
                <h4>Individual District Reports</h4>
                <p><em><strong>Note:</strong> Click on district links below for detailed district-level reports. Links are ordered by district number.</em></p>
                <div class="district-links"><ul>{district_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML
    html_content = get_html_template(f"Jobs Report - {borough}", "../Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    report_file = os.path.join(borough_dir, f'{borough_clean}_report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_file


def create_overall_summary(df, citywide_stats, borough_stats, output_dir, date_range_info, matching_stats=None, superintendent_stats=None):
    """
    Create an overall summary report across all districts with restructured sections:
    1. Overall Summary with Average Match Percentage
    2. Match Payroll Analysis (citywide)
    3. Classification Information (sorted highest to lowest total jobs)
    4. Borough Breakdowns
    """
    import pandas as pd
    
    # Create district stats from raw data for the overall summary
    # (Even though we use superintendent-based reports, we still want district-level summary in overall view)
    if 'District_From_Mapping' in df.columns:
        # Create district stats from superintendent_stats if available, otherwise from raw data
        if superintendent_stats is not None and not superintendent_stats.empty:
            # First, we need to map superintendents to districts
            # Get district mapping from raw data
            district_mapping = df[['Superintendent_Name', 'District_From_Mapping']].dropna().drop_duplicates()
            
            # Merge superintendent stats with district mapping
            supt_with_district = superintendent_stats.merge(
                district_mapping, 
                on='Superintendent_Name', 
                how='left'
            )
            
            # Group by district to create district stats (exclude 'Unknown' districts)
            district_stats = supt_with_district[
                (supt_with_district['District_From_Mapping'] != 'Unknown') & 
                (supt_with_district['District_From_Mapping'].notna())
            ].groupby('District_From_Mapping').agg({
                'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
                'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
            }).reset_index()
            
            # Rename the district column
            district_stats = district_stats.rename(columns={'District_From_Mapping': 'District'})
            
            # Add calculated percentages (these should already be calculated, but recalculate for safety)
            district_stats['Vacancy_Fill_Pct'] = np.where(
                district_stats['Total_Vacancy'] > 0,
                (district_stats['Vacancy_Filled'] / district_stats['Total_Vacancy'] * 100).round(1), 0
            )
            district_stats['Absence_Fill_Pct'] = np.where(
                district_stats['Total_Absence'] > 0,
                (district_stats['Absence_Filled'] / district_stats['Total_Absence'] * 100).round(1), 0
            )
            district_stats['Total_Filled'] = district_stats['Vacancy_Filled'] + district_stats['Absence_Filled']
            district_stats['Total_Unfilled'] = district_stats['Vacancy_Unfilled'] + district_stats['Absence_Unfilled']
            district_stats['Overall_Fill_Pct'] = np.where(
                district_stats['Total'] > 0,
                ((district_stats['Vacancy_Filled'] + district_stats['Absence_Filled']) / district_stats['Total'] * 100).round(1), 0
            )
        else:
            district_stats = pd.DataFrame()  # Empty DataFrame if no superintendent stats
    else:
        district_stats = pd.DataFrame()  # Empty DataFrame if no District column
    
    # === SECTION 1: OVERALL SUMMARY WITH MATCH PERCENTAGE ===
    # Use pre-calculated matching stats instead of recalculating
    citywide_avg_match = 0
    if matching_stats is not None and not matching_stats.empty:
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                citywide_avg_match = matching_stats[match_col].mean()
                break
    
    # Use citywide_stats for overall statistics - already sorted by total jobs (highest to lowest)
    overall_stats = citywide_stats.copy()
    if overall_stats.empty:
        # Fallback: create from district stats if citywide is empty
        overall_stats = superintendent_stats.groupby('Classification', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Absence_Filled': 'sum',
            'Absence_Unfilled': 'sum', 'Total_Vacancy': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
        overall_stats['Vacancy_Fill_Pct'] = np.where(
            overall_stats['Total_Vacancy'] > 0,
            (overall_stats['Vacancy_Filled'] / overall_stats['Total_Vacancy'] * 100).round(1), 0
        )
        overall_stats['Absence_Fill_Pct'] = np.where(
            overall_stats['Total_Absence'] > 0,
            (overall_stats['Absence_Filled'] / overall_stats['Total_Absence'] * 100).round(1), 0
        )
        overall_stats['Total_Filled'] = overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']
        overall_stats['Total_Unfilled'] = overall_stats['Vacancy_Unfilled'] + overall_stats['Absence_Unfilled']
        overall_stats['Overall_Fill_Pct'] = np.where(
            overall_stats['Total'] > 0,
            ((overall_stats['Vacancy_Filled'] + overall_stats['Absence_Filled']) / overall_stats['Total'] * 100).round(1), 0
        )
    
    # Sort by total jobs (highest to lowest per feedback)
    overall_stats = overall_stats.sort_values('Total', ascending=False)

    # === SECTION 2: MATCH PAYROLL ANALYSIS (Borough Level) ===
    payroll_analysis_html = ""
    if matching_stats is not None and not matching_stats.empty:
        # Find the match percentage column
        match_col = None
        for col in matching_stats.columns:
            if 'Match' in col and ('Percentage' in col or '%' in col):
                match_col = col
                break
        
        if match_col:
            # Add borough information to matching data
            borough_info = df[['Location', 'Borough']].drop_duplicates()
            matching_with_borough = matching_stats.merge(borough_info, on='Location', how='left')
            
            # Aggregate by borough to show borough-level analysis (ensuring unique boroughs)
            borough_analysis = matching_with_borough.groupby('Borough', as_index=False).agg({
                'SubCentral Job Days' if 'SubCentral Job Days' in matching_stats.columns else 'SubCentral_Count': 'sum',
                'Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count': 'sum'
            })
            
            # Find matched column and add it
            matched_col = None
            for col in matching_stats.columns:
                if 'Matched' in col and 'Job' in col:
                    matched_col = col
                    break
            
            if matched_col:
                borough_matched = matching_with_borough.groupby('Borough', as_index=False)[matched_col].sum()
                borough_analysis = borough_analysis.merge(borough_matched, on='Borough', how='left')
                
                # Calculate borough-level match percentages
                subcentral_col = 'SubCentral Job Days' if 'SubCentral Job Days' in matching_stats.columns else 'SubCentral_Count'
                borough_analysis['Match_Percentage'] = (
                    borough_analysis[matched_col] / borough_analysis[subcentral_col] * 100
                ).round(1)
                
                # Sort by Match Percentage (lowest to highest per feedback)
                borough_analysis = borough_analysis.sort_values('Match_Percentage', ascending=True)
                
                # Rename column for display (remove underscore)
                borough_analysis_display = borough_analysis.rename(columns={'Match_Percentage': 'Match Percentage'})
                
                # Calculate totals
                total_subcentral = borough_analysis[subcentral_col].sum()
                total_payroll = borough_analysis['Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count'].sum()
                total_matched = borough_analysis[matched_col].sum()
                
                # Create formatters for borough analysis table
                borough_formatters = {
                    'Borough': str,
                    subcentral_col: format_int,
                    'Payroll Job Days' if 'Payroll Job Days' in matching_stats.columns else 'Payroll_Count': format_int,
                    matched_col: format_int,
                    'Match Percentage': format_pct
                }
                
                payroll_analysis_html = f"""
                <div class="section">
                    <h3>2. SubCentral vs Payroll Analysis (Borough Level)</h3>
                    <p><em>This analysis shows borough-level matching across all five boroughs.</em></p>
                    
                    <div class="summary-box">
                        <h4>Citywide Matching Summary</h4>
                        <ul>
                            <li><strong>Total SubCentral Records:</strong> {total_subcentral:,}</li>
                            <li><strong>Total Payroll Records:</strong> {total_payroll:,}</li>
                            <li><strong>Total Matched Records:</strong> {total_matched:,}</li>
                            <li><strong>Average Match Rate:</strong> {citywide_avg_match:.1f}%</li>
                        </ul>
                    </div>
                    
                    <div class="table-responsive">
                        <p><em><strong>Note:</strong> Data is sorted from lowest to highest Match % to identify boroughs needing attention.</em></p>
                        {create_conditional_formatted_table(borough_analysis_display, borough_formatters, 'Match Percentage')}
                    </div>
                </div>
                """

    overall_chart_file = os.path.join(output_dir, 'overall_bar_chart.html')
    create_overall_bar_chart(overall_stats, overall_chart_file)

    # Create district summary for overall summary page
    district_summary = district_stats
    
    district_summary = district_summary.sort_values('Total', ascending=False)

    # Vectorized navigation link generation for districts (exclude 'Unknown' districts)
    district_links = ''.join([
        f'<li><a href="District_{int(float(row.District))}/{int(float(row.District))}_report.html">District {int(float(row.District))} Report</a> - {int(row.Total):,} total jobs</li>\n'
        for _, row in district_summary.sort_values('District').iterrows()
        if str(row.District) != 'Unknown' and str(row.District) != 'nan'
    ]) if not district_summary.empty else ""

    # Create superintendent links (new addition)
    superintendent_totals = superintendent_stats.groupby('Superintendent_Name')['Total'].sum() if superintendent_stats is not None else pd.Series()
    superintendent_links = ''.join([
        f'<li><a href="Superintendent_{superintendent.replace(" ", "_").replace(",", "").replace(".", "")}/{superintendent.replace(" ", "_").replace(",", "").replace(".", "")}_report.html">{superintendent} Report</a> - {int(total):,} total jobs</li>\n'
        for superintendent, total in superintendent_totals.items() if superintendent != 'Unknown'
    ])

    borough_totals = borough_stats.groupby('Borough')['Total'].sum()
    borough_links = ''.join([
        f'<li><a href="Borough_{borough.replace(" ", "_").replace("/", "_")}/{borough.replace(" ", "_").replace("/", "_")}_report.html">{borough} Report</a> - {int(total):,} total jobs</li>\n'
        for borough, total in borough_totals.items() if borough != 'Unknown'
    ])

    # Vectorized statistics
    fill_status_counts = df['Fill_Status'].value_counts()
    type_counts = df['Type'].value_counts()
    total_jobs = len(df)
    total_filled = fill_status_counts.get('Filled', 0)
    total_vacancies = type_counts.get('Vacancy', 0)
    total_absences = type_counts.get('Absence', 0)
    unique_districts = df['District'].nunique()
    unique_schools = df['Location'].nunique()
    unique_classifications = df['Classification'].nunique()

    # Create tabbed summary tables - sorted by total jobs (highest to lowest)
    # Use all the columns needed for tabbed tables
    required_overall_cols = ['Classification', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                            'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                            'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_overall_cols = [col for col in required_overall_cols if col in overall_stats.columns]
    
    overall_formatters = {}
    for col in existing_overall_cols:
        if 'Pct' in col:
            overall_formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            overall_formatters[col] = format_int
        else:
            overall_formatters[col] = str  # For Classification
    
    overall_table_html = create_classification_tabbed_tables(overall_stats[existing_overall_cols], overall_formatters)
    
    # Create borough summary table with proper column formatting
    required_borough_cols = ['Borough', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                            'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                            'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_borough_cols = [col for col in required_borough_cols if col in borough_stats.columns]
    
    if existing_borough_cols and not borough_stats.empty:
        # Aggregate borough data by Borough (sum numeric columns, recalculate percentages)
        borough_agg = borough_stats.groupby('Borough', as_index=False).agg({
            'Vacancy_Filled': 'sum', 'Vacancy_Unfilled': 'sum', 'Total_Vacancy': 'sum',
            'Absence_Filled': 'sum', 'Absence_Unfilled': 'sum', 'Total_Absence': 'sum', 'Total': 'sum'
        })
        
        # Recalculate percentages for aggregated data
        borough_agg['Vacancy_Fill_Pct'] = (
            borough_agg['Vacancy_Filled'] / borough_agg['Total_Vacancy'] * 100
        ).fillna(0).round(1)
        borough_agg['Absence_Fill_Pct'] = (
            borough_agg['Absence_Filled'] / borough_agg['Total_Absence'] * 100
        ).fillna(0).round(1)
        borough_agg['Total_Filled'] = borough_agg['Vacancy_Filled'] + borough_agg['Absence_Filled']
        borough_agg['Total_Unfilled'] = borough_agg['Vacancy_Unfilled'] + borough_agg['Absence_Unfilled']
        borough_agg['Overall_Fill_Pct'] = (
            (borough_agg['Vacancy_Filled'] + borough_agg['Absence_Filled']) / borough_agg['Total'] * 100
        ).fillna(0).round(1)
        
        borough_for_table = borough_agg[existing_borough_cols].sort_values('Overall_Fill_Pct', ascending=True)
        
        borough_formatters = {}
        for col in existing_borough_cols:
            if col == 'Borough':
                borough_formatters[col] = str
            elif 'Pct' in col:
                borough_formatters[col] = format_pct
            elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                         'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
                borough_formatters[col] = format_int
            else:
                borough_formatters[col] = str
        
        borough_table_html = create_borough_tabbed_tables(
            borough_for_table, 
            borough_formatters
        )
    else:
        borough_table_html = "<p><em>No borough data available</em></p>"
    
    # Create district summary table with proper column formatting
    required_district_cols = ['District', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                             'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct', 
                             'Total_Filled', 'Total_Unfilled', 'Total', 'Overall_Fill_Pct']
    existing_district_cols = [col for col in required_district_cols if col in district_summary.columns]
    district_for_table = district_summary[existing_district_cols].sort_values('Overall_Fill_Pct', ascending=True)
    
    district_formatters = {}
    for col in existing_district_cols:
        if col == 'District':
            district_formatters[col] = lambda x: f"District {int(x)}" if pd.notna(x) else x
        elif 'Pct' in col:
            district_formatters[col] = format_pct
        elif col in ['Total', 'Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy',
                     'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Total_Filled', 'Total_Unfilled']:
            district_formatters[col] = format_int
        else:
            district_formatters[col] = str
    
    district_table_html = create_district_tabbed_tables(
        district_for_table, 
        district_formatters
    )
    
    # Create district choropleth map
    district_map_html = ""
    try:
        from district_mapping import create_district_choropleth, get_district_map_section_html
        map_file = os.path.join(output_dir, 'district_fillrate_map.html')
        map_content = create_district_choropleth(district_summary, map_file)
        if map_content:
            district_map_html = get_district_map_section_html(district_summary, 'district_fillrate_map.html')
        else:
            print("⚠ Could not create district choropleth map")
    except Exception as e:
        print(f"⚠ Could not create district map - {e}")
        # Continue without the map
    
    # Build content with clean structure matching original ParaJobs format
    content = f"""
        {get_header_html("Horizontal_logo_White_PublicSchools.png", 
                        "Substitute Paraprofessional Jobs Dashboard", 
                        "Citywide Summary Report", 
                        date_range_info)}
        
        <div class="content">
            <!-- SECTION 1: Overall Summary with Match Percentage -->
            <div class="section">
                <h3>1. Overall Summary</h3>
                <div class="summary-box">
                    <h4>Key Statistics</h4>
                    <ul>
                        <li><strong>Total Jobs:</strong> {total_jobs:,}</li>
                        <li><strong>Total Vacancies:</strong> {total_vacancies:,} ({(total_vacancies/total_jobs*100):.1f}%)</li>
                        <li><strong>Total Absences:</strong> {total_absences:,} ({(total_absences/total_jobs*100):.1f}%)</li>
                        <li><strong>Total Filled:</strong> {total_filled:,} ({(total_filled/total_jobs*100):.1f}%)</li>
                        <li><strong>Average Match %:</strong> {citywide_avg_match:.1f}% (key metric for SubCentral usage)</li>
                        <li><strong>Total Districts:</strong> {unique_districts}</li>
                        <li><strong>Total Schools:</strong> {unique_schools}</li>
                        <li><strong>Total Classifications:</strong> {unique_classifications}</li>
                    </ul>
                </div>
            </div>

            <!-- SECTION 2: Match Payroll Analysis -->
            {payroll_analysis_html}
            
            <!-- SECTION 3: Classification Information -->
            <div class="section">
                <h3>3. Classification Information (Citywide)</h3>
                <h4>Summary Statistics</h4>
                <p><em>Data sorted from highest to lowest total jobs</em></p>
                {overall_table_html}
            </div>
            
            <div class="section">
                <h4>Jobs by Classification Type</h4>
                <div class="chart-container">
                    <iframe src="overall_bar_chart.html" width="1450" height="600" frameborder="0"></iframe>
                </div>
            </div>
            
            <!-- SECTION 4: Borough Level Summary -->
            <div class="section">
                <h3>4. Borough Level Fill Rates</h3>
                <h4>Summary by Borough</h4>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify boroughs needing attention. Use the tabs below to switch between different views. Click on borough links for detailed reports.</em></p>
                {borough_table_html}
            </div>
            
            <!-- SECTION 5: District Level Summary -->
            <div class="section">
                <h3>5. District Level Fill Rates</h3>
                <h4>Summary by District</h4>
                <p><em><strong>Note:</strong> Data is sorted from lowest to highest overall fill rate to identify districts needing attention. Use the tabs below to switch between different views. Click on district links for detailed reports.</em></p>
                {district_table_html}
                {district_map_html}
            </div>
            
            <!-- SECTION 6: Superintendent Level Summary (NEW) -->
            <div class="section">
                <h3>6. Superintendent Level Fill Rates</h3>
                <h4>Individual Superintendent Reports</h4>
                <p><em><strong>Note:</strong> Click on superintendent links below for detailed superintendent-level reports. Links are ordered alphabetically by superintendent name.</em></p>
                <div class="superintendent-links"><ul>{superintendent_links}</ul></div>
            </div>
            
            <div class="section">
                <h4>Individual District Reports</h4>
                <p><em><strong>Note:</strong> Click on district links below for detailed district-level reports. Links are ordered by district number.</em></p>
                <div class="district-links"><ul>{district_links}</ul></div>
            </div>
            
            <div class="section">
                <h4>Individual Borough Reports</h4>
                <p><em><strong>Note:</strong> Borough reports provide classification breakdowns and district summaries. Links are ordered alphabetically by borough.</em></p>
                <div class="borough-links"><ul>{borough_links}</ul></div>
            </div>
        </div>
        
        {get_professional_footer(['SubCentral@schools.nyc.gov'])}
    """
    
    # Generate HTML without admin dashboard styling (matching original ParaJobs format)
    html_content = get_html_template("Jobs Dashboard - Overall Summary", "Horizontal_logo_White_PublicSchools.png", content)
    
    # Save report
    index_file = os.path.join(output_dir, 'index.html')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return index_file
