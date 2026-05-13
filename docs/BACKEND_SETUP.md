# PricePilot Backend Setup - Complete Guide

## 📦 What Was Created

```
backend/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Empty auth router (ready for endpoints)
│   └── __init__.py
├── main.py                   # FastAPI app with CORS
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .env.example             # Template for .env
├── README.md                # Detailed documentation
└── QUICKSTART.md            # Quick start guide
```

---

## 🎯 Key Features

✅ **FastAPI app created** with title and description  
✅ **CORS enabled** for React Native mobile app  
✅ **Test route** at GET / returns "PricePilot API is working"  
✅ **Auth router imported** (empty, ready for endpoints)  
✅ **Environment variables** loaded with python-dotenv  
✅ **All dependencies** in requirements.txt  

---

## 📋 Requirements.txt Contents

```
fastapi
uvicorn
asyncpg
pymongo
python-jose[cryptography]
passlib[bcrypt]
pydantic[email]
python-dotenv
```

**What each package does:**
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server to run FastAPI
- `asyncpg` - PostgreSQL database driver (for Supabase)
- `pymongo` - MongoDB database driver (for MongoDB Atlas)
- `python-jose[cryptography]` - JWT token creation and verification
- `passlib[bcrypt]` - Password hashing with bcrypt
- `pydantic[email]` - Data validation with email support
- `python-dotenv` - Load environment variables from .env file

---

## 🔐 Environment Variables (.env)

```env
DATABASE_URL=your_supabase_postgres_connection_string
MONGODB_URI=your_mongodb_atlas_connection_string
JWT_SECRET=pricepilot_secret_key_2026
JWT_EXPIRE_MINUTES=60
```

**Important:** Never commit `.env` to Git! Use `.env.example` as a template.

---

## 🚀 Setup Steps

### 1. Create Virtual Environment
```bash
python -m venv venv
```

**What this does:** Creates an isolated Python environment in a folder called `venv`.

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**How to verify:** You'll see `(venv)` at the start of your command prompt.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**What this does:** Installs all packages listed in requirements.txt.

### 4. Configure Environment Variables

Edit `.env` file and replace placeholder values with your actual database credentials.

### 5. Run the Server
```bash
uvicorn main:app --reload
```

**What this does:** Starts the FastAPI server on http://127.0.0.1:8000

---

## ✅ Testing the API

### Test Route
Open browser: http://127.0.0.1:8000/

**Expected response:**
```json
{"message": "PricePilot API is working"}
```

### Interactive API Documentation
Open browser: http://127.0.0.1:8000/docs

**What you'll see:**
- Swagger UI with all API endpoints
- Test endpoints directly from browser
- See request/response schemas

### Alternative Documentation
Open browser: http://127.0.0.1:8000/redoc

**What you'll see:**
- ReDoc UI (cleaner documentation view)
- Better for reading API documentation

---

## 📝 Main.py Explanation

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="PricePilot API",
    description="Price comparison API for PricePilot mobile app",
    version="1.0.0"
)

# Configure CORS to allow React Native app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Test route - Root endpoint
@app.get("/")
async def root():
    """Test endpoint to verify API is working"""
    return {"message": "PricePilot API is working"}

