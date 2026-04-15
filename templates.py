"""
HTML Templates and CSS Styles for NYC DOE Reports
"""

import time
import pandas as pd

def get_base_css():
    """Return the base CSS styles used across all reports"""
    return """
            :root {
                --primary-color: #2E86AB;
                --secondary-color: #A23B72;
                --success-color: #2ca02c;
                --warning-color: #ff7f0e;
                --danger-color: #d62728;
                --light-bg: #f5f5f5;
                --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
                --hover-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0; 
                background-color: #f5f5f5;
            }

            .header { 
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 20px; 
                margin: 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .header-text {
                flex: 1;
                text-align: left;
                margin-right: 30px;
            }

            .header-text h1 {
                margin: 0;
                font-size: 2.2em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                line-height: 1.2;
            }

            .header-text h2 {
                margin: 8px 0;
                font-size: 1.2em;
                font-weight: 600;
                opacity: 0.9;
                line-height: 1.3;
            }

            .header-text .date-info {
                margin: 8px 0 0 0;
                font-size: 1.0em;
                opacity: 0.8;
            }

            .header-text p {
                font-size: 1.0em;
                opacity: 0.8;
                margin: 8px 0 0 0;
            }

            .header-logo {
                flex-shrink: 0;
                display: flex;
                align-items: center;
            }

            .logo {
                height: 80px;
                width: auto;
                filter: brightness(1.1);
                margin-left: 20px;
            }

            .content {
                max-width: 1550px;
                margin: 0 auto;
                padding: 20px;
            }

            .section { 
                background: white;
                margin: 20px 0; 
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 1520px;
                margin-left: auto;
                margin-right: auto;
            }

            .section h2, .section h3 { 
                color: var(--primary-color); 
                border-bottom: 3px solid var(--primary-color); 
                padding-bottom: 15px;
                margin-bottom: 20px;
                margin-top: 0;
                font-weight: 700;
                font-size: 1.8em;
            }

            .section h3 {
                font-size: 1.5em;
                font-weight: 600;
            }

            .navigation { 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid var(--primary-color);
            }

            .navigation a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
                display: inline-block;
                margin: 5px;
            }

            .navigation a:hover {
                background: var(--primary-color);
                color: white;
            }

            .summary-box { 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid #1976d2;
            }

            .summary-box h3 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.4em;
            }

            .summary-box ul {
                list-style: none;
                padding: 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }

            .summary-box li {
                padding: 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.7);
                font-size: 1.1em;
                text-align: center;
            }

            .summary-box li:hover {
                background: rgba(255, 255, 255, 0.9);
            }

            .summary-box strong {
                color: var(--primary-color);
                display: block;
                font-size: 0.9em;
                margin-bottom: 5px;
            }

            .table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 25px 0; 
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .table-responsive {
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }

            .table th, .table td { 
                padding: 15px 12px; 
                text-align: center; 
                border-bottom: 1px solid #e0e0e0;
            }

            .table th { 
                background: #6c757d;
                color: white;
                font-weight: 600;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .table tbody tr {
                transition: all 0.3s ease;
            }

            .table tbody tr:nth-child(even) {
                background-color: #f8f9fa;
            }

            .table tbody tr:hover {
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                transform: scale(1.01);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .pie-container { 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin: 25px 0;
            }

            .comparison-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .comparison-grid-four {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }

            .comparison-grid-two {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 25px 0;
            }

            .comparison-grid-four .comparison-card {
                padding: 20px;
                border-radius: 12px;
            }

            .comparison-card {
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
            }

            .comparison-card:hover {
                box-shadow: var(--hover-shadow);
                transform: translateY(-2px);
            }

            .comparison-card.citywide {
                background: linear-gradient(135deg, #e8f4f8, #d6eaf8);
            }

            .comparison-card.borough {
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }

            .comparison-card.district {
                background: linear-gradient(135deg, #f0f8e8, #e8f8d6);
            }

            .comparison-card.school {
                background: linear-gradient(135deg, #fff8e1, #ffe0b2);
            }

            .comparison-card h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }

            .comparison-card ul {
                list-style: none;
                padding: 0;
            }

            .comparison-card li {
                padding: 8px 0;
                border-bottom: 1px solid rgba(46, 134, 171, 0.1);
                font-size: 1.1em;
            }

            .comparison-card li:last-child {
                border-bottom: none;
            }

            /* Highlighted metrics - key performance indicators */
            .comparison-card li.highlight-metric {
                color: #1a365d;
                font-weight: 600;
                font-size: 1.15em;
            }

            .comparison-card li.highlight-metric strong {
                color: #2c5aa0;
            }

            /* Secondary metrics - supporting information with lighter styling */
            .comparison-card li.secondary-metric {
                color: #666666;
                font-size: 1.0em;
            }

            .comparison-card li.secondary-metric strong {
                color: #888888;
                font-weight: 500;
            }

            .links-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .links-section {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .links-section h4 {
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 600;
            }

            .links-section ul {
                list-style: none;
                padding: 0;
            }

            .links-section li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .links-section a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .links-section a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .district-links {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .district-links ul {
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }

            .district-links li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .district-links a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .district-links a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .borough-links {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .borough-links ul {
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }

            .borough-links li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .borough-links a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .borough-links a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .superintendent-links {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
            }

            .superintendent-links ul {
                list-style: none;
                padding: 0;
                columns: 2;
                column-gap: 30px;
            }

            .superintendent-links li {
                padding: 8px 0;
                break-inside: avoid;
            }

            .superintendent-links a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
            }

            .superintendent-links a:hover {
                background: var(--primary-color);
                color: white;
                transform: translateX(5px);
            }

            .chart-container { 
                margin: 25px 0; 
                text-align: center;
                background: white;
                padding: 20px 0;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                border: 1px solid #e0e0e0;
                overflow: hidden;
                max-width: 100%;
            }

            .chart-container iframe {
                max-width: 100%;
                border: none;
                display: block;
                margin: 0 auto;
            }

            .footer {
                background-color: var(--primary-color);
                color: white;
                text-align: center;
                padding: 30px 20px;
                margin-top: 40px;
                font-size: 1.1em;
            }

            .footer p {
                margin: 8px 0;
            }

            .footer a {
                color: #e3f2fd;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            .footer a:hover {
                text-decoration: underline;
                color: #FFD700;
            }

            iframe {
                border: none;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
            }

            iframe:hover {
                box-shadow: var(--hover-shadow);
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }

                .header {
                    padding: 20px;
                }

                .header h1 {
                    font-size: 1.8em;
                }

                .content {
                    padding: 15px;
                }

                .section {
                    padding: 20px;
                    margin: 15px 0;
                }

                .pie-container {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }

                .comparison-grid {
                    grid-template-columns: 1fr;
                }

                .comparison-grid-four {
                    grid-template-columns: 1fr;
                }

                .comparison-grid-two {
                    grid-template-columns: 1fr;
                }

                .summary-box ul {
                    grid-template-columns: 1fr;
                }

                .links-grid {
                    grid-template-columns: 1fr;
                }

                .district-links ul {
                    columns: 1;
                }

                iframe {
                    width: 100% !important;
                    height: 450px !important;
                    max-width: 100%;
                }
            }

            /* Print Styles */
            /* Tabbed Tables */
            .tabbed-container {
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: var(--card-shadow);
            }

            .tab-buttons {
                display: flex;
                background: var(--light-bg);
                border-bottom: 2px solid #ddd;
            }

            .tab-button {
                background: none;
                border: none;
                padding: 15px 25px;
                cursor: pointer;
                font-size: 1.1em;
                font-weight: 600;
                color: #666;
                transition: all 0.3s ease;
                border-bottom: 3px solid transparent;
                flex: 1;
                text-align: center;
            }

            .tab-button:hover {
                background: rgba(46, 134, 171, 0.1);
                color: var(--primary-color);
            }

            .tab-button.active {
                background: white;
                color: var(--primary-color);
                border-bottom-color: var(--primary-color);
            }

            .tab-content {
                display: none;
                padding: 0;
            }

            .tab-content.active {
                display: block;
            }

            .tab-content .table-responsive {
                margin: 0;
                border-radius: 0;
            }

            .tab-content table {
                margin: 0;
                border-radius: 0;
            }

            .tab-content table thead th {
                background: var(--light-bg);
                font-weight: 600;
                color: var(--primary-color);
            }

            /* Print styles for tabs */
            @media print {
                .tab-buttons {
                    display: none;
                }
                
                .tab-content {
                    display: block !important;
                    page-break-inside: avoid;
                    margin-bottom: 20px;
                }
                
                .tab-content:before {
                    content: attr(data-tab-title);
                    display: block;
                    font-weight: bold;
                    font-size: 1.2em;
                    color: var(--primary-color);
                    margin-bottom: 10px;
                    border-bottom: 2px solid var(--primary-color);
                    padding-bottom: 5px;
                }
            }

            @media print {
                body {
                    background: white;
                }

                .section {
                    break-inside: avoid;
                    page-break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid #ddd;
                }

                .header {
                    background: white !important;
                    color: black !important;
                    border: 2px solid var(--primary-color);
                }

                iframe {
                    display: none;
                }
            }
            
            /* Map Styles */
            .map-summary {
                margin: 20px 0;
            }

            .summary-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .stat-card {
                background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: var(--card-shadow);
                transition: all 0.3s ease;
                border: 1px solid rgba(46, 134, 171, 0.2);
            }

            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: var(--hover-shadow);
            }

            .stat-card h4 {
                color: var(--primary-color);
                margin-bottom: 10px;
                font-size: 1.1em;
                font-weight: 600;
            }

            .stat-value {
                font-size: 1.8em;
                font-weight: 700;
                color: var(--secondary-color);
                margin-top: 5px;
            }

            .map-notes {
                background: var(--light-bg);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid var(--primary-color);
                margin-top: 15px;
            }

            @media (max-width: 768px) {
                .summary-stats-grid {
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                }

                .stat-card {
                    padding: 15px;
                }

                .stat-value {
                    font-size: 1.5em;
                }
            }

            /* School Links Grid Styling */
            .school-links {
                margin-top: 30px;
                padding: 20px;
                background: white;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }

            .school-links h3 {
                color: var(--primary-color);
                margin-bottom: 20px;
                font-size: 1.4em;
                font-weight: 600;
                text-align: center;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 10px;
            }

            .schools-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }

            .school-link-card {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 20px;
                text-decoration: none;
                color: #495057;
                transition: all 0.3s ease;
                display: block;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            .school-link-card:hover {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                text-decoration: none;
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(46, 134, 171, 0.3);
                border-color: var(--primary-color);
            }

            .school-link-card:active {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(46, 134, 171, 0.2);
            }

            .school-link-card .school-name {
                font-weight: 600;
                font-size: 1.1em;
                margin-bottom: 8px;
                line-height: 1.3;
            }

            .school-link-card .school-details {
                font-size: 0.9em;
                opacity: 0.8;
                margin-bottom: 4px;
            }

            .school-link-card .school-metrics {
                font-size: 0.85em;
                opacity: 0.7;
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid rgba(0,0,0,0.1);
            }

            .school-link-card:hover .school-metrics {
                border-top-color: rgba(255,255,255,0.3);
            }

            .no-schools-message {
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 40px 20px;
                background: rgba(108, 117, 125, 0.05);
                border-radius: 8px;
                border: 1px dashed #dee2e6;
            }

            /* Responsive adjustments for school links */
            @media (max-width: 768px) {
                .schools-grid {
                    grid-template-columns: 1fr;
                    gap: 12px;
                }
                
                .school-link-card {
                    padding: 15px;
                }
                
                .school-link-card .school-name {
                    font-size: 1em;
                }
            }

            @media (max-width: 480px) {
                .school-links {
                    margin: 20px 10px;
                    padding: 15px;
                }
                
                .school-link-card {
                    padding: 12px;
                }
            }
    """

