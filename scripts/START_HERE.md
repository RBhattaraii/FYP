# 🚀 START HERE - Get to Home Screen in 5 Steps

## Quick Fix (Do This First)

### Step 1: Clear Expo Cache
Open PowerShell in the project folder:
```bash
cd mobile
npx expo start -c
```
**Press Ctrl+C after it starts** (we just want to clear cache)

### Step 2: Fix Firewall
Right-click PowerShell → **Run as Administrator**
```powershell
cd "C:\Users\NITOR 5\Desktop\FYP"
.\fix-firewall.ps1
```
Wait for green "Done!" messages.

### Step 3: Test Network
In the same Administrator PowerShell:
```powershell
.\test-network.ps1
```
This will show you if everything is working.

### Step 4: Start Backend
Open a **new** PowerShell (normal, not admin):
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

**Wait for these messages:**
- ✅ PostgreSQL connection pool created successfully
- ✅ MongoDB connected successfully
- 🚀 PricePilot API started successfully
- Uvicorn running on http://0.0.0.0:8000

### Step 5: Start Mobile App
Open **another** PowerShell:
```bash
cd mobile
npx expo start
```

Scan QR code with Expo Go app on your phone.

## Login Credentials

```
Email: testuser@pricepilot.com
Password: testpass123
```

## What You'll See After Login

✅ **Header**: Logo, "Hello, Alex", notification bell  
✅ **Search Bar**: With voice search icon  
✅ **Categories**: 7 pills (Electronics, Fashion, Home, Beauty, Sports, Books, Toys)  
✅ **Trending Now**: 8 product cards (160×200px)  
✅ **Recommended**: 8 product cards with discounts (280×140px)  
✅ **Bottom Tabs**: Home, Categories, Favorites, Profile  

All with iOS-style design, smooth scrolling, and spring animations!

## If It Still Doesn't Work

### Test 1: Can you reach backend from browser?
Open browser on your phone: `http://192.168.1.92:8000/docs`

- **If it loads**: Firewall is OK, problem is in the app
- **If it doesn't load**: Firewall is still blocking

### Test 2: Temporarily disable firewall
1. Windows Security → Firewall & network protection
2. Turn off **Private network** firewall (temporarily)
3. Try the app again
4. If it works now, the firewall rules aren't being applied

### Test 3: Check your IP
Your IP might have changed. Run:
```powershell
ipconfig | findstr IPv4
```
Look for `192.168.x.x` - the app should auto-detect this.

## Still Stuck?

Run the network test to see what's wrong:
```powershell
.\test-network.ps1
```

This will tell you exactly what's not working.

## Expected Behavior

1. **First time**: App shows login screen
2. **Enter credentials**: testuser@pricepilot.com / testpass123
3. **Success**: Redirects to beautiful home screen
4. **Next time**: App remembers you, goes straight to home

## What I Fixed

1. ✅ **Proper auth flow**: Checks if you're logged in, redirects accordingly
2. ✅ **Auto IP detection**: App adjusts when your IP changes
3. ✅ **Firewall rules**: Comprehensive rules for port 8000
4. ✅ **Cache clearing**: Instructions to clear Expo cache

## Quick Commands Reference

**Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

**Mobile:**
```bash
cd mobile
npx expo start
```

**Clear cache:**
```bash
cd mobile
npx expo start -c
```

**Test network:**
```powershell
.\test-network.ps1
```

**Fix firewall (as Admin):**
```powershell
.\fix-firewall.ps1
```

---

**Ready?** Start with Step 1 above! 🚀
