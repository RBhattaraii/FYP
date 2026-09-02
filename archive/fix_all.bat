@echo off
echo ===== FIX ALL ISSUES =====
echo.

echo [1/3] Installing apscheduler...
cd backend
call venv\Scripts\pip.exe install apscheduler==3.10.4
if %errorlevel% equ 0 (
    echo OK - apscheduler installed
) else (
    echo ERROR - Failed to install apscheduler
)
cd ..
echo.

echo [2/3] Clearing mobile .expo cache...
if exist "mobile\.expo" (
    rmdir /s /q "mobile\.expo"
    echo OK - Cleared .expo cache
) else (
    echo INFO - No .expo cache found
)
echo.

echo [3/3] Clearing mobile node_modules cache...
if exist "mobile\node_modules\.cache" (
    rmdir /s /q "mobile\node_modules\.cache"
    echo OK - Cleared node_modules cache
) else (
    echo INFO - No node_modules cache found
)
echo.

echo ===== ALL FIXES APPLIED =====
echo.
echo Next steps:
echo   1. Start backend:
echo      cd backend
echo      venv\Scripts\activate
echo      uvicorn main:app --host 0.0.0.0 --reload
echo.
echo   2. Start mobile (in new terminal):
echo      cd mobile
echo      npx expo start --clear
echo.
echo   3. Trigger scraper (in third terminal):
echo      cd backend
echo      trigger_scraper.ps1
echo.
pause
