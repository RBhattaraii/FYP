@echo off
REM ============================================================================
REM PricePilot - Complete Fix Script (Batch Version)
REM Fixes: Metro bundler, backend dependencies, and verifies database
REM ============================================================================

echo.
echo ===============================================
echo   PricePilot Complete Fix Script
echo ===============================================
echo.

REM ============================================================================
REM Step 1: Fix Backend Dependencies
REM ============================================================================

echo [Step 1] Installing Backend Dependencies...
echo.

cd /d "C:\Users\NITOR 5\Desktop\FYP\backend"

if exist "venv\Scripts\activate.bat" (
    echo [OK] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo [OK] Installing Python dependencies...
pip install -r requirements.txt --upgrade

echo.
echo [OK] Backend dependencies installed!
echo.

REM ============================================================================
REM Step 2: Clear Mobile Cache
REM ============================================================================

echo [Step 2] Clearing Mobile Cache...
echo.

cd /d "C:\Users\NITOR 5\Desktop\FYP\mobile"

if exist ".expo" (
    echo [OK] Clearing .expo cache...
    rmdir /s /q ".expo"
)

if exist "node_modules\.cache" (
    echo [OK] Clearing node_modules cache...
    rmdir /s /q "node_modules\.cache"
)

echo [OK] Mobile cache cleared!
echo.

REM ============================================================================
REM Step 3: Verify Database Connection
REM ============================================================================

echo [Step 3] Verifying Database...
echo.

cd /d "C:\Users\NITOR 5\Desktop\FYP\backend"

if exist ".env" (
    echo [OK] .env file found
    findstr "DATABASE_URL=" .env >nul
    if %errorlevel% equ 0 (
        echo [OK] DATABASE_URL configured
    ) else (
        echo [ERROR] DATABASE_URL not found in .env!
        echo Please add your Supabase DATABASE_URL to .env
    )
) else (
    echo [ERROR] .env file not found!
    echo Please create .env with DATABASE_URL
)

echo.

REM ============================================================================
REM Step 4: Summary & Next Steps
REM ============================================================================

echo.
echo ===============================================
echo   Fix Complete!
echo ===============================================
echo.

echo Next Steps:
echo.
echo 1. Start Backend Server:
echo    cd C:\Users\NITOR 5\Desktop\FYP\backend
echo    venv\Scripts\activate.bat
echo    uvicorn main:app --host 0.0.0.0 --reload
echo.
echo 2. Trigger Initial Scraping:
echo    cd C:\Users\NITOR 5\Desktop\FYP\backend
echo    powershell -File trigger_scraper.ps1
echo.
echo 3. Start Mobile App:
echo    cd C:\Users\NITOR 5\Desktop\FYP\mobile
echo    npx expo start -c
echo.

echo Tips:
echo   - Metro config is now fixed for path aliases
echo   - apscheduler dependency is installed
echo   - Cache is cleared for clean start
echo.

echo Troubleshooting:
echo   - If home page is empty, run trigger_scraper.ps1
echo   - If images don't match, database might have old data
echo   - Check backend console for error messages
echo.

pause
