# 🛍️ PricePilot - Multi-Platform Price Comparison App

> A full-stack mobile application that scrapes 11+ e-commerce platforms in Nepal, provides intelligent search, and helps users find the best deals.

## 🚀 Quick Start

**Having issues? Start here:**

```powershell
cd C:\Users\NITOR 5\Desktop\FYP
.\quick-start.ps1
```

This will:
1. ✓ Test your system
2. ✓ Start the backend
3. ✓ Check database
4. ✓ Launch mobile app (with cache cleared)

**Or read:** [START_HERE.md](START_HERE.md) for step-by-step instructions.

---

## 📁 Project Structure

```
FYP/
├── backend/              # FastAPI backend server
│   ├── app/
│   │   ├── routers/     # API endpoints (products, auth, scraper)
│   │   ├── services/    # Business logic (coordinator, scheduler)
│   │   ├── models/      # Pydantic data models
│   │   └── database/    # PostgreSQL + MongoDB connections
│   └── main.py          # Application entry point
│
├── mobile/              # React Native (Expo) mobile app
│   ├── app/
│   │   ├── (tabs)/     # Tab screens (home, search, profile)
│   │   └── (auth)/     # Auth screens (login, register)
│   ├── components/      # Reusable UI components
│   ├── services/        # API service layer
│   └── constants/       # App configuration
│
├── scrapers/            # Web scrapers for each platform
│   ├── daraz/          # Daraz scraper
│   ├── oliz/           # Oliz scraper
│   ├── hukut/          # Hukut scraper
│   └── ...             # 8+ more platforms
│
└── docs/               # Documentation
    └── screenshots/     # App screenshots for README

```

---

## 🎯 Key Features

### For Users:
- 🔍 **Smart Search** - Search across 11 platforms simultaneously
- ⚡ **Tiered Loading** - See results in 2 seconds, more load progressively
- 💰 **Best Deals** - Curated products with highest discounts
- 📉 **Price Drops** - Track products with largest price reductions
- 🔐 **User Accounts** - Save preferences and search history
- 📱 **Native Mobile** - Fast, responsive React Native app

### For Developers:
- 🏗️ **Modular Architecture** - Clean separation of concerns
- 🔄 **Async Scrapers** - Concurrent scraping with asyncio
- 💾 **Dual Database** - PostgreSQL (relational) + MongoDB (raw data)
- 🔥 **FastAPI** - High-performance async Python backend
- 📊 **Type Safety** - TypeScript frontend, Pydantic backend
- 🧪 **Testable** - Comprehensive test scripts included

---

## 🛠️ Technology Stack

### Backend:
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database (curated products)
- **MongoDB** - NoSQL database (raw scraper data)
- **APScheduler** - Task scheduling (daily scraper runs)
- **asyncio** - Asynchronous programming
- **httpx** - HTTP client for scraping
- **Playwright** - Browser automation (for JS-heavy sites)

### Mobile:
- **React Native** - Cross-platform mobile framework
- **Expo** - Development tooling and build system
- **TypeScript** - Type-safe JavaScript
- **Expo Router** - File-based routing
- **Expo Secure Store** - Encrypted credential storage

### Scrapers:
- **BeautifulSoup4** - HTML parsing
- **httpx** - Async HTTP requests
- **Playwright** - Browser automation
- **asyncio** - Concurrent execution

---

## 📋 Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.10+ ([Download](https://python.org/))
- **PostgreSQL** 14+ ([Download](https://postgresql.org/))
- **MongoDB** 6+ ([Download](https://mongodb.com/))
- **Expo Go** app (for testing on physical device)

---

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd FYP
```

### 2. Setup Backend
```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start server
uvicorn main:app --host 0.0.0.0 --reload
```

### 3. Setup Mobile App
```powershell
cd mobile

# Install dependencies
npm install

# Start development server
npx expo start
```

### 4. Setup Databases
```sql
-- PostgreSQL
CREATE DATABASE pricepilot;

-- MongoDB (auto-creates on first connection)
```

---

## 🚀 Running the Application

### Method 1: One-Click Start (Recommended)
```powershell
.\quick-start.ps1
```

### Method 2: Manual Start
```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Terminal 2 - Mobile
cd mobile
npx expo start --clear

# Terminal 3 - Trigger Scraper (optional)
cd backend
.\trigger_scraper.ps1
```

### Method 3: Using Batch Files
```powershell
# Backend
cd backend
.\start_backend.bat

# Mobile
cd mobile
.\fix-and-start.ps1
```

---

## 🧪 Testing

### Test Everything
```powershell
.\test-everything.ps1
```

### Test Backend Only
```powershell
curl http://localhost:8000/docs
curl http://localhost:8000/products/home
```

### Test Mobile App
1. Open Expo Go on your device
2. Scan QR code from Metro bundler
3. App should load and show products

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### Products
```http
GET  /products/home              # Home screen products
GET  /products/search?q=laptop   # Search products
GET  /products/{id}              # Product detail
GET  /products/search/status     # Poll search progress
```

#### Authentication
```http
POST /auth/register              # Register new user
POST /auth/login                 # Login user
GET  /auth/me                    # Get user profile
```

#### Scraper
```http
POST /scraper/trigger            # Trigger manual scrape
GET  /scraper/status             # Get scraper status
```

**Full API Docs:** http://localhost:8000/docs (Swagger UI)

---

## 🔧 Troubleshooting

### Common Issues:

1. **"Unable to resolve @/constants/api"**
   ```powershell
   cd mobile
   npx expo start --clear --reset-cache
   ```

2. **"No Products Yet" in app**
   ```powershell
   # Check backend has data
   curl http://localhost:8000/products/home
   
   # If empty, run scraper
   cd backend
   .\trigger_scraper.ps1
   ```

3. **"Unable to connect" from mobile**
   ```powershell
   # Check firewall
   cd mobile
   .\fix-firewall.ps1
   
   # Verify backend accessible
   curl http://YOUR_PC_IP:8000/docs
   ```

4. **Backend won't start**
   ```powershell
   cd backend
   .\venv\Scripts\activate
   pip install --upgrade -r requirements.txt
   ```

**Full troubleshooting guide:** [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)

---

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Quick start guide (read first!)
- **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** - Complete solution overview
- **[COMPLETE_FIX_GUIDE.md](COMPLETE_FIX_GUIDE.md)** - Detailed troubleshooting
- **[mobile/HOW_TO_TEST.md](mobile/HOW_TO_TEST.md)** - Testing procedures

---

## 🎓 For Students / Viva

### Q: How does the tiered search work?

**A:** 
1. User searches "laptop"
2. Backend immediately scrapes 3 fast platforms (Tier 1: ~2s)
3. Returns Tier 1 results to user instantly
4. Backend continues scraping 8 more platforms in background (Tier 2: ~8s)
5. Frontend polls every 2 seconds for new results
6. User sees results progressively as they arrive

**Benefits:**
- Fast initial response (2s vs 10s)
- Better UX (content appears progressively)
- User can start browsing immediately

### Q: Why use both PostgreSQL and MongoDB?

**A:**
- **MongoDB**: Stores raw scraper output (unstructured, fast writes)
- **PostgreSQL**: Stores curated products (structured, complex queries)

**Flow:** Scrapers → MongoDB (raw) → Coordinator curates → PostgreSQL (refined)

---

## 📞 Support

Having issues? Check these resources:

1. **[START_HERE.md](START_HERE.md)** - Quick fixes
2. **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** - Detailed solutions
3. **[test-everything.ps1](test-everything.ps1)** - Diagnostic tool

---

**Made with ❤️ for FYP Project**
