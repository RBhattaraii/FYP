# ✅ Authentication System Complete!

## 📁 Files Created

1. **`app/models/user.py`** - Pydantic models for validation
   - `RegisterRequest` - Registration data validation
   - `LoginRequest` - Login credentials validation
   - `AuthResponse` - Authentication response format

2. **`app/auth/jwt_handler.py`** - JWT token management
   - `create_access_token()` - Generate JWT tokens
   - `verify_access_token()` - Verify and decode tokens

3. **`app/auth/password.py`** - Password hashing
   - `hash_password()` - Hash passwords with bcrypt
   - `verify_password()` - Verify password against hash

4. **`app/routers/auth.py`** - Authentication endpoints
   - `POST /auth/register` - User registration
   - `POST /auth/login` - User login

---

## 🔐 Security Features

### ✅ Password Security:
- **Minimum 8 characters**
- **Must contain at least one number**
- **Hashed with bcrypt** (never stored as plain text)
- **Unique salt** for each password

### ✅ SQL Injection Prevention:
- **Parameterized queries** ($1, $2, $3)
- **Never use string formatting** for SQL

### ✅ Rate Limiting:
- **Register**: 3 requests per minute
- **Login**: 5 requests per minute
- **Prevents brute-force attacks**

### ✅ JWT Security:
- **Secret key** from environment variables
- **Expiry time** configurable
- **Signed tokens** (can't be tampered with)

---

## 🚀 API Endpoints

### POST /auth/register

**Register a new user**

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user"
}
```

**Errors:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Validation error (password too short, invalid email, etc.)
- `429 Too Many Requests` - Rate limit exceeded (3 per minute)
- `500 Internal Server Error` - Database error

---

### POST /auth/login

**Login with email and password**

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user"
}
```

**Errors:**
- `401 Unauthorized` - Invalid email or password
- `401 Unauthorized` - Account is deactivated
- `429 Too Many Requests` - Rate limit exceeded (5 per minute)
- `500 Internal Server Error` - Database error

---

## 🧪 Testing the API

### Start the server:
```bash
cd backend
uvicorn main:app --reload
```

### Test Registration:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@pricepilot.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Test Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@pricepilot.com",
    "password": "testpass123"
  }'
```

### Test with Swagger UI:
1. Go to: http://localhost:8000/docs
2. Expand `/auth/register` or `/auth/login`
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

---

## 📝 Step-by-Step Flow

### Registration Flow:

```
1. User fills registration form
   ↓
2. Mobile app sends POST /auth/register
   {email, password, full_name}
   ↓
3. FastAPI receives request
   ↓
4. Pydantic validates data
   - Email format correct?
   - Password >= 8 characters?
   - Password has number?
   ↓
5. Rate limiter checks (3/minute)
   ↓
6. Check if email exists in database
   SELECT id FROM users WHERE email = $1
   ↓
7. If exists → Return 400 "Email already registered"
   ↓
8. Hash password with bcrypt
   "password123" → "$2b$12$KIXxLV..."
   ↓
9. Insert user into database
   INSERT INTO users (email, password_hash, full_name, role)
   VALUES ($1, $2, $3, $4)
   ↓
10. Generate JWT token
    Token contains: user_id, expiry
    ↓
11. Return response
    {token, user_id, email, role}
    ↓
12. Mobile app stores token
    (SecureStore, AsyncStorage, etc.)
```

### Login Flow:

```
1. User fills login form
   ↓
2. Mobile app sends POST /auth/login
   {email, password}
   ↓
3. FastAPI receives request
   ↓
4. Pydantic validates data
   ↓
5. Rate limiter checks (5/minute)
   ↓
6. Look up user by email
   SELECT id, email, password_hash, role, is_active
   FROM users WHERE email = $1
   ↓
7. If not found → Return 401 "Invalid email or password"
   ↓
8. Check if account is active
   If not → Return 401 "Account is deactivated"
   ↓
9. Verify password with bcrypt
   Compare entered password with stored hash
   ↓
10. If wrong → Return 401 "Invalid email or password"
    ↓
11. Generate JWT token
    Token contains: user_id, expiry
    ↓
12. Return response
    {token, user_id, email, role}
    ↓
