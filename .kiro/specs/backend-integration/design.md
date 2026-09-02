# Backend-Frontend Integration Design

## Overview
This design document outlines the technical architecture for integrating the PricePilot backend with the React Native frontend using real scraped data with tiered search for optimal user experience.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Mobile App (Frontend)                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Home Screen          Search Screen        Profile Screen    │
│  ┌────────────┐       ┌──────────┐        ┌──────────┐      │
│  │ GET /auth  │       │ GET      │        │ GET      │      │
│  │    /me     │       │ /products│        │ /auth/me │      │
│  │            │       │  /search │        │          │      │
│  │ GET        │       │          │        └──────────┘      │
│  │ /products  │       │ (Tier 1  │                          │
│  │  /home     │       │  first)  │                          │
│  └────────────┘       │          │                          │
│                       │ Poll for │                          │
│                       │ Tier 2   │                          │
│                       └──────────┘                          │
└────────────────┬──────────────────────────────────┬─────────┘
                 │                                   │
                 │ HTTP/JSON                         │
                 │                                   │
┌────────────────▼───────────────────────────────────▼─────────┐
│                    FastAPI Backend                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Routers:                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  auth.py     │  │ products.py  │  │ scraper.py   │      │
│  │              │  │              │  │              │      │
│  │ POST /login  │  │ GET /home    │  │ Daily scrape │      │
│  │ POST /reg    │  │ GET /search  │  │ scheduler    │      │
│  │ GET /me      │  │ GET /status  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  Services:                                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           scraper_coordinator.py                      │   │
│  │  • Tiered search orchestration                        │   │
│  │  • Daily homepage scraping                            │   │
│  │  • Product curation logic                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────┬───────────────────────────────┬──────────────┘
                │                               │
                │                               │
