# Troubleshooting: No Data on Home Screen

## Issue
The mobile app shows an empty home screen with no products because the database hasn't been populated yet.

## Root Cause
The database tables exist but have no product data. You need to run the scraper to populate the database.

## Solution Steps

### Step 1: Verify Backend is Running
Check that your backend terminal shows:
```
[OK] PostgreSQL connection pool created successfully
MongoDB connected successfully
[SCHEDULER] Scheduler started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If you see errors about database connection, check your `.env` file.

### Step 2: Check Database Connection
Test the root endpoint:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing
```

**Expected output:**
```json
{"message":"PricePilot API is working"}
```

### Step 3: Trigger the Scraper

**Method 1: Using PowerShell Script (Recommended)**
```powershell
cd backend
.\trigger_scraper.ps1
```

**Method 2: Using Invoke-WebRequest**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/scraper/trigger -Method POST -UseBasicParsing
```

**Method 3: Using curl.exe**
```powershell
curl.exe -X POST http://localhost:8000/scraper/trigger
```

**Method 4: Using FastAPI Docs**
1. Open http://localhost:8000/docs in browser
2. Find `POST /scraper/trigger` endpoint
3. Click "Try it out"
4. Click "Execute"

### Step 4: Wait for Scraping to Complete
Scraping takes ~30-60 seconds. Watch the backend console for progress.

**Expected console output:**
```
[API] Manual scraping triggered via /scraper/trigger
[SCRAPER] Starting daily homepage scraping...
[SCRAPER] Scraping Daraz homepage...
[SCRAPER] Found 25 products from Daraz
... (more platform logs)
[SCRAPER] Total products scraped: 150
[SCRAPER] Curating products...
[SCRAPER] Saved 50 products to database
[SCRAPER] Scraping complete!
```

### Step 5: Verify Products Were Saved
Check the products endpoint:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/products/home -UseBasicParsing
```

**Expected output:**
```json
{
  "best_deals": [
    {
      "id": 1,
      "title": "Sony Headphones",
      "price": 5999.0,
      "discount_percent": 35,
      ...
    },
    ... (24 more products)
  ],
  "top_price_drops": [
    ... (25 products)
  ]
}
```

### Step 6: Refresh Mobile App
Pull down on the home screen to refresh, or restart the app.

---

## Common Errors

### Error: "Database pool not initialized"

**Cause:** The database connection pool wasn't created on startup.

**Solution:**
1. Check backend console for database connection errors
2. Verify `DATABASE_URL` in `.env` is correct
3. Restart the backend:
   ```powershell
   # Stop: Press Ctrl+C
   # Start again:
   uvicorn main:app --host 0.0.0.0 --reload
   ```

### Error: "405 Method Not Allowed"

**Cause:** You tried to access `/scraper/trigger` via browser (GET request).

**Solution:** The endpoint requires POST. Use one of the methods in Step 3 above.

### Error: "500 Internal Server Error"

**Cause:** Scraper crashed during execution.

**Solution:**
1. Check backend console for detailed error
2. Common causes:
   - Scraping platforms are down
   - Network connectivity issues
   - MongoDB connection failed (non-critical)
   - Database query error

### Error: "timeout" or no response

**Cause:** Scraping is taking longer than expected.

**Solution:**
1. Wait up to 60 seconds for response
2. Check backend console - scraping might still be running
3. After it completes, check `/products/home` endpoint

### Products still empty after scraping

**Possible causes:**
1. **No products met the criteria:**
   - Best deals require >30% discount
   - Top price drops require significant price reduction
   - Check backend console for "Curating products..." logs

2. **Database save failed:**
   - Check for database errors in console
   - Verify PostgreSQL connection

3. **Wrong database:**
   - Make sure DATABASE_URL points to correct database
   - Check if products were saved to different database

**Debug:**
```powershell
# Check scraper status
Invoke-WebRequest -Uri http://localhost:8000/scraper/status -UseBasicParsing
```

**Expected output:**
```json
{
  "last_scrape_time": "2024-01-15T10:30:00Z",
  "last_scrape_status": "completed",
  "last_scrape_products_found": 50,
  "current_products": {
    "best_deals": 25,
    "top_price_drops": 25,
    "total": 50
  }
}
```

---

## Testing the Complete Flow

### Test 1: Backend Health
```powershell
Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing
```
✓ Should return: `{"message":"PricePilot API is working"}`

### Test 2: Empty Database
```powershell
Invoke-WebRequest -Uri http://localhost:8000/products/home -UseBasicParsing
```
✓ Should return: `{"best_deals":[],"top_price_drops":[]}`

### Test 3: Trigger Scraper
```powershell
.\trigger_scraper.ps1
```
✓ Should complete in ~30-60 seconds with success message

### Test 4: Populated Database
```powershell
Invoke-WebRequest -Uri http://localhost:8000/products/home -UseBasicParsing
```
✓ Should return: 50 products (25 best_deals + 25 top_price_drops)

### Test 5: Mobile App
1. Open mobile app
2. Pull down to refresh
3. Should see products in Trending and Recommended sections

---

## Quick Checklist

Before asking for help, verify:

- [ ] Backend is running without errors
- [ ] PostgreSQL connection successful (check startup logs)
- [ ] `.env` file exists with correct `DATABASE_URL`
- [ ] Database schema applied (`python apply_schema_migration.py`)
- [ ] Scraper triggered via POST (not GET)
- [ ] Waited for scraping to complete (~30-60 seconds)
- [ ] Checked `/products/home` endpoint returns products
- [ ] Mobile app API_URL points to correct backend IP
- [ ] Mobile app can reach backend (check network)
- [ ] Refreshed mobile app after populating database

---

## Manual Database Check (Advanced)

If everything else fails, check the database directly:

### Using Supabase Dashboard
1. Go to https://supabase.com
2. Open your project
3. Go to "Table Editor"
4. Select `home_screen_products` table
5. Should see 50 rows

### Using psql
```bash
psql "YOUR_DATABASE_URL"
SELECT COUNT(*) FROM home_screen_products;
# Should return: 50

SELECT section, COUNT(*) FROM home_screen_products GROUP BY section;
# Should return:
# best_deals       | 25
# top_price_drops  | 25
```

---

## Still Not Working?

Check the backend console logs for specific errors. Common log patterns:

**Good (Working):**
```
[OK] PostgreSQL connection pool created successfully
MongoDB connected successfully
[SCHEDULER] Scheduler started successfully
[SCRAPER] Starting daily homepage scraping...
[SCRAPER] Saved 50 products to database
```

**Bad (Not Working):**
```
[ERROR] Failed to connect to PostgreSQL
[ERROR] Database pool not initialized
[ERROR] Failed to save products to database
```

Copy the error messages and check:
1. Database connection string in `.env`
2. Network connectivity to Supabase
3. Database tables exist (run migration script)
4. Database has correct schema

---

## Need Help?

1. **Check backend console logs** - Copy the complete error message
2. **Test each endpoint individually** - Use the tests above
3. **Verify database connection** - Check Supabase dashboard
4. **Check network** - Ensure mobile device can reach backend IP

**For VIVA preparation:** Be ready to explain why the database starts empty and how the scraper populates it. This demonstrates understanding of the data flow and backend architecture.
