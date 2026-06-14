# Dynamic IP Solution - Auto-Detect Backend URL

## ✅ Solution Implemented

The app now **automatically detects your computer's IP address** from the Expo dev server!

### How It Works

The `mobile/constants/api.ts` file now uses Expo's `Constants.expoConfig.hostUri` to get the same IP address that Expo is using. This means:

- ✅ **No manual IP updates needed**
- ✅ **Works when IP changes**
- ✅ **Same IP as Expo dev server**
- ✅ **Automatic detection**

### What Changed

**Before:**
```typescript
export const API_URL = "http://192.168.1.69:8000";  // Hardcoded, breaks when IP changes
```

**After:**
```typescript
const getApiUrl = () => {
  const debuggerHost = Constants.expoConfig?.hostUri;
  if (debuggerHost) {
    const ip = debuggerHost.split(':')[0];
    return `http://${ip}:8000`;
  }
  return "http://192.168.50.1:8000";  // Fallback
};

export const API_URL = getApiUrl();
```

## 🚀 How to Use

### Step 1: Update Firewall for New IP

Since your IP changed to `192.168.50.1`, update the firewall:

**PowerShell as Administrator:**
```powershell
New-NetFirewallRule -DisplayName "PricePilot Backend Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Step 2: Restart Backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### Step 3: Restart Expo with Cache Clear

```bash
cd mobile
expo start -c
```

### Step 4: Check the Detected URL

When you start Expo, look in the terminal for:
```
🔗 API URL: http://192.168.50.1:8000
```

This confirms the app detected the correct IP!

### Step 5: Test on Phone

1. Scan QR code
2. App should now connect to backend automatically
3. Try login with:
   - Email: `testuser@pricepilot.com`
   - Password: `testpass123`

## 🎯 Benefits

### 1. **Automatic IP Detection**
- App uses same IP as Expo dev server
- No manual configuration needed
- Works across different networks

### 2. **Survives IP Changes**
- DHCP assigns new IP? No problem!
- Just restart Expo and it auto-detects
- No code changes needed

### 3. **Developer Friendly**
- Same setup works for all team members
- No hardcoded IPs in code
- Easy to switch networks

## 🔧 Alternative Solution: Static IP (Optional)

If you want to avoid IP changes completely, set a **static IP** for your computer:

### Windows Static IP Setup:

1. Open **Settings** → **Network & Internet**
2. Click **Properties** under your WiFi
3. Click **Edit** next to IP assignment
4. Select **Manual**
5. Turn on **IPv4**
6. Set:
   - IP address: `192.168.50.100` (or any unused IP in your range)
   - Subnet mask: `255.255.255.0`
   - Gateway: `192.168.50.1` (your router)
   - DNS: `8.8.8.8` (Google DNS)
7. Click **Save**

Then update the fallback in `api.ts`:
```typescript
return "http://192.168.50.100:8000";  // Your static IP
```

## 🐛 Troubleshooting

### Issue: "API URL shows undefined"

**Cause**: Expo Constants not loaded
**Fix**: Make sure you're running in Expo Go, not web browser

### Issue: "Still using old IP"

**Cause**: Cache not cleared
**Fix**: 
```bash
cd mobile
expo start -c
```

### Issue: "Can't connect even with correct IP"

**Cause**: Firewall still blocking
**Fix**: 
1. Check firewall rule exists for port 8000
2. Try temporarily disabling firewall to test
3. Check antivirus isn't blocking

### Issue: "Backend not reachable"

**Cause**: Backend not listening on 0.0.0.0
**Fix**: Make sure you start backend with:
```bash
uvicorn main:app --host 0.0.0.0 --reload
```

The `--host 0.0.0.0` is crucial!

## ✅ Verification Checklist

- [ ] Backend running with `--host 0.0.0.0`
- [ ] Firewall rule added for port 8000
- [ ] Expo started with `expo start -c`
- [ ] Console shows correct API URL
- [ ] Phone and computer on same WiFi
- [ ] Can access `http://192.168.50.1:8000/docs` in browser
- [ ] Login works in mobile app

## 📝 Quick Commands

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Frontend
cd mobile
expo start -c

# Check detected IP in Expo terminal:
# Look for: 🔗 API URL: http://192.168.50.1:8000
```

## 🎉 Result

Now your app will:
- ✅ Automatically detect the correct IP
- ✅ Work when IP changes
- ✅ Connect to backend seamlessly
- ✅ No manual updates needed!

---

**Next Step**: Restart Expo with `expo start -c` and check the detected API URL!
