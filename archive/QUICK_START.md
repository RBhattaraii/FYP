# PricePilot - Quick Start Guide 🚀

Complete guide to get PricePilot backend and frontend running together.

---

## Prerequisites

- Python 3.12+ installed
- Node.js 18+ and npm installed
- PostgreSQL (Supabase) account
- MongoDB Atlas account (optional for logs)
- Expo Go app on your phone (or Android/iOS emulator)

---

## Step 1: Backend Setup

### 1.1 Install Backend Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables

Create `backend/.env` file:

```env
# PostgreSQL (Supabase Transaction Pooler)
DATABASE_URL=postgresql://user:password@host:6543/postgres

# MongoDB (for logs)
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 1.3 Apply Database Schema

```bash
python apply_schema_migration.py
```

**Expected output:** "✅ Migration completed successfully!"

### 1.4 Start Backend Server

```bash
uvicorn main:app --host 0.0.0.0 --reload
```

**Expected output:**
```
[OK] PostgreSQL connection pool created successfully
MongoDB connected successfully
[SCHEDULER] Scheduler started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend is now running at:** `http://localhost:8000`

---

## Step 2: Populate Database with Products

Before the frontend can show products, you need to scrape some data.

### Option 1: Using PowerShell (Windows)

```powershell
Invoke-WebRequest -Uri http://localhost:8000/scraper/trigger -Method POST
```

### Option 2: Using curl (if installed)

```bash
curl.exe -X POST http://localhost:8000/scraper/trigger
```

### Option 3: Using Browser

Open: `http://localhost:8000/docs`
- Find `POST /scraper/trigger` endpoint
- Click "Try it out"
- Click "Execute"

**Expected output:**
```json
{
  "status": "success",
  "message": "Homepage scraping completed",
  "results": {
    "total_scraped": 150,
    "platforms_scraped": 9,
    "saved_to_db": 50
  }
}
```

**Scraping takes ~30 seconds.** Wait for it to complete.

### Verify Products Were Saved

```powershell
Invoke-WebRequest -Uri http://localhost:8000/products/home
```

**Expected:** JSON with 50 products (25 best_deals + 25 top_price_drops)

---

## Step 3: Frontend Setup

### 3.1 Install Frontend Dependencies

Open a **new terminal** (keep backend running):

```bash
cd mobile
npm install
```

This installs all dependencies including the new `@react-native-async-storage/async-storage`.

### 3.2 Configure API URL

The app automatically detects your IP address, but verify it's correct:

1. Open `mobile/constants/api.ts`
2. Check the console output when you run `npm start` - it will print the API URL
3. If needed, manually set it to your computer's LAN IP:

```typescript
// For physical device on same WiFi
return "http://192.168.1.XXX:8000";

// For Android emulator
return "http://10.0.2.2:8000";

// For iOS simulator
return "http://localhost:8000";
```

### 3.3 Start Mobile App

```bash
npm start
```

**Choose your platform:**
- Press **`a`** for Android emulator
- Press **`i`** for iOS simulator
- **Scan QR code** with Expo Go app (physical device)

---

## Step 4: Verify Everything Works

### 4.1 Check Home Screen

1. **Open the app**
2. **You should see:**
   - Loading spinner briefly
   - "Trending Now" section with 3 products (best deals)
   - "Recommended for You" section with 2 products (price drops)
3. **If you see "No Products Yet":**
   - Go back to Step 2 and run the scraper

### 4.2 Test Pull-to-Refresh

1. **Swipe down** on the home screen
2. **You should see:**
   - Native refresh indicator
   - Products reload from backend
   - Fresh data appears

### 4.3 Check User Profile (Optional)

1. **Create a test user:**

```bash
cd backend
python create_test_user.py
```

2. **Login to the app** using test credentials
3. **Header should show:** "Hello {YourFirstName}!" instead of "Hello there!"

---

## Common Issues & Solutions

### ❌ "Unable to Load Products"

**Cause:** Frontend can't reach backend

**Solution:**
1. Verify backend is running: Open `http://localhost:8000/docs`
2. Check if backend is listening on `0.0.0.0` (not `127.0.0.1`)
3. Ensure phone and computer on same WiFi network
4. Update API URL in `mobile/constants/api.ts` with correct IP

### ❌ "No Products Yet"

**Cause:** Database is empty

**Solution:**
Run the scraper: `Invoke-WebRequest -Uri http://localhost:8000/scraper/trigger -Method POST`

### ❌ "Invoke-WebRequest : A parameter cannot be found that matches parameter name 'X'"

**Cause:** PowerShell doesn't support `-X` flag (that's curl syntax)

**Solution:**
Use `Invoke-WebRequest -Uri URL -Method POST` (PowerShell syntax)
OR use `curl.exe -X POST URL` (explicit curl.exe)

### ❌ Backend crashes on startup

**Cause:** Missing dependencies or wrong Python version

