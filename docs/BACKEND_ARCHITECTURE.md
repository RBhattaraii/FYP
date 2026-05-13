# PricePilot Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PricePilot System                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  React Native    │         │   FastAPI        │
│  Mobile App      │◄───────►│   Backend        │
│  (Expo Router)   │  HTTP   │   (Python)       │
└──────────────────┘         └────────┬─────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                 ┌──────▼──────┐           ┌───────▼──────┐
                 │  PostgreSQL │           │   MongoDB    │
                 │  (Supabase) │           │   (Atlas)    │
                 │             │           │              │
                 │ Structured  │           │ Raw Scraped  │
                 │    Data     │           │    Data      │
                 └─────────────┘           └──────────────┘
```

---

## Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                    main.py                          │    │
│  │  • FastAPI app instance                            │    │
│  │  • CORS middleware                                 │    │
│  │  • Router registration                             │    │
│  │  • Environment variable loading                    │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │                app/routers/                         │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  auth.py                                     │  │    │
│  │  │  • Login endpoint                            │  │    │
│  │  │  • Register endpoint                         │  │    │
│  │  │  • JWT token creation                        │  │    │
│  │  │  • JWT token verification                    │  │    │
│  │  │  • Password hashing                          │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  products.py (future)                        │  │    │
│  │  │  • Get products                              │  │    │
│  │  │  • Create product                            │  │    │
│  │  │  • Update product                            │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  users.py (future)                           │  │    │
│  │  │  • Get user profile                          │  │    │
│  │  │  • Update user                               │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │                app/models/                          │    │
│  │  • product.py - Product data models                │    │
│  │  • user.py - User data models                      │    │
│  │  • scraped_data.py - Scraped data models           │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │                app/database/                        │    │
│  │  • postgres.py - PostgreSQL connection             │    │
│  │  • mongodb.py - MongoDB connection                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow

```
1. Mobile App Request
   │
   ├─► HTTP Request (with CORS headers)
   │
   ▼
2. FastAPI Server (main.py)
   │
   ├─► CORS Middleware (validates origin)
   │
   ▼
3. Router (app/routers/auth.py)
   │
   ├─► Validate request data (Pydantic)
   │
   ▼
4. Business Logic
   │
   ├─► Process request
   ├─► Hash passwords (if needed)
   ├─► Create JWT tokens (if needed)
   │
   ▼
5. Database (app/database/)
   │
   ├─► Query PostgreSQL or MongoDB
   │
   ▼
6. Response
   │
   ├─► Format response (Pydantic model)
   ├─► Add CORS headers
   │
   ▼
7. Mobile App receives JSON response
```

---

## CORS Flow

```
┌──────────────────┐                    ┌──────────────────┐
│  Mobile App      │                    │  FastAPI Server  │
│  (localhost:8081)│                    │  (localhost:8000)│
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │  1. HTTP Request                      │
         │  Origin: http://localhost:8081        │
         ├──────────────────────────────────────►│
         │                                       │
         │                                       │ 2. CORS Middleware
         │                                       │    checks origin
         │                                       │
         │  3. Response with CORS headers        │
         │  Access-Control-Allow-Origin: *       │
         │◄──────────────────────────────────────┤
         │                                       │
         │  4. Browser allows response           │
         │                                       │
```

**Without CORS:**
```
Mobile App ──X──► Backend
           (Blocked by browser)
```

**With CORS:**
```
Mobile App ──✓──► Backend
           (Allowed)
```

---

## Environment Variables Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        .env file                             │
│  DATABASE_URL=postgresql://...                              │
│  MONGODB_URI=mongodb+srv://...                              │
│  JWT_SECRET=pricepilot_secret_key_2026                      │
│  JWT_EXPIRE_MINUTES=60                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ python-dotenv loads
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                 │
│  from dotenv import load_dotenv                             │
│  load_dotenv()  # Loads .env into environment               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Environment variables available
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ postgres.py│  │ mongodb.py │  │  auth.py   │
│            │  │            │  │            │
│ os.getenv  │  │ os.getenv  │  │ os.getenv  │
│ ("DATABASE │  │ ("MONGODB  │  │ ("JWT_     │
│  _URL")    │  │  _URI")    │  │  SECRET")  │
└────────────┘  └────────────┘  └────────────┘
```

---

## Virtual Environment Concept

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Computer                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  System Python                                     │    │
│  │  • Python 3.11                                     │    │
│  │  • Global packages                                 │    │
│  │  • Used by all projects                            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PricePilot Virtual Environment (venv/)            │    │
│  │  • Isolated Python environment                     │    │
│  │  • Project-specific packages                       │    │
│  │  • fastapi, uvicorn, etc.                          │    │
│  │  • Independent from system Python                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Other Project Virtual Environment                 │    │
│  │  • Different packages                              │    │
│  │  • Different versions                              │    │
│  │  • No conflicts with PricePilot                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ No package version conflicts
- ✅ Each project has its own dependencies
- ✅ Easy to share exact dependencies (requirements.txt)
- ✅ Clean system Python installation

---

## JWT Authentication Flow