def get_base_javascript():
    """Return the base JavaScript used across all reports with DataTables fix"""
    return """
        $(document).ready(function() {
            // Function to initialize DataTables on visible tables only
            function initializeVisibleDataTables() {
                // Only initialize on tables that are visible and not already initialized
                $('.tab-content.active table.table:visible').each(function() {
                    var $table = $(this);
                    
                    // Skip if already initialized
                    if ($.fn.DataTable.isDataTable(this)) {
                        return;
                    }
                    
                    // Validate table structure before initialization
                    var headerCount = $table.find('thead tr:first th').length;
                    var bodyRowCount = $table.find('tbody tr').length;
                    
                    // Only initialize if table has proper structure
                    if (headerCount > 0 && bodyRowCount > 0) {
                        try {
                            $table.DataTable({
                                paging: false, 
                                searching: true, 
                                info: false, 
                                order: [],
                                responsive: true,
                                autoWidth: false,
                                columnDefs: [
                                    { targets: '_all', className: 'text-center' }
                                ]
                            });
                        } catch (e) {
                            console.warn('DataTable initialization failed for table:', e);
                        }
                    }
                });
            }
            
            // Tab functionality with minimal DataTable interference
            $('.tab-button').click(function() {
                var targetTab = $(this).data('tab');
                var container = $(this).closest('.tabbed-container');
                
                // Remove active class from all buttons and content in this container
                container.find('.tab-button').removeClass('active');
                container.find('.tab-content').removeClass('active');
                
                // Add active class to clicked button and corresponding content
                $(this).addClass('active');
                container.find('.tab-content[data-tab="' + targetTab + '"]').addClass('active');
                
                // Initialize DataTables for newly visible tables
                setTimeout(function() {
                    initializeVisibleDataTables();
                }, 100);
            });
            
            // Activate first tab by default
            $('.tabbed-container').each(function() {
                $(this).find('.tab-button:first').addClass('active');
                $(this).find('.tab-content:first').addClass('active');
            });
            
            // Initialize DataTables for initially visible tables after DOM is ready
            setTimeout(function() {
                initializeVisibleDataTables();
            }, 150);
            
            // Handle window resize to adjust responsive features
            $(window).on('resize', function() {
                $('.tab-content.active table.table').each(function() {
                    if ($.fn.DataTable.isDataTable(this)) {
                        $(this).DataTable().columns.adjust().responsive.recalc();
                    }
                });
            });
        });
    """

