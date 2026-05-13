# PostgreSQL Setup with asyncpg (No SQLAlchemy)

## Overview

This guide explains how to set up PostgreSQL connection in FastAPI using **asyncpg only** - no SQLAlchemy, no ORM. All database operations use direct SQL queries.

---

## 🎯 Key Concepts

### What is asyncpg?
- **asyncpg** is a PostgreSQL driver for Python
- It's designed for async/await operations
- Faster than other PostgreSQL drivers
- No ORM - you write raw SQL queries

### What is a Connection Pool?
- A **connection pool** maintains multiple database connections
- Connections are reused instead of creating new ones each time
- More efficient and faster than creating connections per request
- Like a parking lot with reserved spots instead of finding parking each time

### Why No SQLAlchemy?
- **Simpler** - No need to learn ORM syntax
- **More control** - You write exact SQL you want
- **Easier to debug** - You see the actual SQL queries
- **Better for learning** - Understand SQL directly

---

## 📁 File Structure

```
backend/
├── app/
│   └── database/
│       ├── __init__.py
│       └── postgres.py          ✅ PostgreSQL connection
├── database_schema.sql           ✅ SQL to run in Supabase
└── main.py                       ✅ Updated with startup/shutdown events
```

---

## 🔧 Setup Steps

### Step 1: Get Supabase Database URL

1. Go to your Supabase project
2. Click **Settings** → **Database**
3. Scroll to **Connection String** → **URI**
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```

### Step 2: Update .env File

Open `backend/.env` and update:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

Replace `[YOUR-PASSWORD]` with your actual Supabase database password.

### Step 3: Run SQL in Supabase

1. Go to Supabase → **SQL Editor**
2. Click **New Query**
3. Copy the contents of `backend/database_schema.sql`
4. Paste and click **Run**
5. You should see: "Success. No rows returned"

### Step 4: Verify Table Created

In Supabase:
1. Go to **Table Editor**
2. You should see the `users` table
3. Click on it to see the columns

---

## 📝 Code Explanation

### postgres.py - Line by Line

```python
import asyncpg
from dotenv import load_dotenv

load_dotenv()
```
**What it does:**
- Imports asyncpg library for PostgreSQL
- Imports load_dotenv to read .env file
- Loads environment variables

```python
pool: Optional[asyncpg.Pool] = None
```
**What it does:**
- Creates a global variable to store the connection pool
- Initially set to None (will be created on startup)

```python
async def create_pool():
    global pool
    database_url = os.getenv("DATABASE_URL")
    
    pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=60
    )
```
**What it does:**
- Creates a connection pool with 2-10 connections
- `min_size=2`: Always keep 2 connections open
- `max_size=10`: Allow up to 10 concurrent connections
- `command_timeout=60`: Queries timeout after 60 seconds

```python
async def get_db() -> asyncpg.Connection:
    async with pool.acquire() as connection:
        yield connection
```
**What it does:**
- Gets a connection from the pool
- Used as a FastAPI dependency
- Automatically returns connection to pool when done

### main.py - Startup/Shutdown Events

```python
@app.on_event("startup")
async def startup():
    await create_pool()
```
**What it does:**
- Runs when FastAPI starts
- Creates the database connection pool
- Only runs once at startup

```python
@app.on_event("shutdown")
async def shutdown():
    await close_pool()
```
**What it does:**
- Runs when FastAPI shuts down
- Closes all database connections
- Cleans up resources

---

## 🔒 Parameterized Queries (SQL Injection Prevention)

### ✅ SAFE - Parameterized Query

```python
# Use $1, $2, $3 as placeholders
query = "SELECT * FROM users WHERE email = $1"
result = await db.fetchrow(query, user_email)
```

**Why it's safe:**
- User input is treated as **data**, not as SQL code
- asyncpg automatically escapes special characters
- Prevents SQL injection attacks

### ❌ UNSAFE - String Formatting (Never Do This!)

```python
# DO NOT USE!
query = f"SELECT * FROM users WHERE email = '{user_email}'"
result = await db.fetchrow(query)
```

**Why it's dangerous:**
- User input is directly inserted into SQL
- Attacker can inject malicious SQL code

**Example attack:**
```python
user_email = "'; DROP TABLE users; --"
# This would delete your entire users table!
```

### Parameterized Query Examples

```python
# Single parameter
await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

# Multiple parameters
await db.fetchrow(
    "SELECT * FROM users WHERE email = $1 AND role = $2",
    email,
    role
)

# INSERT with parameters
await db.execute(
    "INSERT INTO users (email, password_hash, full_name) VALUES ($1, $2, $3)",
    email,
    hashed_password,
    full_name
)

