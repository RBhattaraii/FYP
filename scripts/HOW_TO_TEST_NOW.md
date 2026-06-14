# 🧪 How to Test Login & Register Screens - RIGHT NOW!

## � Testing Documents

**New to testing?** Start with these documents:
- **QUICK_START.md** - One-page quick reference (⚡ fastest)
- **START_TESTING.md** - Step-by-step visual guide (🎯 recommended for first time)
- **TESTING_CHECKLIST.md** - Quick verification checklist
- **TROUBLESHOOTING.md** - Problem solutions
- **TESTING_SUMMARY.md** - Complete reference
- **README_TESTING.md** - Overview of all documents

**This document** provides comprehensive test scenarios with detailed expected results.

---

## �🚀 Quick Start (3 Steps)

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --reload
   ```

2. **Start Expo** (Terminal 2):
   ```bash
   cd mobile
   npm start
   ```

3. **Open on Phone**:
   - Open Expo Go app
   - Scan QR code from terminal
   - Wait for app to load

**Test Login**: `testuser@pricepilot.com` / `testpass123`

---

## 🎨 NEW: Modern UI Design!

The login screen has been redesigned with a modern purple theme (#7C3AED) and clean interface with icons!

## ✅ Start Both Servers

### **Terminal 1: Start Backend**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```
✅ **Backend**: Should run on http://192.168.1.69:8000

### **Terminal 2: Start Expo**
```bash
cd mobile
npm start
```
✅ **Expo**: Should run on http://192.168.1.69:8081  
✅ **QR Code**: Will be displayed in terminal

---

## 📱 Step-by-Step Testing Guide

### **Step 1: Open App on Your Phone**

