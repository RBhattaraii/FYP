# 🔥 Complete Firewall Fix Guide

## Problem

The app detects the correct IP (`192.168.1.92`) but can't connect because **Windows Firewall is blocking port 8000**.

## ✅ Solution: One-Click Firewall Fix

### Step 1: Run Firewall Fix Script

**Double-click** `FIX_FIREWALL.bat` in the FYP folder.

This will:
- ✅ Remove old firewall rules
- ✅ Add Port 8000 Inbound rule (TCP)
- ✅ Add Port 8000 Outbound rule (TCP)
- ✅ Allow Python program
- ✅ Allow Uvicorn program
- ✅ Work for ALL future IP addresses

**You'll be prompted for Administrator permission - click "Yes"**

### Step 2: Verify Firewall Rules

After running the script, you should see:
```
✓ Port 8000 Inbound (TCP) - Added
✓ Port 8000 Outbound (TCP) - Added
✓ Python Program Rule - Added
✓ Uvicorn Program Rule - Added
```

### Step 3: Start Backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### Step 4: Test Backend is Reachable

**On your computer**, open browser:
```
http://localhost:8000/docs
```

**On your phone**, open browser:
```
http://192.168.1.92:8000/docs
```

Both should load the FastAPI docs page!

### Step 5: Start Frontend

```bash
cd mobile
expo start -c
```

### Step 6: Test Login

1. Scan QR code
2. Login with:
   - Email: `testuser@pricepilot.com`
   - Password: `testpass123`
3. Should work now!

## 🎯 What the Script Does

### Firewall Rules Added:

1. **Port 8000 Inbound (TCP)** - Allows incoming connections on port 8000
2. **Port 8000 Outbound (TCP)** - Allows outgoing connections on port 8000
3. **Python Program** - Allows Python executable to accept connections
4. **Uvicorn Program** - Allows Uvicorn to accept connections

### Profiles:
- **Private** - Home/Work networks (enabled)
- **Domain** - Corporate networks (enabled)
- **Public** - Public WiFi (disabled for security)

## 🔍 Manual Verification

### Check Firewall Rules:

**PowerShell:**
```powershell
Get-NetFirewallRule -DisplayName "PricePilot*" | Format-Table DisplayName, Enabled, Direction, Action
```

Should show:
```
DisplayName                          Enabled Direction Action
-----------                          ------- --------- ------
PricePilot Backend Port 8000 TCP     True    Inbound   Allow
PricePilot Backend Port 8000 TCP Out True    Outbound  Allow
PricePilot Python Backend            True    Inbound   Allow
PricePilot Uvicorn                   True    Inbound   Allow
```

### Check if Port 8000 is Listening:

**PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Should show the backend process listening on port 8000.

### Test Connection from Phone:

**On phone browser:**
```
http://192.168.1.92:8000/docs
```

If this loads, firewall is working!

## 🐛 Troubleshooting

### Issue: "Access Denied" when running script

**Solution**: Right-click `FIX_FIREWALL.bat` → Run as Administrator

### Issue: Script runs but still can't connect

**Check 1**: Is backend running with `--host 0.0.0.0`?
```bash
uvicorn main:app --host 0.0.0.0 --reload
```

**Check 2**: Is antivirus blocking?
- Temporarily disable antivirus
- Test connection
- Add exception for Python/Uvicorn

**Check 3**: Are you on the same WiFi?
- Computer and phone must be on same network
- Not on guest network
- Not using VPN

### Issue: IP keeps changing

**Solution**: Set static IP (see below)

## 🔒 Set Static IP (Recommended)

To prevent IP from changing:

1. Open **Settings** → **Network & Internet**
2. Click **Properties** under your WiFi
3. Click **Edit** next to IP assignment
4. Select **Manual**
5. Turn on **IPv4**
6. Set:
   - **IP address**: `192.168.1.100` (choose unused IP)
   - **Subnet mask**: `255.255.255.0`
   - **Gateway**: `192.168.1.1` (your router)
   - **Preferred DNS**: `8.8.8.8`
   - **Alternate DNS**: `8.8.4.4`
7. Click **Save**

Now your IP will always be `192.168.1.100`!

## ✅ Success Checklist

- [ ] Ran `FIX_FIREWALL.bat` as Administrator
- [ ] Saw "Firewall Configuration Complete!"
- [ ] Backend running with `--host 0.0.0.0`
- [ ] Can access `http://localhost:8000/docs` on computer
- [ ] Can access `http://192.168.1.92:8000/docs` on phone browser
- [ ] Frontend running with `expo start -c`
- [ ] App shows correct IP in logs
- [ ] Login works in mobile app

## 🚀 Quick Start After Fix

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Frontend
cd mobile
expo start -c

# Scan QR code and test!
```

## 📝 Files Created

- `FIX_FIREWALL.bat` - One-click firewall fix (run this!)
- `fix-firewall.ps1` - PowerShell script (runs automatically)
- `FIREWALL_FIX_GUIDE.md` - This guide

---

## 🎉 After Running the Fix

The firewall will:
- ✅ Allow port 8000 for ALL IP addresses
- ✅ Work when your IP changes
- ✅ Allow Python and Uvicorn programs
- ✅ Only allow on private networks (secure)

**You'll never need to update firewall rules again!**

---

**Next Step: Double-click `FIX_FIREWALL.bat` now!** 🚀
