@echo off
REM ============================================================================
REM PricePilot - Start Everything Script
REM Opens 3 terminals: Backend, Mobile, and Instructions
REM ============================================================================

echo.
echo ===============================================
echo   Starting PricePilot Development Environment
echo ===============================================
echo.

REM Start Backend in new terminal
echo [1/3] Starting Backend Server...
start "PricePilot - Backend Server" cmd /k "cd /d C:\Users\NITOR 5\Desktop\FYP\backend && venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --reload"

REM Wait 5 seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start Mobile in new terminal
echo [2/3] Starting Mobile App...
start "PricePilot - Mobile App" cmd /k "cd /d C:\Users\NITOR 5\Desktop\FYP\mobile && npx expo start -c"

REM Show instructions in new terminal
echo [3/3] Opening Instructions...
start "PricePilot - Instructions" cmd /k "cd /d C:\Users\NITOR 5\Desktop\FYP && echo. && echo ============================================= && echo   PricePilot Quick Commands && echo ============================================= && echo. && echo Backend Server: RUNNING (Terminal 1) && echo Mobile App: STARTING (Terminal 2) && echo. && echo Next Steps: && echo. && echo 1. Wait for Mobile to show QR code && echo. && echo 2. If home page is empty, trigger scraper: && echo    cd backend && echo    powershell -File trigger_scraper.ps1 && echo. && echo 3. Scan QR code with Expo Go app && echo. && echo 4. Check database status: && echo    cd backend && echo    python check_database.py && echo. && echo Troubleshooting: && echo    - See FIX_COMPLETE_GUIDE.md for detailed help && echo    - Backend logs in Terminal 1 && echo    - Mobile logs in Terminal 2 && echo. && echo Press any key to close this window... && pause >nul"

echo.
echo ===============================================
echo   All Services Starting!
echo ===============================================
echo.
echo Backend: Terminal 1
echo Mobile:  Terminal 2
echo Instructions: Terminal 3
echo.
echo Check the new terminal windows for progress.
echo.

timeout /t 3 /nobreak >nul
exit
