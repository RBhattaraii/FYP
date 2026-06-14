@echo off
echo ============================================================================
echo QUICK FIX - PricePilot Backend
echo ============================================================================
echo.

cd /d "%~dp0"

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [FIX 1] Fixing bcrypt version...
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4

echo.
echo [FIX 2] Creating test user...
python create_test_user.py

echo.
echo [FIX 3] Testing backend...
python test_backend_direct.py

echo.
echo ============================================================================
echo FIXES COMPLETE!
echo ============================================================================
echo.
echo Next steps:
echo 1. Run test_all.bat again to verify all tests pass
echo 2. Start backend: uvicorn main:app --host 0.0.0.0 --reload
echo 3. Start Expo: cd ..\mobile ^&^& npm start
echo.

pause