def generate_clean_table_html(df, formatters=None):
    """
    Generate clean HTML table with consistent structure for DataTables
    Preserves existing formatting and links from the DataFrame
    """
    
    if df.empty:
        return '<p><em>No data available.</em></p>'
    
    # Use pandas to_html but with clean classes - this preserves all formatting and links
    html = df.to_html(
        index=False, 
        classes="table table-striped", 
        border=1, 
        escape=False,  # This preserves HTML links and formatting
        table_id=None
    )
    
    return html

def get_html_template(title, logo_path, content, extra_css="", extra_js=""):
    """
    Generate a complete HTML template for reports
    
    Args:
        title: Page title
        logo_path: Relative path to logo file
        content: HTML content to insert in the body
        extra_css: Additional CSS styles
        extra_js: Additional JavaScript
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
        <style>
            {get_base_css()}
            {extra_css}
        </style>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script>
            {get_base_javascript()}
            {extra_js}
        </script>
    </head>
    <body>
        {content}
    </body>
    </html>
    """

def get_header_html(logo_path, title, subtitle="", date_range_info=""):
    """Generate header HTML section"""
    return f"""
    <div class="header">
        <div class="header-content">
            <div class="header-text">
                <h1>{title}</h1>
                {f"<h2>{subtitle}</h2>" if subtitle else ""}
                {f'<div class="date-info">{date_range_info}</div>' if date_range_info else ""}
                <p>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            <div class="header-logo">
                <img src="{logo_path}" alt="NYC Public Schools" class="logo">
            </div>
        </div>
    </div>
    """

