# PostgreSQL Connection Flow Diagrams

## Connection Pool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Startup Event                         │    │
│  │  @app.on_event("startup")                          │    │
│  │  async def startup():                              │    │
│  │      await create_pool()                           │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Connection Pool Created                    │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │    │
│  │  │  Conn 1  │ │  Conn 2  │ │  Conn 3  │  ...     │    │
│  │  └──────────┘ └──────────┘ └──────────┘          │    │
│  │  Min: 2 connections, Max: 10 connections          │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         API Routes Use Connections                 │    │
│  │  @app.get("/users")                                │    │
│  │  async def get_users(db = Depends(get_db)):        │    │
│  │      # db is a connection from the pool            │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Shutdown Event                        │    │
│  │  @app.on_event("shutdown")                         │    │
│  │  async def shutdown():                             │    │
│  │      await close_pool()                            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow with Database Connection

```
1. HTTP Request arrives
   │
   ├─► FastAPI receives request
   │
   ▼
2. Route handler called
   │
   ├─► @app.get("/users")
   ├─► async def get_users(db = Depends(get_db))
   │
   ▼
3. get_db() dependency executed
   │
   ├─► Acquires connection from pool
   ├─► Connection is available for use
   │
   ▼
4. Execute database query
   │
   ├─► query = "SELECT * FROM users WHERE role = $1"
   ├─► users = await db.fetch(query, "admin")
   │
   ▼
5. Process results
   │
   ├─► Convert to list of dicts
   ├─► return [dict(user) for user in users]
   │
   ▼
6. Connection returned to pool
   │
   ├─► Automatic (context manager)
   ├─► Connection ready for next request
   │
   ▼
7. HTTP Response sent
   │
   └─► JSON response to client
```

---

## Connection Pool vs No Pool

### Without Connection Pool (Slow)

```
Request 1                Request 2                Request 3
    │                        │                        │
    ├─► Create Connection    ├─► Create Connection    ├─► Create Connection
    │   (Slow! ~100ms)       │   (Slow! ~100ms)       │   (Slow! ~100ms)
    │                        │                        │
    ├─► Execute Query        ├─► Execute Query        ├─► Execute Query
    │   (Fast! ~10ms)        │   (Fast! ~10ms)        │   (Fast! ~10ms)
    │                        │                        │
    └─► Close Connection     └─► Close Connection     └─► Close Connection

Total time per request: ~110ms
```

### With Connection Pool (Fast)

```
Request 1                Request 2                Request 3
    │                        │                        │
    ├─► Get from Pool        ├─► Get from Pool        ├─► Get from Pool
    │   (Fast! ~1ms)         │   (Fast! ~1ms)         │   (Fast! ~1ms)
    │                        │                        │
    ├─► Execute Query        ├─► Execute Query        ├─► Execute Query
    │   (Fast! ~10ms)        │   (Fast! ~10ms)        │   (Fast! ~10ms)
    │                        │                        │
    └─► Return to Pool       └─► Return to Pool       └─► Return to Pool

Total time per request: ~11ms (10x faster!)
```

---

## Parameterized Query Flow

### ✅ Safe Parameterized Query

```
User Input: email = "user@example.com"
                │
                ▼
Python Code:
query = "SELECT * FROM users WHERE email = $1"
result = await db.fetchrow(query, email)
                │
                ▼
asyncpg processes:
1. Separates SQL from data
2. Escapes special characters in email
3. Treats email as pure data
                │
                ▼
Sent to PostgreSQL:
SQL: SELECT * FROM users WHERE email = $1
Data: ["user@example.com"]
                │
                ▼
PostgreSQL executes safely:
- Email is treated as string data only
- No SQL code execution possible
                │
                ▼
Result: User record returned safely ✅
```

### ❌ Unsafe String Formatting

```
User Input: email = "'; DROP TABLE users; --"
                │
                ▼
Python Code (WRONG!):
query = f"SELECT * FROM users WHERE email = '{email}'"
result = await db.fetchrow(query)
                │
                ▼
Resulting SQL:
SELECT * FROM users WHERE email = ''; DROP TABLE users; --'
                │
                ▼
PostgreSQL executes:
1. SELECT * FROM users WHERE email = ''  (returns nothing)
2. DROP TABLE users;                     (DELETES TABLE!)
3. --'                                   (comment, ignored)
                │
                ▼
Result: YOUR ENTIRE USERS TABLE IS DELETED! ❌
```

---

## Database Schema with Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        users table                           │
├─────────────────────────────────────────────────────────────┤
│  id            UUID PRIMARY KEY                              │
│  email         TEXT UNIQUE NOT NULL                          │
│  password_hash TEXT NOT NULL                                 │
│  full_name     TEXT                                          │
│  role          TEXT DEFAULT 'user'                           │
│  is_active     BOOLEAN DEFAULT TRUE                          │
│  created_at    TIMESTAMPTZ DEFAULT NOW()                     │
│  updated_at    TIMESTAMPTZ DEFAULT NOW()  ◄─── Auto-updated │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ Trigger watches for UPDATEs
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              update_updated_at() function                    │
├─────────────────────────────────────────────────────────────┤
│  BEFORE UPDATE ON users                                      │
│  FOR EACH ROW                                                │
│  EXECUTE:                                                    │
│      NEW.updated_at = NOW()                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Trigger Execution Flow

