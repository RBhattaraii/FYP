# ============================================================================
# PricePilot - One-Click Quick Start
# Runs system tests and starts both backend + mobile app
# ============================================================================

param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     PricePilot Quick Start             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$hasNode = Test-Command "node"
$hasPython = Test-Command "python"
$hasNpm = Test-Command "npm"

if (-not $hasNode) {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    Write-Host "  Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

if (-not $hasPython) {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "  Install from: https://python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Node.js: " -NoNewline -ForegroundColor Green
node --version
Write-Host "✓ Python: " -NoNewline -ForegroundColor Green
python --version
Write-Host "✓ npm: " -NoNewline -ForegroundColor Green
npm --version
Write-Host ""

# Step 1: Run system tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host " Step 1: Testing System" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if backend is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✓ Backend is already running" -ForegroundColor Green
        Write-Host ""
        
        # Run tests
        Write-Host "Running API tests..." -ForegroundColor Yellow
        & ".\test-everything.ps1"
        Write-Host ""
        
    } catch {
        Write-Host "⚠ Backend not running. Starting it first..." -ForegroundColor Yellow
        Write-Host ""
        
        # Start backend in background
        Write-Host "Starting backend server..." -ForegroundColor Yellow
        $backendPath = Join-Path $PSScriptRoot "backend"
        
        # Create a new PowerShell window for backend
        $backendScript = @"
Set-Location '$backendPath'
& '.\venv\Scripts\activate.ps1'
uvicorn main:app --host 0.0.0.0 --reload
"@
        
        $scriptBlock = [scriptblock]::Create($backendScript)
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {$backendScript}" -WindowStyle Normal
        
        Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Test again
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✓ Backend started successfully" -ForegroundColor Green
        } catch {
            Write-Host "✗ Backend failed to start!" -ForegroundColor Red
            Write-Host "  Please start manually:" -ForegroundColor Yellow
            Write-Host "  cd backend" -ForegroundColor Gray
            Write-Host "  .\venv\Scripts\activate" -ForegroundColor Gray
            Write-Host "  uvicorn main:app --host 0.0.0.0 --reload" -ForegroundColor Gray
            exit 1
        }
        Write-Host ""
    }
} else {
    Write-Host "⊘ Skipping tests (--SkipTests flag)" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Check if products exist
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Step 2: Checking Database" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

try {
    $productsResponse = Invoke-RestMethod -Uri "http://localhost:8000/products/home" -Method GET -TimeoutSec 5
    $totalProducts = $productsResponse.best_deals.Count + $productsResponse.top_price_drops.Count
    
    if ($totalProducts -gt 0) {
        Write-Host "✓ Found $totalProducts products in database" -ForegroundColor Green
    } else {
        Write-Host "⚠ Database is empty!" -ForegroundColor Yellow
        Write-Host ""
        $runScraper = Read-Host "Run scraper now to populate database? (y/n)"
        
        if ($runScraper -eq "y") {
            Write-Host ""
            Write-Host "Triggering scraper..." -ForegroundColor Yellow
            try {
                $scraperResponse = Invoke-RestMethod -Uri "http://localhost:8000/scraper/trigger" -Method POST -TimeoutSec 3
                Write-Host "✓ Scraper started! This will take 30-60 seconds..." -ForegroundColor Green
                Write-Host ""
                Write-Host "Waiting for scraping to complete..." -ForegroundColor Yellow
                Start-Sleep -Seconds 45
                
                # Check again
                $productsResponse = Invoke-RestMethod -Uri "http://localhost:8000/products/home" -Method GET -TimeoutSec 5
                $totalProducts = $productsResponse.best_deals.Count + $productsResponse.top_price_drops.Count
                Write-Host "✓ Now have $totalProducts products" -ForegroundColor Green
            } catch {
                Write-Host "✗ Scraper failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "⚠ Could not check products: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Start mobile app
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host " Step 3: Starting Mobile App" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$mobilePath = Join-Path $PSScriptRoot "mobile"
Set-Location $mobilePath

Write-Host "Running mobile fix-and-start script..." -ForegroundColor Yellow
Write-Host ""

# Run the fix-and-start script
& ".\fix-and-start.ps1"
