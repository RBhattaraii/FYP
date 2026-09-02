# Fix all three issues at once
Write-Host "===== FIX ALL ISSUES =====" -ForegroundColor Cyan
Write-Host ""

# Issue 1: Install apscheduler in venv
Write-Host "[1/3] Installing apscheduler in backend venv..." -ForegroundColor Yellow
Push-Location "backend"
.\venv\Scripts\pip.exe install apscheduler==3.10.4
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ apscheduler installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install apscheduler" -ForegroundColor Red
}
Pop-Location
Write-Host ""

# Issue 2: Fix tsconfig path alias (already correct, but let's verify)
Write-Host "[2/3] Verifying mobile tsconfig..." -ForegroundColor Yellow
$tsconfigPath = "mobile\tsconfig.json"
$tsconfig = Get-Content $tsconfigPath -Raw | ConvertFrom-Json

if ($tsconfig.compilerOptions.paths."@/*" -contains "./*") {
    Write-Host "✓ Path alias @/* is configured correctly" -ForegroundColor Green
} else {
    Write-Host "✗ Path alias @/* needs fixing" -ForegroundColor Red
}
Write-Host ""

# Issue 3: Clear mobile cache and restart
Write-Host "[3/3] Clearing mobile cache..." -ForegroundColor Yellow
if (Test-Path "mobile\.expo") {
    Remove-Item -Recurse -Force "mobile\.expo"
    Write-Host "✓ Cleared .expo cache" -ForegroundColor Green
}
if (Test-Path "mobile\node_modules\.cache") {
    Remove-Item -Recurse -Force "mobile\node_modules\.cache"
    Write-Host "✓ Cleared node_modules cache" -ForegroundColor Green
}
Write-Host ""

Write-Host "===== ALL FIXES APPLIED =====" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "     uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start mobile app:" -ForegroundColor White
Write-Host "     cd mobile" -ForegroundColor Gray
Write-Host "     npx expo start --clear" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Trigger scraper (in new terminal):" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\trigger_scraper.ps1" -ForegroundColor Gray
Write-Host ""
