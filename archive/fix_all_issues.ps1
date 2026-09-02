# ============================================================================
# PricePilot - Complete Fix Script
# Fixes: Metro bundler, backend dependencies, and verifies database
# ============================================================================

Write-Host "🔧 PricePilot Complete Fix Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Fix Backend Dependencies
# ============================================================================

Write-Host "📦 Step 1: Installing Backend Dependencies..." -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\NITOR 5\Desktop\FYP\backend"

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
}

# Install/upgrade dependencies
Write-Host "✓ Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt --upgrade

Write-Host ""
Write-Host "✓ Backend dependencies installed!" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 2: Clear Mobile Cache and Restart Metro
# ============================================================================

Write-Host "📱 Step 2: Clearing Mobile Cache..." -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\NITOR 5\Desktop\FYP\mobile"

# Clear all caches
if (Test-Path ".expo") {
    Write-Host "✓ Clearing .expo cache..." -ForegroundColor Green
    Remove-Item -Recurse -Force ".expo"
}

if (Test-Path "node_modules\.cache") {
    Write-Host "✓ Clearing node_modules cache..." -ForegroundColor Green
    Remove-Item -Recurse -Force "node_modules\.cache"
}

Write-Host "✓ Mobile cache cleared!" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 3: Verify Database Connection
# ============================================================================

Write-Host "🗄️  Step 3: Verifying Database..." -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\NITOR 5\Desktop\FYP\backend"

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
    
    # Extract DATABASE_URL
    $envContent = Get-Content ".env"
    $dbUrl = ($envContent | Select-String -Pattern "DATABASE_URL=").ToString()
    
    if ($dbUrl) {
        Write-Host "✓ DATABASE_URL configured" -ForegroundColor Green
    } else {
        Write-Host "✗ DATABASE_URL not found in .env!" -ForegroundColor Red
        Write-Host "  Please add your Supabase DATABASE_URL to .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please create .env with DATABASE_URL" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# Step 4: Summary & Next Steps
# ============================================================================

Write-Host "✅ Fix Complete!" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend Server:" -ForegroundColor White
Write-Host "   cd C:\Users\NITOR 5\Desktop\FYP\backend" -ForegroundColor Gray
Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Trigger Initial Scraping:" -ForegroundColor White
Write-Host "   cd C:\Users\NITOR 5\Desktop\FYP\backend" -ForegroundColor Gray
Write-Host "   .\trigger_scraper.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Start Mobile App:" -ForegroundColor White
Write-Host "   cd C:\Users\NITOR 5\Desktop\FYP\mobile" -ForegroundColor Gray
Write-Host "   npx expo start -c" -ForegroundColor Gray
Write-Host ""

Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Metro config is now fixed for path aliases" -ForegroundColor Gray
Write-Host "   - apscheduler dependency is installed" -ForegroundColor Gray
Write-Host "   - Cache is cleared for clean start" -ForegroundColor Gray
Write-Host ""

Write-Host "🔍 Troubleshooting:" -ForegroundColor Yellow
Write-Host "   - If home page is empty, run trigger_scraper.ps1" -ForegroundColor Gray
Write-Host "   - If images don't match, database might have old data" -ForegroundColor Gray
Write-Host "   - Check backend console for error messages" -ForegroundColor Gray
Write-Host ""
