@echo off
echo ========================================
echo PricePilot Complete Fix and Start
echo ========================================
echo.

echo Step 1: Clearing Expo cache...
cd mobile
call npx expo start -c --clear
echo.

echo ========================================
echo Cache cleared! Now follow these steps:
echo ========================================
echo.
echo 1. STOP the Expo server (Ctrl+C)
echo 2. Run fix-firewall.ps1 as Administrator
echo 3. Start backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --host 0.0.0.0 --reload
echo 4. Start mobile: cd mobile ^&^& npx expo start
echo.
pause