```
1. User Registration/Login
   │
   ├─► POST /auth/register or /auth/login
   │   Body: { email, password }
   │
   ▼
2. Backend validates credentials
   │
   ├─► Check email/password
   ├─► Hash password (bcrypt)
   │
   ▼
3. Create JWT Token
   │
   ├─► Payload: { user_id, email, exp }
   ├─► Sign with JWT_SECRET
   │
   ▼
4. Return token to mobile app
   │
   ├─► Response: { token: "eyJ..." }
   │
   ▼
5. Mobile app stores token
   │
   ├─► Save in AsyncStorage
   │
   ▼
6. Future requests include token
   │
   ├─► Header: Authorization: Bearer eyJ...
   │
   ▼
7. Backend verifies token
   │
   ├─► Decode with JWT_SECRET
   ├─► Check expiration
   ├─► Extract user info
   │
   ▼
8. Process authenticated request
```

---

## Database Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL (Supabase)                   │
│                      Structured Data                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  users table   │  │ products table │  │ prices table │  │
│  ├────────────────┤  ├────────────────┤  ├──────────────┤  │
│  │ id             │  │ id             │  │ id           │  │
│  │ email          │  │ name           │  │ product_id   │  │
│  │ hashed_password│  │ price          │  │ price        │  │
│  │ full_name      │  │ url            │  │ date         │  │
│  │ created_at     │  │ store          │  │ store        │  │
│  └────────────────┘  │ category       │  └──────────────┘  │
│                      │ image_url      │                     │
│                      │ created_at     │                     │
│                      └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      MongoDB (Atlas)                         │
│                      Raw Scraped Data                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  scraped_data collection                           │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  {                                                 │    │
│  │    _id: ObjectId,                                  │    │
│  │    product_url: "https://...",                     │    │
│  │    store: "amazon",                                │    │
│  │    raw_html: "<html>...</html>",                   │    │
│  │    scraped_at: ISODate,                            │    │
│  │    parsed_data: {                                  │    │
│  │      title: "Product Name",                        │    │
│  │      price: 99.99,                                 │    │
│  │      availability: "In Stock"                      │    │
│  │    },                                              │    │
│  │    status: "processed"                             │    │
│  │  }                                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Why Two Databases?**

**PostgreSQL (Structured):**
- ✅ Relational data (users, products, prices)
- ✅ ACID compliance
- ✅ Complex queries with JOINs
- ✅ Data integrity with foreign keys

**MongoDB (Flexible):**
- ✅ Raw HTML storage
- ✅ Flexible schema for different stores
- ✅ Fast writes for scraping
- ✅ No predefined structure needed

---

## Package Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    requirements.txt                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ pip install -r requirements.txt
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│    fastapi     │ │    uvicorn     │ │   asyncpg      │
│                │ │                │ │                │
│ Web framework  │ │ ASGI server    │ │ PostgreSQL     │
│ for building   │ │ to run FastAPI │ │ driver         │
│ APIs           │ │                │ │                │
└────────────────┘ └────────────────┘ └────────────────┘

┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│    pymongo     │ │  python-jose   │ │    passlib     │
│                │ │                │ │                │
│ MongoDB driver │ │ JWT tokens     │ │ Password       │
│                │ │ creation &     │ │ hashing with   │
│                │ │ verification   │ │ bcrypt         │
└────────────────┘ └────────────────┘ └────────────────┘

┌────────────────┐ ┌────────────────┐
│    pydantic    │ │ python-dotenv  │
│                │ │                │
│ Data validation│ │ Load .env file │
│ with email     │ │ environment    │
│ support        │ │ variables      │
└────────────────┘ └────────────────┘
```

---

## API Endpoints (Current & Future)

```
┌─────────────────────────────────────────────────────────────┐
│                    PricePilot API                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ GET  /                                                   │
│     Returns: {"message": "PricePilot API is working"}       │
│                                                              │
│  ⏭️ POST /auth/register                                      │
│     Body: { email, password, full_name }                    │
│     Returns: { token, user }                                │
│                                                              │
│  ⏭️ POST /auth/login                                         │
│     Body: { email, password }                               │
│     Returns: { token, user }                                │
│                                                              │
│  ⏭️ GET  /auth/me                                            │
│     Headers: Authorization: Bearer <token>                  │
│     Returns: { user }                                       │
│                                                              │
│  ⏭️ GET  /products                                           │
│     Query: ?skip=0&limit=10                                 │
│     Returns: [ { product } ]                                │
│                                                              │
│  ⏭️ GET  /products/{id}                                      │
│     Returns: { product }                                    │
│                                                              │
│  ⏭️ POST /products                                           │
│     Body: { name, price, url, store }                       │
│     Returns: { product }                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture provides:

✅ **Separation of Concerns** - Routers, models, database separate  
✅ **Scalability** - Easy to add new endpoints and features  
✅ **Security** - JWT authentication, password hashing, CORS  
✅ **Flexibility** - Two databases for different data types  
✅ **Maintainability** - Clear structure, isolated dependencies  
✅ **Documentation** - Automatic API docs with FastAPI  

The backend is ready to grow with your project!
