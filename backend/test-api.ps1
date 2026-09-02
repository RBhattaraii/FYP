# PricePilot API Testing Script
# Run this to test all backend endpoints

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PricePilot Backend API Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# Test 1: Root endpoint
Write-Host "1. Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
    Write-Host "   ✓ Root endpoint working" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Trigger scraping (populate database)
Write-Host "2. Triggering homepage scraping (this may take 30-60 seconds)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/scraper/trigger" -Method POST -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   ✓ Scraping completed" -ForegroundColor Green
    Write-Host "   Status: $($result.status)" -ForegroundColor Gray
    Write-Host "   Total scraped: $($result.results.total_scraped)" -ForegroundColor Gray
    Write-Host "   Platforms scraped: $($result.results.platforms_scraped)" -ForegroundColor Gray
    Write-Host "   Best deals: $($result.results.best_deals_count)" -ForegroundColor Gray
    Write-Host "   Top price drops: $($result.results.top_price_drops_count)" -ForegroundColor Gray
    Write-Host "   Saved to DB: $($result.results.saved_to_db)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Scraping failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Get scraping status
Write-Host "3. Getting scraping status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/scraper/status" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   ✓ Status retrieved" -ForegroundColor Green
    Write-Host "   Last scrape: $($result.last_scrape_time)" -ForegroundColor Gray
    Write-Host "   Next scrape: $($result.next_scrape_time)" -ForegroundColor Gray
    Write-Host "   Current products: $($result.current_products.total)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Get home screen products
Write-Host "4. Getting home screen products..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/products/home" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   ✓ Products retrieved" -ForegroundColor Green
    Write-Host "   Best deals: $($result.best_deals.Count)" -ForegroundColor Gray
    Write-Host "   Top price drops: $($result.top_price_drops.Count)" -ForegroundColor Gray
    
    if ($result.best_deals.Count -gt 0) {
        Write-Host "   Sample product: $($result.best_deals[0].title)" -ForegroundColor Gray
        Write-Host "   Price: Rs. $($result.best_deals[0].price)" -ForegroundColor Gray
        Write-Host "   Store: $($result.best_deals[0].store_name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Failed to get products: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Search products (Tier 1)
Write-Host "5. Testing tiered search (query: laptop)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/products/search?q=laptop" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   ✓ Search completed" -ForegroundColor Green
    Write-Host "   Request ID: $($result.request_id)" -ForegroundColor Gray
    Write-Host "   Tier: $($result.tier)" -ForegroundColor Gray
    Write-Host "   Complete: $($result.is_complete)" -ForegroundColor Gray
    Write-Host "   Results count: $($result.results_count)" -ForegroundColor Gray
    Write-Host "   Message: $($result.message)" -ForegroundColor Gray
    
    # Save request ID for polling
    $requestId = $result.request_id
    
    # Wait a bit for Tier 2
    Write-Host "   Waiting 5 seconds for Tier 2 scraping..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Test 6: Poll for Tier 2 results
    Write-Host ""
    Write-Host "6. Polling for Tier 2 results..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/products/search/status?request_id=$requestId" -UseBasicParsing
        $statusResult = $response.Content | ConvertFrom-Json
        Write-Host "   ✓ Status retrieved" -ForegroundColor Green
        Write-Host "   Complete: $($statusResult.is_complete)" -ForegroundColor Gray
        Write-Host "   New results: $($statusResult.new_results_count)" -ForegroundColor Gray
        Write-Host "   Message: $($statusResult.message)" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Poll failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "   ✗ Search failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: User profile (requires login first)
Write-Host "7. Testing user profile endpoint..." -ForegroundColor Yellow
Write-Host "   Note: This requires a valid JWT token" -ForegroundColor Gray
Write-Host "   Skipping for now (needs authentication)" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoints Available:" -ForegroundColor Yellow
Write-Host "  GET  $baseUrl/" -ForegroundColor White
Write-Host "  GET  $baseUrl/products/home" -ForegroundColor White
Write-Host "  GET  $baseUrl/products/search?q=<query>" -ForegroundColor White
Write-Host "  GET  $baseUrl/products/search/status?request_id=<id>" -ForegroundColor White
Write-Host "  GET  $baseUrl/auth/me (requires token)" -ForegroundColor White
Write-Host "  POST $baseUrl/scraper/trigger" -ForegroundColor White
Write-Host "  GET  $baseUrl/scraper/status" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Frontend integration - create mobile/services/api.ts" -ForegroundColor White
Write-Host "  2. Update mobile/app/(tabs)/home.tsx to fetch real data" -ForegroundColor White
Write-Host "  3. Update mobile/components/Header.tsx to show user name" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: BACKEND_INTEGRATION_COMPLETE.md" -ForegroundColor Gray
Write-Host ""