# Import and include routers
from app.routers import auth
app.include_router(auth.router)
```

**Line-by-line explanation:**

1. **Import FastAPI**: Main framework class
2. **Import CORSMiddleware**: Enables cross-origin requests
3. **Import load_dotenv**: Loads environment variables from .env
4. **load_dotenv()**: Reads .env file and loads variables
5. **app = FastAPI(...)**: Creates FastAPI application instance
6. **app.add_middleware(...)**: Adds CORS middleware to allow mobile app connections
7. **@app.get("/")**: Decorator that creates a GET endpoint at root URL
8. **async def root()**: Async function that handles the request
9. **return {...}**: Returns JSON response
10. **from app.routers import auth**: Imports auth router
11. **app.include_router(...)**: Registers auth router with the app

---

## 🎓 Viva Questions & Answers

### Q1: What is FastAPI and why use it?
**A:** FastAPI is a modern Python web framework for building APIs. We use it because:
- Fast performance (comparable to Node.js)
- Automatic API documentation (Swagger UI)
- Built-in data validation with Pydantic
- Easy to learn and use
- Native async support

### Q2: What is CORS and why do we need it?
**A:** CORS (Cross-Origin Resource Sharing) is a security feature that allows or restricts web applications from making requests to a different domain. We need it because:
- Our React Native mobile app runs on a different origin than the backend
- Without CORS, browsers block these cross-origin requests
- We configure it to allow our mobile app to communicate with the API

### Q3: What is a virtual environment and why use it?
**A:** A virtual environment is an isolated Python environment for a project. We use it because:
- Keeps project dependencies separate from system Python
- Prevents version conflicts between different projects
- Makes it easy to share exact dependencies via requirements.txt
- Allows different projects to use different package versions

### Q4: What does `uvicorn main:app --reload` do?
**A:** This command starts the FastAPI server:
- `uvicorn` - ASGI server that runs FastAPI
- `main:app` - Tells uvicorn to run the `app` object from `main.py`
- `--reload` - Auto-restarts server when code changes (development only)

### Q5: What is python-dotenv and why use it?
**A:** python-dotenv loads environment variables from a `.env` file. We use it because:
- Keeps sensitive information (passwords, API keys) out of code
- Different environments (dev, production) can have different values
- `.env` file is not committed to Git (stays private)
- Easy to configure without changing code

### Q6: Explain the packages in requirements.txt
**A:**
- **fastapi** - Web framework for building the API
- **uvicorn** - Server that runs the FastAPI application
- **asyncpg** - PostgreSQL driver for Supabase database
- **pymongo** - MongoDB driver for MongoDB Atlas
- **python-jose** - Creates and verifies JWT tokens for authentication
- **passlib** - Hashes passwords securely with bcrypt
- **pydantic** - Validates request/response data
- **python-dotenv** - Loads environment variables from .env file

### Q7: What is the purpose of the test route?
**A:** The test route (GET /) serves as a health check:
- Verifies the server is running
- Confirms the API is accessible
- Tests that CORS is configured correctly
- Provides a simple endpoint to test with

### Q8: Why is the auth router empty?
**A:** The auth router is a placeholder for future authentication endpoints:
- Will contain login, register, token refresh endpoints
- Keeps authentication logic organized in one file
- Already imported in main.py, ready to add endpoints
- Follows separation of concerns principle

### Q9: What is the difference between .env and .env.example?
**A:**
- **.env** - Contains actual credentials (never commit to Git)
- **.env.example** - Template with placeholder values (safe to commit)
- Team members copy .env.example to .env and fill in their own credentials

### Q10: How does FastAPI generate automatic documentation?
**A:** FastAPI uses:
- Type hints in Python functions to understand data types
- Pydantic models for request/response schemas
- Docstrings for endpoint descriptions
- Generates Swagger UI at /docs and ReDoc at /redoc automatically

---

## 🔧 Common Commands

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Run server on different port
uvicorn main:app --reload --port 8080

# Run server accessible from other devices
uvicorn main:app --reload --host 0.0.0.0

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Check installed packages
pip list
```

---

## 🐛 Troubleshooting

### Issue: "python is not recognized"
**Cause:** Python not installed or not in system PATH  
**Fix:** Install Python from python.org and check "Add to PATH" during installation

### Issue: "pip is not recognized"
**Cause:** pip not in system PATH  
**Fix:** Use `python -m pip` instead of `pip`

### Issue: "Module not found"
**Cause:** Virtual environment not activated or dependencies not installed  
**Fix:** 
1. Activate virtual environment: `venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`

### Issue: "Port 8000 already in use"
**Cause:** Another process is using port 8000  
**Fix:** Use different port: `uvicorn main:app --reload --port 8080`

### Issue: ".env file not loading"
**Cause:** .env file not in correct location or python-dotenv not installed  
**Fix:**
1. Ensure .env is in backend/ folder (same as main.py)
2. Install python-dotenv: `pip install python-dotenv`

### Issue: "CORS error in mobile app"
**Cause:** CORS not configured correctly  
**Fix:** Check that CORSMiddleware is added in main.py with `allow_origins=["*"]`

---

## 📚 Next Steps

1. ✅ Backend setup complete
2. ⏭️ Create database models in `app/models/`
3. ⏭️ Create database connections in `app/database/`
4. ⏭️ Implement authentication in `app/routers/auth.py`
5. ⏭️ Create product and user routers
6. ⏭️ Connect mobile app to backend

---

## 🎯 Summary

You now have a working FastAPI backend with:
- ✅ FastAPI app configured
- ✅ CORS enabled for mobile app
- ✅ Test route working
- ✅ Auth router ready
- ✅ Environment variables configured
- ✅ All dependencies installed
- ✅ Documentation generated automatically

**Test it:** Run `uvicorn main:app --reload` and visit http://127.0.0.1:8000/
