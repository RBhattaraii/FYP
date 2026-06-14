@echo off
echo ========================================
echo PricePilot - Start Full App
echo ========================================
echo.
echo This will start:
echo 1. Backend server (FastAPI)
echo 2. Frontend server (Expo)
echo.
echo Make sure:
echo - Firewall allows port 8000
echo - Phone and computer on same WiFi
echo.
echo ========================================
echo.

echo Starting Backend...
start "PricePilot Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "PricePilot Frontend" cmd /k "cd /d %~dp0mobile && expo start -c"

echo.
echo ========================================
echo Both servers starting...
echo.
echo Backend: http://0.0.0.0:8000
echo Frontend: Check Expo terminal for QR code
echo.
echo Scan QR code with Expo Go app!
echo ========================================
echo.

pause
