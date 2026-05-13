# PricePilot Backend Setup Guide

## Overview
This is the FastAPI backend for the PricePilot mobile application. It provides REST API endpoints for product price comparison, user authentication, and web scraping.

---

## Prerequisites
- Python 3.8 or higher installed on your system
- pip (Python package installer)

---

## Setup Instructions

### Step 1: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from other Python projects.

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

**What this does:**
- Creates a folder called `venv` containing an isolated Python environment
- Prevents conflicts between different project dependencies

---

### Step 2: Activate the Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**How to know it's activated:**
- You'll see `(venv)` at the beginning of your command prompt
- Example: `(venv) C:\Users\YourName\Desktop\FYP\backend>`

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs:**
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server to run FastAPI
- `asyncpg` - PostgreSQL database driver
- `pymongo` - MongoDB database driver
- `python-jose[cryptography]` - JWT token creation and verification
- `passlib[bcrypt]` - Password hashing
- `pydantic[email]` - Data validation with email support
- `python-dotenv` - Load environment variables from .env file

**Verification:**
```bash
pip list
```
This shows all installed packages.

---

### Step 4: Configure Environment Variables

1. Open the `.env` file in the `backend` folder
2. Replace the placeholder values with your actual credentials:

```env
DATABASE_URL=your_supabase_postgres_connection_string
MONGODB_URI=your_mongodb_atlas_connection_string
JWT_SECRET=pricepilot_secret_key_2026
JWT_EXPIRE_MINUTES=60
```

**Where to get these values:**
- **DATABASE_URL**: From your Supabase project settings
- **MONGODB_URI**: From your MongoDB Atlas cluster connection string
- **JWT_SECRET**: Keep the default or generate a random secret key
- **JWT_EXPIRE_MINUTES**: Token expiration time (60 minutes = 1 hour)

---

### Step 5: Run the Server

```bash
uvicorn main:app --reload
```

**Command breakdown:**
- `uvicorn` - The ASGI server
- `main:app` - Run the `app` object from `main.py`
- `--reload` - Auto-restart server when code changes (for development only)

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 6: Test the API

Open your browser and go to:
- **API Test Route**: http://127.0.0.1:8000/
  - Should return: `{"message": "PricePilot API is working"}`

- **Interactive API Docs**: http://127.0.0.1:8000/docs
  - Swagger UI for testing all endpoints

- **Alternative API Docs**: http://127.0.0.1:8000/redoc
  - ReDoc UI (cleaner documentation view)

---

## Project Structure

```
backend/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication endpoints (empty for now)
│   └── __init__.py
├── main.py                   # FastAPI app with CORS enabled
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (DO NOT COMMIT)
├── .env.example             # Template for environment variables
└── README.md                # This file
```

---

## Key Concepts for Viva

### 1. What is FastAPI?
FastAPI is a modern Python web framework for building APIs. It's fast, easy to use, and automatically generates interactive documentation.

### 2. What is CORS?
CORS (Cross-Origin Resource Sharing) allows your React Native mobile app to make requests to the backend API from a different origin (domain/port). Without CORS, browsers block these requests for security.

### 3. What is a Virtual Environment?
A virtual environment is an isolated Python environment that keeps project dependencies separate. This prevents version conflicts between different projects.

### 4. What is uvicorn?
Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server that runs FastAPI applications. It handles incoming HTTP requests and sends them to your FastAPI app.

### 5. What is python-dotenv?
python-dotenv loads environment variables from a `.env` file into your application. This keeps sensitive information (like database passwords) out of your code.

### 6. Why use requirements.txt?
`requirements.txt` lists all Python packages your project needs. Anyone can install the exact same dependencies using `pip install -r requirements.txt`.

---

## Common Commands

### Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Deactivate virtual environment:
```bash
deactivate
```

### Install new package:
```bash
pip install package-name
```

### Update requirements.txt after installing new packages:
```bash
pip freeze > requirements.txt
```

### Run server:
```bash
uvicorn main:app --reload
```

### Run server on different port:
```bash
uvicorn main:app --reload --port 8080
```

### Run server accessible from other devices:
```bash
uvicorn main:app --reload --host 0.0.0.0
```

---

## Troubleshooting

### Issue: "python is not recognized"
**Solution**: Make sure Python is installed and added to your system PATH.

### Issue: "pip is not recognized"
**Solution**: Use `python -m pip` instead of `pip`.

### Issue: "Module not found"
**Solution**: Make sure virtual environment is activated and dependencies are installed.

### Issue: "Port 8000 already in use"
**Solution**: Either stop the other process or use a different port:
```bash
uvicorn main:app --reload --port 8080
```

### Issue: ".env file not loading"
**Solution**: Make sure `.env` is in the same directory as `main.py` and `python-dotenv` is installed.

---

## Next Steps

1. ✅ Backend setup complete
2. ⏭️ Create database models in `app/models/`
3. ⏭️ Create database connections in `app/database/`
4. ⏭️ Implement authentication endpoints in `app/routers/auth.py`
5. ⏭️ Create product and user routers
6. ⏭️ Connect mobile app to backend API

---

## Important Notes

- **Never commit `.env` file to Git** - It contains sensitive credentials
- **Always use virtual environment** - Keeps dependencies isolated
- **Use `--reload` only in development** - In production, remove this flag
- **Keep `requirements.txt` updated** - Run `pip freeze > requirements.txt` after installing new packages

---

## Questions for Viva

**Q: Why do we use FastAPI instead of Flask?**
A: FastAPI is faster, has automatic API documentation, built-in data validation with Pydantic, and native async support.

**Q: What is the purpose of CORS middleware?**
A: CORS allows the React Native mobile app to make API requests from a different origin. Without it, browsers block cross-origin requests.

**Q: Why do we need a virtual environment?**
A: To isolate project dependencies and prevent conflicts between different Python projects.

**Q: What does `uvicorn main:app --reload` do?**
A: It runs the FastAPI application with auto-reload enabled, so the server restarts automatically when code changes.

**Q: Why use environment variables?**
A: To keep sensitive information (database URLs, secret keys) out of the code and version control.
