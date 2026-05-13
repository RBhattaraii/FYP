# Security Features - Quick Reference

## 🔒 Security Improvements Added

### 1. Rate Limiting
- **Login**: 5 requests/minute
- **Register**: 3 requests/minute
- **Returns**: 429 (Too Many Requests) when exceeded

### 2. Restricted CORS
- **Allowed origins**:
  - `http://localhost:8081` (Expo default)
  - `http://localhost:19006` (Expo web)
- **Blocks**: All other websites

### 3. Security Headers
- **X-Content-Type-Options: nosniff** - Prevents MIME-sniffing
- **X-Frame-Options: DENY** - Prevents clickjacking
- **X-XSS-Protection: 1; mode=block** - Blocks XSS attacks

---

## 📝 Code Changes

### main.py

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Restricted CORS
allow_origins=[
    "http://localhost:8081",
    "http://localhost:19006",
]

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### auth.py

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request):
    pass

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request):
    pass
```

---

## 🎓 Viva Key Points

### Rate Limiting
- **What**: Limits requests per time period
- **Why**: Prevents brute force attacks and spam
- **How**: Uses IP address to track requests

### CORS Restriction
- **What**: Controls which websites can access API
- **Why**: Prevents malicious websites from accessing your API
- **How**: Checks Origin header in requests

### Security Headers
- **nosniff**: Prevents browser from guessing file types
- **DENY**: Prevents site from being in iframe (clickjacking)
- **XSS Protection**: Blocks malicious scripts

---

## 🧪 Testing

### Test Rate Limit
```bash
# Make 6 login requests quickly
# First 5 succeed, 6th returns 429
```

### Test CORS
```bash
# Request from allowed origin: ✅ Works
# Request from other origin: ❌ Blocked
```

### Test Security Headers
```bash
curl -I http://localhost:8000/
# Should see all 3 security headers
```

---

## 📚 Full Documentation

See `docs/SECURITY_SETUP.md` for:
- Detailed explanations
- Attack examples
- 12 viva questions with answers
- Troubleshooting guide
