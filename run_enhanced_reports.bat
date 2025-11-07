@echo off
REM Batch script to run school PDF generation
REM Run this from the ParaJobs Superintendent's Reports directory

echo =======================================
echo  School PDF Report Generator
echo =======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Python is available
echo.

REM Check if required files exist
if not exist "school_only_pdf_generator.py" (
    echo ERROR: school_only_pdf_generator.py not found
    echo Please make sure this script is in the correct directory
    pause
    exit /b 1
)

if not exist "school_report_pdf_generator.py" (
    echo ERROR: school_report_pdf_generator.py not found
    echo Please copy school_report_pdf_generator.py to this directory
    pause
    exit /b 1
)

if not exist "school_list.txt" (
    echo ERROR: school_list.txt not found
    echo This file should contain the list of schools to process
    pause
    exit /b 1
)

echo All required files found
echo.

REM Count schools in list
for /f %%i in ('type school_list.txt ^| find /c /v ""') do set school_count=%%i
echo Found %school_count% schools in school_list.txt
echo.

REM Show menu and run
echo What would you like to do?
echo.
echo 1. Generate PDF Reports for Listed Schools
echo 2. Show School List Information
echo 3. Edit School List (opens in notepad)
echo 4. Test ReportLab Installation
echo 5. Run Interactive Menu
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Generating PDF Reports for Listed Schools...
    python -c "from school_only_pdf_generator import generate_school_pdfs_from_list; generate_school_pdfs_from_list()"
) else if "%choice%"=="2" (
    echo.
    echo Showing School List Information...
    python -c "from school_only_pdf_generator import show_school_list_info; show_school_list_info()"
) else if "%choice%"=="3" (
    echo.
    echo Opening school list in notepad...
    notepad school_list.txt
) else if "%choice%"=="4" (
    echo.
    echo Testing ReportLab Installation...
    python -c "try: import reportlab; print('✅ ReportLab is installed'); print('Version:', reportlab.Version if hasattr(reportlab, 'Version') else 'Unknown')\nexcept ImportError: print('❌ ReportLab not installed'); print('Run: pip install reportlab')"
) else if "%choice%"=="5" (
    echo.
    echo Starting Interactive Menu...
    python school_only_pdf_generator.py
) else (
    echo Invalid choice. Please run the script again.
)

echo.
echo =======================================
echo Process completed
echo =======================================
pause