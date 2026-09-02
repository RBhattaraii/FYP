# Complete Fix Guide - PricePilot Mobile App

## Current Issues
1. ✗ Metro bundler showing "Unable to resolve @/constants/api" error
2. ✗ Frontend showing dummy/no data even though backend has products
3. ✗ Images not matching products

## Root Causes
1. **Metro bundler cache** - Old cached imports causing resolution errors
2. **Backend not accessible from mobile** - Network configuration issue
3. **Need to verify data exists in database**

---

## 🚀 COMPLETE FIX (Step-by-Step)

### Step 1: Stop Everything
```powershell
# Stop all Node.js processes (Metro bundler)
taskkill /F /IM node.exe
```

### Step 2: Clear Metro Cache
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\mobile

# Delete cache directories
rmdir /s /q .expo
rmdir /s /q node_modules\.cache

# Clear watchman cache (if installed)
watchman watch-del-all
```

### Step 3: Verify Backend Has Data
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\backend

# Activate virtual environment
.\venv\Scripts\activate

# Start backend server
uvicorn main:app --host 0.0.0.0 --reload
```

**In another terminal, test the endpoint:**
```powershell
# Test home endpoint
curl http://localhost:8000/products/home

# Should return JSON with best_deals and top_price_drops arrays
# If empty arrays, run: curl -X POST http://localhost:8000/scraper/trigger
```

### Step 4: Check Network Connectivity

Your mobile device needs to access the backend. The API URL is automatically detected from:
- `constants/api.ts` line 38: `return 'http://10.0.2.2:8000';` (Android emulator)
- Or dynamically from your LAN IP

**Test from mobile device:**
1. Find your PC's IP address: `ipconfig` (look for IPv4 Address)
2. On mobile browser, visit: `http://YOUR_IP:8000/docs`
3. If it doesn't work, check Windows Firewall

### Step 5: Start Mobile App (Fresh)
```powershell
cd C:\Users\NITOR 5\Desktop\FYP\mobile

# Start with cleared cache
npx expo start --clear

# Or use the batch file
.\clear-cache-and-start.bat
```

### Step 6: Verify Data Flow

**Backend logs should show:**
```
INFO:     192.168.x.x:xxxx - "GET /products/home HTTP/1.1" 200 OK
```

**Mobile app should show:**
```
🔗 API URL: http://10.0.2.2:8000
📱 Platform: android
```

If you see "Loading products..." forever, check:
1. Backend is running: `http://localhost:8000/docs`
2. Firewall allows incoming connections on port 8000
3. Mobile device can reach the backend

---

## ✅ How to Verify Everything Works

### Test 1: Backend Has Data
```bash
curl http://localhost:8000/products/home
```
**Expected:** JSON with products array (not empty)

### Test 2: Mobile Can Reach Backend
Open mobile browser → `http://YOUR_PC_IP:8000/docs`
**Expected:** FastAPI Swagger UI loads

### Test 3: Mobile App Loads Data
Open PricePilot app → Home tab
**Expected:** Products appear (not "No Products Yet")

---

## 🔧 Troubleshooting

### Problem: "Unable to resolve @/constants/api"
**Solution:** Clear Metro cache and restart
```bash
cd mobile
npx expo start --clear
```

### Problem: "No Products Yet" in app
**Solutions:**
1. Verify backend has data: `curl http://localhost:8000/products/home`
2. If empty, trigger scraper: `curl -X POST http://localhost:8000/scraper/trigger`
3. Wait 30 seconds, then refresh app

### Problem: "Unable to connect" error
**Solutions:**
1. Check backend is running: Visit `http://localhost:8000/docs`
2. Check firewall: Run `.\fix-firewall.ps1` in `mobile/` folder
3. Verify IP address in `constants/api.ts`

### Problem: Images not loading
**Cause:** CORS or image URL issues
**Solution:** Backend CORS is already configured, but verify:
```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be present
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📋 Quick Reference

### Backend Commands
```bash
cd C:\Users\NITOR 5\Desktop\FYP\backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### Mobile Commands
```bash
cd C:\Users\NITOR 5\Desktop\FYP\mobile
npx expo start --clear
```

### Scraper Commands
```bash
# Trigger scraper from backend
curl -X POST http://localhost:8000/scraper/trigger

# Or use PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/scraper/trigger" -Method POST
```

---

## 🎯 Expected Final State

**Backend:**
- Running on `http://0.0.0.0:8000`
- `/products/home` returns 25+ products
- `/docs` accessible

**Mobile App:**
- Metro bundler running without errors
- Home screen shows product cards
- Images loading correctly
- Products clickable → detail page works

**Database:**
- PostgreSQL has products in `home_screen_products` table
- MongoDB has raw scraper data in `raw_products` collection
