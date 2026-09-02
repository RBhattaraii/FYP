# PricePilot Setup Checklist ✅

Use this checklist to verify your complete integration setup.

---

## 📋 Pre-Setup Verification

- [ ] Python 3.12+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Git installed (for version control)
- [ ] Expo Go app installed on phone (or emulator setup)
- [ ] Supabase account created (PostgreSQL)
- [ ] MongoDB Atlas account created (optional, for logs)

---

## 🔧 Backend Setup

### Step 1: Backend Dependencies
- [ ] Navigate to backend folder: `cd backend`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\activate` (Windows)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify apscheduler installed: `pip list | findstr apscheduler`

### Step 2: Environment Configuration
- [ ] Create `.env` file in `backend/` folder
- [ ] Add `DATABASE_URL` (Supabase Transaction Pooler connection string)
- [ ] Add `MONGODB_URI` (MongoDB Atlas connection string)
- [ ] Add `JWT_SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] Add `JWT_ALGORITHM=HS256`
- [ ] Add `ACCESS_TOKEN_EXPIRE_MINUTES=1440`

### Step 3: Database Schema
- [ ] Run migration script: `python apply_schema_migration.py`
- [ ] Verify success message: "✅ Migration completed successfully!"
- [ ] Check tables exist: `python verify_schema.py`
- [ ] Expected tables: `home_screen_products`, `search_cache`, `scrape_metadata`

### Step 4: Start Backend
- [ ] Start server: `uvicorn main:app --host 0.0.0.0 --reload`
- [ ] Check console for startup messages:
  - [ ] "[OK] PostgreSQL connection pool created successfully"
  - [ ] "MongoDB connected successfully"
  - [ ] "[SCHEDULER] Scheduler started successfully"
  - [ ] "INFO: Uvicorn running on http://0.0.0.0:8000"
- [ ] Open browser: `http://localhost:8000/docs`
- [ ] Verify API documentation loads (FastAPI Swagger UI)

### Step 5: Populate Database
- [ ] Run scraper (PowerShell): `Invoke-WebRequest -Uri http://localhost:8000/scraper/trigger -Method POST`
- [ ] Wait ~30 seconds for scraping to complete
- [ ] Check response: `"status": "success"`
- [ ] Verify products saved: `"saved_to_db": 50`
- [ ] Test home endpoint: `Invoke-WebRequest -Uri http://localhost:8000/products/home`
- [ ] Verify response has `best_deals` and `top_price_drops` arrays with products

---

## 📱 Frontend Setup

### Step 6: Frontend Dependencies
- [ ] Open new terminal (keep backend running)
- [ ] Navigate to mobile folder: `cd mobile`
- [ ] Install dependencies: `npm install`
- [ ] Verify AsyncStorage installed: Check `node_modules/@react-native-async-storage`
- [ ] No errors during installation

### Step 7: API Configuration
- [ ] Open `mobile/constants/api.ts`
- [ ] Verify API_URL configuration:
  - [ ] For Android emulator: `http://10.0.2.2:8000`
  - [ ] For iOS simulator: `http://localhost:8000`
  - [ ] For physical device: `http://YOUR_LAN_IP:8000`
- [ ] Save file

### Step 8: Verify Integration Files
- [ ] Check `mobile/services/api.ts` exists
- [ ] Check imports in `mobile/app/(tabs)/home.tsx`:
  - [ ] `import { fetchHomeScreenProducts, Product } from '../../services/api';`
- [ ] Check imports in `mobile/components/Header.tsx`:
  - [ ] `import { fetchUserProfile } from '../services/api';`
  - [ ] `import AsyncStorage from '@react-native-async-storage/async-storage';`

### Step 9: Start Mobile App
- [ ] Start Expo: `npm start`
- [ ] Check console output:
  - [ ] "🔗 API URL: http://..."
  - [ ] "📱 Platform: ios" or "android"
  - [ ] QR code displays
  - [ ] No error messages
- [ ] Choose platform:
  - [ ] Press `a` for Android emulator
  - [ ] Press `i` for iOS simulator
  - [ ] Scan QR with Expo Go (physical device)
- [ ] App installs and opens successfully

---

## 🧪 Testing Integration

### Step 10: Test Home Screen
- [ ] App shows loading spinner briefly
- [ ] Products appear in Trending section (3 products)
- [ ] Products appear in Recommended section (2 products)
- [ ] Each product shows:
  - [ ] Product image
  - [ ] Product title
  - [ ] Subtitle with discount/price drop info
  - [ ] Store name
- [ ] No error messages
- [ ] No crashes

### Step 11: Test Pull-to-Refresh
- [ ] Swipe down on home screen
- [ ] Refresh indicator appears (native spinner)
- [ ] Products reload
- [ ] UI updates with fresh data
- [ ] Refresh indicator disappears

### Step 12: Test Loading State
- [ ] Force close app
- [ ] Reopen app
- [ ] Loading spinner shows for 1-2 seconds
- [ ] Then products appear
- [ ] Smooth transition from loading to content

### Step 13: Test Error Handling
- [ ] Stop backend server (Ctrl+C in backend terminal)
- [ ] Force close mobile app
- [ ] Reopen app
- [ ] Loading spinner shows
- [ ] After 10 seconds, error message appears:
  - [ ] "Unable to Load Products"
  - [ ] Error details
  - [ ] Hint about backend server
