@echo off
echo ========================================
echo PricePilot Firewall Fix
echo ========================================
echo.
echo This will configure Windows Firewall to allow
echo the backend server on port 8000.
echo.
echo You will be prompted for Administrator permission.
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%~dp0fix-firewall.ps1""' -Verb RunAs}"

echo.
echo Done! Check the PowerShell window for results.
echo.
pause