# UPDATE with parameters
await db.execute(
    "UPDATE users SET full_name = $1 WHERE id = $2",
    new_name,
    user_id
)

# DELETE with parameters
await db.execute("DELETE FROM users WHERE id = $1", user_id)
```

---

## 📊 Database Schema Explanation

### Users Table Structure

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT,
    role          TEXT NOT NULL DEFAULT 'user',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Column Explanations

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique identifier (auto-generated) |
| `email` | TEXT | User's email (required, unique) |
| `password_hash` | TEXT | Encrypted password (required) |
| `full_name` | TEXT | User's full name (optional) |
| `role` | TEXT | User role: 'user' or 'admin' (default: 'user') |
| `is_active` | BOOLEAN | Account active status (default: true) |
| `created_at` | TIMESTAMPTZ | When user was created (auto-set) |
| `updated_at` | TIMESTAMPTZ | When user was last updated (auto-updated) |

### What is UUID?

**UUID** = Universal Unique Identifier

- 128-bit number
- Looks like: `550e8400-e29b-41d4-a716-446655440000`
- Globally unique (no two UUIDs are the same)
- Better than auto-incrementing integers for distributed systems

**Why use UUID instead of integer ID?**
- ✅ Unique across all databases
- ✅ Can't guess other user IDs
- ✅ More secure
- ✅ Can generate on client side

### What is TIMESTAMPTZ?

**TIMESTAMPTZ** = Timestamp with Time Zone

- Stores date and time with timezone information
- Example: `2024-01-15 10:30:00+00:00`
- Automatically converts to user's timezone
- Better than regular TIMESTAMP

### Trigger and Function

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
```

**What this does:**

1. **Function**: Defines what to do (set updated_at to current time)
2. **Trigger**: Automatically calls the function before every UPDATE
3. **Result**: updated_at is always current without manual updates

**Example:**
```sql
-- You write:
UPDATE users SET full_name = 'Jane Doe' WHERE id = '...';

-- Trigger automatically does:
-- SET updated_at = NOW()

-- Final result:
-- Both full_name AND updated_at are updated!
```

### Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**What is an index?**
- Like an index in a book - helps find things quickly
- Makes searches much faster
- Trade-off: Slightly slower inserts, much faster reads

**Example:**
```sql
-- Without index: Scans all 1,000,000 rows
SELECT * FROM users WHERE email = 'user@example.com';

-- With index: Finds row instantly
SELECT * FROM users WHERE email = 'user@example.com';
```

---

## 🔄 Common Database Operations

### Fetch One Row

```python
from fastapi import Depends
from app.database.postgres import get_db

@app.get("/users/{user_id}")
async def get_user(user_id: str, db = Depends(get_db)):
    query = "SELECT * FROM users WHERE id = $1"
    user = await db.fetchrow(query, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)
```

### Fetch Multiple Rows

```python
@app.get("/users")
async def get_users(db = Depends(get_db)):
    query = "SELECT * FROM users WHERE is_active = $1"
    users = await db.fetch(query, True)
    
    return [dict(user) for user in users]
```

### Insert Row

```python
@app.post("/users")
async def create_user(email: str, password: str, db = Depends(get_db)):
    # Hash password first (using passlib)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)
    
    query = """
        INSERT INTO users (email, password_hash)
        VALUES ($1, $2)
        RETURNING id, email, created_at
    """
    user = await db.fetchrow(query, email, hashed_password)
    
    return dict(user)
```

### Update Row

```python
@app.put("/users/{user_id}")
async def update_user(user_id: str, full_name: str, db = Depends(get_db)):
    query = """
        UPDATE users
        SET full_name = $1
        WHERE id = $2
        RETURNING *
    """
    user = await db.fetchrow(query, full_name, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)
```

### Delete Row

```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: str, db = Depends(get_db)):
    query = "DELETE FROM users WHERE id = $1 RETURNING id"
    user = await db.fetchrow(query, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
```

### Transaction Example

```python
@app.post("/transfer")
async def transfer_money(from_id: str, to_id: str, amount: float, db = Depends(get_db)):
    # Use transaction to ensure both operations succeed or both fail
    async with db.transaction():
        # Deduct from sender
        await db.execute(
            "UPDATE accounts SET balance = balance - $1 WHERE user_id = $2",
            amount,
            from_id
        )
        
        # Add to receiver
        await db.execute(
            "UPDATE accounts SET balance = balance + $1 WHERE user_id = $2",
            amount,
            to_id
        )
        
        # If any query fails, both are rolled back automatically
    
    return {"message": "Transfer successful"}
```

