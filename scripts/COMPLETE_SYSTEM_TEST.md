# ✅ Complete System Test - PricePilot

## 🎯 Purpose

This document helps you verify that ALL configured components are working correctly:
- Backend (FastAPI)
- Database (PostgreSQL + MongoDB)
- Authentication (JWT + bcrypt)
- Mobile App (React Native Expo)
- Login & Register Screens

---

## 🚀 Quick Test (Run BAT File)

**Easiest way**: Double-click `test_all.bat` in the FYP folder

This will automatically test:
1. ✅ Backend dependencies
2. ✅ Database connections
3. ✅ Password hashing
4. ✅ JWT tokens
5. ✅ Login flow
6. ✅ Register flow
7. ✅ Mobile app dependencies

---

## 📋 Manual Testing Checklist

### Part 1: Backend Components

#### Test 1.1: Backend Dependencies ✅
```bash
cd backend
venv\Scripts\activate
pip list | findstr "fastapi uvicorn asyncpg pymongo bcrypt passlib python-jose"
```

**Expected Output:**
```
asyncpg                4.x.x
bcrypt                 4.0.1
fastapi                0.x.x
passlib                1.7.4
pymongo                4.6.0
python-jose            3.3.0
uvicorn                0.x.x
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.2: PostgreSQL Connection ✅
```bash
cd backend
venv\Scripts\activate
python test_connection.py
```

**Expected Output:**
```
✅ PostgreSQL connection successful!
✅ Users table exists
✅ Number of users: X
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.3: MongoDB Connection ✅
```bash
cd backend
venv\Scripts\activate
python test_mongodb.py
```

**Expected Output:**
```
✅ MongoDB connection successful!
Database: pricepilot_raw
Collection: raw_products
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.4: Password Hashing ✅
```bash
cd backend
venv\Scripts\activate
python -c "from app.auth.password import hash_password, verify_password; h = hash_password('test123'); print('✅ Hash:', h[:30]); print('✅ Verify:', verify_password('test123', h))"
```

**Expected Output:**
```
✅ Hash: $2b$12$...
✅ Verify: True
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.5: JWT Token Generation ✅
```bash
cd backend
venv\Scripts\activate
python -c "from app.auth.jwt_handler import create_access_token; t = create_access_token('test-user-id'); print('✅ Token:', t[:50])"
```

**Expected Output:**
```
✅ Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.6: Test User Exists ✅
```bash
cd backend
venv\Scripts\activate
python create_test_user.py
```

**Expected Output:**
```
✅ Test user created/updated successfully!
Email: testuser@pricepilot.com
Password: testpass123
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 1.7: Backend Diagnostic Test ✅
```bash
cd backend
venv\Scripts\activate
python test_backend_direct.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED!
   Backend is working correctly.
```

**Status**: [ ] PASS [ ] FAIL

---

### Part 2: Backend Server

#### Test 2.1: Start Backend Server ✅
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ PostgreSQL connection pool created successfully
✅ MongoDB connected successfully (or warning if failed)
🚀 PricePilot API started successfully
INFO:     Application startup complete.
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 2.2: Backend API Docs ✅

**Open browser**: `http://localhost:8000/docs`

**Expected**: FastAPI Swagger UI with endpoints:
- POST /auth/register
- POST /auth/login

**Status**: [ ] PASS [ ] FAIL

---

#### Test 2.3: Backend Health Check ✅

**Open browser**: `http://localhost:8000`

**Expected**: JSON response with API info

**Status**: [ ] PASS [ ] FAIL

---

### Part 3: Mobile App

#### Test 3.1: Mobile Dependencies ✅
```bash
cd mobile
npm list expo expo-router react-native
```

