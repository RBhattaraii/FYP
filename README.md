# PricePilot 🚀

**Smart Price Comparison & Deal Finder for Nepal**

Real-time price tracking across 11 e-commerce platforms with tiered search, automatic deal discovery, and progressive loading for optimal UX.

A price comparison mobile application built with React Native and FastAPI.

## 🚀 Quick Start

**New to the project?** Check out the [scripts folder](./scripts/) for setup guides and helper scripts.

**Start here:** [scripts/START_HERE.md](./scripts/START_HERE.md) - Complete 5-step guide to get the app running

## Project Structure

```
PricePilot/
├── mobile/               # React Native (Expo + TypeScript)
│   ├── app/              # Expo Router screens
│   │   ├── (auth)/       # Login & Register screens
│   │   ├── (tabs)/       # Tab navigation screens
│   │   └── index.tsx     # Root redirect
│   ├── components/       # Reusable UI components
│   ├── constants/        # Theme, API config
│   ├── assets/           # Images, fonts, etc.
│   ├── app.json          # Expo configuration
│   ├── package.json      # Dependencies
│   └── tsconfig.json     # TypeScript config
│
├── backend/              # FastAPI (Python)
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── models/       # Data models
│   │   ├── database/     # Database connections
│   │   ├── auth/         # JWT authentication
│   │   └── __init__.py
│   ├── main.py           # FastAPI app entry
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Environment variables
│
├── scripts/              # Helper scripts & documentation
│   ├── START_HERE.md     # Quick start guide
│   ├── fix-firewall.ps1  # Firewall configuration
│   ├── test-network.ps1  # Network diagnostics
│   └── ...               # More scripts and docs
│
├── docs/                 # Architecture documentation
└── .kiro/                # Kiro specs
```

## Tech Stack

### Frontend
- **Framework**: React Native with Expo (SDK 54)
- **Language**: TypeScript
- **Navigation**: Expo Router
- **HTTP Client**: Fetch API
- **Design**: iOS-style with SF Pro Display font

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT (python-jose) + bcrypt
- **Databases**:
  - PostgreSQL (Supabase) - Structured data
  - MongoDB Atlas - Raw scraped data

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Expo Go app on your phone
- PostgreSQL (Supabase account)
- MongoDB Atlas account

### Quick Setup

**For detailed setup instructions, see [scripts/START_HERE.md](./scripts/START_HERE.md)**

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure `.env` file with your database credentials

5. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --reload
   ```

### Mobile Setup

1. Navigate to mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Expo development server:
   ```bash
   npx expo start
   ```

4. Scan QR code with Expo Go app

### Test Credentials

```
Email: testuser@pricepilot.com
Password: testpass123
```

## Features

### ✅ Completed
- User authentication (register, login, JWT)
- Modern login/register screens with indigo theme
- Home screen with iOS-style design:
  - Header with greeting and notifications
  - Search bar with voice icon
  - Category pills (7 categories)
  - Trending products section
  - Recommended products with discounts
  - Bottom tab navigation
- Auto IP detection for DHCP networks
- Security features (rate limiting, CORS, headers)

### 🚧 In Progress
- Product detail screen
- Search functionality
- Category filtering

### 📋 Planned
- Favorites system
- User profile management
- Price comparison API integration
- Web scraping for product data
- Price history tracking
- Price alerts

## Architecture

- **Frontend**: Mobile app with Expo Router navigation
- **Backend**: RESTful API with asyncpg (no ORM)
- **Databases**: 
  - PostgreSQL for structured product and user data
  - MongoDB for raw scraped HTML and flexible data

## Scripts & Documentation

All helper scripts and detailed documentation are in the [scripts/](./scripts/) folder:

- **START_HERE.md** - Quick start guide
- **fix-firewall.ps1** - Fix Windows Firewall blocking
- **test-network.ps1** - Test network connectivity
- **CURRENT_STATUS.md** - Complete project status
- **TROUBLESHOOTING.md** - Common issues and solutions

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Style
- Backend: Follow PEP 8
- Frontend: ESLint + Prettier

## Troubleshooting

Having issues? Check:
1. [scripts/TROUBLESHOOTING.md](./scripts/TROUBLESHOOTING.md)
2. [scripts/NETWORK_FIX_GUIDE.md](./scripts/NETWORK_FIX_GUIDE.md)
3. [scripts/FIREWALL_FIX_GUIDE.md](./scripts/FIREWALL_FIX_GUIDE.md)

## License

MIT


---

## 🚀 Quick Start (After Fresh Clone/Setup)

### Option 1: Automated Setup

**Run the fix script first:**
```powershell
cd C:\Users\NITOR 5\Desktop\FYP
.\fix_all_issues.ps1
```

**Then start everything:**
```cmd
start_everything.bat
```

This will:
- ✅ Install all backend dependencies
- ✅ Clear mobile cache
- ✅ Start backend server (Terminal 1)
- ✅ Start mobile app (Terminal 2)
- ✅ Show instructions (Terminal 3)

### Option 2: Manual Setup

**1. Install Backend Dependencies:**
```powershell
cd backend
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Setup Database:**
- Go to Supabase SQL Editor
- Run `backend/database_schema.sql`

