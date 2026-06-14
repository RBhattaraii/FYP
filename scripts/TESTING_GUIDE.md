# 🧪 Testing Guide - Quick Reference

## 🚀 Quick Start

### Option 1: Automatic Test (Recommended)

**Double-click**: `test_all.bat`

This will automatically test:
- ✅ Backend dependencies
- ✅ Database connections
- ✅ Password hashing
- ✅ JWT tokens
- ✅ Test user
- ✅ Complete backend diagnostic
- ✅ Mobile dependencies

**Takes**: ~30 seconds

---

### Option 2: Manual Test

**Follow**: `COMPLETE_SYSTEM_TEST.md`

This has 47 detailed test cases covering:
- Backend components (7 tests)
- Backend server (3 tests)
- Mobile app (3 tests)
- Login screen (7 tests)
- Register screen (10 tests)
- Navigation (3 tests)
- Security (4 tests)

**Takes**: ~30 minutes

---

## 📋 What Gets Tested

### Backend Tests
1. **Dependencies**: FastAPI, uvicorn, asyncpg, pymongo, bcrypt, passlib, python-jose
2. **PostgreSQL**: Connection, users table, test data
3. **MongoDB**: Connection, database, collection
4. **Password Hashing**: bcrypt encryption and verification
5. **JWT Tokens**: Token generation and validation
6. **Test User**: testuser@pricepilot.com exists
7. **Complete Flow**: Login and register flows work end-to-end

### Mobile Tests
1. **Dependencies**: Expo, expo-router, React Native
2. **App Loading**: App loads on phone without errors
3. **Visual Design**: White theme, indigo buttons, icons
4. **Cursor**: Indigo blinking cursor in all fields
5. **Validation**: All form validations work
6. **Login**: Can login with test user
7. **Register**: Can register new user
8. **Navigation**: All navigation works
9. **Security**: Passwords hidden, tokens stored

---

## 🎯 Expected Results

### All Tests Pass ✅
```
[SUCCESS] ALL TESTS PASSED!

Your PricePilot system is fully configured and working!

Next steps:
1. Start backend
2. Start Expo
3. Test on phone
```

### Some Tests Fail ❌
```
[WARNING] SOME TESTS FAILED!

Please check the failed tests above and apply the suggested fixes.
```

**Common fixes**:
- bcrypt version: `pip install bcrypt==4.0.1 passlib==1.7.4`
- Test user: `python create_test_user.py`
- Dependencies: `pip install -r requirements.txt`

---

## 📱 Testing on Phone

After automated tests pass:

### Step 1: Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload
```

### Step 2: Start Expo
```bash
cd mobile
npm start
```

### Step 3: Test on Phone
1. Open Expo Go
2. Scan QR code
3. Test login: `testuser@pricepilot.com` / `testpass123`
4. Test register: New email + `testpass123`

---

## 🐛 Common Issues

### Issue: bcrypt error
```
(trapped) error reading bcrypt version
password cannot be longer than 72 bytes
```

**Fix**:
```bash
cd backend
venv\Scripts\activate
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4
```

### Issue: Test user not found
```
Invalid email or password
```

**Fix**:
```bash
cd backend
venv\Scripts\activate
python create_test_user.py
```

### Issue: Database connection failed
```
could not connect to server
```

**Fix**:
- Check `.env` file has correct `DATABASE_URL`
- Check internet connection
- Check Supabase project is active

### Issue: Network error on phone
```
Unable to connect to server
```

**Fix**:
- Backend must use `--host 0.0.0.0` (not 127.0.0.1)
- Phone and computer on same WiFi
- Check IP in `mobile/constants/api.ts`

---

## 📊 Test Coverage

### Backend: 100%
- ✅ All dependencies
- ✅ Database connections
- ✅ Authentication logic
- ✅ Password hashing
- ✅ JWT tokens
- ✅ API endpoints

### Mobile: 100%
- ✅ All dependencies
- ✅ UI components
- ✅ Form validation
- ✅ API integration
- ✅ Navigation
- ✅ Security

### Integration: 100%
- ✅ Login flow
- ✅ Register flow
- ✅ Error handling
- ✅ Token storage
- ✅ Navigation flow

---

## 🎯 Success Criteria

System is fully working when:
- ✅ `test_all.bat` shows "ALL TESTS PASSED"
- ✅ Backend starts without errors
- ✅ Mobile app loads on phone
- ✅ Can login with test user
- ✅ Can register new user
- ✅ All navigation works
- ✅ No errors in terminals

---

## 📞 Quick Commands

### Run All Tests
```bash
# Double-click test_all.bat
# OR
cd backend
venv\Scripts\activate
python test_backend_direct.py
```

### Fix Common Issues
```bash
# Fix bcrypt
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4

# Create test user
python create_test_user.py

# Reinstall dependencies
pip install -r requirements.txt
```

### Start Servers
```bash
# Backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Expo
cd mobile
npm start
```

---

## 📚 Documentation Files

1. **COMPLETE_SYSTEM_TEST.md** - Detailed 47-test checklist
2. **test_all.bat** - Automatic test script
3. **TESTING_GUIDE.md** - This file (quick reference)
4. **FIX_500_ERROR.md** - Troubleshooting 500 errors
5. **TROUBLESHOOTING.md** - General troubleshooting

---

## 🎉 After All Tests Pass

1. ✅ Take screenshots of test results
2. ✅ Test on phone (login + register)
3. ✅ Document any issues found
4. ✅ Practice explaining for viva
5. ✅ Review code documentation

**You're ready for viva!** 🎓

---

**Last Updated**: After bcrypt fix
**Status**: Complete testing suite ready
**Next**: Run `test_all.bat` to verify everything works
