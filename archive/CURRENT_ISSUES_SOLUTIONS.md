# Current Issues & Solutions

## Summary
Based on the recent logs, here are the issues and their solutions:

---

## ✅ Issue 1: APScheduler Import Error (SOLVED)
**Error:**
```
ModuleNotFoundError: No module named 'apscheduler'
```

**Status:** ✅ ALREADY INSTALLED
- APScheduler 3.10.4 is already installed in the venv
- This error occurred when running without activating the venv
- Backend should start successfully now

**Solution:**
Always activate venv before running:
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --reload
```

---

## ✅ Issue 2: Scraper 405 Error (EXPLAINED)
**Error:**
```
INFO: 127.0.0.1:53085 - "GET /scraper/trigger HTTP/1.1" 405 Method Not Allowed
```

**Cause:** You tried to access `/scraper/trigger` from a browser (which uses GET)
**Fix:** The endpoint requires POST method

**Correct usage:**
```powershell
# From backend directory
.\trigger_scraper.ps1
```

Or using curl:
```powershell
curl -X POST http://localhost:8000/scraper/trigger
```

---

## ⚠️ Issue 3: Home Page Shows No Data (NEEDS ACTION)

**Backend logs show:**
```
INFO: 192.168.50.1:54564 - "GET /products/home HTTP/1.1" 200 OK
```
✅ API is working and returning 200 OK

**But frontend shows empty:**
This means the database is empty (no products scraped yet)

### Solution Steps:

#### Step 1: Start Backend (if not running)
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --reload
```

#### Step 2: Trigger the Scraper
```powershell
# In a NEW terminal (keep backend running)
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\trigger_scraper.ps1
```

**Expected output:**
```
✓ Scraper triggered successfully!

Results:
  Status: success
  Message: Scraping completed successfully

Details:
  Total scraped: 50
  Platforms scraped: 5/5
  Best deals: 25
  Top price drops: 25
  Saved to DB: true

✓ Database populated! Refresh your app to see products.
```

#### Step 3: Refresh Mobile App
- Pull down on the home screen to refresh
- You should see 25 "Trending Now" products (best deals)
- You should see 25 "Recommended" products (top price drops)

---

## ✅ Issue 4: Missing @/constants/api Import (DOES NOT EXIST)

**Error from logs:**
```
Unable to resolve "@/constants/api" from "services\api.ts"
```

**Cause:** This is an OLD error from BEFORE the integration
**Actual code:** The file `services/api.ts` correctly imports from `'../constants/api'`

**Status:** ✅ ALREADY FIXED
- The mobile app no longer uses `@/constants/api`
- All imports use relative paths `'../constants/api'`
- This error is NOT appearing in current logs

---

## 🔍 Debugging: Why No Data?

### Check Database Content

**PostgreSQL:**
```powershell
# Connect to PostgreSQL
psql -U postgres -d pricepilot

# Check products count
SELECT COUNT(*) FROM products;

# Check sample products
SELECT id, title, price, store_name FROM products LIMIT 5;

# Exit
\q
```

**MongoDB:**
```powershell
# Connect to MongoDB
mongosh "mongodb+srv://cluster0.your-cluster.mongodb.net/pricepilot" --username your-username

# Check best_deals
use pricepilot
db.best_deals.countDocuments()
db.best_deals.find().limit(3).pretty()

# Check top_price_drops
db.top_price_drops.countDocuments()
db.top_price_drops.find().limit(3).pretty()
```

### Expected Database State:
- **PostgreSQL `products` table:** 50 products
- **MongoDB `best_deals` collection:** 25 products
- **MongoDB `top_price_drops` collection:** 25 products

---

## 📱 Frontend Display Logic

The home screen (`mobile/app/(tabs)/home.tsx`) shows:

1. **Loading state** while fetching
2. **Error state** if API fails
3. **Empty state** if database is empty (no products scraped)
4. **Content state** with products when available

**Current behavior (from logs):**
- API returns 200 OK ✅
- But response is likely empty or has empty arrays
- Frontend shows "No Products Yet" message

**This is CORRECT behavior** when database is empty!

---

## 🚀 Quick Fix (Run These Commands)

```powershell
# Terminal 1: Start Backend
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Trigger Scraper
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\trigger_scraper.ps1

# Wait for scraping to complete (~30 seconds)
# Then refresh mobile app (pull down on home screen)
```

---

## ✅ Verification Checklist

After running the scraper:

1. ✅ Backend console shows "Scraping completed successfully"
2. ✅ PowerShell shows "Total scraped: 50"
3. ✅ Mobile app shows products on home screen
4. ✅ Can click on products (will still show mock data on detail page)
5. ✅ Pull-to-refresh works

---

## 🎯 Next Steps

If products still don't appear after scraping:

1. Check backend logs for errors during scraping
2. Verify database connection in backend `.env` file
3. Check database content using commands above
4. Check mobile app console logs (React Native debugger)
5. Verify API_URL in mobile app is correct (should auto-detect)

---

## 📝 Notes

- Home screen integration: ✅ COMPLETE
- Product detail page integration: ❌ NOT DONE (still uses mock data)
- Search integration: ❌ NOT DONE (still uses mock data)
- Explore page integration: ❌ NOT DONE (still uses mock data)

The home screen SHOULD work once you run the scraper!
