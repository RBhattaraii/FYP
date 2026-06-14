@echo off
echo ========================================
echo Starting Expo with Clear Cache
echo ========================================
echo.
echo This will:
echo 1. Clear Expo cache
echo 2. Start development server
echo 3. Open QR code for scanning
echo.
echo ========================================
echo.

cd /d "%~dp0"
call npx expo start -c

pause
