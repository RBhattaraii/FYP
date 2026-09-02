# Database Migration - Backend Integration Tables

## Overview
This document describes the database schema changes made for the backend-frontend integration feature. Three new tables were added to support home screen product curation, tiered search caching, and scraping metadata tracking.

## Migration Date
**Created:** 2024

## Tables Added

### 1. home_screen_products
Stores curated products for home screen display (best deals and top price drops).

**Schema:**
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
```

**Indexes:**
- `idx_home_products_section` - Index on section column for fast filtering by best_deals/top_price_drops
- `idx_home_products_scraped` - Index on scraped_at for sorting by date

**Purpose:**
- Stores 25 best deals (highest discount percentage)
- Stores 25 top price drops (largest absolute price reduction)
- Data is refreshed daily at midnight
- Old products are deleted and replaced with new curated products

---

### 2. search_cache
Stores search results with tiered caching (Tier 1 and Tier 2 results).

**Schema:**
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
```

**Indexes:**
- `idx_search_cache_query` - Index on query for fast lookup by search term
- `idx_search_cache_request` - Index on request_id for polling status
- `idx_search_cache_cached` - Index on tier1_cached_at for expiry checks

**Purpose:**
- Caches search results for 24 hours to reduce scraping load
- Tier 1: Fast platforms (Daraz, Sastodeal, Oliz) - returns in ~2 seconds
- Tier 2: Remaining 8 platforms - scrapes in background, completes in ~10 seconds
- JSONB columns store product arrays for flexible querying
- request_id allows frontend to poll for Tier 2 results

---

### 3. scrape_metadata
Tracks daily scraping status and search scraping metadata.

**Schema:**
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
```

**Indexes:**
- `idx_scrape_metadata_type` - Index on scrape_type for filtering by daily vs search scrapes
- `idx_scrape_metadata_last` - Index on last_scrape_time for checking if scraping needed

**Purpose:**
- Tracks when the last daily homepage scrape occurred
- Prevents duplicate scraping within 24 hours
- Records scraping success/failure status
- Stores error messages for debugging

---

## Migration Process

### Step 1: Update Schema File
The `database_schema.sql` file was updated to include the three new tables with their indexes and example queries.

### Step 2: Apply Migration
Run the migration script to create tables in the database:

```bash
python apply_schema_migration.py
```

This script:
- Connects to PostgreSQL using DATABASE_URL from .env
- Creates all three tables using `CREATE TABLE IF NOT EXISTS`
- Creates all indexes using `CREATE INDEX IF NOT EXISTS`
- Verifies tables exist after creation
- Uses `statement_cache_size=0` for Supabase pgbouncer compatibility

### Step 3: Verify Schema
Run the verification script to check table structures:

```bash
python verify_schema.py
```

This script:
- Lists all columns for each table
- Lists all indexes for each table
- Confirms all tables and indexes exist

### Step 4: Test CRUD Operations
Run the test script to verify basic operations:

```bash
python test_new_tables.py
```

This script:
- Tests INSERT and SELECT on home_screen_products
- Tests INSERT and SELECT with JSONB on search_cache
- Tests INSERT and SELECT on scrape_metadata
- Cleans up all test data

---

## Usage Examples

### home_screen_products

**Insert a product:**
```python
await db.execute("""
    INSERT INTO home_screen_products 
    (section, title, price, original_price, discount_percent, 
     image_url, store_name, product_url, category)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
""", 'best_deals', 'iPhone 15 Pro Max', 149999.00, 199999.00, 25,
     'https://example.com/image.jpg', 'Daraz', 
     'https://daraz.com.np/product', 'Electronics')
```

**Get all best deals:**
```python
products = await db.fetch("""
    SELECT * FROM home_screen_products 
    WHERE section = $1 
    ORDER BY scraped_at DESC 
    LIMIT 25
""", 'best_deals')
```

**Delete old products (for daily refresh):**
```python
await db.execute("""
    DELETE FROM home_screen_products 
    WHERE scraped_at < NOW() - INTERVAL '1 day'
""")
```

---

### search_cache

**Insert Tier 1 cache:**
```python
import json

tier1_data = json.dumps([
    {"title": "Dell Inspiron", "price": 75000, "store_name": "Daraz"}
])

await db.execute("""
    INSERT INTO search_cache 
    (query, tier1_results, tier1_cached_at, is_complete, request_id)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (query) DO UPDATE
    SET tier1_results = EXCLUDED.tier1_results,
        tier1_cached_at = EXCLUDED.tier1_cached_at
""", 'laptop', tier1_data, datetime.now(), False, 'uuid-123')
```

**Update with Tier 2 results:**
```python
tier2_data = json.dumps([
    {"title": "HP Pavilion", "price": 80000, "store_name": "Better"}
])