- [ ] Restart backend server
- [ ] Pull down to refresh in app
- [ ] Products load successfully (error recovery works)

### Step 14: Test Empty State
- [ ] (Optional) Clear database products
- [ ] Restart backend
- [ ] Pull to refresh in app
- [ ] "No Products Yet" message appears
- [ ] Instructions show how to run scraper
- [ ] Scraper endpoint displayed
- [ ] Run scraper
- [ ] Pull to refresh
- [ ] Products appear

### Step 15: Test User Profile (Optional)
- [ ] Create test user: `python backend/create_test_user.py`
- [ ] Login to app with test credentials
- [ ] Check header greeting
- [ ] Should show: "Hello {FirstName}!" (not "Hello there!")
- [ ] Force close and reopen app
- [ ] Greeting shows immediately (cached)

---

## 🎯 Final Verification

### Backend Checklist
- [ ] Backend starts without errors
- [ ] PostgreSQL connection successful
- [ ] MongoDB connection successful (if configured)
- [ ] Scheduler started successfully
- [ ] API docs accessible at `/docs`
- [ ] `/products/home` returns 50 products
- [ ] Scraper can be triggered manually
- [ ] Logs show successful operations

### Frontend Checklist
- [ ] App installs without errors
- [ ] No dependency warnings
- [ ] API URL configured correctly
- [ ] Home screen loads real data
- [ ] Loading states work correctly
- [ ] Error handling works
- [ ] Pull-to-refresh works
- [ ] User profile integration works
- [ ] No console errors or warnings

### Integration Checklist
- [ ] Frontend successfully fetches from backend
- [ ] Network requests complete in <3 seconds
- [ ] Type-safe data flow (no type errors)
- [ ] Error messages are user-friendly
- [ ] App recovers from network errors
- [ ] Data updates in real-time
- [ ] No hardcoded dummy data in use

---

## 📊 Performance Benchmarks

Test and verify these performance targets:

- [ ] Home screen loads in <3 seconds
- [ ] Pull-to-refresh completes in <2 seconds
- [ ] User profile loads in <1 second (cached)
- [ ] Backend `/products/home` responds in <500ms
- [ ] Scraper completes in ~30 seconds
- [ ] No UI freezing or lag during data load
- [ ] Smooth scrolling with loaded products

---

## 🐛 Troubleshooting Completed

If you checked all boxes above but still have issues:

### Backend Issues
- [ ] Checked backend terminal for errors
- [ ] Verified `.env` file has correct credentials
- [ ] Tested endpoints in browser/Postman
- [ ] Restarted backend server
- [ ] Reinstalled dependencies: `pip install -r requirements.txt --upgrade`

### Frontend Issues
- [ ] Checked Expo terminal for errors
- [ ] Verified API_URL points to correct IP
- [ ] Tested backend from same network
- [ ] Cleared Metro cache: Press `c` in Expo terminal
- [ ] Reinstalled node_modules: `rm -rf node_modules && npm install`

### Network Issues
- [ ] Backend listens on `0.0.0.0` (not `127.0.0.1`)
- [ ] Phone and computer on same WiFi
- [ ] Firewall allows connections on port 8000
- [ ] Correct IP address in API_URL (run `ipconfig`)

---

## 📚 Documentation Reviewed

- [ ] Read `INTEGRATION_SUMMARY.md` - Overview of what was built
- [ ] Read `QUICK_START.md` - Setup instructions
- [ ] Read `FRONTEND_INTEGRATION_COMPLETE.md` - Frontend details
- [ ] Read `BACKEND_INTEGRATION_COMPLETE.md` - Backend details
- [ ] Reviewed `mobile/services/api.ts` - API service code
- [ ] Reviewed `mobile/app/(tabs)/home.tsx` - Home screen code

---

## 🎓 VIVA Preparation

- [ ] Can explain backend architecture
- [ ] Can explain frontend architecture
- [ ] Can demonstrate app functionality
- [ ] Can explain tiered search strategy
- [ ] Can explain data flow from scraper to UI
- [ ] Can explain error handling approach
- [ ] Can explain type safety with TypeScript
- [ ] Can demonstrate error recovery
- [ ] Can explain caching strategy
- [ ] Can answer questions about tech stack choices

---

## 🎉 Completion Status

### When ALL boxes are checked:
✅ Backend is fully operational
✅ Frontend is fully integrated
✅ Real data flows from backend to mobile app
✅ Error handling and loading states work
✅ User experience is smooth and professional
✅ App is ready for demonstration and VIVA

**Your PricePilot integration is COMPLETE!** 🚀

---

## 📝 Notes Section

Use this space to track any issues or customizations:

```
Date: ___________
Issues encountered:
- 
- 
- 

Solutions applied:
- 
- 
- 

Customizations made:
- 
- 
- 

Performance observations:
- 
- 
- 
```

---

## 🎬 Demo Preparation Checklist

Before presenting to supervisor/examiner:

- [ ] Both backend and frontend running
- [ ] Database populated with products
- [ ] Test user account created
- [ ] Know how to trigger scraper manually
- [ ] Can explain each endpoint's purpose
- [ ] Prepared to show code structure
- [ ] Can demonstrate error handling live
- [ ] Can explain tech stack choices
- [ ] Know performance metrics
- [ ] Prepared to answer architecture questions

---

**Save this checklist and use it every time you set up the project!**
