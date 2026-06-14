# 🔧 Fix 500 Error - Login/Register Failed

## 🐛 Problem

You're getting:
```
Response status: 500
Response data: {"detail": "Login failed"}
Response data: {"detail": "Registration failed"}
```

This means the backend is catching an exception. Let's diagnose and fix it.

---

## 🔍 Step 1: Check Backend Terminal

Look at **Terminal 1 (Backend)** where you ran `uvicorn main:app --host 0.0.0.0 --reload`

You should see error messages like:
```
Login error: <error message here>
Registration error: <error message here>
```

**Common errors:**
- `asyncpg.exceptions.UndefinedTableError` → Users table doesn't exist
- `asyncpg.exceptions.ConnectionDoesNotExistError` → Database connection failed
- `bcrypt error` → Password hashing issue
- `JWT error` → Token generation issue

---

## 🔧 Step 2: Run Diagnostic Test

This will test all backend components:

```bash
cd backend
venv\Scripts\activate
python test_backend_direct.py
```

This will test:
1. ✅ Database connection
2. ✅ Users table exists
3. ✅ Password hashing
4. ✅ JWT token generation
5. ✅ Login flow
6. ✅ Register flow

**Look for any ❌ FAIL messages**

---

## 🔧 Step 3: Common Fixes

### Fix 1: Users Table Doesn't Exist

**Symptom**: `UndefinedTableError: relation "users" does not exist`

**Fix**:
```bash
cd backend
venv\Scripts\activate
python -c "import asyncio; from app.database.postgres import create_tables; asyncio.run(create_tables())"
```

Or manually create the table:
```bash
# Connect to your Supabase database and run:
# The SQL is in backend/database_schema.sql
```

---

### Fix 2: Test User Doesn't Exist

**Symptom**: Login works but says "Invalid email or password"

**Fix**:
```bash
cd backend
venv\Scripts\activate
python create_test_user.py
```

This creates the test user: `testuser@pricepilot.com` / `testpass123`

---

### Fix 3: Database Connection Failed

**Symptom**: `ConnectionDoesNotExistError` or `could not connect to server`

**Fix**:
1. Check `.env` file has correct `DATABASE_URL`
2. Check internet connection (Supabase is online)
3. Check Supabase project is active

**Test connection**:
```bash
cd backend
venv\Scripts\activate
python test_connection.py
```

---

### Fix 4: Password Hashing Issue

**Symptom**: `bcrypt error` or `passlib error`

**Fix**:
```bash
cd backend
venv\Scripts\activate
pip uninstall bcrypt passlib
pip install bcrypt==4.0.1 passlib==1.7.4
```

---

### Fix 5: JWT Token Issue

**Symptom**: `JWT error` or `jose error`

**Fix**:
```bash
cd backend
venv\Scripts\activate
pip install python-jose[cryptography]==3.3.0
```

---

## 🔧 Step 4: Quick Fix Script

Run this to fix most common issues:

```bash
cd backend
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Create tables
python -c "import asyncio; from app.database.postgres import create_tables; asyncio.run(create_tables())"

# Create test user
python create_test_user.py

# Test everything
python test_backend_direct.py
```

---

## 🔧 Step 5: Restart Backend

After fixing, restart the backend:

```bash
# Stop backend (Ctrl+C in Terminal 1)
# Then restart:
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

---

## 🔧 Step 6: Test Again

1. **Reload app on phone**: Shake phone → Tap "Reload"
2. **Try login**: `testuser@pricepilot.com` / `testpass123`
3. **Check Terminal 1**: Should see no errors
4. **Check Expo terminal**: Should see `Response status: 200`

---

## 📋 Diagnostic Checklist

Run through this checklist:

### Backend
- [ ] Backend terminal shows no errors
- [ ] Can see "Uvicorn running on http://0.0.0.0:8000"
- [ ] No error messages when trying to login/register

### Database
- [ ] `.env` file has correct `DATABASE_URL`
- [ ] Can connect to database (run `python test_connection.py`)
- [ ] Users table exists
- [ ] Test user exists (run `python create_test_user.py`)

### Dependencies
- [ ] `bcrypt==4.0.1` installed
- [ ] `passlib==1.7.4` installed
- [ ] `python-jose[cryptography]` installed
- [ ] All requirements.txt packages installed

### Network
- [ ] Backend running on `0.0.0.0:8000` (not 127.0.0.1)
- [ ] Phone and computer on same WiFi
- [ ] IP in `mobile/constants/api.ts` is correct

---

## 🆘 Still Not Working?

### Check Backend Logs

Look at Terminal 1 and find the exact error message after "Login error:" or "Registration error:"

**Copy the full error message and we can diagnose it.**

Common error patterns:

#### Error: `relation "users" does not exist`
**Fix**: Create users table
```bash
python -c "import asyncio; from app.database.postgres import create_tables; asyncio.run(create_tables())"
```

#### Error: `could not connect to server`
**Fix**: Check DATABASE_URL in .env file

#### Error: `Invalid salt`
**Fix**: Reinstall bcrypt
```bash
pip uninstall bcrypt
pip install bcrypt==4.0.1
```

#### Error: `No module named 'jose'`
**Fix**: Install python-jose
```bash
pip install python-jose[cryptography]
```

---

## 🎯 Expected Behavior

### When Login Works:
**Terminal 1 (Backend):**
```
INFO:     192.168.1.69:xxxxx - "POST /auth/login HTTP/1.1" 200 OK
```

**Expo Terminal:**
```
LOG  Attempting login to: http://192.168.1.69:8000/auth/login
LOG  Response status: 200
LOG  Response data: { token: "eyJ...", email: "testuser@pricepilot.com" }
```

**Phone:**
- Navigates to Home screen

### When Register Works:
**Terminal 1 (Backend):**
```
INFO:     192.168.1.69:xxxxx - "POST /auth/register HTTP/1.1" 200 OK
```

**Expo Terminal:**
```
LOG  Attempting registration to: http://192.168.1.69:8000/auth/register
LOG  Response status: 200
LOG  Response data: { token: "eyJ...", email: "newuser@test.com" }
```

**Phone:**
- Navigates to Home screen

---

## 📞 Quick Commands Reference

```bash
# Activate venv
cd backend
venv\Scripts\activate

# Test database connection
python test_connection.py

# Create users table
python -c "import asyncio; from app.database.postgres import create_tables; asyncio.run(create_tables())"

# Create test user
python create_test_user.py

# Run diagnostic test
python test_backend_direct.py

# Reinstall dependencies
pip install -r requirements.txt

# Start backend
uvicorn main:app --host 0.0.0.0 --reload
```

---

## 🎯 Next Steps

1. **Run diagnostic test**: `python test_backend_direct.py`
2. **Check what fails**: Look for ❌ FAIL messages
3. **Apply the fix**: Use the fixes above
4. **Restart backend**: Stop and start uvicorn
5. **Test on phone**: Try login/register again

**Let me know what the diagnostic test shows!**
