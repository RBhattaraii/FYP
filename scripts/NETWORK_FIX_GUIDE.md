# Network Fix Guide - Get to Home Screen

## Problem
- App redirecting to login but network requests failing
- Windows Firewall blocking port 8000
- Expo cache causing routing issues

## Complete Fix (Follow in Order)

### Step 1: Clear Expo Cache
```bash
cd mobile
npx expo start -c --clear
```
**Then press Ctrl+C to stop it**

### Step 2: Fix Windows Firewall
1. Right-click PowerShell and select **"Run as Administrator"**
2. Navigate to project:
   ```powershell
   cd "C:\Users\NITOR 5\Desktop\FYP"
   ```
3. Run firewall fix:
   ```powershell
   .\fix-firewall.ps1
   ```
4. Verify rules were added (should see green "Done!" messages)

### Step 3: Verify Firewall Rules
Open Windows Firewall settings and check:
- **Inbound Rules**: Look for "PricePilot Backend Port 8000 TCP"
- **Should show**: Enabled, Allow, Port 8000, TCP, Private/Domain profiles

### Step 4: Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

**Verify backend started:**
- Should see: `Uvicorn running on http://0.0.0.0:8000`
- Should see: `✅ PostgreSQL connection pool created successfully`
- Should see: `✅ MongoDB connected successfully`

### Step 5: Test Backend from Browser
Open browser and go to: `http://192.168.1.92:8000/docs`

**If this doesn't load:**
- Firewall is still blocking
- Try temporarily disabling Windows Firewall to test
- Check if antivirus is blocking

### Step 6: Start Mobile App
```bash
cd mobile
npx expo start
```

Scan QR code with Expo Go app

### Step 7: Test Login
Use test credentials:
- **Email**: `testuser@pricepilot.com`
- **Password**: `testpass123`

After successful login, you'll see the home screen with:
- Header with "Hello, Alex" and notification bell
- Search bar with voice icon
- Category pills (Electronics, Fashion, etc.)
- Trending Now section (8 products)
- Recommended for You section (8 products with discounts)

## If Still Not Working

### Option A: Temporarily Disable Firewall (Testing Only)
1. Open Windows Security
2. Firewall & network protection
3. Turn off for Private network (temporarily)
4. Test if app works
5. Turn firewall back on
6. If it worked, the firewall rules aren't being applied correctly

### Option B: Check IP Address
Your IP might have changed again. Check current IP:
```powershell
ipconfig | findstr IPv4
```

Look for `192.168.x.x` address. The app auto-detects this from Expo's dev server.

### Option C: Use ngrok (Temporary Solution)
If firewall keeps blocking:
```bash
# Install ngrok
choco install ngrok

# Start backend first
cd backend
uvicorn main:app --host 0.0.0.0 --reload

# In another terminal, tunnel port 8000
ngrok http 8000
```

Then update `mobile/constants/api.ts` with the ngrok URL.

## What Changed

### 1. Fixed `mobile/app/index.tsx`
Now properly checks authentication:
- If logged in → Home screen
- If not logged in → Login screen

### 2. Auto IP Detection
`mobile/constants/api.ts` automatically detects your IP from Expo's dev server, so it adjusts when your DHCP IP changes.

### 3. Firewall Rules
Added comprehensive rules for:
- Port 8000 TCP inbound/outbound
- Python.exe program
- Uvicorn.exe program

## Expected Flow

1. **First time**: App shows login screen
2. **Enter credentials**: testuser@pricepilot.com / testpass123
3. **After login**: Redirects to home screen with full UI
4. **Next time**: App remembers you and goes straight to home screen

## Test User

Already created in database:
- **Email**: testuser@pricepilot.com
- **Password**: testpass123
- **Name**: Test User

## Home Screen Features

Once you login, you'll see:
- ✅ iOS-style design with SF Pro Display font
- ✅ Smooth scrolling with momentum and bounce
- ✅ Spring animations on buttons
- ✅ Haptic feedback on iOS
- ✅ 7 category pills (horizontal scroll)
- ✅ 8 trending products (160×200px cards)
- ✅ 8 recommended products (280×140px cards with discounts)
- ✅ Bottom tab navigation (4 tabs)
- ✅ All using dummy data (no API calls needed)

## Quick Commands

**Clear everything and start fresh:**
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Mobile (after backend is running)
cd mobile
npx expo start -c
```

**Check if backend is reachable:**
```bash
curl http://192.168.1.92:8000/docs
```

**Check firewall rules:**
```powershell
Get-NetFirewallRule -DisplayName "PricePilot*" | Format-Table DisplayName, Enabled, Direction, Action
```