**3. Configure Environment:**
```powershell
cd backend
# Create .env file
echo DATABASE_URL=your_supabase_connection_string > .env
```

**4. Start Backend:**
```powershell
cd backend
venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --reload
```

**5. Trigger Initial Scraping:**
```powershell
cd backend
.\trigger_scraper.ps1
```

**6. Start Mobile App:**
```powershell
cd mobile
npx expo start -c
```

---

## 🔧 Recent Fixes Applied

All issues have been resolved! See [`FIXES_APPLIED.md`](FIXES_APPLIED.md) for details.

### Issues Fixed:
- ✅ Metro bundler path alias resolution (`@/constants/api`)
- ✅ Missing `apscheduler` dependency
- ✅ Empty home page / no data
- ✅ Method Not Allowed (405) on scraper endpoint

### Files Created:
- `mobile/metro.config.js` - Metro bundler configuration
- `backend/check_database.py` - Database diagnostic tool
- `fix_all_issues.ps1` / `.bat` - Automated fix scripts
- `FIX_COMPLETE_GUIDE.md` - Comprehensive troubleshooting guide
- `start_everything.bat` - One-click startup script

---

## 📚 Documentation

- **[FIX_COMPLETE_GUIDE.md](FIX_COMPLETE_GUIDE.md)** - Detailed troubleshooting and setup guide
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Summary of all recent fixes
- **[QUICK_START.md](QUICK_START.md)** - Original quick start guide
- **[TROUBLESHOOTING_EMPTY_HOME.md](TROUBLESHOOTING_EMPTY_HOME.md)** - Empty home page solutions

---

## 🛠️ Useful Scripts

### Backend Scripts
```powershell
cd backend

# Check database connection and data
python check_database.py

# Trigger manual scraping
.\trigger_scraper.ps1

# Start backend server
uvicorn main:app --host 0.0.0.0 --reload
```

### Mobile Scripts
```powershell
cd mobile

# Clear cache and start fresh
npx expo start -c

# Start normally
npx expo start
```

### Fix Scripts
```powershell
# PowerShell version
.\fix_all_issues.ps1

# CMD version
fix_all_issues.bat

# Start everything at once
start_everything.bat
```

---

## 🔍 Verification Checklist

### ✅ Backend
- [ ] Backend starts without errors
- [ ] `python check_database.py` shows products > 0
- [ ] API works: `http://localhost:8000/products/home`

### ✅ Mobile
- [ ] Metro bundler starts without path alias errors
- [ ] App loads in Expo Go
- [ ] Home screen shows products with images

### ✅ Database
- [ ] All 4 tables exist (users, home_screen_products, search_cache, scrape_metadata)
- [ ] home_screen_products has 200+ products
- [ ] Images and prices are valid