def get_professional_footer(contact_emails=None):
    """Return the professional footer HTML with NYC Public Schools branding"""
    contact_info = ""
    if contact_emails:
        contact_links = " | ".join([f'<a href="mailto:{email}" style="color: #e3f2fd;">{email}</a>' for email in contact_emails])
        contact_info = f"<p>Contact: {contact_links}</p>"
    else:
        contact_info = f"<p>Contact: <a href=\"mailto:SubCentral@schools.nyc.gov\" style=\"color: #e3f2fd;\">SubCentral@schools.nyc.gov</a></p>"
    
    return f"""
    <div class="footer">
        <p>Property of the New York City Department of Education</p>
        {contact_info}
        <p>HR School Support Analysis Team | {pd.Timestamp.now().year}</p>
    </div>
    """

def get_navigation_html(back_links):
    """
    Generate navigation HTML
    
    Args:
        back_links: List of tuples (url, text) for navigation links
    """
    links = " | ".join([f'<a href="{url}">{text}</a>' for url, text in back_links])
    return f"""
    <div class="navigation">
        {links}
    </div>
    """

def get_comparison_card_html(title, stats, card_class=""):
    """
    Generate a comparison card HTML
    
    Args:
        title: Card title
        stats: Dictionary of statistics to display
        card_class: CSS class for styling
    """
    # Define which metrics should be highlighted (prominent)
    highlight_metrics = {
        "Total SubCentral Jobs",
        "SubCentral Fill Rate", 
        "% Payroll Jobs Also in SubCentral"
    }
    
    # Separate highlighted and secondary metrics
    highlighted_items = []
    secondary_items = []
    
    for label, value in stats.items():
        if label in highlight_metrics:
            highlighted_items.append((label, value))
        else:
            secondary_items.append((label, value))
    
    # Build stats HTML with highlighted metrics first
    stats_html = ""
    
    # Add highlighted metrics first
    for label, value in highlighted_items:
        stats_html += f'<li class="highlight-metric"><strong>{label}:</strong> {value}</li>'
    
    # Add secondary metrics below
    for label, value in secondary_items:
        stats_html += f'<li class="secondary-metric"><strong>{label}:</strong> {value}</li>'
    
    return f"""
    <div class="comparison-card {card_class}">
        <h4>{title}</h4>
        <ul>
            {stats_html}
        </ul>
    </div>
    """

