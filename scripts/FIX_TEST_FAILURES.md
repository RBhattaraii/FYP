# 🔧 Fix Test Failures

## 📊 Test Results Summary

From your test run:
- ✅ **PASS**: Backend Dependencies
- ❌ **FAIL**: Database Connections (PostgreSQL)
- ✅ **PASS**: Password Hashing
- ✅ **PASS**: JWT Token Generation
- ❌ **FAIL**: Test User
- ❌ **FAIL**: Backend Diagnostic
- ✅ **PASS**: Mobile Dependencies

**3 tests failed** - Let's fix them!

---

## 🔧 Quick Fix (Automatic)

Run this to fix all issues automatically:

```bash
cd backend
quick_fix.bat
```

This will:
1. Fix bcrypt version (downgrade to 4.0.1)
2. Create test user
3. Test backend

**Takes**: ~2 minutes

---

## 🔧 Manual Fix (Step by Step)

### Fix 1: bcrypt Version Warning

**Issue**: bcrypt version should be 4.0.1

**Fix**:
```bash
cd backend
venv\Scripts\activate
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4
```

---

### Fix 2: PostgreSQL Connection Failed

**Issue**: Cannot connect to PostgreSQL database

**Possible Causes**:
1. DATABASE_URL in `.env` is incorrect
2. Internet connection issue
3. Supabase project is paused/inactive

**Fix**:

#### Check 1: Verify .env file
Open `backend\.env` and check:
```
DATABASE_URL=postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

Make sure:
- No quotes around the URL
- No spaces
- Password is URL-encoded

#### Check 2: Test connection manually
```bash
cd backend
venv\Scripts\activate
python test_connection.py
```

If this fails, the issue is with your Supabase connection.

#### Check 3: Verify Supabase project
1. Go to https://supabase.com
2. Check if your project is active
3. Check if you can connect from Supabase dashboard

---

### Fix 3: Test User Creation Failed

**Issue**: Cannot create test user (related to PostgreSQL issue)

**Fix**:

After fixing PostgreSQL connection, run:
```bash
cd backend
venv\Scripts\activate
python create_test_user.py
```

Select option `1` to create test user.

**Expected Output**:
```
✅ Test user created successfully!
   Email: testuser@pricepilot.com
   Password: testpass123
```

---

### Fix 4: Backend Diagnostic Failed

**Issue**: `ImportError: cannot import name 'get_db_pool'`

**Status**: ✅ **FIXED** - I've updated the test file

The test file was trying to import `get_db_pool` which doesn't exist. I've fixed it to use `create_pool` instead.

**Verify Fix**:
```bash
cd backend
venv\Scripts\activate
python test_backend_direct.py
```

---

## 🎯 After Fixing

### Step 1: Run Tests Again

```bash
cd C:\Users\NITOR 5\Desktop\FYP
test_all.bat
```

**Expected**: All tests should now PASS

---

### Step 2: Start Backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

**Expected Output**:
```
✅ PostgreSQL connection pool created successfully
✅ MongoDB connected successfully
🚀 PricePilot API started successfully
INFO: Application startup complete.
```

---

### Step 3: Test on Phone

1. Start Expo: `cd mobile && npm start`
2. Scan QR code with Expo Go
3. Test login: `testuser@pricepilot.com` / `testpass123`
4. Should navigate to Home screen ✅

---

## 📋 Verification Checklist

After applying fixes:

- [ ] bcrypt version is 4.0.1
- [ ] PostgreSQL connection works
- [ ] Test user exists in database
- [ ] Backend diagnostic test passes
- [ ] `test_all.bat` shows ALL TESTS PASSED
- [ ] Backend starts without errors
- [ ] Can login on phone
- [ ] Can register on phone

---

## 🐛 If PostgreSQL Still Fails

### Option 1: Check Supabase Dashboard

1. Go to https://supabase.com
2. Login to your account
3. Select your project
4. Go to Settings → Database
5. Check connection string
6. Make sure project is not paused

### Option 2: Test with psql

If you have psql installed:
```bash
psql "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
```

If this fails, the issue is with Supabase, not your code.

### Option 3: Create New Supabase Project

If your project is inactive:
1. Create new Supabase project
2. Get new DATABASE_URL
3. Update `backend\.env`
4. Run `database_schema.sql` to create tables
5. Run `create_test_user.py`

---

## 📞 Quick Commands Reference

```bash
# Fix bcrypt
cd backend
venv\Scripts\activate
pip install bcrypt==4.0.1 passlib==1.7.4

# Create test user
python create_test_user.py

# Test backend
python test_backend_direct.py

# Test connection
python test_connection.py

# Run all tests
cd ..
test_all.bat

# Start backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

---

## 🎯 Expected Final Result

When everything is fixed, `test_all.bat` should show:

```
============================================================================
TEST SUMMARY
============================================================================
[PASS] Test 1: Backend Dependencies
[PASS] Test 2: Database Connections
[PASS] Test 3: Password Hashing
[PASS] Test 4: JWT Token Generation
[PASS] Test 5: Test User
[PASS] Test 6: Backend Diagnostic
[PASS] Test 7: Mobile Dependencies
============================================================================

[SUCCESS] ALL TESTS PASSED!

Your PricePilot system is fully configured and working!
```

---

## 🆘 Still Having Issues?

1. **Check backend terminal** for error messages
2. **Check .env file** for correct DATABASE_URL
3. **Check internet connection**
4. **Check Supabase project status**
5. **Run `python test_connection.py`** to isolate the issue

**Most likely issue**: Supabase connection problem

**Quick test**: Can you access https://supabase.com and see your project?

---

**Next**: Run `backend\quick_fix.bat` to fix all issues automatically!