┌───────────────▼──────────┐    ┌──────────────▼──────────────┐
│   PostgreSQL (Supabase)  │    │    MongoDB (Atlas)          │
│                          │    │                             │
│  • users                 │    │  • scraping_logs            │
│  • home_screen_products  │    │  • scraping_metadata        │
│  • search_cache          │    │                             │
│  • scrape_metadata       │    │                             │
└──────────────────────────┘    └─────────────────────────────┘
```

---

## Database Schema Design

### PostgreSQL Tables

#### 1. users table (existing)
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

#### 2. home_screen_products table (new)
Stores curated products for home screen sections.

```sql
CREATE TABLE home_screen_products (
    id                SERIAL PRIMARY KEY,
    section           TEXT NOT NULL,  -- 'best_deals' or 'top_price_drops'
    title             TEXT NOT NULL,
    price             DECIMAL(10, 2) NOT NULL,
    original_price    DECIMAL(10, 2),
    discount_percent  INTEGER,
    image_url         TEXT NOT NULL,
    store_name        TEXT NOT NULL,
    product_url       TEXT NOT NULL,
    category          TEXT,
    scraped_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_home_products_section ON home_screen_products(section);
CREATE INDEX idx_home_products_scraped ON home_screen_products(scraped_at);
```

#### 3. search_cache table (new)
Stores search results with tiered caching.

```sql
CREATE TABLE search_cache (
    id                SERIAL PRIMARY KEY,
    query             TEXT NOT NULL,
    tier1_results     JSONB,
    tier2_results     JSONB,
    tier1_cached_at   TIMESTAMPTZ,
    tier2_cached_at   TIMESTAMPTZ,
    is_complete       BOOLEAN DEFAULT FALSE,
    request_id        TEXT UNIQUE,
    UNIQUE(query)
);

CREATE INDEX idx_search_cache_query ON search_cache(query);
CREATE INDEX idx_search_cache_request ON search_cache(request_id);
CREATE INDEX idx_search_cache_cached ON search_cache(tier1_cached_at);
```

#### 4. scrape_metadata table (new)
Tracks daily scraping status.

```sql
CREATE TABLE scrape_metadata (
    id                SERIAL PRIMARY KEY,
    scrape_type       TEXT NOT NULL,  -- 'daily_homepage' or 'search'
    last_scrape_time  TIMESTAMPTZ,
    next_scrape_time  TIMESTAMPTZ,
    status            TEXT,  -- 'idle', 'running', 'completed', 'failed'
    products_found    INTEGER,
    error_message     TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scrape_metadata_type ON scrape_metadata(scrape_type);
CREATE INDEX idx_scrape_metadata_last ON scrape_metadata(last_scrape_time);
```

### MongoDB Collections

#### 1. scraping_logs collection
Stores detailed scraping logs for debugging.

```javascript
{
    _id: ObjectId,
    scrape_type: "daily_homepage" | "search",
    platform: "daraz" | "sastodeal" | ...,
    query: "laptop",  // null for homepage scraping
    status: "success" | "failed",
    products_found: 25,
    duration_ms: 1500,
    error_message: null,
    scraped_at: ISODate("2024-01-15T00:00:00Z")
}
```

---

## API Endpoints Design

### 1. GET /auth/me
Get logged-in user profile (for header greeting).

**Request:**
```
GET /auth/me
Headers: Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2024-01-01T12:00:00Z"
}
```

**Implementation:**
- Extract JWT token from Authorization header
- Verify token and extract user_id
- Query PostgreSQL users table
- Return user data (exclude password_hash)

---

### 2. GET /products/home
Get curated products for home screen.

**Request:**
```
GET /products/home
```

**Response:**
```json
{
    "best_deals": [
        {
            "id": 1,
            "title": "iPhone 15 Pro Max",
            "price": 149999,
            "original_price": 199999,
            "discount_percent": 25,
            "image_url": "https://...",
            "store_name": "Daraz",
            "product_url": "https://...",
            "category": "Electronics"
        }
    ],
    "top_price_drops": [...]
}
```

**Implementation:**
- Query home_screen_products table
- Filter by section='best_deals' and section='top_price_drops'
- Limit 25 per section
- Return JSON response

---

### 3. GET /products/search?q=laptop
Tiered search with progressive results.

**Request:**
```
GET /products/search?q=laptop
```

**Response (Tier 1 - Immediate):**
```json
{
    "request_id": "uuid-xyz",
    "query": "laptop",
    "tier": 1,
    "is_complete": false,
    "results": [
        {
            "title": "Dell Inspiron 15",
            "price": 75000,
            "original_price": 85000,
            "discount_percent": 12,
            "image_url": "https://...",
            "store_name": "Daraz",
            "product_url": "https://...",
            "category": "Electronics"
        }
    ],
    "results_count": 15,
    "tier1_platforms": ["Daraz", "Sastodeal", "Oliz"],
    "message": "Tier 1 results. Continue polling for more."
}
```

**Implementation:**
1. Check cache first (if exists and not expired, return all results)
2. If cache miss:
   - Generate unique request_id
   - Scrape Tier 1 platforms (Daraz, Sastodeal, Oliz) concurrently
   - Save Tier 1 results to search_cache table
   - Start Tier 2 scraping in background task
   - Return Tier 1 results immediately
3. Background task continues scraping Tier 2

---

### 4. GET /products/search/status?query=laptop&request_id=xyz
Poll for additional search results.

**Request:**
```
GET /products/search/status?query=laptop&request_id=xyz
```

**Response (While Tier 2 scraping):**
```json
{
    "request_id": "uuid-xyz",
    "is_complete": false,
    "new_results_count": 8,
    "new_results": [...],
    "message": "Tier 2 scraping in progress..."
}
```

**Response (Tier 2 complete):**
```json
{
    "request_id": "uuid-xyz",
    "is_complete": true,
    "new_results_count": 45,
    "new_results": [...],
    "message": "All platforms scraped successfully."
}
```

**Implementation:**
- Query search_cache table by request_id
- Check is_complete flag
- If complete, return tier2_results
- If not complete, return empty or partial tier2_results

---

### 5. POST /scraper/trigger (Admin only)
Manually trigger homepage scraping for testing.

**Request:**
```
POST /scraper/trigger
Headers: Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
    "status": "started",
    "message": "Homepage scraping triggered",
    "estimated_completion": "10 minutes"
}
```

---

## Tiered Search Flow

### Flow Diagram

```
User searches "laptop"
        │
        ▼