def create_classification_tabbed_tables(data, formatters, debug_district=False):
    """
    Create tabbed summary tables for CLASSIFICATION data with Combined Totals and Vacancy/Absence Details tabs
    Expected columns: Classification, Vacancy_Filled, Vacancy_Unfilled, Total_Vacancy, Vacancy_Fill_Pct,
                     Absence_Filled, Absence_Unfilled, Total_Absence, Absence_Fill_Pct, 
                     Total_Filled, Total_Unfilled, Total, Overall_Fill_Pct
    """
    from data_processing import format_pct, format_int
    
    if data is None or data.empty:
        return """
        <div class="tabbed-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="combined">Combined Totals</button>
                <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
            </div>
            <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
            <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
                <p><em><strong>Note:</strong> Absences are historically harder to fill. Schools with a high number of unfilled absences should be encouraged to: either record the absences at their earliest opportunity OR create vacancies to offset the number of daily absences.</em></p>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = data.copy()
    
    # Debug prints for district reports only
    if debug_district:
        print("\n=== DISTRICT CLASSIFICATION TABBED TABLE DEBUG ===")
        print(f"Input DataFrame shape: {df_copy.shape}")
        print(f"Input DataFrame columns: {list(df_copy.columns)}")
        
        # Expected columns for details tab
        expected_detail_cols = ['Vacancy_Filled', 'Vacancy_Unfilled', 'Total_Vacancy', 'Vacancy_Fill_Pct',
                               'Absence_Filled', 'Absence_Unfilled', 'Total_Absence', 'Absence_Fill_Pct']
        print(f"Expected detail columns: {expected_detail_cols}")
        
        # Check which columns are present
        missing_cols = [col for col in expected_detail_cols if col not in df_copy.columns]
        present_cols = [col for col in expected_detail_cols if col in df_copy.columns]
        print(f"Present detail columns: {present_cols}")
        if missing_cols:
            print(f"Missing detail columns: {missing_cols}")
        else:
            print("✓ All required detail columns are present")
        
        print(f"Sample data:\n{df_copy.head()}")
        print("=== END DISTRICT DEBUG ===\n")
    
    # Build Combined Totals DataFrame - exactly like your working example
    combined_df = pd.DataFrame()
    combined_df['Classification'] = df_copy['Classification']
    combined_df['Total Filled'] = df_copy['Total_Filled'].apply(formatters.get('Total_Filled', format_int))
    combined_df['Total Unfilled'] = df_copy['Total_Unfilled'].apply(formatters.get('Total_Unfilled', format_int))
    combined_df['Total Jobs'] = df_copy['Total'].apply(formatters.get('Total', format_int))
    combined_df['Fill Rate %'] = df_copy['Overall_Fill_Pct'].apply(formatters.get('Overall_Fill_Pct', format_pct))
    
    # Build Details DataFrame - exactly like your working example
    details_df = pd.DataFrame()
    details_df['Classification'] = df_copy['Classification']
    details_df['Vacancy Filled'] = df_copy['Vacancy_Filled'].apply(formatters.get('Vacancy_Filled', format_int))
    details_df['Vacancy Unfilled'] = df_copy['Vacancy_Unfilled'].apply(formatters.get('Vacancy_Unfilled', format_int))
    details_df['Total Vacancy'] = df_copy['Total_Vacancy'].apply(formatters.get('Total_Vacancy', format_int))
    details_df['Vacancy Fill %'] = df_copy['Vacancy_Fill_Pct'].apply(formatters.get('Vacancy_Fill_Pct', format_pct))
    details_df['Absence Filled'] = df_copy['Absence_Filled'].apply(formatters.get('Absence_Filled', format_int))
    details_df['Absence Unfilled'] = df_copy['Absence_Unfilled'].apply(formatters.get('Absence_Unfilled', format_int))
    details_df['Total Absence'] = df_copy['Total_Absence'].apply(formatters.get('Total_Absence', format_int))
    details_df['Absence Fill %'] = df_copy['Absence_Fill_Pct'].apply(formatters.get('Absence_Fill_Pct', format_pct))
    
    # Add TOTALS row at the bottom of both tables
    t_total = df_copy['Total'].sum()
    t_filled = df_copy['Total_Filled'].sum()
    t_unfilled = df_copy['Total_Unfilled'].sum()
    t_fill_pct = t_filled / t_total * 100 if t_total > 0 else 0
    t_vac = df_copy['Total_Vacancy'].sum()
    t_vac_filled = df_copy['Vacancy_Filled'].sum()
    t_vac_unfilled = df_copy['Vacancy_Unfilled'].sum()
    t_vac_pct = t_vac_filled / t_vac * 100 if t_vac > 0 else 0
    t_abs = df_copy['Total_Absence'].sum()
    t_abs_filled = df_copy['Absence_Filled'].sum()
    t_abs_unfilled = df_copy['Absence_Unfilled'].sum()
    t_abs_pct = t_abs_filled / t_abs * 100 if t_abs > 0 else 0
    combined_df = pd.concat([combined_df, pd.DataFrame([{
        'Classification': '<strong>TOTAL</strong>',
        'Total Filled': f'<strong>{format_int(t_filled)}</strong>',
        'Total Unfilled': f'<strong>{format_int(t_unfilled)}</strong>',
        'Total Jobs': f'<strong>{format_int(t_total)}</strong>',
        'Fill Rate %': f'<strong>{format_pct(t_fill_pct)}</strong>',
    }])], ignore_index=True)
    details_df = pd.concat([details_df, pd.DataFrame([{
        'Classification': '<strong>TOTAL</strong>',
        'Vacancy Filled': f'<strong>{format_int(t_vac_filled)}</strong>',
        'Vacancy Unfilled': f'<strong>{format_int(t_vac_unfilled)}</strong>',
        'Total Vacancy': f'<strong>{format_int(t_vac)}</strong>',
        'Vacancy Fill %': f'<strong>{format_pct(t_vac_pct)}</strong>',
        'Absence Filled': f'<strong>{format_int(t_abs_filled)}</strong>',
        'Absence Unfilled': f'<strong>{format_int(t_abs_unfilled)}</strong>',
        'Total Absence': f'<strong>{format_int(t_abs)}</strong>',
        'Absence Fill %': f'<strong>{format_pct(t_abs_pct)}</strong>',
    }])], ignore_index=True)
    
    # Debug the DataFrame structure before converting to HTML
    if debug_district:
        print(f"Combined DataFrame shape: {combined_df.shape}, columns: {list(combined_df.columns)}")
        print(f"Details DataFrame shape: {details_df.shape}, columns: {list(details_df.columns)}")
    
    # Generate clean HTML tables - USE THE HELPER FUNCTION
    combined_html = generate_clean_table_html(combined_df)
    details_html = generate_clean_table_html(details_df)
    
    return f"""
    <div class="tabbed-container">
        <div class="tab-buttons">
            <button class="tab-button active" data-tab="combined">Combined Totals</button>
            <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
        </div>
        
        <div class="tab-content active" data-tab="combined" data-tab-title="Combined Totals">
            <div class="table-responsive">{combined_html}</div>
        </div>
        
        <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
            <div class="table-responsive">{details_html}</div>
            <p><em><strong>Note:</strong> Absences are historically harder to fill. Schools with a high number of unfilled absences should be encouraged to: either record the absences at their earliest opportunity OR create vacancies to offset the number of daily absences.</em></p>
        </div>
    </div>
    """

def create_district_tabbed_tables(data, formatters):
    """
    Create tabbed summary tables for DISTRICT data with Combined Totals and Vacancy/Absence Details tabs
    Expected columns: District, Vacancy_Filled, Vacancy_Unfilled, Total_Vacancy, Vacancy_Fill_Pct,
                     Absence_Filled, Absence_Unfilled, Total_Absence, Absence_Fill_Pct, 
                     Total_Filled, Total_Unfilled, Total, Overall_Fill_Pct
    """
    # Use provided formatters, with fallbacks
    def safe_format_int(x):
        if pd.isna(x) or x == '' or x == 'Unknown':
            return str(x)
        try:
            return f"{int(float(x)):,}"
        except (ValueError, TypeError):
            return str(x)
    
    def safe_format_pct(x):
        if pd.isna(x) or x == '' or x == 'Unknown':
            return str(x)
        try:
            return f"{float(x):.1f}%"
        except (ValueError, TypeError):
            return str(x)
    
    # Get formatters or use defaults
    format_int = formatters.get('Total Jobs', safe_format_int) if formatters else safe_format_int
    format_pct = formatters.get('Fill Rate %', safe_format_pct) if formatters else safe_format_pct
    district_formatter = formatters.get('District', lambda x: str(int(float(x))) if pd.notna(x) and x != '' else x) if formatters else lambda x: str(int(float(x))) if pd.notna(x) and x != '' else x
    
    if data is None or data.empty:
        return """
        <div class="tabbed-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="combined">Combined Totals</button>
                <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
            </div>
            <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
            <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = data.copy()
    
    # Sort by Fill Rate (lowest to highest) for administrative reports
    df_copy = df_copy.sort_values('Fill Rate %', ascending=True)
    
    # Build Combined Totals DataFrame - exactly like your working example
    combined_df = pd.DataFrame()
    combined_df['District'] = df_copy['District'].apply(district_formatter)
    combined_df['Total Filled'] = df_copy['Total_Filled'].apply(format_int)
    combined_df['Total Unfilled'] = df_copy['Total_Unfilled'].apply(format_int)
    combined_df['Total Jobs'] = df_copy['Total Jobs'].apply(format_int)
    combined_df['Fill Rate %'] = df_copy['Fill Rate %'].apply(format_pct)
    
    # Build Details DataFrame - exactly like your working example
    details_df = pd.DataFrame()
    details_df['District'] = df_copy['District'].apply(district_formatter)
    details_df['Vacancy Filled'] = df_copy['Vacancy_Filled'].apply(format_int)
    details_df['Vacancy Unfilled'] = df_copy['Vacancy_Unfilled'].apply(format_int)
    details_df['Total Vacancy'] = df_copy['Total_Vacancy'].apply(format_int)
    details_df['Vacancy Fill %'] = df_copy['Vacancy_Fill_Pct'].apply(format_pct)
    details_df['Absence Filled'] = df_copy['Absence_Filled'].apply(format_int)
    details_df['Absence Unfilled'] = df_copy['Absence_Unfilled'].apply(format_int)
    details_df['Total Absence'] = df_copy['Total_Absence'].apply(format_int)
    details_df['Absence Fill %'] = df_copy['Absence_Fill_Pct'].apply(format_pct)
    
    # Generate HTML tables exactly like your working example
    combined_html = combined_df.to_html(index=False, classes=None, border=1, escape=False).replace('<table border="1" class="dataframe">', '<table border="1" class="table table-striped">')
    details_html = details_df.to_html(index=False, classes=None, border=1, escape=False).replace('<table border="1" class="dataframe">', '<table border="1" class="table table-striped">')
    
    return f"""
    <div class="tabbed-container">
        <div class="tab-buttons">
            <button class="tab-button" data-tab="combined">Combined Totals</button>
            <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
        </div>
        
        <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
            <div class="table-responsive">{combined_html}</div>
        </div>
        
        <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
            <div class="table-responsive">{details_html}</div>
        </div>
    </div>
    """

