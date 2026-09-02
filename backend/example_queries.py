"""
Example Query Patterns for Backend Integration Tables
This file demonstrates the query patterns that will be used in the actual implementation.
These are reference examples - NOT for direct use in production code.
"""

import asyncpg
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta


# ============================================================================
# HOME SCREEN PRODUCTS - Query Patterns
# ============================================================================

async def insert_curated_products(db: asyncpg.Connection, products: List[Dict[str, Any]]):
    """
    Insert curated products for home screen (used during daily scraping).
    This will be called by the scraper coordinator service.
    """
    # Build list of tuples for bulk insert
    product_data = [
        (
            p['section'],           # 'best_deals' or 'top_price_drops'
            p['title'],
            p['price'],
            p.get('original_price'),
            p.get('discount_percent'),
            p['image_url'],
            p['store_name'],
            p['product_url'],
            p.get('category')
        )
        for p in products
    ]
    
    # Bulk insert using executemany
    await db.executemany("""
        INSERT INTO home_screen_products 
        (section, title, price, original_price, discount_percent, 
         image_url, store_name, product_url, category)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    """, product_data)


async def delete_old_home_products(db: asyncpg.Connection):
    """
    Delete all old home screen products before inserting new curated products.
    This is called before each daily scraping to refresh the home screen.
    """
    result = await db.execute("DELETE FROM home_screen_products")
    return result


async def get_home_screen_products(db: asyncpg.Connection):
    """
    Get all home screen products grouped by section.
    This will be used in GET /products/home endpoint.
    """
    # Get best deals
    best_deals = await db.fetch("""
        SELECT id, title, price, original_price, discount_percent,
               image_url, store_name, product_url, category
        FROM home_screen_products
        WHERE section = $1
        ORDER BY scraped_at DESC
        LIMIT 25
    """, 'best_deals')
    
    # Get top price drops
    top_price_drops = await db.fetch("""
        SELECT id, title, price, original_price, discount_percent,
               image_url, store_name, product_url, category
        FROM home_screen_products
        WHERE section = $1
        ORDER BY scraped_at DESC
        LIMIT 25
    """, 'top_price_drops')
    
    # Convert to dict format for JSON response
    return {
        'best_deals': [dict(row) for row in best_deals],
        'top_price_drops': [dict(row) for row in top_price_drops]
    }


# ============================================================================
# SEARCH CACHE - Query Patterns
# ============================================================================

async def get_cached_search(db: asyncpg.Connection, query: str):
    """
    Get cached search results if they exist and are not expired.
    Returns None if cache miss or expired.
    """
    cache = await db.fetchrow("""
        SELECT query, tier1_results, tier2_results, 
               tier1_cached_at, tier2_cached_at, is_complete, request_id
        FROM search_cache
        WHERE query = $1
        AND tier1_cached_at > NOW() - INTERVAL '24 hours'
    """, query.lower().strip())
    
    if not cache:
        return None
    
    # Parse JSONB results
    tier1_results = json.loads(cache['tier1_results']) if cache['tier1_results'] else []
    tier2_results = json.loads(cache['tier2_results']) if cache['tier2_results'] else []
    
    return {
        'query': cache['query'],
        'tier1_results': tier1_results,
        'tier2_results': tier2_results,
        'is_complete': cache['is_complete'],
        'request_id': cache['request_id'],
        'cached_at': cache['tier1_cached_at']
    }


async def insert_tier1_cache(db: asyncpg.Connection, query: str, 
                              tier1_results: List[Dict], request_id: str):
    """
    Insert or update Tier 1 search cache.
    Uses ON CONFLICT to handle duplicate queries.
    """
    tier1_json = json.dumps(tier1_results)
    
    await db.execute("""
        INSERT INTO search_cache 
        (query, tier1_results, tier1_cached_at, is_complete, request_id)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (query) DO UPDATE
        SET tier1_results = EXCLUDED.tier1_results,
            tier1_cached_at = EXCLUDED.tier1_cached_at,
            is_complete = EXCLUDED.is_complete,
            request_id = EXCLUDED.request_id
    """, query.lower().strip(), tier1_json, datetime.now(), False, request_id)


async def update_tier2_cache(db: asyncpg.Connection, request_id: str, 
                              tier2_results: List[Dict]):
    """
    Update cache with Tier 2 results when background scraping completes.
    """
    tier2_json = json.dumps(tier2_results)
    
    await db.execute("""
        UPDATE search_cache
        SET tier2_results = $1,
            tier2_cached_at = $2,
            is_complete = TRUE
        WHERE request_id = $3
    """, tier2_json, datetime.now(), request_id)


async def get_search_status(db: asyncpg.Connection, request_id: str):
    """
    Get search status for polling endpoint.
    Returns whether Tier 2 scraping is complete and new results.
    """
    cache = await db.fetchrow("""
        SELECT query, tier2_results, is_complete
        FROM search_cache
        WHERE request_id = $1
    """, request_id)
    
    if not cache:
        return None
    
    tier2_results = json.loads(cache['tier2_results']) if cache['tier2_results'] else []
    
    return {
        'query': cache['query'],
        'is_complete': cache['is_complete'],
        'new_results': tier2_results,
        'new_results_count': len(tier2_results)
    }


