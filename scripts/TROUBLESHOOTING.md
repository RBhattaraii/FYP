# 🔧 Troubleshooting Guide

## Problem: Backend Won't Start

### Symptom
```
Error: No module named 'fastapi'
```

### Solution
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

---

### Symptom
```
Error: Address already in use
```

### Solution
Backend is already running. Check for existing process:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

---

## Problem: Expo Won't Start

### Symptom
```
Error: Cannot find module 'expo-router'
```

### Solution
```bash
cd mobile
npm install
```

---

### Symptom
```
Error: Port 8081 already in use
```

### Solution
Expo is already running. Check terminal or:
```bash
# Find process using port 8081
netstat -ano | findstr :8081

# Kill the process
taskkill /PID <PID> /F
```

---

## Problem: App Won't Load on Phone

### Symptom
"Failed to download remote update"

### Possible Causes & Solutions

#### 1. Different WiFi Networks
**Check**: Phone and computer on same WiFi?
**Solution**: Connect both to same network

#### 2. Backend Not Accessible
**Check**: Backend running with `--host 0.0.0.0`?
**Solution**: 
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```
⚠️ Must use `--host 0.0.0.0` (not 127.0.0.1)

#### 3. Wrong IP Address
**Check**: IP in `mobile/constants/api.ts` correct?
**Solution**:
1. Find your IP:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" under WiFi adapter

2. Update `mobile/constants/api.ts`:
   ```typescript
   export const API_URL = "http://YOUR_IP:8000";
   ```

3. Restart Expo:
   ```bash
   cd mobile
   npm start
   ```

#### 4. Firewall Blocking
**Check**: Windows Firewall blocking connections?
**Solution**: Allow Python and Node.js through firewall

---

## Problem: Network Error on Login/Register

### Symptom
"Unable to connect to server. Please check your connection."

### Console Shows
```
Network error: [TypeError: Network request failed]
```

### Solutions

#### 1. Check Backend Running
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```
Should see: "Uvicorn running on http://0.0.0.0:8000"

#### 2. Test Backend Directly
Open browser on phone:
```
http://192.168.1.69:8000/docs
```
Should see FastAPI documentation page.

If this doesn't work:
- Backend not accessible from phone
- Check firewall
- Check WiFi network

#### 3. Check API URL
Open `mobile/constants/api.ts`:
```typescript
export const API_URL = "http://192.168.1.69:8000";
```
Should match your computer's IP.

#### 4. Reload App
Shake phone → Tap "Reload"

---

## Problem: Login/Register Button Does Nothing

### Symptom
Click button, nothing happens, no error

### Solutions

#### 1. Check Console Logs
Look in Expo terminal for errors

#### 2. Check Validation
Are there validation errors below input fields?

#### 3. Reload App
Shake phone → Tap "Reload"

---

## Problem: "Invalid email or password" on Login

### Symptom
Using correct credentials but getting error

### Solutions

#### 1. Check Credentials
Must be EXACT:
- Email: `testuser@pricepilot.com`
- Password: `testpass123`

#### 2. Check for Spaces
No spaces before/after email or password

#### 3. Check Database
Test user might not exist. Create it:
```bash
cd backend
venv\Scripts\activate
python create_test_user.py
```

---

## Problem: "Email already registered" on Register

### Symptom
Can't register with any email

### Solution
Email must be unique. Try:
- `newuser1@test.com`
- `newuser2@test.com`
- `yourname123@test.com`

---

## Problem: Eye Icons Not Showing

### Symptom
Password toggle icons missing

### Solutions

#### 1. Wait for Fonts
Icons load from @expo/vector-icons. Wait 5-10 seconds.

#### 2. Reload App
Shake phone → Tap "Reload"

#### 3. Check Internet
Phone needs internet to download fonts first time

---

## Problem: App Crashes on Navigation

### Symptom
App crashes when clicking "Sign Up" or "Login" links

### Solutions

#### 1. Check Expo Router
```bash
cd mobile
npm install expo-router
```

#### 2. Reload App
Shake phone → Tap "Reload"

#### 3. Restart Expo
Stop Expo (Ctrl+C) and restart:
```bash
npm start
```

---

## Problem: Validation Not Working

### Symptom
Can submit form with empty fields or invalid data

### Solutions

#### 1. Check Code
Validation should happen in `validateForm()` function

#### 2. Reload App
Shake phone → Tap "Reload"

#### 3. Check Console
Look for JavaScript errors in Expo terminal

---

## Problem: Password Not Clearing on Error

### Symptom
Password field keeps value after error

### Solution
This is a bug. Should clear password on error.
Check code in login.tsx / register.tsx:
```typescript
setPassword('');
```

---

## Problem: Can't Reach Home Screen

### Symptom
Login/register succeeds but stays on same screen

### Solutions

#### 1. Check Navigation
Should see in console:
```
Response status: 200
```

#### 2. Check Home Screen Exists
File should exist: `mobile/app/(tabs)/home.tsx`

#### 3. Check Expo Router
```bash
cd mobile
npm install expo-router
```

---

## Problem: Backend Database Errors

### Symptom
```
Error: could not connect to server
```

### Solutions

#### 1. Check .env File
Open `backend/.env`:
```
DATABASE_URL=postgresql://...
```
Should have valid Supabase connection string

#### 2. Check Internet
Backend needs internet to connect to Supabase

#### 3. Test Connection
```bash
cd backend
venv\Scripts\activate
python test_connection.py
```

---

## Problem: MongoDB Errors

### Symptom
```
Error: SSL handshake failed
```

### Solution
Check `requirements.txt`:
```
pymongo[srv]==4.6.0
```
Must be version 4.6.0 (not 4.17.0)

---

## Quick Diagnostic Commands

### Check if Backend Running
```bash
curl http://192.168.1.69:8000/docs
```
Should return HTML

### Check if Expo Running
```bash
curl http://192.168.1.69:8081
```
Should return something

### Check Python Packages
```bash
cd backend
venv\Scripts\activate
pip list
```
Should see fastapi, uvicorn, asyncpg, etc.

### Check Node Packages
```bash
cd mobile
npm list expo-router
```
Should show version 6.0.23

---

## Still Having Issues?

1. **Read error message carefully**
   - Error messages usually tell you what's wrong

2. **Check console logs**
   - Both Expo terminal and backend terminal

3. **Try the basics**
   - Restart backend
   - Restart Expo
   - Reload app on phone
   - Restart phone

4. **Check documentation**
   - `HOW_TO_TEST_NOW.md`
   - `TESTING_CHECKLIST.md`
   - `mobile/LOGIN_SCREEN_EXPLANATION.md`
   - `mobile/REGISTER_SCREEN_EXPLANATION.md`

5. **Document the issue**
   - What were you doing?
   - What did you expect?
   - What actually happened?
   - What error messages did you see?
   - What have you tried?

---

**Last Updated**: After modern UI redesign
**Status**: Comprehensive troubleshooting guide