def create_borough_tabbed_tables(data, formatters):
    """
    Create tabbed summary tables for BOROUGH data with Combined Totals and Vacancy/Absence Details tabs
    Expected columns: Borough, Vacancy_Filled, Vacancy_Unfilled, Total_Vacancy, Vacancy_Fill_Pct,
                     Absence_Filled, Absence_Unfilled, Total_Absence, Absence_Fill_Pct, 
                     Total_Filled, Total_Unfilled, Total, Overall_Fill_Pct
    """
    from data_processing import format_pct, format_int
    
    if data is None or data.empty:
        return """
        <div class="tabbed-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="combined">Combined Totals</button>
                <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
            </div>
            <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
            <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = data.copy()
    
    # Sort by Fill Rate % from lowest to highest
    df_copy = df_copy.sort_values('Fill Rate %', ascending=True)
    
    # Build Combined Totals DataFrame - exactly like your working example
    combined_df = pd.DataFrame()
    combined_df['Borough'] = df_copy['Borough']
    combined_df['Total Filled'] = df_copy['Total_Filled'].apply(format_int)
    combined_df['Total Unfilled'] = df_copy['Total_Unfilled'].apply(format_int)
    combined_df['Total Jobs'] = df_copy['Total Jobs'].apply(format_int)
    combined_df['Fill Rate %'] = df_copy['Fill Rate %'].apply(format_pct)
    
    # Build Details DataFrame - exactly like your working example
    details_df = pd.DataFrame()
    details_df['Borough'] = df_copy['Borough']
    details_df['Vacancy Filled'] = df_copy['Vacancy_Filled'].apply(format_int)
    details_df['Vacancy Unfilled'] = df_copy['Vacancy_Unfilled'].apply(format_int)
    details_df['Total Vacancy'] = df_copy['Total_Vacancy'].apply(format_int)
    details_df['Vacancy Fill %'] = df_copy['Vacancy_Fill_Pct'].apply(format_pct)
    details_df['Absence Filled'] = df_copy['Absence_Filled'].apply(format_int)
    details_df['Absence Unfilled'] = df_copy['Absence_Unfilled'].apply(format_int)
    details_df['Total Absence'] = df_copy['Total_Absence'].apply(format_int)
    details_df['Absence Fill %'] = df_copy['Absence_Fill_Pct'].apply(format_pct)
    
    # Generate clean HTML tables - USE THE HELPER FUNCTION
    combined_html = generate_clean_table_html(combined_df)
    details_html = generate_clean_table_html(details_df)
    
    return f"""
    <div class="tabbed-container">
        <div class="tab-buttons">
            <button class="tab-button active" data-tab="combined">Combined Totals</button>
            <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
        </div>
        
        <div class="tab-content active" data-tab="combined" data-tab-title="Combined Totals">
            <div class="table-responsive">{combined_html}</div>
        </div>
        
        <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
            <div class="table-responsive">{details_html}</div>
        </div>
    </div>
    """

def create_school_tabbed_tables(data, formatters):
    """
    Create tabbed summary tables for SCHOOL data with Combined Totals and Vacancy/Absence Details tabs
    Expected columns: School, Vacancy_Filled, Vacancy_Unfilled, Total_Vacancy, Vacancy_Fill_Pct,
                     Absence_Filled, Absence_Unfilled, Total_Absence, Absence_Fill_Pct, 
                     Total_Filled, Total_Unfilled, Total, Overall_Fill_Pct
    """
    from data_processing import format_pct, format_int
    
    if data is None or data.empty:
        return """
        <div class="tabbed-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="combined">Combined Totals</button>
                <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
            </div>
            <div class="tab-content" data-tab="combined" data-tab-title="Combined Totals">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
            <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
                <div class="table-responsive">
                    <p><em>No data available for this table.</em></p>
                </div>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = data.copy()
    
    # Sort by Fill Rate (lowest to highest) for administrative reports
    df_copy = df_copy.sort_values('Fill Rate %', ascending=True)
    
    # Build Combined Totals DataFrame - exactly like your working example
    combined_df = pd.DataFrame()
    combined_df['School'] = df_copy['School']
    combined_df['Total Filled'] = df_copy['Total_Filled'].apply(format_int)
    combined_df['Total Unfilled'] = df_copy['Total_Unfilled'].apply(format_int)
    combined_df['Total Jobs'] = df_copy['Total Jobs'].apply(format_int)
    combined_df['Fill Rate %'] = df_copy['Fill Rate %'].apply(format_pct)
    if 'Avg Jobs Per Day' in df_copy.columns:
        combined_df['Avg Jobs Per Day'] = df_copy['Avg Jobs Per Day'].apply(
            lambda x: f"{float(x):.1f}" if pd.notna(x) else '0.0'
        )
    
    # Build Details DataFrame - exactly like your working example
    details_df = pd.DataFrame()
    details_df['School'] = df_copy['School']
    details_df['Vacancy Filled'] = df_copy['Vacancy_Filled'].apply(format_int)
    details_df['Vacancy Unfilled'] = df_copy['Vacancy_Unfilled'].apply(format_int)
    details_df['Total Vacancy'] = df_copy['Total_Vacancy'].apply(format_int)
    details_df['Vacancy Fill %'] = df_copy['Vacancy_Fill_Pct'].apply(format_pct)
    details_df['Absence Filled'] = df_copy['Absence_Filled'].apply(format_int)
    details_df['Absence Unfilled'] = df_copy['Absence_Unfilled'].apply(format_int)
    details_df['Total Absence'] = df_copy['Total_Absence'].apply(format_int)
    details_df['Absence Fill %'] = df_copy['Absence_Fill_Pct'].apply(format_pct)
    
    # Generate clean HTML tables - USE THE HELPER FUNCTION
    combined_html = generate_clean_table_html(combined_df)
    details_html = generate_clean_table_html(details_df)
    
    return f"""
    <div class="tabbed-container">
        <div class="tab-buttons">
            <button class="tab-button active" data-tab="combined">Combined Totals</button>
            <button class="tab-button" data-tab="details">Vacancy and Absence Details</button>
        </div>
        
        <div class="tab-content active" data-tab="combined" data-tab-title="Combined Totals">
            <div class="table-responsive">{combined_html}</div>
        </div>
        
        <div class="tab-content" data-tab="details" data-tab-title="Vacancy and Absence Details">
            <div class="table-responsive">{details_html}</div>
        </div>
    </div>
    """

