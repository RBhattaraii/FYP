@echo off
echo ========================================
echo PRICEPILOT - FRESH START WITH FIXED URLS
echo ========================================
echo.

echo Step 1: Clearing caches...
python clear_search_cache.py
python clear_home_products.py
echo.

echo Step 2: Verifying URL generation...
python quick_test.py
echo.

echo Step 3: Checking database status...
python verify_all_caches_clear.py
echo.

echo Step 4: Starting backend server...
echo Press Ctrl+C to stop the server when done
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