**Solution:**
1. Ensure Python 3.12+: `python --version`
2. Reinstall dependencies: `pip install -r requirements.txt --upgrade`
3. Check `.env` file exists and has correct values

### ❌ Module not found errors in mobile app

**Cause:** Dependencies not installed

**Solution:**
```bash
cd mobile
rm -rf node_modules
npm install
```

### ❌ "Network request failed" on physical device

**Cause:** Phone can't reach computer's IP

**Solution:**
1. **Find your computer's IP:**
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" under your WiFi adapter
   ```
2. **Update API URL:**
   ```typescript
   // mobile/constants/api.ts
   return "http://YOUR_IP_HERE:8000";
   ```
3. **Restart Expo:** Press `r` in terminal

---

## Testing the Complete Flow

### End-to-End Test

1. ✅ **Backend running** - Terminal shows Uvicorn logs
2. ✅ **Database populated** - `/products/home` returns 50 products
3. ✅ **Mobile app running** - Expo dev server active
4. ✅ **Home screen loads** - Shows real products from backend
5. ✅ **Pull-to-refresh works** - Reloads data successfully
6. ✅ **User profile works** - Header shows personalized greeting

### Performance Test

1. **Open app** - Home screen loads in <3 seconds
2. **Pull-to-refresh** - Completes in <2 seconds
3. **No freezing** - App remains responsive during loading
4. **Error recovery** - Stop backend, see error, restart backend, pull-to-refresh recovers

---

## Daily Development Workflow

### Morning Startup

```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2: Frontend
cd mobile
npm start
```

### During Development

- **Backend changes:** Uvicorn auto-reloads
- **Frontend changes:** Expo auto-refreshes
- **Database changes:** Rerun migration script
- **New dependencies:** Restart servers after installing

### End of Day

- **Commit changes:** `git add . && git commit -m "message"`
- **Stop servers:** `Ctrl+C` in both terminals
- **Deactivate venv:** `deactivate` (in backend terminal)

---

## Architecture Overview

```
┌─────────────────┐
│  React Native   │
│   Mobile App    │
│   (Expo 54)     │
└────────┬────────┘
         │ HTTP
         │ fetch()
         ↓
┌─────────────────┐
│   FastAPI       │
│   Backend       │
│  (Python 3.12)  │
└───┬─────────┬───┘
    │         │
    ↓         ↓
┌─────────┐ ┌──────────┐
│PostgreSQL│ │ MongoDB  │
│(Supabase)│ │ (Atlas)  │
└─────────┘ └──────────┘
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/products/home` | GET | Curated products for home screen |
| `/products/search?q=query` | GET | Tiered product search |
| `/products/search/status?request_id=id` | GET | Poll for Tier 2 results |
| `/auth/register` | POST | Create new user account |
| `/auth/login` | POST | Login and get JWT token |
| `/auth/me` | GET | Get current user profile |
| `/scraper/trigger` | POST | Manually run scraper |
| `/scraper/status` | GET | Get scraping metadata |

---

## Documentation

- **Backend:** `BACKEND_INTEGRATION_COMPLETE.md`
- **Frontend:** `FRONTEND_INTEGRATION_COMPLETE.md`
- **API Docs:** `http://localhost:8000/docs` (when backend running)
- **Database Schema:** `backend/DATABASE_MIGRATION.md`
- **Project Structure:** `docs/FOLDER_STRUCTURE.md`

---

## Next Steps

1. ✅ Backend integration - **COMPLETE**
2. ✅ Frontend integration - **COMPLETE**
3. 🔄 Implement search screen with progressive loading
4. 🔄 Add price history tracking
5. 🔄 Implement wishlist functionality
6. 🔄 Add push notifications for price drops
7. 🔄 Write end-to-end tests
8. 🔄 Deploy to production

---

## Support

If you encounter issues not covered here:

1. **Check logs:**
   - Backend: Terminal output where Uvicorn is running
   - Frontend: Expo terminal output
   - Browser: Network tab in React Native Debugger

2. **Verify setup:**
   - Backend accessible: `http://localhost:8000/docs`
   - Database connected: Check startup logs
   - Products exist: `GET /products/home`

3. **Common fixes:**
   - Restart backend: `Ctrl+C` then `uvicorn main:app --host 0.0.0.0 --reload`
   - Restart frontend: Press `r` in Expo terminal
   - Clear cache: Press `c` in Expo terminal
   - Reinstall deps: `pip install -r requirements.txt` / `npm install`

---

**🎉 Congratulations! PricePilot is now fully integrated and running!**

Your app can now:
- Scrape 9 e-commerce platforms
- Curate best deals and price drops
- Display real-time data in mobile app
- Handle user authentication
- Provide tiered search (Tier 1 fast, Tier 2 comprehensive)
- Run automatic daily scraping at midnight

**Ready for demo and VIVA presentation!** 🚀