┌───────────────────────────────────────────┐
│ 1. Frontend: GET /products/search?q=laptop│
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│ 2. Backend: Check cache                   │
│    • Cache hit? Return all results        │
│    • Cache miss? Proceed to Tier 1        │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│ 3. Tier 1 Scraping (Concurrent)           │
│    ┌─────────────────────────────────┐    │
│    │ Daraz    (1-2s)                 │    │
│    │ Sastodeal (1-2s)                │    │
│    │ Oliz     (1-2s)                 │    │
│    └─────────────────────────────────┘    │
│    • Wait for all 3 to complete           │
│    • Max wait: 2 seconds                  │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│ 4. Save Tier 1 to cache                   │
│    • Insert into search_cache             │
│    • Set tier1_results                    │
│    • Set is_complete = FALSE              │
└───────────────┬───────────────────────────┘
                │
                ├──────────────────────────────────┐
                │                                  │
                ▼                                  ▼
┌───────────────────────────────┐  ┌──────────────────────────┐
│ 5. Return Tier 1 to frontend  │  │ 6. Start Tier 2 in       │
│    • ~15 results              │  │    background task       │
│    • Response time: ~2s       │  │    (BackgroundTasks)     │
│    • is_complete = false      │  │                          │
└───────────────┬───────────────┘  │  ┌────────────────────┐  │
                │                  │  │ Better             │  │
                │                  │  │ CGDigital          │  │
                │                  │  │ HardwarePasal      │  │
                │                  │  │ Hukut              │  │
                │                  │  │ Jeevee             │  │
                │                  │  │ NeoStore           │  │
                │                  │  │ UfoNepal           │  │
                │                  │  │ Hamrobazar         │  │
                │                  │  └────────────────────┘  │
                │                  │  • Scrape concurrently   │
                │                  │  • Max wait: 10s         │
                │                  └──────────┬───────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────────┐  ┌──────────────────────────┐
│ 7. Frontend displays Tier 1   │  │ 8. Save Tier 2 to cache  │
│    • User sees results        │  │    • Update search_cache │
│    • Can scroll/interact      │  │    • Set tier2_results   │
│    • Loading indicator shown  │  │    • Set is_complete=TRUE│
└───────────────┬───────────────┘  └──────────┬───────────────┘
                │                             │
                ▼                             │
┌───────────────────────────────┐            │
│ 9. Frontend polls status      │            │
│    GET /search/status?        │◄───────────┘
│    request_id=xyz             │
│    • Every 2s                 │
│    • Max 6 polls (12s)        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ 10. Display Tier 2 results    │
│     • Append to list          │
│     • ~45 more products       │
│     • Total: ~60 products     │
└───────────────────────────────┘
```

---

## Daily Homepage Scraping Flow

### Scheduler Design

```
┌─────────────────────────────────────────┐
│     APScheduler (Background Thread)      │
│                                          │
│  • Runs at midnight (00:00) daily       │
│  • Checks last_scrape_time               │
│  • Only runs if >24 hours ago           │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  scrape_homepage_daily() function        │
│                                          │
│  1. Update scrape_metadata status        │
│     to 'running'                         │
│                                          │
│  2. Scrape all 11 platforms              │
│     (concurrent)                         │
│                                          │
│  3. Extract featured products            │
│     from homepage HTML                   │
│                                          │
│  4. Analyze products:                    │
│     • Find best deals (>30% off)         │
│     • Find top price drops               │
│                                          │
│  5. Curate top 50 products:              │
│     • 25 best deals                      │
│     • 25 top price drops                 │
│                                          │
│  6. Delete old home_screen_products      │
│                                          │
│  7. Insert new products                  │
│                                          │
│  8. Update scrape_metadata:              │
│     • status = 'completed'               │
│     • products_found = 50                │
│     • last_scrape_time = NOW()           │
│     • next_scrape_time = NOW() + 24h     │
│                                          │
│  9. Log to MongoDB scraping_logs         │
└─────────────────────────────────────────┘
```

### Scraping Logic

**For each platform:**
1. Scrape homepage URL only (not search, not categories)
2. Extract featured products section
3. Parse product cards: title, price, image, URL
4. Store in temporary array

**Product Curation Algorithm:**
```python
def curate_products(all_products):
    # 1. Calculate discount percentage
    for product in all_products:
        if product.original_price:
            product.discount_percent = (
                (product.original_price - product.price) 
                / product.original_price * 100
            )
    
    # 2. Find best deals (highest discount %)
    best_deals = sorted(
        all_products, 
        key=lambda p: p.discount_percent, 
        reverse=True
    )[:25]
    
    # 3. Find top price drops (largest absolute price drop)
    top_drops = sorted(
        all_products,
        key=lambda p: p.original_price - p.price,
        reverse=True
    )[:25]
    
    return best_deals, top_drops