1. **Open Expo Go** app on your phone (must be on same WiFi as computer)
2. **Scan the QR code** shown in the Expo terminal
3. **Wait 10-20 seconds** for app to load
4. **You should see**: Modern login screen with:
   - Purple "PricePilot" logo (#7C3AED)
   - "Welcome Back!" header
   - Email input with mail icon
   - Password input with lock icon
   - Purple "Sign In" button
   - "Don't have an account? Sign Up" link

---

### **Step 2: Test Login Screen**

#### **Test 2.1: Empty Validation**
1. **Don't enter anything**
2. Click **"Sign In"** button
3. **Expected**: 
   - "Email is required" error below email field
   - "Password is required" error below password field
   - Red borders on both input fields

✅ **Pass** if you see error messages with red borders

#### **Test 2.2: Email Validation**
1. Enter email: `test@test` (invalid format)
2. Click **"Sign In"**
3. **Expected**: "Please enter a valid email address" error
4. Try email: `notanemail` (no @ symbol)
5. **Expected**: Same error

✅ **Pass** if email validation works

#### **Test 2.3: Password Toggle**
1. Enter password: `test123`
2. Click **eye icon** (right side of password field)
3. **Expected**: Password becomes visible, icon changes to eye-off
4. Click **eye icon** again
5. **Expected**: Password hidden, icon changes back to eye

✅ **Pass** if toggle works

#### **Test 2.4: Successful Login**
1. Enter email: `testuser@pricepilot.com`
2. Enter password: `testpass123`
3. Click **"Sign In"**
4. **Expected**:
   - Button shows spinning circle
   - Console logs: "Attempting login to: http://192.168.1.69:8000/auth/login"
   - Console logs: "Response status: 200"
   - After 1-2 seconds, navigates to Home screen
   - Home screen shows "Home Screen" text

✅ **Pass** if you reach home screen

#### **Test 2.5: Wrong Password**
1. Enter email: `testuser@pricepilot.com`
2. Enter password: `wrongpassword`
3. Click **"Sign In"**
4. **Expected**:
   - Red error box at top: "Invalid email or password"
   - Password field cleared
   - Email field kept

✅ **Pass** if error shows and password clears

#### **Test 2.6: Network Error Handling**
1. Turn off WiFi on phone
2. Enter email: `testuser@pricepilot.com`
3. Enter password: `testpass123`
4. Click **"Sign In"**
5. **Expected**:
   - Red error box: "Unable to connect to server. Please check your connection."
   - Console logs: "Network error: [error details]"
6. Turn WiFi back on

✅ **Pass** if network error is handled gracefully

---

### **Step 3: Navigate to Register Screen**

1. On login screen, tap **"Don't have an account? Sign Up"** at bottom
2. **Expected**: Navigates to Register screen
3. **You should see**:
   - Blue "PricePilot" logo (old design - not yet updated)
   - "Create your account" tagline
   - 4 input fields (Full Name Optional, Email, Password, Confirm Password)
   - 2 eye icons (one for each password)
   - Blue "Register" button
   - "Already have an account? Login" link
   - Password hint: "Must be at least 8 characters and contain a number"

⚠️ **Note**: Register screen still has old blue design. Will be updated to match login screen's modern purple design.

---

### **Step 4: Test Register Screen**

#### **Test 4.1: Empty Validation**
1. **Don't enter anything**
2. Click **"Register"** button
3. **Expected**:
   - "Email is required"
   - "Password is required"
   - "Please confirm your password"
   - Red borders on inputs

✅ **Pass** if you see 3 error messages

#### **Test 4.2: Invalid Email**
1. Enter email: `notanemail`
2. Enter password: `testpass123`
3. Enter confirm: `testpass123`
4. Click **"Register"**
5. **Expected**:
   - "Please enter a valid email address"
   - Email border turns red

✅ **Pass** if email validation works

#### **Test 4.3: Short Password**
1. Enter email: `test@test.com`
2. Enter password: `short`
3. Enter confirm: `short`
4. Click **"Register"**
5. **Expected**:
   - "Password must be at least 8 characters"

✅ **Pass** if length validation works

#### **Test 4.4: Password Without Number**
1. Enter email: `test@test.com`
2. Enter password: `password` (no number)
3. Enter confirm: `password`
4. Click **"Register"**
5. **Expected**:
   - "Password must contain at least one number"

✅ **Pass** if number validation works

#### **Test 4.5: Passwords Don't Match**
1. Enter email: `test@test.com`
2. Enter password: `password123`
3. Enter confirm: `password456` (different)
4. Click **"Register"**
5. **Expected**:
   - "Passwords do not match"

✅ **Pass** if match validation works

#### **Test 4.6: Both Password Toggles**
1. Enter password: `testpass123`
2. Click **eye icon** on password field
3. **Expected**: Password visible
4. Enter confirm: `testpass123`
5. Click **eye icon** on confirm field
6. **Expected**: Confirm password visible
7. Click both eye icons again
8. **Expected**: Both hidden

✅ **Pass** if both toggles work independently

#### **Test 4.7: Successful Registration**
1. Enter full name: `Test User` (or leave empty - it's optional)
2. Enter email: `newuser123@test.com` (must be unique!)
3. Enter password: `testpass123`
4. Enter confirm: `testpass123`
5. Click **"Register"**
6. **Expected**:
   - Button shows spinning circle
   - After 1-2 seconds, navigates to Home screen

✅ **Pass** if registration works

#### **Test 4.8: Duplicate Email**
1. Enter email: `testuser@pricepilot.com` (already exists)
2. Enter password: `testpass123`
3. Enter confirm: `testpass123`
4. Click **"Register"**
5. **Expected**:
   - Red error box: "Email already registered"
   - Password fields cleared
   - Email kept

✅ **Pass** if duplicate is rejected

---

### **Step 5: Test Navigation**

#### **From Register to Login**:
1. On register screen, tap **"Already have an account? Login"**
2. **Expected**: Goes back to login screen

✅ **Pass** if navigation works

#### **From Login to Register**:
1. On login screen, tap **"Don't have an account? Register"**
2. **Expected**: Goes to register screen

✅ **Pass** if navigation works

---

## 🎯 Quick Test Checklist

Use this to quickly verify everything works:

- [ ] App loads on phone
- [ ] Login screen appears
- [ ] Login empty validation works
- [ ] Login password toggle works
- [ ] Can login with testuser@pricepilot.com / testpass123
- [ ] Wrong password shows error
- [ ] Can navigate to register
- [ ] Register screen appears with 4 inputs
- [ ] Register empty validation works
- [ ] Email format validation works
- [ ] Password length validation works
- [ ] Password number validation works
- [ ] Password match validation works
- [ ] Both password toggles work
- [ ] Can register with new email
- [ ] Duplicate email shows error
- [ ] Can navigate back to login

---

## � How to Check Console Logs (For Debugging)

If something doesn't work, check the console logs:

### **In Expo Terminal**:
Look for these logs when you click "Sign In":
```
Attempting login to: http://192.168.1.69:8000/auth/login
Response status: 200
Response data: { token: "...", email: "..." }
```

### **If Network Error**:
```
Network error: [TypeError: Network request failed]
```
This means phone can't reach backend. Check WiFi and backend server.

### **If Wrong Password**:
```
Response status: 401
Response data: { detail: "Invalid email or password" }
```
This is normal - backend correctly rejected wrong password.

---

## 📱 Testing on Different Devices

### **Your Current Setup**:
- Computer IP: `192.168.1.69`
- Backend: `http://192.168.1.69:8000`
- Expo: `http://192.168.1.69:8081`

### **If Testing on Different Computer**:
1. Find your computer's IP address:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" under your WiFi adapter

2. Update `mobile/constants/api.ts`:
   ```typescript
   export const API_URL = "http://YOUR_IP_HERE:8000";
   ```

3. Restart Expo server:
   ```bash
   cd mobile
   npm start
   ```

---

## �🐛 If Something Doesn't Work

### **Issue: App won't load on phone**
**Fix**: 
1. Make sure phone and computer on same WiFi
2. Shake phone → Tap "Reload"

### **Issue: "Network error" on login/register**
**Symptoms**: 
- "Unable to connect to server" error
- Console shows "Network error"

**Fix**:
1. **Check backend is running**:
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --reload
   ```
   - Must use `--host 0.0.0.0` (not 127.0.0.1)
   - Should see: "Uvicorn running on http://0.0.0.0:8000"

2. **Check same WiFi network**:
   - Phone and computer must be on same WiFi
   - WiFi 6 is fine, DNS can be different

3. **Check IP address**:
   - Open `mobile/constants/api.ts`
   - Should be: `http://192.168.1.69:8000`
   - If your computer's IP changed, update this file

4. **Try reloading app**:
   - Shake phone → Tap "Reload"

### **Issue: "Invalid email or password" on login**
**Fix**:
- Use exact credentials: `testuser@pricepilot.com` / `testpass123`
- Check for typos

### **Issue: "Email already registered" on register**
**Fix**:
- Use a different email
- Try: `newuser1@test.com`, `newuser2@test.com`, etc.

### **Issue: Eye icons not showing**
**Fix**:
- Wait a few seconds for fonts to load
- Or shake phone → Reload

---

## 📊 Test Results Template

Use this to track your testing:

```
✅ Login Screen:
   ✅ Empty validation
   ✅ Password toggle
   ✅ Successful login
   ✅ Wrong password error
   ✅ Navigate to register

✅ Register Screen:
   ✅ Empty validation
   ✅ Email format validation
   ✅ Password length validation
   ✅ Password number validation
   ✅ Password match validation
   ✅ Both password toggles
   ✅ Successful registration
   ✅ Duplicate email error
   ✅ Navigate to login

✅ Overall:
   ✅ All features working
   ✅ Ready for viva
```

---

## 🎉 What to Do After Testing

Once all tests pass:

1. ✅ Take screenshots of:
   - Login screen
   - Register screen
   - Error messages
   - Successful navigation

2. ✅ Practice explaining:
   - How validation works
   - How security works
   - How navigation works

3. ✅ Read documentation:
   - `LOGIN_SCREEN_EXPLANATION.md`
   - `REGISTER_SCREEN_EXPLANATION.md`
   - `AUTH_SCREENS_SUMMARY.md`

4. ✅ Prepare for viva:
   - Understand code flow
   - Know security features
   - Can explain validation rules

---

## 🚀 You're Ready!

**Both servers are running. Your app is loaded. Start testing now!**

1. Open Expo Go on your phone
2. Scan the QR code
3. Follow the test steps above
4. Check off each test as you complete it

**Let me know which tests pass and which fail (if any)!** 🎉