13. Mobile app stores token
```

---

## 🎓 Viva Questions & Answers

### Q1: What is password hashing?
**A**: Password hashing converts a plain text password into a scrambled string that can't be reversed. It's like making a smoothie - you can't un-blend it back to fruits!

Example:
- Plain: `"password123"`
- Hashed: `"$2b$12$KIXxLVz9eN7P.FZJL5FZ0.Xw8Z..."`

### Q2: Why hash passwords?
**A**: Security! If someone hacks the database, they can't see actual passwords. They only see hashed values which are useless without the original password.

### Q3: What is bcrypt?
**A**: bcrypt is a password hashing algorithm designed specifically for passwords. It's slow on purpose (makes brute-force attacks harder) and includes a "salt" (random data) to make each hash unique.

### Q4: What is a salt?
**A**: A salt is random data added to the password before hashing. This means the same password gets different hashes each time, preventing attackers from using pre-computed hash tables.

### Q5: What is JWT?
**A**: JWT (JSON Web Token) is a secure way to transmit information between client and server. It's like a digital ID card that proves who you are.

Structure: `header.payload.signature`
- Header: Algorithm used (HS256)
- Payload: Data (user_id, expiry)
- Signature: Verification code

### Q6: How does JWT work?
**A**: 
1. User logs in → Server creates JWT with user_id
2. Server sends token to client
3. Client stores token
4. Client sends token with every request
5. Server verifies token and identifies user

### Q7: Why use JWT instead of sessions?
**A**: 
- Stateless (server doesn't store session data)
- Scalable (works across multiple servers)
- Mobile-friendly (easy to use in mobile apps)

### Q8: What is parameterized query?
**A**: A parameterized query uses placeholders ($1, $2) instead of directly inserting user input into SQL. This prevents SQL injection attacks.

❌ UNSAFE: `f"SELECT * FROM users WHERE email = '{email}'"`
✅ SAFE: `"SELECT * FROM users WHERE email = $1"` with `email` as parameter

### Q9: What is SQL injection?
**A**: SQL injection is when an attacker inserts malicious SQL code through user input.

Example attack:
- Input: `"'; DROP TABLE users; --"`
- Unsafe query: `SELECT * FROM users WHERE email = ''; DROP TABLE users; --'`
- Result: Deletes entire users table!

Parameterized queries prevent this by treating input as data, not SQL code.

### Q10: What is rate limiting?
**A**: Rate limiting restricts how many requests a user can make in a time period. This prevents brute-force attacks (trying many passwords).

- Register: 3/minute (prevents spam accounts)
- Login: 5/minute (prevents password guessing)

### Q11: Why return same error for "user not found" and "wrong password"?
**A**: Security! If we return different errors, attackers can enumerate which emails are registered.

❌ BAD: "Email not found" vs "Wrong password"
✅ GOOD: "Invalid email or password" (same for both)

### Q12: What happens during registration?
**A**: 
1. Validate email and password
2. Check if email exists
3. Hash password with bcrypt
4. Store user in database
5. Generate JWT token
6. Return token to client

### Q13: What happens during login?
**A**: 
1. Look up user by email
2. Check if user exists
3. Verify password against hash
4. Generate JWT token
5. Return token to client

### Q14: How does the mobile app use the token?
**A**: 
1. Store token after login/register
2. Send token with every request in Authorization header:
   `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Server verifies token and identifies user

---

## ✅ What You Have Now

### Authentication System:
- ✅ User registration with validation
- ✅ User login with password verification
- ✅ JWT token generation
- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ Complete error handling

### Databases:
- ✅ PostgreSQL (users table)
- ✅ MongoDB (raw scraped data)

### Security:
- ✅ Password hashing
- ✅ Parameterized queries
- ✅ Rate limiting
- ✅ JWT tokens
- ✅ CORS restrictions
- ✅ Security headers

### Documentation:
- ✅ Complete API documentation
- ✅ Viva preparation materials
- ✅ Code examples
- ✅ Step-by-step flows

---

## 🎯 Next Steps

### Option A: Test Authentication
1. Start the server
2. Test registration endpoint
3. Test login endpoint
4. Verify JWT token works

### Option B: Add Protected Routes
Create endpoints that require authentication:
- GET /users/me - Get current user info
- PUT /users/me - Update user profile
- GET /products - Get products (requires auth)

### Option C: Set Up Mobile App
1. Initialize React Native project
2. Create login/register screens
3. Connect to backend API
4. Store JWT token
5. Send token with requests

---

## 🎉 Summary

**Authentication system is complete and ready to use!**

- ✅ Secure password hashing
- ✅ JWT token authentication
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ Complete documentation
- ✅ Viva preparation ready

**Your backend now has:**
- User registration
- User login
- Secure authentication
- Complete security features

**Ready to test or move to mobile app development!** 🚀
