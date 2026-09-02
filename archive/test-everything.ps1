# ============================================================================
# PricePilot - Complete System Test
# Tests backend, database, and API endpoints
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PricePilot System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$passedTests = 0
$failedTests = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$ExpectedContent = $null
    )
    
    Write-Host "[TEST] $Name" -ForegroundColor Yellow -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            
            if ($ExpectedContent -and $content -notlike "*$ExpectedContent*") {
                Write-Host " ✗ FAIL (unexpected content)" -ForegroundColor Red
                $script:failedTests++
            } else {
                Write-Host " ✓ PASS" -ForegroundColor Green
                $script:passedTests++
                return $content
            }
        } else {
            Write-Host " ✗ FAIL (Status: $($response.StatusCode))" -ForegroundColor Red
            $script:failedTests++
        }
    } catch {
        Write-Host " ✗ FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:failedTests++
        return $null
    }
}

# Test 1: Backend is running
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Backend Health Checks" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "API Documentation" -Url "$baseUrl/docs" | Out-Null
Test-Endpoint -Name "Health Check" -Url "$baseUrl/" | Out-Null

# Test 2: Products endpoint
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Products API" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$homeData = Test-Endpoint -Name "Home Screen Products" -Url "$baseUrl/products/home"

if ($homeData) {
    $bestDealsCount = $homeData.best_deals.Count
    $priceDropsCount = $homeData.top_price_drops.Count
    $totalProducts = $bestDealsCount + $priceDropsCount
    
    Write-Host ""
    Write-Host "  📦 Products found:" -ForegroundColor Cyan
    Write-Host "     - Best Deals: $bestDealsCount" -ForegroundColor White
    Write-Host "     - Price Drops: $priceDropsCount" -ForegroundColor White
    Write-Host "     - Total: $totalProducts" -ForegroundColor White
    
    if ($totalProducts -eq 0) {
        Write-Host ""
        Write-Host "  ⚠ Warning: Database is empty!" -ForegroundColor Yellow
        Write-Host "  Run scraper to populate: " -NoNewline -ForegroundColor Yellow
        Write-Host ".\trigger_scraper.ps1" -ForegroundColor Cyan
    } else {
        # Show sample product
        $sampleProduct = $homeData.best_deals[0]
        Write-Host ""
        Write-Host "  📱 Sample Product:" -ForegroundColor Cyan
        Write-Host "     Title: $($sampleProduct.title)" -ForegroundColor White
        Write-Host "     Price: Rs $($sampleProduct.price)" -ForegroundColor White
        Write-Host "     Store: $($sampleProduct.store_name)" -ForegroundColor White
        Write-Host "     Image: $($sampleProduct.image_url.Substring(0, [Math]::Min(50, $sampleProduct.image_url.Length)))..." -ForegroundColor White
    }
}

# Test 3: Search API
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Search API" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$searchData = Test-Endpoint -Name "Search (query: laptop)" -Url "$baseUrl/products/search?q=laptop"

if ($searchData) {
    Write-Host ""
    Write-Host "  🔍 Search Results:" -ForegroundColor Cyan
    Write-Host "     - Results: $($searchData.results_count)" -ForegroundColor White
    Write-Host "     - Tier: $($searchData.tier)" -ForegroundColor White
    Write-Host "     - Complete: $($searchData.is_complete)" -ForegroundColor White
    Write-Host "     - Request ID: $($searchData.request_id)" -ForegroundColor White
}

# Test 4: Auth endpoints
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Authentication API" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Test auth/me without token (should fail with 401)
Write-Host "[TEST] Auth endpoint (unauthorized)" -ForegroundColor Yellow -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/me" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host " ✗ FAIL (should return 401)" -ForegroundColor Red
    $script:failedTests++
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host " ✓ PASS (401 Unauthorized)" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host " ✗ FAIL (unexpected error)" -ForegroundColor Red
        $script:failedTests++
    }
}

# Test 5: Database connectivity
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Database Connectivity" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Test PostgreSQL (indirectly through products endpoint)
Write-Host "[TEST] PostgreSQL connection" -ForegroundColor Yellow -NoNewline
if ($homeData) {
    Write-Host " ✓ PASS (products loaded)" -ForegroundColor Green
    $script:passedTests++
} else {
    Write-Host " ✗ FAIL (could not load products)" -ForegroundColor Red
    $script:failedTests++
}

# Test 6: Mobile app requirements
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Mobile App Connectivity" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Get local IP
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" -ErrorAction SilentlyContinue | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "  Your PC IP Address: " -NoNewline -ForegroundColor Cyan
    Write-Host $ipAddress -ForegroundColor White
    Write-Host ""
    Write-Host "  Mobile device should access:" -ForegroundColor Cyan
    Write-Host "     Physical device: " -NoNewline -ForegroundColor White
    Write-Host "http://${ipAddress}:8000" -ForegroundColor Yellow
    Write-Host "     Android emulator: " -NoNewline -ForegroundColor White
    Write-Host "http://10.0.2.2:8000" -ForegroundColor Yellow
    
    # Test if port is accessible from outside
    Write-Host ""
    Write-Host "[TEST] Backend accessible from network" -ForegroundColor Yellow -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://${ipAddress}:8000/docs" -Method GET -TimeoutSec 3 -ErrorAction Stop
        Write-Host " ✓ PASS" -ForegroundColor Green
        $script:passedTests++
    } catch {
        Write-Host " ⚠ WARNING (might be firewall)" -ForegroundColor Yellow
        Write-Host "    Run: cd mobile; .\fix-firewall.ps1" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠ Could not detect IP address" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Passed: " -NoNewline -ForegroundColor Green
Write-Host $passedTests -ForegroundColor White
Write-Host "  Failed: " -NoNewline -ForegroundColor Red
Write-Host $failedTests -ForegroundColor White
Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "✓ All tests passed! System is ready." -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed. Check issues above." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
if ($totalProducts -eq 0) {
    Write-Host "  1. Populate database: .\trigger_scraper.ps1" -ForegroundColor Yellow
    Write-Host "  2. Start mobile app: cd mobile; .\fix-and-start.ps1" -ForegroundColor Yellow
} else {
    Write-Host "  1. Start mobile app: cd mobile; .\fix-and-start.ps1" -ForegroundColor Yellow
    Write-Host "  2. Open app on your device" -ForegroundColor Yellow
    Write-Host "  3. Check Home tab for products" -ForegroundColor Yellow
}
Write-Host ""