```

---

## File Structure

```
backend/
├── app/
│   ├── routers/
│   │   ├── auth.py (existing - add /me endpoint)
│   │   ├── products.py (modify - add /home, /search, /status)
│   │   └── scraper.py (new - admin trigger endpoint)
│   ├── services/
│   │   ├── scraper_coordinator.py (new - main scraping logic)
│   │   ├── scraper_service.py (existing - individual scrapers)
│   │   └── scheduler.py (new - APScheduler setup)
│   ├── models/
│   │   └── product.py (new - Pydantic models)
│   └── database/
│       ├── postgres.py (existing)
│       └── mongo.py (existing)
├── main.py (modify - register new routers, start scheduler)
└── database_schema.sql (modify - add new tables)

mobile/
├── app/
│   └── (tabs)/
│       └── home.tsx (modify - fetch real data)
├── components/
│   └── Header.tsx (modify - fetch user name)
└── constants/
    └── api.ts (existing)
```

---

## Technology Stack

### Backend
- **FastAPI**: Web framework
- **APScheduler**: Task scheduling for daily scraping
- **asyncio**: Async/concurrent scraping
- **asyncpg**: PostgreSQL driver
- **pymongo**: MongoDB driver

### Frontend
- **React Native**: Mobile framework
- **Expo**: Development platform
- **fetch API**: HTTP requests
- **AsyncStorage**: Cache user data locally

---

## Caching Strategy

### Search Cache
- **Tier 1**: Cached immediately after scraping (1-2s)
- **Tier 2**: Cached when all platforms complete (10s max)
- **Expiry**: 24 hours
- **Cleanup**: Periodic job deletes expired entries

### Home Screen Cache
- **Frontend**: Cache products in AsyncStorage for 1 hour
- **Backend**: Products updated daily at midnight
- **Invalidation**: Frontend checks timestamp, refetches if stale

---

## Error Handling

### Scraper Failures
- Each scraper wrapped in try-catch
- If one fails, others continue
- Failures logged to MongoDB
- Return partial results

### Database Failures
- PostgreSQL connection errors: Return 503 Service Unavailable
- MongoDB logging failures: Continue without logging (non-critical)

### Network Failures
- Frontend retries 3 times with exponential backoff
- Shows user-friendly error message
- Cached data used as fallback if available

---

## Security Considerations

- JWT authentication for /auth/me endpoint
- Admin-only access for /scraper/trigger
- Rate limiting on search endpoint (max 10 searches/minute per user)
- SQL injection prevention (parameterized queries)
- Input validation (Pydantic models)

---

## Performance Optimization

### Backend
- Connection pooling (PostgreSQL)
- Concurrent scraping (asyncio.gather)
- Background tasks (FastAPI BackgroundTasks)
- Database indexing (queries, sections, cached_at)

### Frontend
- Local caching (AsyncStorage)
- Optimistic UI updates
- Lazy loading (progressive results)
- Image caching (expo-image)

---

## Testing Strategy

### Unit Tests
- Test individual scrapers
- Test curation algorithm
- Test API endpoints

### Integration Tests
- Test end-to-end search flow
- Test daily scraping job
- Test tiered search progression

### Manual Testing
- Test on real device
- Verify progressive loading works
- Check all 11 platforms scraped

---

This design provides a solid foundation for implementing the backend-frontend integration with tiered search functionality!
