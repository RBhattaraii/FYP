# 🔥 Fix Windows Firewall for Expo

## The Problem

Windows Firewall is blocking your phone from connecting to the Expo server on your computer.

## ✅ Solution 1: Allow Node.js Through Firewall (RECOMMENDED)

### Step 1: Open Windows Defender Firewall

1. Press `Windows + R`
2. Type: `firewall.cpl`
3. Press Enter

### Step 2: Allow an App Through Firewall

1. Click **"Allow an app or feature through Windows Defender Firewall"** (left sidebar)
2. Click **"Change settings"** button (top right)
3. Click **"Allow another app..."** button (bottom)
4. Click **"Browse..."**
5. Navigate to: `C:\Program Files\nodejs\node.exe`
6. Click **"Add"**
7. Make sure **both "Private" and "Public"** checkboxes are checked for Node.js
8. Click **"OK"**

### Step 3: Restart Expo

```bash
# Press Ctrl+C in the terminal running Expo
# Then restart:
cd mobile
npx expo start --clear
```

### Step 4: Scan QR Code Again

Open Expo Go on your phone and scan the QR code.

---

## ✅ Solution 2: Create Firewall Rule for Port 8081

### Open PowerShell as Administrator

1. Press `Windows + X`
2. Click **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

### Run These Commands

```powershell
# Allow inbound connections on port 8081
New-NetFirewallRule -DisplayName "Expo Metro Bundler" -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow

# Allow inbound connections on port 19000-19001 (Expo DevTools)
New-NetFirewallRule -DisplayName "Expo DevTools" -Direction Inbound -Protocol TCP -LocalPort 19000-19001 -Action Allow
```

### Restart Expo

```bash
cd mobile
npx expo start --clear
```

---

## ✅ Solution 3: Temporarily Disable Firewall (TESTING ONLY)

**⚠️ WARNING: Only do this for testing! Re-enable after testing.**

### Step 1: Disable Firewall

1. Press `Windows + R`
2. Type: `firewall.cpl`
3. Press Enter
4. Click **"Turn Windows Defender Firewall on or off"** (left sidebar)
5. Select **"Turn off Windows Defender Firewall"** for both Private and Public networks
6. Click **"OK"**

### Step 2: Test Expo

```bash
cd mobile
npx expo start --clear
```

Scan QR code with Expo Go - it should work now.

### Step 3: Re-enable Firewall (IMPORTANT!)

1. Go back to firewall settings
2. Select **"Turn on Windows Defender Firewall"** for both networks
3. Click **"OK"**
4. Then use Solution 1 or 2 to allow Node.js permanently

---

## ✅ Solution 4: Use Localhost Tunnel (If Firewall Can't Be Changed)

If you can't modify firewall settings (e.g., on a work/school computer), use tunnel mode:

```bash
cd mobile
npx expo start --tunnel
```

This creates a public URL that bypasses local network restrictions.

**Note**: Tunnel mode is slower but works anywhere.

---

## 🧪 Test If Port is Blocked

### Check if port 8081 is accessible from your phone:

1. **On your computer**, open browser and go to: `http://192.168.1.69:8081`
   - You should see Expo DevTools

2. **On your phone**, open browser and go to: `http://192.168.1.69:8081`
   - If you see Expo DevTools → Firewall is OK
   - If you see "Can't connect" → Firewall is blocking

---

## 📊 Quick Checklist

- [ ] Same WiFi network (both devices)
- [ ] Node.js allowed through firewall
- [ ] Port 8081 allowed through firewall
- [ ] Expo server running (`npx expo start`)
- [ ] Can access `http://192.168.1.69:8081` from phone's browser

---

## 🎯 Recommended Approach

1. **Try Solution 2 first** (create firewall rule) - it's the cleanest
2. If that doesn't work, **try Solution 1** (allow Node.js)
3. If still not working, **try Solution 3** (temporarily disable) to confirm it's a firewall issue
4. If nothing works, **use Solution 4** (tunnel mode)

---

## 💡 After Fixing

Once you fix the firewall:

1. Restart Expo: `npx expo start --clear`
2. Scan QR code with Expo Go
3. Wait 30-60 seconds
4. You should see: **"Login Screen"**

Let me know which solution works for you!