# Keep the old function for backward compatibility but make it call the appropriate new function
def create_tabbed_summary_tables(data, formatters):
    """
    Backward compatibility function - determines whether to use classification or school tables
    """
    if 'Classification' in data.columns:
        return create_classification_tabbed_tables(data, formatters)
    elif 'School' in data.columns:
        return create_school_tabbed_tables(data, formatters)
    else:
        # Fallback - use classification function and let it handle the error
        return create_classification_tabbed_tables(data, formatters)


def create_simple_table_with_tabbed_styling(df, formatters):
    """Create a simple table with the same styling as tabbed tables but without tabs"""
    if df is None or df.empty:
        return """
        <div class="tab-content active">
            <div class="table-responsive">
                <p><em>No data available for this table.</em></p>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Apply formatters to create display values  
    for col, formatter in formatters.items():
        if col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].apply(formatter)
            except Exception as e:
                print(f"Warning: Error formatting column {col}: {e}")
    
    table_html = df_copy.to_html(
        index=False,
        classes='table table-striped',
        escape=False
    )
    
    final_html = f"""
    <div class="tab-content active">
        <div class="table-responsive">{table_html}</div>
    </div>
    """
    
    return final_html

def create_conditional_formatted_table(df, formatters, match_col='Match Percentage', table_id='payroll-analysis-table'):
    """Create a simple table with conditional formatting for match percentages"""
    
    # Validate inputs
    if df is None or df.empty:
        return """
        <div class="tab-content active">
            <div class="table-responsive">
                <p><em>No data available for this table.</em></p>
            </div>
        </div>
        """
    
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Apply formatters to create display values
    for col, formatter in formatters.items():
        if col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].apply(formatter)
            except Exception as e:
                print(f"Warning: Error formatting column {col}: {e}")
    
    # Generate table HTML manually to add conditional formatting
    html_rows = []
    
    # Header row
    header_cells = []
    for col in df_copy.columns:
        header_cells.append(f'<th>{col}</th>')
    header_html = f'<thead><tr>{"".join(header_cells)}</tr></thead>'
    
    # Data rows with conditional formatting
    data_rows = []
    for _, row in df_copy.iterrows():
        cells = []
        for col in df_copy.columns:
            cell_value = row[col]
            cell_class = ""
            
            # Apply conditional formatting for match percentage column
            if col == match_col and isinstance(row[col], str) and '%' in row[col]:
                try:
                    # Extract numeric value from percentage string
                    pct_value = float(row[col].replace('%', '').replace(',', ''))
                    if pct_value >= 90:
                        cell_class = ' style="background-color: #d4edda; color: #155724;"'  # Green (90%+)
                    elif pct_value >= 70:
                        cell_class = ' style="background-color: #fff3cd; color: #856404;"'  # Yellow (70-89%)
                    else:
                        cell_class = ' style="background-color: #f8d7da; color: #721c24; font-weight: bold;"'  # Red (<70%)
                except (ValueError, AttributeError):
                    pass
            
            cells.append(f'<td{cell_class}>{cell_value}</td>')
        data_rows.append(f'<tr>{"".join(cells)}</tr>')
    
    tbody_html = f'<tbody>{"".join(data_rows)}</tbody>'
    
    # Find the index of the match column for default sorting
    try:
        match_col_index = list(df_copy.columns).index(match_col)
    except ValueError:
        # If match column not found, default to first column
        match_col_index = 0
    
    table_html = f"""
    <table class="table table-striped sortable-table" id="{table_id}">
        {header_html}
        {tbody_html}
    </table>
    
    <script>
    $(document).ready(function() {{
        $('#{table_id}').DataTable({{
            "paging": false,
            "searching": true,
            "ordering": true,
            "info": false,
            "autoWidth": false,
            "order": [[ {match_col_index}, "asc" ]],
            "columnDefs": [
                {{ "orderable": true, "targets": "_all" }}
            ]
        }});
    }});
    </script>
    """
    
    return f"""
    <div class="tab-content active">
        <div class="table-responsive">{table_html}</div>
    </div>
    """

def create_simple_nomination_table(df, formatters, table_id='nomination-table'):
    """
    Create a simple table for nomination metrics without search/sorting features
    and with narrower columns appropriate for nomination data
    
    Args:
        df (pd.DataFrame): DataFrame with nomination data
        formatters (dict): Column formatters
        table_id (str): HTML table ID
    
    Returns:
        str: HTML table string
    """
    if df.empty:
        return "<p><em>No nomination data available.</em></p>"
    
    # Create the table HTML with custom styling for nomination tables
    table_html = f'<table id="{table_id}" class="table table-striped table-hover nomination-table">'
    
    # Create header
    table_html += '<thead class="table-dark"><tr>'
    for col in df.columns:
        # Make the metric column narrower
        width_style = 'style="width: 40%;"' if col == 'Metric' else 'style="width: 60%;"'
        table_html += f'<th {width_style}>{col}</th>'
    table_html += '</tr></thead>'
    
    # Create body
    table_html += '<tbody>'
    for _, row in df.iterrows():
        table_html += '<tr>'
        for col in df.columns:
            value = row[col]
            
            # Apply formatters if available
            if col in formatters and formatters[col]:
                try:
                    formatted_value = formatters[col](value)
                except:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)
            
            table_html += f'<td>{formatted_value}</td>'
        table_html += '</tr>'
    
    table_html += '</tbody></table>'
    
    # Add custom CSS for nomination tables
    table_html += """
    <style>
    .nomination-table {
        font-size: 0.95em;
        margin-bottom: 20px;
    }
    
    .nomination-table th {
        background-color: #343a40 !important;
        color: white !important;
        font-weight: 600;
        text-align: center;
        border: 1px solid #495057;
    }
    
    .nomination-table td {
        text-align: center;
        vertical-align: middle;
        border: 1px solid #dee2e6;
        padding: 8px 12px;
    }
    
    .nomination-table tr:hover {
        background-color: #f8f9fa;
    }
    
    .nomination-table .fw-bold {
        font-weight: bold;
    }
    
    .nomination-table .text-success {
        color: #198754 !important;
    }
    
    .nomination-table .text-info {
        color: #0dcaf0 !important;
    }
    
    .nomination-table .text-warning {
        color: #ffc107 !important;
    }
    
    .nomination-table .text-danger {
        color: #dc3545 !important;
    }
    </style>
    """
    
    return table_html
