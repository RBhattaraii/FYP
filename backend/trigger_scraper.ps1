# PowerShell script to trigger the scraper
Write-Host "Triggering scraper..." -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/scraper/trigger" -Method POST -UseBasicParsing
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Scraper triggered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Results:" -ForegroundColor Cyan
    Write-Host "  Status: $($content.status)"
    Write-Host "  Message: $($content.message)"
    Write-Host ""
    Write-Host "Details:" -ForegroundColor Cyan
    Write-Host "  Total scraped: $($content.results.total_scraped)"
    Write-Host "  Platforms scraped: $($content.results.platforms_scraped)"
    Write-Host "  Platforms failed: $($content.results.platforms_failed)"
    Write-Host "  Best deals: $($content.results.best_deals_count)"
    Write-Host "  Top price drops: $($content.results.top_price_drops_count)"
    Write-Host "  Saved to DB: $($content.results.saved_to_db)"
    Write-Host ""
    Write-Host "✓ Database populated! Refresh your app to see products." -ForegroundColor Green
}
catch {
    Write-Host "✗ Error triggering scraper:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. Backend is running (uvicorn main:app --host 0.0.0.0 --reload)"
    Write-Host "  2. Database is connected (check backend console logs)"
    Write-Host "  3. .env file has correct DATABASE_URL"
}
