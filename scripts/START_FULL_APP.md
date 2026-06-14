# Start Full PricePilot App (Backend + Frontend)

## Network Error Fix

The "Network request failed" error means the backend server isn't running or isn't reachable from your phone.

## ✅ Solution: Start Both Backend and Frontend

### Step 1: Start Backend Server

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
✅ PostgreSQL connection pool created successfully
✅ MongoDB connected successfully
🚀 PricePilot API started successfully
```

### Step 2: Start Frontend (Expo)

**Terminal 2 (Frontend):**
```bash
cd mobile
npm start
```

Or if you need to clear cache:
```bash
cd mobile
expo start -c
```

### Step 3: Test on Phone

1. **Scan QR code** with Expo Go
2. **App loads to login screen**
3. **Login with test credentials:**
   - Email: `testuser@pricepilot.com`
   - Password: `testpass123`
4. **After login** → Redirects to home screen

## 🔍 Troubleshooting Network Error

### Error: "Network request failed"

**Cause**: Backend not running or not reachable

**Check 1: Is backend running?**
```bash
# In backend terminal, you should see:
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Check 2: Can you reach backend from browser?**
Open in browser: `http://192.168.1.69:8000/docs`
- ✅ If it loads → Backend is running
- ❌ If it doesn't load → Backend not reachable

**Check 3: Is IP address correct?**
```bash
# Find your computer's IP
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
```

Update `mobile/constants/api.ts` if IP changed:
```typescript
export const API_URL = "http://YOUR_IP_HERE:8000";
```

**Check 4: Firewall blocking?**
- Windows Firewall might be blocking port 8000
- Allow Python/uvicorn through firewall
- Or temporarily disable firewall for testing

**Check 5: Same WiFi network?**
- Computer and phone must be on same WiFi
- Not on guest network
- Not using VPN

### Error: "Unable to connect to server"

**Fix 1: Restart backend with correct host**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

The `--host 0.0.0.0` is important! It allows connections from other devices.

**Fix 2: Check Windows Firewall**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Python Backend" -Direction Inbound -Program "C:\Users\NITOR 5\Desktop\FYP\backend\venv\Scripts\python.exe" -Action Allow
```

**Fix 3: Update IP in mobile app**
1. Find your IP: `ipconfig`
2. Update `mobile/constants/api.ts`
3. Restart Expo: `expo start -c`

## 📱 Complete Testing Flow

### 1. Start Backend
```bash
cd C:\Users\NITOR 5\Desktop\FYP\backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### 2. Verify Backend Running
Open browser: `http://192.168.1.69:8000/docs`
Should show FastAPI docs page

### 3. Start Frontend
```bash
cd C:\Users\NITOR 5\Desktop\FYP\mobile
npm start
```

### 4. Test on Phone
1. Scan QR code
2. Login screen appears
3. Enter credentials:
   - Email: `testuser@pricepilot.com`
   - Password: `testpass123`
4. Tap "Login"
5. Should redirect to home screen

## 🎯 Expected Behavior

### Login Flow:
1. **App starts** → Login screen
2. **Enter credentials** → Tap login
3. **Backend validates** → Returns JWT token
4. **App stores token** → Redirects to home
5. **Home screen loads** → Shows dummy products

### Home Screen:
- Header with "Hello, [Name]"
- Search bar
- Category pills
- Trending products (dummy data)
- Recommended products (dummy data)
- Bottom tabs

## 🐛 Common Issues

### Issue 1: Backend not starting
**Error**: `ModuleNotFoundError` or `ImportError`
**Fix**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 2: Database connection failed
**Error**: PostgreSQL or MongoDB connection error
**Fix**: Check `.env` file has correct credentials

### Issue 3: Port 8000 already in use
**Error**: `Address already in use`
**Fix**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Issue 4: IP address changed
**Symptom**: Was working, now network error
**Fix**:
1. Run `ipconfig` to get new IP
2. Update `mobile/constants/api.ts`
3. Restart Expo with `expo start -c`

## ✅ Success Checklist

- [ ] Backend running on `http://0.0.0.0:8000`
- [ ] Can access `http://192.168.1.69:8000/docs` in browser
- [ ] Frontend running (Expo)
- [ ] Phone and computer on same WiFi
- [ ] Scanned QR code
- [ ] Login screen appears
- [ ] Can login with test credentials
- [ ] Redirects to home screen after login

## 📝 Quick Commands

**Start everything:**
```bash
# Terminal 1: Backend
cd backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Frontend
cd mobile && npm start
```

**Check IP address:**
```bash
ipconfig
```

**Test backend:**
```bash
curl http://192.168.1.69:8000/docs
```

---

**Next Step**: Start the backend first, then start the frontend!