---

## 🎓 Viva Questions & Answers

### Q1: Why use asyncpg instead of SQLAlchemy?
**A:** 
- **Simpler**: No need to learn ORM syntax
- **More control**: Write exact SQL queries
- **Faster**: asyncpg is one of the fastest PostgreSQL drivers
- **Easier to debug**: See actual SQL queries
- **Better for learning**: Understand SQL directly

### Q2: What is a connection pool and why use it?
**A:** 
- A connection pool maintains multiple database connections
- Connections are reused instead of creating new ones each time
- **Benefits**:
  - Faster (no connection overhead)
  - More efficient (limited number of connections)
  - Better resource management

### Q3: What are parameterized queries?
**A:** 
- Queries that use placeholders ($1, $2) instead of direct string formatting
- User input is treated as data, not SQL code
- **Prevents SQL injection attacks**
- Example: `SELECT * FROM users WHERE email = $1`

### Q4: What is SQL injection and how do we prevent it?
**A:** 
- **SQL injection**: Attacker inserts malicious SQL code through user input
- **Example attack**: `'; DROP TABLE users; --`
- **Prevention**: Always use parameterized queries with $1, $2 placeholders
- Never use f-strings or string concatenation for SQL

### Q5: Explain the users table structure
**A:** 
- **id**: UUID primary key (unique identifier)
- **email**: User's email (unique, required)
- **password_hash**: Encrypted password (never store plain passwords)
- **full_name**: User's name (optional)
- **role**: User role (default: 'user')
- **is_active**: Account status (default: true)
- **created_at**: When user was created (auto-set)
- **updated_at**: When user was last updated (auto-updated by trigger)

### Q6: What is a UUID and why use it?
**A:** 
- **UUID**: Universal Unique Identifier (128-bit number)
- **Benefits**:
  - Globally unique (no duplicates)
  - Can't guess other user IDs (more secure)
  - Works in distributed systems
  - Can generate on client side

### Q7: What is a database trigger?
**A:** 
- Automatic action that runs when certain events occur
- Our trigger: Updates `updated_at` before every UPDATE
- **Benefits**:
  - Automatic (no manual updates needed)
  - Consistent (never forget to update timestamp)
  - Reliable (always runs)

### Q8: What is an index and why use it?
**A:** 
- Like an index in a book - helps find things quickly
- Makes searches much faster
- We created indexes on `email` and `role` for faster lookups
- **Trade-off**: Slightly slower inserts, much faster reads

### Q9: What is TIMESTAMPTZ?
**A:** 
- Timestamp with timezone information
- Stores date, time, and timezone
- Automatically converts to user's timezone
- Better than regular TIMESTAMP

### Q10: Explain the startup and shutdown events
**A:** 
- **Startup**: Runs when FastAPI starts
  - Creates database connection pool
  - Only runs once
- **Shutdown**: Runs when FastAPI stops
  - Closes all database connections
  - Cleans up resources

### Q11: What is the difference between fetchrow and fetch?
**A:** 
- **fetchrow**: Returns a single row (or None)
  - Use for: Getting one user by ID
- **fetch**: Returns list of rows
  - Use for: Getting all users, search results

### Q12: What is a transaction and when to use it?
**A:** 
- Group of operations that must all succeed or all fail
- **Example**: Money transfer (deduct from A, add to B)
- If any operation fails, all are rolled back
- Ensures data consistency

---

## 🐛 Troubleshooting

### Issue: "Database pool not initialized"
**Cause**: Connection pool not created  
**Fix**: Make sure `create_pool()` is called in startup event

### Issue: "Connection refused"
**Cause**: Wrong DATABASE_URL or Supabase not accessible  
**Fix**: 
1. Check DATABASE_URL in .env
2. Verify Supabase project is running
3. Check internet connection

### Issue: "Syntax error in SQL"
**Cause**: Invalid SQL query  
**Fix**: 
1. Test query in Supabase SQL Editor first
2. Check for typos in table/column names
3. Verify parameter placeholders ($1, $2)

### Issue: "asyncpg.exceptions.UniqueViolationError"
**Cause**: Trying to insert duplicate email  
**Fix**: Check if email already exists before inserting

---

## 📚 Summary

✅ **asyncpg setup complete** - No SQLAlchemy, direct SQL  
✅ **Connection pool** - Efficient database connections  
✅ **Parameterized queries** - SQL injection prevention  
✅ **Users table** - With UUID, triggers, and indexes  
✅ **Startup/shutdown events** - Proper resource management  
✅ **Helper functions** - fetch_one, fetch_all, execute_query  

You're ready to build database operations with raw SQL!