```
1. User makes UPDATE request
   │
   ├─► UPDATE users SET full_name = 'Jane Doe' WHERE id = '...'
   │
   ▼
2. PostgreSQL receives UPDATE
   │
   ├─► Prepares to update row
   │
   ▼
3. BEFORE UPDATE trigger fires
   │
   ├─► Calls update_updated_at() function
   │
   ▼
4. Function executes
   │
   ├─► NEW.updated_at = NOW()
   ├─► Sets updated_at to current timestamp
   │
   ▼
5. UPDATE proceeds with modified data
   │
   ├─► full_name = 'Jane Doe'
   ├─► updated_at = '2024-01-15 10:30:00+00:00'  (added by trigger)
   │
   ▼
6. Row updated in database
   │
   └─► Both fields updated automatically!
```

---

## Index Performance Comparison

### Without Index (Slow)

```
Query: SELECT * FROM users WHERE email = 'user@example.com'

┌─────────────────────────────────────────────────────────────┐
│                      users table                             │
│  (1,000,000 rows)                                           │
├─────────────────────────────────────────────────────────────┤
│  Row 1:  id=..., email='alice@example.com'    ◄─── Check   │
│  Row 2:  id=..., email='bob@example.com'      ◄─── Check   │
│  Row 3:  id=..., email='charlie@example.com'  ◄─── Check   │
│  ...                                                         │
│  Row 500,000: id=..., email='user@example.com' ◄─── FOUND! │
│  ...                                                         │
│  Row 1,000,000: id=..., email='zoe@example.com'            │
└─────────────────────────────────────────────────────────────┘

Scanned: 500,000 rows
Time: ~5 seconds ❌
```

### With Index (Fast)

```
Query: SELECT * FROM users WHERE email = 'user@example.com'

┌─────────────────────────────────────────────────────────────┐
│                   idx_users_email index                      │
│  (B-tree structure - like a sorted phone book)              │
├─────────────────────────────────────────────────────────────┤
│  'a...' → Row 1                                             │
│  'b...' → Row 2                                             │
│  'c...' → Row 3                                             │
│  ...                                                         │
│  'user@example.com' → Row 500,000  ◄─── Direct lookup!     │
│  ...                                                         │
│  'z...' → Row 1,000,000                                     │
└─────────────────────────────────────────────────────────────┘

Scanned: ~10 rows (binary search)
Time: ~0.01 seconds ✅ (500x faster!)
```

---

## UUID vs Integer ID

### Integer ID (Sequential)

```
User 1: id = 1
User 2: id = 2
User 3: id = 3
User 4: id = 4
...

Problems:
❌ Easy to guess other user IDs
❌ Reveals total number of users
❌ Conflicts in distributed systems
❌ Less secure
```

### UUID (Random)

```
User 1: id = 550e8400-e29b-41d4-a716-446655440000
User 2: id = 7c9e6679-7425-40de-944b-e07fc1f90ae7
User 3: id = 3d813cca-5b4a-4b3d-9c8e-7f8c9d0e1f2a
User 4: id = 9f8e7d6c-5b4a-3c2d-1e0f-9a8b7c6d5e4f
...

Benefits:
✅ Impossible to guess other user IDs
✅ Globally unique
✅ Works in distributed systems
✅ More secure
✅ Can generate on client side
```

---

## Transaction Flow

### Without Transaction (Risky)

```
Transfer $100 from Alice to Bob

Step 1: Deduct from Alice
UPDATE accounts SET balance = balance - 100 WHERE user_id = 'alice'
✅ Success

Step 2: Add to Bob
UPDATE accounts SET balance = balance + 100 WHERE user_id = 'bob'
❌ ERROR! (Network failure)

Result:
- Alice lost $100
- Bob didn't receive $100
- Money disappeared! ❌
```

### With Transaction (Safe)

```
Transfer $100 from Alice to Bob

BEGIN TRANSACTION
    │
    ├─► Step 1: Deduct from Alice
    │   UPDATE accounts SET balance = balance - 100 WHERE user_id = 'alice'
    │   ✅ Success
    │
    ├─► Step 2: Add to Bob
    │   UPDATE accounts SET balance = balance + 100 WHERE user_id = 'bob'
    │   ❌ ERROR! (Network failure)
    │
    └─► ROLLBACK (undo all changes)

Result:
- Alice still has $100
- Bob still has original balance
- No money lost! ✅
- Can retry the transaction
```

---

## asyncpg vs SQLAlchemy

### asyncpg (What we use)

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Python Code                          │
├─────────────────────────────────────────────────────────────┤
│  query = "SELECT * FROM users WHERE email = $1"             │
│  user = await db.fetchrow(query, email)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Direct SQL
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL                              │
└─────────────────────────────────────────────────────────────┘

Pros:
✅ Simple and direct
✅ Full control over SQL
✅ Faster
✅ Easier to debug
✅ See exact SQL queries
```

### SQLAlchemy (ORM - Not used)

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Python Code                          │
├─────────────────────────────────────────────────────────────┤
│  user = session.query(User).filter(User.email == email).first() │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ ORM translates to SQL
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLAlchemy ORM                            │
│  Converts Python objects to SQL                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Generated SQL
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL                              │
└─────────────────────────────────────────────────────────────┘

Cons:
❌ More complex
❌ Less control
❌ Slower
❌ Harder to debug
❌ Hidden SQL queries
```

---

## Summary

These diagrams show:

1. **Connection Pool** - Reuses connections for efficiency
2. **Request Flow** - How database connections are acquired and released
3. **Parameterized Queries** - Prevents SQL injection
4. **Triggers** - Automatically updates timestamps
5. **Indexes** - Makes searches 500x faster
6. **UUID vs Integer** - Better security with UUIDs
7. **Transactions** - Ensures data consistency
8. **asyncpg vs SQLAlchemy** - Direct SQL vs ORM

All designed for simplicity, security, and performance!