**Expected Output:**
```
expo@54.0.0
expo-router@6.0.23
react-native@0.81.5
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 3.2: Start Expo Server ✅
```bash
cd mobile
npm start
```

**Expected Output:**
```
› Metro waiting on exp://192.168.1.69:8081
› Scan the QR code above with Expo Go
```

**Status**: [ ] PASS [ ] FAIL

---

#### Test 3.3: App Loads on Phone ✅

1. Open Expo Go app
2. Scan QR code
3. Wait for app to load

**Expected**: 
- White background
- "LOGIN TO YOUR ACCOUNT" title
- Indigo "Login" button
- No errors

**Status**: [ ] PASS [ ] FAIL

---

### Part 4: Login Screen

#### Test 4.1: Visual Design ✅

**Check**:
- [ ] White background (#FFFFFF)
- [ ] "LOGIN TO YOUR ACCOUNT" title
- [ ] Email field with mail icon
- [ ] Password field with lock icon
- [ ] Indigo "Login" button (#6366F1)
- [ ] "Remember me" checkbox
- [ ] "Forgot password?" link
- [ ] "Sign Up" link
- [ ] No social login buttons

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.2: Cursor Blinking ✅

1. Tap email field
2. Look for indigo blinking cursor |

**Expected**: Visible indigo cursor

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.3: Empty Validation ✅

1. Leave fields empty
2. Tap "Login"

**Expected**:
- "Email is required" error
- "Password is required" error
- Red borders on fields

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.4: Email Validation ✅

1. Enter: `notanemail`
2. Tap "Login"

**Expected**: "Please enter a valid email address"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.5: Successful Login ✅

1. Email: `testuser@pricepilot.com`
2. Password: `testpass123`
3. Tap "Login"

**Expected**:
- Loading spinner
- Navigate to Home screen
- Backend logs: `200 OK`

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.6: Wrong Password ✅

1. Email: `testuser@pricepilot.com`
2. Password: `wrongpassword`
3. Tap "Login"

**Expected**:
- Red error: "Invalid email or password"
- Password field cleared
- Email kept

**Status**: [ ] PASS [ ] FAIL

---

#### Test 4.7: Network Error Handling ✅

1. Turn off WiFi on phone
2. Try to login

**Expected**: "Unable to connect to server" error

**Status**: [ ] PASS [ ] FAIL

---

### Part 5: Register Screen

#### Test 5.1: Navigate to Register ✅

1. Tap "Sign Up" link on login screen

**Expected**: Navigate to register screen

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.2: Visual Design ✅

**Check**:
- [ ] White background
- [ ] Back arrow (top left)
- [ ] "SIGN UP" title
- [ ] First Name field with person icon
- [ ] Last Name field with person icon
- [ ] Email field with mail icon
- [ ] Password field with lock icon
- [ ] Confirm Password field with lock icon
- [ ] Indigo "Sign Up" button
- [ ] "Login" link

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.3: Cursor Blinking ✅

1. Tap each field
2. Look for indigo cursor in all fields

**Expected**: Visible indigo cursor in all 5 fields

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.4: Required Fields ✅

1. Leave all fields empty
2. Tap "Sign Up"

**Expected**:
- "First name is required"
- "Last name is required"
- "Email is required"
- "Password is required"
- "Please confirm your password"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.5: Email Validation ✅

1. First Name: `John`
2. Last Name: `Doe`
3. Email: `notanemail`
4. Password: `testpass123`
5. Confirm: `testpass123`
6. Tap "Sign Up"

**Expected**: "Please enter a valid email address"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.6: Password Length Validation ✅

1. First Name: `John`
2. Last Name: `Doe`
3. Email: `test@test.com`
4. Password: `short`
5. Confirm: `short`
6. Tap "Sign Up"

**Expected**: "Password must be at least 8 characters"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.7: Password Number Validation ✅

1. Password: `password` (no number)
2. Confirm: `password`
3. Tap "Sign Up"

**Expected**: "Password must contain at least one number"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.8: Password Match Validation ✅

1. Password: `password123`
2. Confirm: `password456`
3. Tap "Sign Up"

**Expected**: "Passwords do not match"

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.9: Successful Registration ✅

1. First Name: `John`
2. Last Name: `Doe`
3. Email: `newuser1@test.com` (unique!)
4. Password: `testpass123`
5. Confirm: `testpass123`
6. Tap "Sign Up"

**Expected**:
- Loading spinner
- Navigate to Home screen
- Backend logs: `200 OK`

**Status**: [ ] PASS [ ] FAIL

---

#### Test 5.10: Duplicate Email ✅

1. First Name: `Jane`
2. Last Name: `Smith`
3. Email: `testuser@pricepilot.com` (exists)
4. Password: `testpass123`
5. Confirm: `testpass123`
6. Tap "Sign Up"

**Expected**: "Email already registered" error

**Status**: [ ] PASS [ ] FAIL

---

### Part 6: Navigation

#### Test 6.1: Login → Register ✅

1. On login screen, tap "Sign Up"

**Expected**: Navigate to register

**Status**: [ ] PASS [ ] FAIL

---

#### Test 6.2: Register → Login ✅

1. On register screen, tap "Login"

**Expected**: Navigate to login

**Status**: [ ] PASS [ ] FAIL

---

#### Test 6.3: Back Button ✅

1. On register screen, tap back arrow

**Expected**: Navigate to login

**Status**: [ ] PASS [ ] FAIL

---

### Part 7: Security

#### Test 7.1: Passwords Hidden ✅

**Check**: Passwords show as dots (••••••••)

**Status**: [ ] PASS [ ] FAIL

---

#### Test 7.2: Password Toggle ✅

1. Enter password
2. Tap eye icon

**Expected**: Password becomes visible

**Status**: [ ] PASS [ ] FAIL

---

#### Test 7.3: No Passwords in Logs ✅

**Check backend terminal**: No plain text passwords logged

**Status**: [ ] PASS [ ] FAIL

---

#### Test 7.4: JWT Token Stored ✅

After successful login/register, token is stored securely

**Status**: [ ] PASS [ ] FAIL

---

## 📊 Test Summary

### Backend Components
- [ ] Dependencies installed correctly
- [ ] PostgreSQL connection works
- [ ] MongoDB connection works
- [ ] Password hashing works
- [ ] JWT token generation works
- [ ] Test user exists
- [ ] Diagnostic test passes

### Backend Server
- [ ] Server starts without errors
- [ ] API docs accessible
- [ ] Health check works

### Mobile App
- [ ] Dependencies installed
- [ ] Expo server starts
- [ ] App loads on phone

### Login Screen
- [ ] Visual design correct
- [ ] Cursor blinking works
- [ ] Empty validation works
- [ ] Email validation works
- [ ] Successful login works
- [ ] Wrong password handled
- [ ] Network error handled

### Register Screen
- [ ] Visual design correct
- [ ] Cursor blinking works
- [ ] Required fields validated
- [ ] Email validation works
- [ ] Password length validated
- [ ] Password number validated
- [ ] Password match validated
- [ ] Successful registration works
- [ ] Duplicate email handled

### Navigation
- [ ] Login ↔ Register works
- [ ] Back button works

### Security
- [ ] Passwords hidden
- [ ] Password toggle works
- [ ] No passwords in logs
- [ ] JWT tokens stored

---

## 🎯 Overall Status

**Total Tests**: 47
**Passed**: ___
**Failed**: ___

**Status**: [ ] ALL PASS [ ] SOME FAIL

---

## 🐛 Common Issues & Fixes

### Issue: Backend won't start
**Fix**: 
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: bcrypt error
**Fix**:
```bash
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4
```

### Issue: Test user doesn't exist
**Fix**:
```bash
python create_test_user.py
```

### Issue: Network error on phone
**Fix**:
- Check same WiFi
- Check IP in `mobile/constants/api.ts`
- Backend must use `--host 0.0.0.0`

---

## 📞 Quick Commands

```bash
# Backend
cd backend
venv\Scripts\activate
python test_backend_direct.py
uvicorn main:app --host 0.0.0.0 --reload

# Mobile
cd mobile
npm start

# Test user
cd backend
venv\Scripts\activate
python create_test_user.py
```

---

## ✅ Success Criteria

System is fully working when:
- ✅ All backend tests pass
- ✅ Backend starts without errors
- ✅ Mobile app loads on phone
- ✅ Can login with test user
- ✅ Can register new user
- ✅ Navigation works
- ✅ All security features work

---

**Last Updated**: After bcrypt fix and modern theme update
**Status**: Ready for comprehensive testing
