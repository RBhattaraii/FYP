# PostgreSQL Quick Start Guide

## 🚀 Setup in 3 Steps

### Step 1: Get Supabase Database URL
1. Go to Supabase → **Settings** → **Database**
2. Copy **Connection String** (URI format)
3. Update `backend/.env`:
   ```env
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```

### Step 2: Create Users Table
1. Go to Supabase → **SQL Editor**
2. Copy contents of `backend/database_schema.sql`
3. Paste and click **Run**

### Step 3: Run FastAPI Server
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

---

## ✅ Verify It Works

Check server logs for:
```
✅ PostgreSQL connection pool created successfully
🚀 PricePilot API started successfully
```

---

## 📝 Quick Reference

### Get Database Connection
```python
from fastapi import Depends
from app.database.postgres import get_db

@app.get("/users")
async def get_users(db = Depends(get_db)):
    # db is now a PostgreSQL connection
    pass
```

### Fetch One Row
```python
query = "SELECT * FROM users WHERE id = $1"
user = await db.fetchrow(query, user_id)
return dict(user) if user else None
```

### Fetch Multiple Rows
```python
query = "SELECT * FROM users WHERE role = $1"
users = await db.fetch(query, "admin")
return [dict(user) for user in users]
```

### Insert Row
```python
query = """
    INSERT INTO users (email, password_hash, full_name)
    VALUES ($1, $2, $3)
    RETURNING *
"""
user = await db.fetchrow(query, email, hashed_password, full_name)
return dict(user)
```

### Update Row
```python
query = "UPDATE users SET full_name = $1 WHERE id = $2 RETURNING *"
user = await db.fetchrow(query, new_name, user_id)
return dict(user)
```

### Delete Row
```python
query = "DELETE FROM users WHERE id = $1 RETURNING id"
result = await db.fetchrow(query, user_id)
return {"deleted": result is not None}
```

---

## 🔒 Security Rules

### ✅ ALWAYS Use Parameterized Queries
```python
# CORRECT
query = "SELECT * FROM users WHERE email = $1"
await db.fetchrow(query, user_email)
```

### ❌ NEVER Use String Formatting
```python
# WRONG - SQL Injection vulnerability!
query = f"SELECT * FROM users WHERE email = '{user_email}'"
await db.fetchrow(query)
```

---

## 🎯 Key Points for Viva

1. **asyncpg** = PostgreSQL driver (no ORM)
2. **Connection pool** = Reusable database connections
3. **Parameterized queries** = Use $1, $2 to prevent SQL injection
4. **UUID** = Unique identifier (better than integer IDs)
5. **Trigger** = Automatically updates `updated_at` timestamp
6. **Index** = Makes searches faster

---

## 📚 Full Documentation

See `docs/POSTGRES_SETUP.md` for detailed explanations and viva Q&A.
