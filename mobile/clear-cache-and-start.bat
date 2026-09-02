@echo off
echo.
echo ========================================
echo    Clearing Metro Cache and Starting
echo ========================================
echo.

echo [1/4] Stopping any running Metro bundler...
taskkill /F /IM node.exe 2>nul

echo [2/4] Clearing Metro bundler cache...
rd /s /q .expo 2>nul
rd /s /q node_modules\.cache 2>nul

echo [3/4] Clearing npm cache...
call npm cache clean --force

echo [4/4] Starting fresh Expo server...
echo.
echo ✓ Cache cleared!
echo ✓ Starting Expo with --clear flag...
echo.

call npx expo start --clear

pause
