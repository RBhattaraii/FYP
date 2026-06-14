# Test Network Connectivity for PricePilot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PricePilot Network Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current IP addresses
Write-Host "1. Your IP Addresses:" -ForegroundColor Yellow
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}
foreach ($ip in $ips) {
    Write-Host "   - $($ip.IPAddress)" -ForegroundColor White
}
Write-Host ""

# Check if backend is running
Write-Host "2. Backend Status:" -ForegroundColor Yellow
$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    Write-Host "   [OK] Backend is running on port 8000" -ForegroundColor Green
    Write-Host "   Process: $($listening.OwningProcess)" -ForegroundColor White
} else {
    Write-Host "   [X] Backend is NOT running" -ForegroundColor Red
    Write-Host "   Start it with: cd backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor Yellow
}
Write-Host ""

# Check firewall rules
Write-Host "3. Firewall Rules:" -ForegroundColor Yellow
$rules = Get-NetFirewallRule -DisplayName "PricePilot*" -ErrorAction SilentlyContinue
if ($rules) {
    foreach ($rule in $rules) {
        $status = if ($rule.Enabled) { "[OK] Enabled" } else { "[X] Disabled" }
        Write-Host "   $status - $($rule.DisplayName)" -ForegroundColor White
    }
} else {
    Write-Host "   [X] No PricePilot firewall rules found" -ForegroundColor Red
    Write-Host "   Run fix-firewall.ps1 as Administrator" -ForegroundColor Yellow
}
Write-Host ""

# Test HTTP connection
Write-Host "4. Testing HTTP Connection:" -ForegroundColor Yellow
if ($listening) {
    $testIp = ($ips | Select-Object -First 1).IPAddress
    $url = "http://${testIp}:8000/docs"
    Write-Host "   Testing: $url" -ForegroundColor White
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "   [OK] Backend is reachable! Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "   [X] Cannot reach backend: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   This means firewall is still blocking" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [SKIP] Skipped (backend not running)" -ForegroundColor Gray
}
Write-Host ""

# Check Windows Firewall status
Write-Host "5. Windows Firewall Status:" -ForegroundColor Yellow
$profiles = Get-NetFirewallProfile
foreach ($profile in $profiles) {
    $status = if ($profile.Enabled) { "ON" } else { "OFF" }
    Write-Host "   [$status] - $($profile.Name) Profile" -ForegroundColor White
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Recommendations
Write-Host "Recommendations:" -ForegroundColor Yellow
if (-not $listening) {
    Write-Host "  1. Start the backend first" -ForegroundColor White
}
if (-not $rules) {
    Write-Host "  2. Run fix-firewall.ps1 as Administrator" -ForegroundColor White
}
if ($listening -and $rules) {
    Write-Host "  [OK] Everything looks good! Try the mobile app now." -ForegroundColor Green
}
Write-Host ""

pause