await db.execute("""
    UPDATE search_cache 
    SET tier2_results = $1, 
        tier2_cached_at = $2, 
        is_complete = TRUE 
    WHERE query = $3
""", tier2_data, datetime.now(), 'laptop')
```

**Get cached results:**
```python
cache = await db.fetchrow("""
    SELECT * FROM search_cache 
    WHERE query = $1 
    AND tier1_cached_at > NOW() - INTERVAL '24 hours'
""", 'laptop')

if cache:
    tier1_results = json.loads(cache['tier1_results'])
    tier2_results = json.loads(cache['tier2_results']) if cache['tier2_results'] else []
```

**Delete expired cache:**
```python
await db.execute("""
    DELETE FROM search_cache 
    WHERE tier1_cached_at < NOW() - INTERVAL '24 hours'
""")
```

---

### scrape_metadata

**Insert scrape metadata:**
```python
await db.execute("""
    INSERT INTO scrape_metadata 
    (scrape_type, last_scrape_time, next_scrape_time, status, products_found)
    VALUES ($1, $2, $3, $4, $5)
""", 'daily_homepage', datetime.now(), 
     datetime.now() + timedelta(hours=24), 'completed', 50)
```

**Check if scraping needed:**
```python
last_scrape = await db.fetchrow("""
    SELECT * FROM scrape_metadata 
    WHERE scrape_type = $1 
    ORDER BY last_scrape_time DESC 
    LIMIT 1
""", 'daily_homepage')

if not last_scrape or last_scrape['last_scrape_time'] < datetime.now() - timedelta(hours=24):
    # Scraping needed
    pass
```

---

## Performance Optimization

### Indexes Created
- **6 indexes total** across 3 tables
- All frequently queried columns are indexed
- Composite indexes for section filtering and date sorting

### Query Optimization Tips
1. Always use parameterized queries ($1, $2, etc.) to prevent SQL injection
2. Use `LIMIT` to restrict result sets
3. Query by indexed columns (section, query, scrape_type)
4. Use `ON CONFLICT` for upserts instead of SELECT then INSERT/UPDATE
5. Use JSONB for flexible product storage without schema changes

### Connection Pool Settings
The postgres.py file already uses connection pooling with optimal settings:
- `min_size=2` - Keep 2 connections open
- `max_size=10` - Allow up to 10 concurrent connections
- `statement_cache_size=0` - Disable for pgbouncer compatibility

---

## Migration Verification Checklist

✅ **database_schema.sql updated** with new tables
✅ **Migration script created** (apply_schema_migration.py)
✅ **Verification script created** (verify_schema.py)
✅ **Test script created** (test_new_tables.py)
✅ **All 3 tables created** in database
✅ **All 6 indexes created** successfully
✅ **CRUD operations tested** and working
✅ **JSONB columns tested** with JSON data
✅ **Parameterized queries tested** ($1, $2, etc.)
✅ **pgbouncer compatibility** confirmed (statement_cache_size=0)

---

## Rollback Procedure (if needed)

If you need to rollback this migration:

```sql
-- Drop tables in reverse order
DROP TABLE IF EXISTS scrape_metadata CASCADE;
DROP TABLE IF EXISTS search_cache CASCADE;
DROP TABLE IF EXISTS home_screen_products CASCADE;
```

**Note:** This will delete all data in these tables. Use with caution!

---

## Next Steps

1. ✅ Database schema created
2. 🔄 Create Pydantic models for API responses (Task 2)
3. 🔄 Implement scraper coordinator service (Task 3)
4. 🔄 Implement API endpoints (Tasks 6-9)
5. 🔄 Implement daily scheduler (Task 11)
6. 🔄 Frontend integration (Tasks 13-16)

---

## Files Modified/Created

### Modified:
- `backend/database_schema.sql` - Added 3 new tables with indexes

### Created:
- `backend/apply_schema_migration.py` - Migration script
- `backend/verify_schema.py` - Verification script
- `backend/test_new_tables.py` - Test script
- `backend/DATABASE_MIGRATION.md` - This documentation file

---

## Contact
If you encounter any issues with the migration, check:
1. DATABASE_URL is correct in .env file
2. PostgreSQL connection is working
3. Supabase project is active
4. Run verify_schema.py to check table structures
