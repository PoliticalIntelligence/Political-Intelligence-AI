@echo off

cd /d "C:\Users\KCPL\Desktop\Political-Intelligence-AI"

echo ===================================
echo Using Python:
echo ===================================

venv\Scripts\python.exe -c "import sys; print(sys.executable)"

echo.
echo ===================================
echo Playwright Test
echo ===================================

venv\Scripts\python.exe -c "import playwright; print('Playwright OK')"

echo.
echo ===================================
echo Running Scraper
echo ===================================

venv\Scripts\python.exe main.py

echo.
echo Exit Code: %ERRORLEVEL%

pause