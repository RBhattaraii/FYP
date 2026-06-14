@echo off
REM ============================================================================
REM PricePilot - Complete System Test
REM This script tests all configured components automatically
REM ============================================================================

echo.
echo ============================================================================
echo PRICEPILOT - COMPLETE SYSTEM TEST
echo ============================================================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please create venv first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ============================================================================
echo TEST 1: Backend Dependencies
echo ============================================================================
echo.

echo [TEST] Checking critical packages...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] FastAPI not installed
    set TEST1=FAIL
) else (
    echo [PASS] FastAPI installed
)

pip show uvicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Uvicorn not installed
    set TEST1=FAIL
) else (
    echo [PASS] Uvicorn installed
)

pip show asyncpg >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] asyncpg not installed
    set TEST1=FAIL
) else (
    echo [PASS] asyncpg installed
)

pip show pymongo >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] pymongo not installed
    set TEST1=FAIL
) else (
    echo [PASS] pymongo installed
)

pip show bcrypt >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] bcrypt not installed
    set TEST1=FAIL
) else (
    for /f "tokens=2" %%i in ('pip show bcrypt ^| findstr "Version"') do set BCRYPT_VERSION=%%i
    echo [PASS] bcrypt installed (version: %BCRYPT_VERSION%)
    if not "%BCRYPT_VERSION:~0,3%"=="4.0" (
        echo [WARN] bcrypt version should be 4.0.1 for compatibility
    )
)

pip show passlib >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] passlib not installed
    set TEST1=FAIL
) else (
    echo [PASS] passlib installed
)

pip show python-jose >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] python-jose not installed
    set TEST1=FAIL
) else (
    echo [PASS] python-jose installed
)

echo.
echo ============================================================================
echo TEST 2: Database Connections
echo ============================================================================
echo.

echo [TEST] Testing PostgreSQL connection...
python test_connection.py >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] PostgreSQL connection failed
    set TEST2=FAIL
) else (
    echo [PASS] PostgreSQL connection successful
)

echo [TEST] Testing MongoDB connection...
python test_mongodb.py >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] MongoDB connection failed (optional)
) else (
    echo [PASS] MongoDB connection successful
)

echo.
echo ============================================================================
echo TEST 3: Password Hashing
echo ============================================================================
echo.

echo [TEST] Testing bcrypt password hashing...
python -c "from app.auth.password import hash_password, verify_password; h = hash_password('test123'); assert verify_password('test123', h), 'Verification failed'; print('[PASS] Password hashing works')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Password hashing failed
    echo [INFO] This usually means bcrypt version issue
    echo [FIX]  Run: pip uninstall bcrypt passlib -y
    echo [FIX]  Then: pip install bcrypt==4.0.1 passlib==1.7.4
    set TEST3=FAIL
) else (
    echo [PASS] Password hashing works correctly
)

echo.
echo ============================================================================
echo TEST 4: JWT Token Generation
echo ============================================================================
echo.

echo [TEST] Testing JWT token generation...
python -c "from app.auth.jwt_handler import create_access_token; t = create_access_token('test-id'); assert len(t) > 50, 'Token too short'; print('[PASS] JWT token generation works')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] JWT token generation failed
    set TEST4=FAIL
) else (
    echo [PASS] JWT token generation works correctly
)

echo.
echo ============================================================================
echo TEST 5: Test User
echo ============================================================================
echo.

echo [TEST] Creating/verifying test user...
python create_test_user.py >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Test user creation failed
    set TEST5=FAIL
) else (
    echo [PASS] Test user exists (testuser@pricepilot.com / testpass123)
)

echo.
echo ============================================================================
echo TEST 6: Complete Backend Diagnostic
echo ============================================================================
echo.

echo [TEST] Running comprehensive backend test...
echo [INFO] This may take 10-15 seconds...
python test_backend_direct.py
if %errorlevel% neq 0 (
    echo [FAIL] Backend diagnostic test failed
    set TEST6=FAIL
) else (
    echo [PASS] All backend components working
)

echo.
echo ============================================================================
echo TEST 7: Mobile App Dependencies
echo ============================================================================
echo.

cd /d "%~dp0mobile"

if not exist "node_modules\" (
    echo [FAIL] node_modules not found
    echo [INFO] Run: npm install
    set TEST7=FAIL
) else (
    echo [PASS] node_modules exists
)

if not exist "package.json" (
    echo [FAIL] package.json not found
    set TEST7=FAIL
) else (
    echo [PASS] package.json exists
    
    findstr /C:"expo" package.json >nul
    if %errorlevel% neq 0 (
        echo [FAIL] Expo not in package.json
        set TEST7=FAIL
    ) else (
        echo [PASS] Expo configured
    )
    
    findstr /C:"expo-router" package.json >nul
    if %errorlevel% neq 0 (
        echo [FAIL] expo-router not in package.json
        set TEST7=FAIL
    ) else (
        echo [PASS] expo-router configured
    )
)

echo.
echo ============================================================================
echo TEST SUMMARY
echo ============================================================================
echo.

if "%TEST1%"=="FAIL" (
    echo [FAIL] Test 1: Backend Dependencies
) else (
    echo [PASS] Test 1: Backend Dependencies
)

if "%TEST2%"=="FAIL" (
    echo [FAIL] Test 2: Database Connections
) else (
    echo [PASS] Test 2: Database Connections
)

if "%TEST3%"=="FAIL" (
    echo [FAIL] Test 3: Password Hashing
) else (
    echo [PASS] Test 3: Password Hashing
)

if "%TEST4%"=="FAIL" (
    echo [FAIL] Test 4: JWT Token Generation
) else (
    echo [PASS] Test 4: JWT Token Generation
)

if "%TEST5%"=="FAIL" (
    echo [FAIL] Test 5: Test User
) else (
    echo [PASS] Test 5: Test User
)

if "%TEST6%"=="FAIL" (
    echo [FAIL] Test 6: Backend Diagnostic
) else (
    echo [PASS] Test 6: Backend Diagnostic
)

if "%TEST7%"=="FAIL" (
    echo [FAIL] Test 7: Mobile Dependencies
) else (
    echo [PASS] Test 7: Mobile Dependencies
)

echo.
echo ============================================================================

if "%TEST1%%TEST2%%TEST3%%TEST4%%TEST5%%TEST6%%TEST7%"=="" (
    echo.
    echo [SUCCESS] ALL TESTS PASSED!
    echo.
    echo Your PricePilot system is fully configured and working!
    echo.
    echo Next steps:
    echo 1. Start backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --host 0.0.0.0 --reload
    echo 2. Start Expo: cd mobile ^&^& npm start
    echo 3. Test on phone with Expo Go app
    echo.
) else (
    echo.
    echo [WARNING] SOME TESTS FAILED!
    echo.
    echo Please check the failed tests above and apply the suggested fixes.
    echo See COMPLETE_SYSTEM_TEST.md for detailed troubleshooting.
    echo.
)

echo ============================================================================
echo.

pause