---

## 🐛 Troubleshooting

### Issue: "Unable to resolve @/constants/api"
**Solution:**
```powershell
cd mobile
npx expo start -c
```
Metro config is now fixed. The `-c` flag clears cache.

### Issue: Home Page is Empty
**Solution:**
```powershell
cd backend
.\trigger_scraper.ps1
```
This populates the database with real products.

### Issue: ModuleNotFoundError: apscheduler
**Solution:**
```powershell
cd backend
venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade
```

### More Issues?
See [`FIX_COMPLETE_GUIDE.md`](FIX_COMPLETE_GUIDE.md) for comprehensive troubleshooting.

---

## 📊 Project Structure

```
PricePilot/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Pydantic models
│   │   └── database/     # Database connection
│   ├── venv/             # Python virtual environment
│   ├── main.py           # FastAPI app entry point
│   ├── check_database.py # Database diagnostic tool
│   └── trigger_scraper.ps1
│
├── mobile/               # React Native (Expo) app
│   ├── app/             # Expo Router pages
│   ├── components/      # Reusable UI components
│   ├── services/        # API client
│   ├── constants/       # Configuration (API URLs)
│   └── metro.config.js  # Metro bundler config
│
├── scrapers/            # Scraper implementations
│
├── fix_all_issues.ps1   # Automated fix script
├── start_everything.bat # One-click startup
└── FIX_COMPLETE_GUIDE.md # Troubleshooting guide
```

---

## 🎯 Key Features

### Backend
- ✅ Tiered search (Tier 1: 2s, Tier 2: background)
- ✅ Daily automatic scraping (midnight)
- ✅ 11 platform scrapers (8 working, 3 known issues)
- ✅ PostgreSQL database (Supabase)
- ✅ JWT authentication
- ✅ Rate limiting

### Mobile
- ✅ Expo Router navigation
- ✅ Progressive loading
- ✅ Auto-detected API URLs
- ✅ Product detail views
- ✅ Search with live updates

### Scrapers
**Working (8/11):**
- Daraz, Oliz, HardwarePasal, Hukut, Jeevee, NeoStore, CGDigital, UfoNepal

**Known Issues (3/11):**
- Sastodeal, Hamrobazar (implementation incomplete)
- Better (Playwright incompatible with Windows)

---

## 🆘 Need Help?

1. **Check logs:**
   - Backend: Terminal 1 (where uvicorn is running)
   - Mobile: Terminal 2 (where expo is running)
   - Database: `python check_database.py`

2. **Read guides:**
   - [`FIX_COMPLETE_GUIDE.md`](FIX_COMPLETE_GUIDE.md) - Comprehensive troubleshooting
   - [`FIXES_APPLIED.md`](FIXES_APPLIED.md) - Recent fixes summary

3. **Restart everything:**
   - Stop all terminals (Ctrl+C)
   - Run `.\fix_all_issues.ps1`
   - Run `start_everything.bat`

---

## 📈 Expected Performance

- **Backend startup:** ~5 seconds
- **Initial scraping:** ~30 seconds (200-400 products)
- **Home screen load:** Instant (cached data)
- **Search Tier 1:** ~2 seconds
- **Search Tier 2:** +8 seconds (background)

---

## ✅ Success Indicators

When everything is working correctly:

1. **Backend Terminal:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete.
   ```

2. **Mobile Terminal:**
   ```
   🔗 API URL: http://192.168.x.x:8000
   Metro waiting on exp://192.168.x.x:8081
   ```

3. **Database Check:**
   ```powershell
   python check_database.py
   ```
   Shows:
   - ✓ Connected to database
   - Total products: 200-400
   - Best deals: 8-25
   - Top price drops: 25

4. **Mobile App:**
   - Home screen shows products
   - Images load correctly
   - Can click products for details
   - Search works

---

**Your app is ready! 🎉**

Run `start_everything.bat` to begin!
