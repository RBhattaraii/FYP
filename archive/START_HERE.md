# 🚀 START HERE - PricePilot Complete Setup

## Current Situation
- ✓ Backend has 328 scraped products
- ✓ Backend API is working
- ✗ Mobile app showing "Unable to resolve @/constants/api" error (Metro cache issue)
- ✗ Mobile app not displaying real data (need to clear cache and restart)

---

## 🎯 Quick Fix (3 Minutes)

### Step 1: Test Backend (30 seconds)
```powershell
cd C:\Users\NITOR 5\Desktop\FYP
.\test-everything.ps1
```

**What to look for:**
- ✓ All tests should pass
- ✓ Should show products count (e.g., "Total: 33")
- ✓ Sample product displayed

**If backend not running:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### Step 2: Fix & Start Mobile App (2 minutes)
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\mobile
.\fix-and-start.ps1
```

**What it does:**
1. ✓ Stops running Metro bundler
2. ✓ Clears all cache (Metro, Expo, Watchman)
3. ✓ Checks backend connectivity
4. ✓ Shows your network IP
5. ✓ Starts Expo with --clear flag

### Step 3: Open App on Device

**On Android Emulator:**
- Press `a` in Metro terminal
- Or scan QR code with Expo Go app

**On Physical Device:**
- Install Expo Go from Play Store
- Scan QR code shown in terminal
- Make sure device is on same WiFi as PC

### Step 4: Verify

**You should see:**
- ✓ Home screen loads (no errors)
- ✓ "Best Deals" section with products
- ✓ "Price Drops" section with products
- ✓ Product images loading
- ✓ Clicking product opens detail page

**If still no products:**
- Pull down to refresh
- Check backend logs for API calls
- Verify: `http://localhost:8000/products/home` returns data

---

## 🔧 If Problems Persist

### Problem 1: Metro bundler error still showing
```powershell
# Nuclear option - complete cache clear
cd mobile
rmdir /s /q .expo
rmdir /s /q node_modules\.cache
npx expo start --clear --reset-cache
```

### Problem 2: "No products" in app but backend has data
**Check API URL in app:**
1. Open Metro terminal
2. Look for: `🔗 API URL: http://10.0.2.2:8000`
3. Verify that URL is reachable

**Test manually:**
```powershell
# Android emulator
curl http://10.0.2.2:8000/products/home

# Physical device (replace with your IP)
curl http://192.168.x.x:8000/products/home
```

### Problem 3: Firewall blocking connections
```powershell
cd mobile
.\fix-firewall.ps1
```

### Problem 4: Database is empty
```powershell
cd backend
.\trigger_scraper.ps1
# Wait 30-60 seconds for scraping to complete
```

---

## 📱 App Structure Overview

### Home Screen (`mobile/app/(tabs)/home.tsx`)
- Fetches from `/products/home` endpoint
- Shows 2 sections:
  - **Best Deals** (top 25 by discount %)
  - **Price Drops** (top 25 by price reduction)
- Pull-to-refresh to reload
- Click product → detail page

### API Service (`mobile/services/api.ts`)
- `fetchHomeScreenProducts()` - Get home screen data
- `searchProducts(query)` - Search with tiered strategy
- `fetchProductDetail(id)` - Get single product
- Auto-detects correct backend URL

### Backend Endpoints
- `GET /products/home` - Home screen products
- `GET /products/search?q=laptop` - Search
- `GET /products/{id}` - Product detail
- `POST /scraper/trigger` - Trigger scraping

---

## 🎓 For Viva / Presentation

### Q: How does the mobile app connect to backend?

**A:** The app uses automatic network detection:

```typescript
// constants/api.ts
const getApiUrl = () => {
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';  // Emulator special address
  }
  return `http://${detectLanIP()}:8000`;  // Physical device uses LAN IP
}
```

### Q: How does data flow from scrapers to mobile app?

**A:** 
1. Scrapers collect products → MongoDB (`raw_products`)
2. Scraper coordinator curates best deals → PostgreSQL (`home_screen_products`)
3. FastAPI endpoints query PostgreSQL → JSON response
4. Mobile app fetches JSON → Displays in UI

### Q: What happens if backend is not reachable?

**A:**
- `fetchWithTimeout()` throws error after 10 seconds
- Home screen shows error message with retry button
- User can pull-to-refresh to retry

### Q: How are images loaded?

**A:**
- Image URLs stored in database
- React Native `<Image>` component fetches from URL
- Uses `image_url` field from backend Product model
- Cached automatically by React Native

---

## 📊 Success Metrics

After following this guide, you should have:

✓ Backend running with 33+ products in database  
✓ Mobile app connecting to backend successfully  
✓ Home screen displaying real product data  
✓ Product images loading  
✓ Product detail page working  
✓ Search functionality operational  
✓ No Metro bundler errors  

---

## 🆘 Still Stuck?

### Check logs:

**Backend logs:**
```powershell
cd backend
# Should show:
# INFO: 192.168.x.x:xxxx - "GET /products/home HTTP/1.1" 200 OK
```

**Metro bundler logs:**
```
🔗 API URL: http://10.0.2.2:8000
📱 Platform: android
```

**App console (in Metro terminal):**
Press `j` to open debugger, check Console for errors

### Quick diagnostics:
```powershell
# Test backend
curl http://localhost:8000/products/home

# Test from network (replace IP)
curl http://YOUR_IP:8000/products/home

# Check if port is open
Test-NetConnection -ComputerName localhost -Port 8000
```

---

## 🚀 You're Ready!

Run these two commands and you're done:

```powershell
# Terminal 1 - Backend
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2 - Mobile
cd C:\Users\NITOR 5\Desktop\FYP\mobile
.\fix-and-start.ps1
```

Open the app and enjoy! 🎉
