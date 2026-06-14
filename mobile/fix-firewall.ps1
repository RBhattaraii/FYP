# Run this script as Administrator to allow Expo through Windows Firewall

Write-Host "🔥 Adding Firewall Rules for Expo..." -ForegroundColor Cyan

# Allow port 8081 (Metro Bundler)
New-NetFirewallRule -DisplayName "Expo Metro Bundler" -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow -ErrorAction SilentlyContinue
Write-Host "✅ Port 8081 allowed (Metro Bundler)" -ForegroundColor Green

# Allow ports 19000-19001 (Expo DevTools)
New-NetFirewallRule -DisplayName "Expo DevTools" -Direction Inbound -Protocol TCP -LocalPort 19000-19001 -Action Allow -ErrorAction SilentlyContinue
Write-Host "✅ Ports 19000-19001 allowed (Expo DevTools)" -ForegroundColor Green

# Allow port 8000 (FastAPI Backend)
New-NetFirewallRule -DisplayName "PricePilot Backend API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
Write-Host "✅ Port 8000 allowed (Backend API)" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Firewall rules added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Expo: cd mobile && npx expo start --clear" -ForegroundColor White
Write-Host "2. Scan QR code with Expo Go on your phone" -ForegroundColor White
Write-Host "3. Wait for app to load" -ForegroundColor White
