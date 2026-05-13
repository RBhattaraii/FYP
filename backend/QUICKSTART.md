# PricePilot Backend - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Server
```bash
uvicorn main:app --reload
```

---

## ✅ Test the API

Open your browser and visit:
- **Test Route**: http://127.0.0.1:8000/
- **API Docs**: http://127.0.0.1:8000/docs

You should see:
```json
{"message": "PricePilot API is working"}
```

---

## 📝 What Each File Does

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app with CORS enabled |
| `requirements.txt` | List of Python packages to install |
| `.env` | Environment variables (database URLs, secrets) |
| `app/routers/auth.py` | Authentication endpoints (empty for now) |

---

## 🎓 For Your Viva

### Q: What is FastAPI?
**A:** A modern Python web framework for building APIs with automatic documentation.

### Q: What is CORS?
**A:** Cross-Origin Resource Sharing - allows the mobile app to connect to the backend API.

### Q: Why use a virtual environment?
**A:** To keep project dependencies isolated and prevent conflicts.

### Q: What does `uvicorn main:app --reload` do?
**A:** Runs the FastAPI server with auto-reload (restarts when code changes).

### Q: What is in requirements.txt?
**A:** 
- `fastapi` - Web framework
- `uvicorn` - Server to run FastAPI
- `asyncpg` - PostgreSQL driver
- `pymongo` - MongoDB driver
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `pydantic` - Data validation
- `python-dotenv` - Load environment variables

---

## 🔧 Common Issues

**Issue:** "python is not recognized"  
**Fix:** Install Python and add to PATH

**Issue:** "Module not found"  
**Fix:** Activate virtual environment and install dependencies

**Issue:** "Port 8000 already in use"  
**Fix:** Use different port: `uvicorn main:app --reload --port 8080`

---

## 📚 Full Documentation

See `README.md` for detailed setup instructions and explanations.
