# PricePilot Firewall Fix Script
# Run this as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PricePilot Firewall Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "Running as Administrator... OK" -ForegroundColor Green
Write-Host ""

# Remove old rules if they exist
Write-Host "Removing old firewall rules..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "PricePilot*" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Python Backend" -ErrorAction SilentlyContinue
Write-Host "Old rules removed" -ForegroundColor Green
Write-Host ""

# Add new comprehensive rules
Write-Host "Adding new firewall rules..." -ForegroundColor Yellow

# Rule 1: Allow Port 8000 Inbound (TCP)
Write-Host "1. Adding Port 8000 Inbound (TCP)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "PricePilot Backend Port 8000 TCP" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null
Write-Host "   Done!" -ForegroundColor Green

# Rule 2: Allow Port 8000 Outbound (TCP)
Write-Host "2. Adding Port 8000 Outbound (TCP)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "PricePilot Backend Port 8000 TCP Out" `
    -Direction Outbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null
Write-Host "   Done!" -ForegroundColor Green

# Rule 3: Allow Python Program
$pythonPath = "C:\Users\NITOR 5\Desktop\FYP\backend\venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "3. Adding Python Program Rule..." -ForegroundColor Cyan
    New-NetFirewallRule -DisplayName "PricePilot Python Backend" `
        -Direction Inbound `
        -Program $pythonPath `
        -Action Allow `
        -Profile Any `
        -Enabled True | Out-Null
    Write-Host "   Done!" -ForegroundColor Green
} else {
    Write-Host "3. Python not found at: $pythonPath" -ForegroundColor Yellow
    Write-Host "   Skipping Python program rule" -ForegroundColor Yellow
}

# Rule 4: Allow Uvicorn if found
$uvicornPath = "C:\Users\NITOR 5\Desktop\FYP\backend\venv\Scripts\uvicorn.exe"
if (Test-Path $uvicornPath) {
    Write-Host "4. Adding Uvicorn Program Rule..." -ForegroundColor Cyan
    New-NetFirewallRule -DisplayName "PricePilot Uvicorn" `
        -Direction Inbound `
        -Program $uvicornPath `
        -Action Allow `
        -Profile Any `
        -Enabled True | Out-Null
    Write-Host "   Done!" -ForegroundColor Green
} else {
    Write-Host "4. Uvicorn not found, skipping" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firewall Configuration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Display current IP
Write-Host "Your current IP addresses:" -ForegroundColor Cyan
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"} | ForEach-Object {
    Write-Host "  - $($_.IPAddress)" -ForegroundColor Yellow
}
Write-Host ""

# Test if port 8000 is listening
Write-Host "Checking if backend is running on port 8000..." -ForegroundColor Cyan
$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    Write-Host "  Backend is running on port 8000!" -ForegroundColor Green
} else {
    Write-Host "  Backend is NOT running. Start it with:" -ForegroundColor Yellow
    Write-Host "  cd backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor White
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Start backend: cd backend && uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor White
Write-Host "2. Start frontend: cd mobile && expo start -c" -ForegroundColor White
Write-Host "3. Scan QR code and test login" -ForegroundColor White
Write-Host ""

pause