async def delete_expired_cache(db: asyncpg.Connection):
    """
    Delete expired cache entries (older than 24 hours).
    This will be called by a periodic cleanup job.
    """
    result = await db.execute("""
        DELETE FROM search_cache
        WHERE tier1_cached_at < NOW() - INTERVAL '24 hours'
    """)
    return result


# ============================================================================
# SCRAPE METADATA - Query Patterns
# ============================================================================

async def get_last_scrape_metadata(db: asyncpg.Connection, scrape_type: str):
    """
    Get the last scrape metadata for a given type.
    Used to check if daily scraping is needed.
    """
    metadata = await db.fetchrow("""
        SELECT id, scrape_type, last_scrape_time, next_scrape_time,
               status, products_found, error_message, created_at
        FROM scrape_metadata
        WHERE scrape_type = $1
        ORDER BY last_scrape_time DESC
        LIMIT 1
    """, scrape_type)
    
    return dict(metadata) if metadata else None


async def should_scrape_homepage(db: asyncpg.Connection) -> bool:
    """
    Check if homepage scraping is needed (>24 hours since last scrape).
    """
    last_scrape = await get_last_scrape_metadata(db, 'daily_homepage')
    
    if not last_scrape:
        return True  # Never scraped before
    
    last_time = last_scrape['last_scrape_time']
    if not last_time:
        return True
    
    # Check if more than 24 hours ago
    return datetime.now() - last_time > timedelta(hours=24)


async def insert_scrape_metadata(db: asyncpg.Connection, scrape_type: str,
                                  status: str, products_found: int = None,
                                  error_message: str = None):
    """
    Insert scrape metadata after scraping completes.
    """
    await db.execute("""
        INSERT INTO scrape_metadata
        (scrape_type, last_scrape_time, next_scrape_time, 
         status, products_found, error_message)
        VALUES ($1, $2, $3, $4, $5, $6)
    """, scrape_type, datetime.now(), datetime.now() + timedelta(hours=24),
         status, products_found, error_message)


async def update_scrape_status(db: asyncpg.Connection, scrape_id: int, 
                                status: str, products_found: int = None,
                                error_message: str = None):
    """
    Update scrape metadata status (for running -> completed/failed transitions).
    """
    await db.execute("""
        UPDATE scrape_metadata
        SET status = $1,
            products_found = $2,
            error_message = $3
        WHERE id = $4
    """, status, products_found, error_message, scrape_id)


# ============================================================================
# TRANSACTION EXAMPLE - Daily Scraping Workflow
# ============================================================================

async def daily_scraping_workflow(db: asyncpg.Connection, 
                                   curated_products: List[Dict]):
    """
    Example of using a transaction for daily scraping workflow.
    Ensures all operations succeed or all fail together.
    """
    async with db.transaction():
        # Step 1: Delete old products
        await db.execute("DELETE FROM home_screen_products")
        
        # Step 2: Insert new curated products
        product_data = [
            (
                p['section'],
                p['title'],
                p['price'],
                p.get('original_price'),
                p.get('discount_percent'),
                p['image_url'],
                p['store_name'],
                p['product_url'],
                p.get('category')
            )
            for p in curated_products
        ]
        
        await db.executemany("""
            INSERT INTO home_screen_products 
            (section, title, price, original_price, discount_percent,
             image_url, store_name, product_url, category)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, product_data)
        
        # Step 3: Update scrape metadata
        await db.execute("""
            INSERT INTO scrape_metadata
            (scrape_type, last_scrape_time, next_scrape_time, 
             status, products_found)
            VALUES ($1, $2, $3, $4, $5)
        """, 'daily_homepage', datetime.now(), 
             datetime.now() + timedelta(hours=24), 'completed', 
             len(curated_products))
    
    # If any step fails, entire transaction is rolled back


# ============================================================================
# NOTES FOR IMPLEMENTATION
# ============================================================================

"""
Key Points for Backend Integration:

1. ALWAYS use parameterized queries ($1, $2, etc.) - NEVER string interpolation
2. Use db.execute() for INSERT/UPDATE/DELETE (no return value needed)
3. Use db.fetchrow() for single row SELECT
4. Use db.fetch() for multiple rows SELECT
5. Use db.executemany() for bulk inserts (much faster than loops)
6. Use transactions for multi-step operations that must succeed/fail together
7. Use ON CONFLICT for upserts (avoid SELECT then INSERT/UPDATE)
8. Use json.dumps() to convert Python dicts to JSONB strings
9. Use json.loads() to convert JSONB strings back to Python dicts
10. Always normalize queries (lowercase, strip) for cache consistency

Performance Tips:
- Bulk inserts are ~10x faster than individual inserts
- Indexes make WHERE, ORDER BY, and JOIN operations fast
- JSONB columns are fast and flexible for product arrays
- Connection pooling prevents connection overhead
- Transactions ensure data consistency

Supabase/pgbouncer Compatibility:
- Use statement_cache_size=0 in connection settings
- This is already configured in app/database/postgres.py
"""
