@echo off
echo ========================================
echo  ENHANCED SCRAPER LAUNCHER - WINDOWS
echo ========================================
echo.
echo This will launch 6 individual scrapers + 1 monitor
echo Each scraper runs in its own terminal window
echo.
echo Scrapers will run until ALL products are collected
echo Target: 100,000+ products across all platforms
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo 🚀 Starting all enhanced scrapers...
echo.

REM Launch each scraper in a new command window
echo ⚡ Launching Jeevee scraper...
start "JEEVEE SCRAPER" cmd /k "python enhanced_jeevee_scraper.py"
timeout /t 2 >nul

echo ⚡ Launching CGDigital scraper...
start "CGDIGITAL SCRAPER" cmd /k "python enhanced_cgdigital_scraper.py"
timeout /t 2 >nul

echo ⚡ Launching Hukut scraper...
start "HUKUT SCRAPER" cmd /k "python enhanced_hukut_scraper.py"
timeout /t 2 >nul

echo ⚡ Launching Oliz scraper...
start "OLIZ SCRAPER" cmd /k "python enhanced_oliz_scraper.py"
timeout /t 2 >nul

echo ⚡ Launching Better scraper...
start "BETTER SCRAPER" cmd /k "python enhanced_better_scraper.py"
timeout /t 2 >nul

echo ⚡ Launching HardwarePasal scraper...
start "HARDWAREPASAL SCRAPER" cmd /k "python enhanced_hardwarepasal_scraper.py"
timeout /t 3 >nul

echo ⚡ Launching Progress Monitor...
start "SCRAPER MONITOR" cmd /k "python scraper_monitor.py"

echo.
echo ✅ All scrapers launched successfully!
echo.
echo 📊 Monitor Window: Real-time progress tracking
echo 🔄 Scraper Windows: Individual platform scrapers
echo.
echo 💡 INSTRUCTIONS:
echo   • Each scraper runs independently until completion
echo   • Monitor window shows live progress every 30 seconds
echo   • Close individual scraper windows to stop them
echo   • Run enhanced_master_consolidator.py to merge databases
echo.
echo ⚠️  IMPORTANT:
echo   • Keep this window open to see launch status
echo   • Scrapers handle rate limiting automatically
echo   • Expected runtime: 2-8 hours depending on network
echo.
echo Press any key to exit launcher (scrapers will continue)...
pause >nul