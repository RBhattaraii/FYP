# ============================================================================
# PricePilot Mobile - Fix and Start Script
# Clears all caches and starts fresh Metro bundler
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PricePilot Mobile - Fix & Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop any running Metro bundler
Write-Host "[1/5] Stopping Metro bundler..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Stop-Process -Name node -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Stopped running Metro processes" -ForegroundColor Green
} else {
    Write-Host "  ✓ No running Metro processes" -ForegroundColor Green
}
Start-Sleep -Seconds 1

# Step 2: Clear Metro bundler cache
Write-Host ""
Write-Host "[2/5] Clearing Metro cache..." -ForegroundColor Yellow
if (Test-Path ".expo") {
    Remove-Item -Recurse -Force ".expo" -ErrorAction SilentlyContinue
    Write-Host "  ✓ Cleared .expo cache" -ForegroundColor Green
} else {
    Write-Host "  ✓ No .expo cache found" -ForegroundColor Green
}

if (Test-Path "node_modules\.cache") {
    Remove-Item -Recurse -Force "node_modules\.cache" -ErrorAction SilentlyContinue
    Write-Host "  ✓ Cleared node_modules cache" -ForegroundColor Green
} else {
    Write-Host "  ✓ No node_modules cache found" -ForegroundColor Green
}

# Step 3: Clear watchman (if installed)
Write-Host ""
Write-Host "[3/5] Clearing watchman..." -ForegroundColor Yellow
$watchmanExists = Get-Command watchman -ErrorAction SilentlyContinue
if ($watchmanExists) {
    watchman watch-del-all 2>$null
    Write-Host "  ✓ Watchman cache cleared" -ForegroundColor Green
} else {
    Write-Host "  ⊘ Watchman not installed (OK)" -ForegroundColor Gray
}

# Step 4: Verify backend connectivity
Write-Host ""
Write-Host "[4/5] Checking backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✓ Backend is running!" -ForegroundColor Green
    
    # Check if products exist
    try {
        $productsResponse = Invoke-RestMethod -Uri "http://localhost:8000/products/home" -Method GET -TimeoutSec 3
        $totalProducts = $productsResponse.best_deals.Count + $productsResponse.top_price_drops.Count
        if ($totalProducts -gt 0) {
            Write-Host "  ✓ Found $totalProducts products in database" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Warning: Database is empty. Run scraper to add products." -ForegroundColor Yellow
            Write-Host "    Command: Invoke-WebRequest -Uri 'http://localhost:8000/scraper/trigger' -Method POST" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠ Warning: Could not check products (endpoint may have issues)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Backend not running!" -ForegroundColor Red
    Write-Host "    Please start backend first:" -ForegroundColor Yellow
    Write-Host "    cd ..\backend" -ForegroundColor Gray
    Write-Host "    .\venv\Scripts\activate" -ForegroundColor Gray
    Write-Host "    uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# Step 5: Get local IP for reference
Write-Host ""
Write-Host "[5/5] Network information..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" -ErrorAction SilentlyContinue | Select-Object -First 1).IPAddress
if ($ipAddress) {
    Write-Host "  Your PC IP: $ipAddress" -ForegroundColor Cyan
    Write-Host "  Backend URL (physical device): http://${ipAddress}:8000" -ForegroundColor Gray
    Write-Host "  Backend URL (Android emulator): http://10.0.2.2:8000" -ForegroundColor Gray
} else {
    Write-Host "  ⊘ Could not detect IP address" -ForegroundColor Gray
}

# Final step: Start Expo with cleared cache
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Expo Metro Bundler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Expo with --clear flag
npx expo start --clear
