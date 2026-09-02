"""
Products Router
API endpoints for home screen products and tiered search
"""
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import List
import asyncpg
import asyncio

from app.database.postgres import get_db
from app.auth.jwt_handler import get_current_user_optional
from app.models.product import (
    Product,
    HomeScreenResponse,
    SearchResponse,
    SearchStatusResponse
)
from app.services.scraper_coordinator import (
    tiered_search,
    get_search_status,
    live_search_and_save
)
from app.limiter import limiter

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


@router.get("/home", response_model=HomeScreenResponse)
async def get_home_screen_products(db: asyncpg.Connection = Depends(get_db)):
    """
    Get curated products for home screen.
    
    Returns two sections:
    - best_deals: Top 25 products with highest discount percentage
    - top_price_drops: Top 25 products with largest price reduction
    
    Products are refreshed daily at midnight.
    """
    try:
        # Get best deals
        best_deals_rows = await db.fetch("""
            SELECT COALESCE(p.id, hsp.id) as id, hsp.title, hsp.price, hsp.original_price, hsp.discount_percent,
                   hsp.image_url, hsp.store_name, hsp.product_url, hsp.category
            FROM home_screen_products hsp
            LEFT JOIN products p ON p.product_url = hsp.product_url
            WHERE hsp.section = $1
            ORDER BY hsp.scraped_at DESC
            LIMIT 25
        """, 'best_deals')
        
        # Get top price drops
        top_price_drops_rows = await db.fetch("""
            SELECT COALESCE(p.id, hsp.id) as id, hsp.title, hsp.price, hsp.original_price, hsp.discount_percent,
                   hsp.image_url, hsp.store_name, hsp.product_url, hsp.category
            FROM home_screen_products hsp
            LEFT JOIN products p ON p.product_url = hsp.product_url
            WHERE hsp.section = $1
            ORDER BY hsp.scraped_at DESC
            LIMIT 25
        """, 'top_price_drops')
        
        # Convert to Product models
        best_deals = [Product(**dict(row)) for row in best_deals_rows]
        top_price_drops = [Product(**dict(row)) for row in top_price_drops_rows]
        
        # Fetch new categories
        tech_gadgets_rows = await db.fetch("""
            SELECT COALESCE(p.id, hsp.id) as id, hsp.title, hsp.price, hsp.original_price, hsp.discount_percent,
                   hsp.image_url, hsp.store_name, hsp.product_url, hsp.category
            FROM home_screen_products hsp
            LEFT JOIN products p ON p.product_url = hsp.product_url
            WHERE hsp.section = $1
            ORDER BY hsp.scraped_at DESC
        """, 'tech_gadgets')
        
        audio_essentials_rows = await db.fetch("""
            SELECT COALESCE(p.id, hsp.id) as id, hsp.title, hsp.price, hsp.original_price, hsp.discount_percent,
                   hsp.image_url, hsp.store_name, hsp.product_url, hsp.category
            FROM home_screen_products hsp
            LEFT JOIN products p ON p.product_url = hsp.product_url
            WHERE hsp.section = $1
            ORDER BY hsp.scraped_at DESC
        """, 'audio_essentials')
        
        home_appliances_rows = await db.fetch("""
            SELECT COALESCE(p.id, hsp.id) as id, hsp.title, hsp.price, hsp.original_price, hsp.discount_percent,
                   hsp.image_url, hsp.store_name, hsp.product_url, hsp.category
            FROM home_screen_products hsp
            LEFT JOIN products p ON p.product_url = hsp.product_url
            WHERE hsp.section = $1
            ORDER BY hsp.scraped_at DESC
        """, 'home_appliances')

        tech_gadgets = [Product(**dict(row)) for row in tech_gadgets_rows]
        audio_essentials = [Product(**dict(row)) for row in audio_essentials_rows]
        home_appliances = [Product(**dict(row)) for row in home_appliances_rows]

        return HomeScreenResponse(
            best_deals=best_deals,
            top_price_drops=top_price_drops,
            tech_gadgets=tech_gadgets,
            audio_essentials=audio_essentials,
            home_appliances=home_appliances
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch home screen products: {e}")
        raise HTTPException(status_code=500, detail="Failed to load home screen products")


@router.get("/search/realtime", response_model=SearchResponse)
@limiter.limit("10/minute")
async def realtime_search_products(
    request: Request,
    q: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Tiered real-time search with progressive results.
    
    This endpoint implements the tiered search strategy:
    1. Checks cache first (returns if valid and complete)
    2. If cache miss:
       - Scrapes ALL platforms simultaneously for best results
       - Returns complete results with is_complete=true
    3. Results are cached for 24 hours
    
    Query Parameters:
    - q: Search query string (required, non-empty)
    
    Rate Limiting:
    - Max 10 searches per minute per IP address
    
    Requirements:
    - FR5: Tiered Real-time Search with Progressive Results
    - NFR1: Response time optimized with caching
    """
    # Validate query parameter (non-empty)
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )
    
    query_str = q.strip()
    
    try:
        # Check cache first and trigger tiered search using coordinator service
        search_result = await tiered_search(db, query_str)
        
        # Get tier1 platform names
        tier1_platforms = search_result.get('tier1_platforms', [])
        
        # Determine message based on cache status and completeness
        from_cache = search_result.get('from_cache', False)
        is_complete = search_result.get('is_complete', False)
        
        if from_cache:
            message = f"Cached results from all platforms ({search_result['results_count']} products)"
        elif is_complete:
            message = f"Fresh results from all platforms ({search_result['results_count']} products)"
        else:
            message = f"Tier 1 results ready. Poll /products/search/status for more results from {len(tier1_platforms)} platforms."
        
        # Apply Entity Resolution grouping
        from app.services.entity_resolution import resolve_entities
        raw_results = search_result.get('results', [])
        resolved_results = resolve_entities(raw_results)
        
        # Convert product dicts to Product models
        products = []
        for p in resolved_results:
            try:
                products.append(Product(**p))
            except Exception as e:
                print(f"[WARN] Failed to convert product to model: {e}")
                continue
        
        return SearchResponse(
            request_id=search_result.get('request_id', 'unknown'),
            query=query_str,
            tier=search_result.get('tier', 1),
            is_complete=is_complete,
            results=products,
            results_count=len(products),
            tier1_platforms=tier1_platforms,
            message=message
        )
        
    except Exception as e:
        print(f"[ERROR] Tiered search failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search", response_model=SearchResponse)
@limiter.limit("10/minute")
async def search_products(
    request: Request,
    q: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Main search endpoint with tiered real-time scraping and progressive results.
    
    **Task 7.1: GET /products/search?q=<query>**
    
    This endpoint implements the tiered search strategy defined in FR5:
    
    Flow:
    1. Validates query parameter (non-empty)
    2. Checks cache first using coordinator service
    3. If cache miss, triggers tiered search:
       - Scrapes ALL platforms simultaneously for comprehensive results
       - Returns complete results with metadata
    4. Returns Tier 1 results with metadata:
       - request_id: Unique identifier for this search
       - is_complete: Whether scraping is done (true for all platforms)
       - tier1_platforms: List of platforms scraped
    5. Includes message for frontend about result status
    6. Rate limited to max 10 searches/minute per IP
    
    Query Parameters:
    - q: Search query string (required, non-empty)
    
    Rate Limiting:
    - Max 10 searches per minute per IP address
    
    Response:
    - Returns SearchResponse with products, metadata, and status
    - Cached results return within <200ms
    - Fresh results complete within <10s (all platforms)
    
    Requirements:
    - FR5: Tiered Real-time Search with Progressive Results
    - NFR1: Performance targets (<2s Tier 1, <10s complete)
    
    Example:
        GET /products/search?q=laptop
        
        Response:
        {
            "request_id": "uuid-xyz",
            "query": "laptop",
            "tier": "all",
            "is_complete": true,
            "results": [...],
            "results_count": 45,
            "tier1_platforms": ["Daraz", "Sastodeal", "Oliz", ...],
            "message": "Found 45 products from all platforms"
        }
    """
    # Validate query parameter (non-empty)
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )
    
    query_str = q.strip()
    
    try:
        # Check cache first and trigger tiered search using coordinator service
        search_result = await tiered_search(db, query_str)
        
        # Get tier1 platform names (all platforms in this implementation)
        tier1_platforms = search_result.get('tier1_platforms', [])
        
        # Determine message based on cache status and completeness
        from_cache = search_result.get('from_cache', False)
        is_complete = search_result.get('is_complete', False)
        
        if from_cache:
            message = f"Cached results from all platforms ({search_result['results_count']} products)"
        elif is_complete:
            message = f"Fresh results from all platforms ({search_result['results_count']} products)"
        else:
            # This shouldn't happen with current implementation, but handle gracefully
            message = f"Results ready. Found {search_result['results_count']} products."
        
        # Apply Entity Resolution grouping
        from app.services.entity_resolution import resolve_entities
        raw_results = search_result.get('results', [])
        resolved_results = resolve_entities(raw_results)
        
        # Convert product dicts to Product models
        products = []
        for p in resolved_results:
            try:
                products.append(Product(**p))
            except Exception as e:
                print(f"[WARN] Failed to convert product to model: {e}")
                continue
        
        return SearchResponse(
            request_id=search_result.get('request_id', 'unknown'),
            query=query_str,
            tier=search_result.get('tier', 'all'),
            is_complete=is_complete,
            results=products,
            results_count=len(products),
            tier1_platforms=tier1_platforms,
            message=message
        )
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search/db", response_model=SearchResponse)
async def search_products_database(
    q: str,
    background_tasks: BackgroundTasks,
    page: int = 1,
    limit: int = 50,
    sort_by: str = 'relevance',
    is_category: bool = False,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Search for products in the pre-scraped global database with pagination.
    
    This is the optimized database search endpoint that searches the pre-scraped
    product database with advanced relevance ranking and pagination.
    
    For real-time scraping with tiered results, use /search instead.
    
    Query Parameters:
    - q: Search query string (required)
    - page: Page number (default: 1)
    - limit: Results per page (default: 50, max: 100)
    - sort_by: Sort order ('relevance', 'price_asc', 'price_desc', 'discount')
    """
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
    # Cap limit for safety
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1
        
    offset = (page - 1) * limit
    
    try:
        query_str = q.strip().lower()
        
        # Synonym expansion for better Korean Beauty Point search results
        synonyms = {
            'facewash': 'cleanser',
            'face wash': 'cleanser',
            'makeup': 'foundation concealer lipstick blush mascara eyeshadow palette',
            'skincare': 'serum cream toner lotion essence ampoule',
            'perfume': 'fragrance scent cologne',
            'lipstick': 'lip tint gloss balm',
        }
        
        # If the query exactly matches a key, append the synonyms to the query string
        # using 'OR' so the full-text search engine matches any of the related words!
        if query_str in synonyms:
            syn_words = synonyms[query_str].split()
            or_clause = ' OR '.join(syn_words)
            query_str = f"{query_str} OR {or_clause}"
        
        # Removed live scraper background task to prevent hangs and strictly use offline data
        
        where_clause = """
                (
                    p.search_vector @@ websearch_to_tsquery('english', $1)
                    OR p.title ILIKE '%' || $1 || '%'
                    OR p.title % $1
                    OR p.category ILIKE '%' || $1 || '%'
                )
        """
        if is_category:
            where_clause = "p.category ILIKE '%' || $1 || '%'"
            
        # Complex CTE for relevance ranking and grouping
        sql_base = f"""
        WITH search_context AS (
            SELECT 
                $1::text AS raw_query,
                lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_query,
                string_to_array(lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ') AS tokens
        ),
        scored_products AS (
            SELECT 
                p.id, p.title, p.price, p.original_price, p.discount_percent,
                p.image_url, p.store_name, p.product_url, p.category,
                lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_title,
                (
                    -- 1. Exact match (+100)
                    CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) = (SELECT clean_query FROM search_context) THEN 100 ELSE 0 END
                    
                    -- 2. Starts with query (+80)
                    + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE (SELECT clean_query FROM search_context) || '%' THEN 80 ELSE 0 END
                    
                    -- 3. Contains entire query (+60)
                    + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE '%' || (SELECT clean_query FROM search_context) || '%' THEN 60 ELSE 0 END
                    
                    -- 4. Contains all keywords / full text search (+40)
                    + CASE WHEN p.search_vector @@ websearch_to_tsquery('english', $1) THEN 40 ELSE 0 END
                    
                    -- 5. Brand match (+20) (first token matches first word of title)
                    + CASE WHEN split_part(lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ', 1) = (SELECT tokens[1] FROM search_context) THEN 20 ELSE 0 END
                    
                    -- 5.5. Complete laptop product boost (+150) when searching for "laptop"
                    + CASE WHEN 
                        (SELECT clean_query FROM search_context) = 'laptop'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(pavilion|inspiron|thinkpad|vivobook|ideapad|aspire|zenbook|elitebook|macbook)\\y'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) !~ '\\y(battery|backpack|bag|case|cover|charger|adapter|cable|stand|table|desk|speaker|webcam|internal|external|component|part|accessory|fan|cooling|sleeve|screw|repair|tool)\\y'
                      THEN 150 ELSE 0 END
                      
                    -- 5.6. Computer model boost (+100) for actual computer products 
                    + CASE WHEN 
                        lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(hp|dell|lenovo|asus|acer|apple)\\s+(pavilion|inspiron|thinkpad|vivobook|ideapad|aspire|zenbook|elitebook|macbook)'
                        OR lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(intel|amd|ryzen|core)\\s+(i[3-9]|[3-9][0-9]{3}[a-z]?)'
                      THEN 100 ELSE 0 END
                    
                    -- 6. Heavy accessory penalty (-500) if query doesn't contain accessory words, but product does
                    - CASE WHEN 
                        (SELECT clean_query FROM search_context) !~ '\\y(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens|bag|pouch|sleeve|fan|cooling|table|desk|speaker|webcam|internal|external|component|part|accessory|battery|backpack|screw|repair|tool)\\y'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens|bag|pouch|sleeve|fan|cooling|table|desk|speaker|webcam|internal|external|component|part|accessory|battery|backpack|screw|repair|tool)\\y'
                      THEN 500 ELSE 0 END
                      
                    -- 7. Fuzzy score (+ up to 10)
                    + (similarity((SELECT raw_query FROM search_context), p.title) * 10)
                    
                    -- 8. Category match (+80)
                    + CASE WHEN p.category ILIKE '%' || (SELECT raw_query FROM search_context) || '%' THEN 80 ELSE 0 END
                ) AS relevance_score
            FROM products p
            WHERE 
                {where_clause}
        ),
        filtered_scored_products AS (
            SELECT *
            FROM scored_products
            WHERE relevance_score > -1000  -- Allow all products to show, even heavily penalized ones, so no data is hidden
        ),
        grouped_products AS (
            SELECT 
                clean_title,
                store_name,
                MAX(relevance_score) as best_score,
                MIN(price) as best_price,
                1 as store_count,
                (array_agg(id ORDER BY price ASC))[1] as best_id
            FROM filtered_scored_products
            GROUP BY clean_title, store_name
        )
        """
        
        # 1. Get total count for pagination
        count_sql = sql_base + " SELECT COUNT(*) as total FROM grouped_products"
        count_row = await db.fetchrow(count_sql, query_str)
        
        total_results = count_row['total'] if count_row else 0
        total_pages = (total_results + limit - 1) // limit if total_results > 0 else 1
        
        # If this is a category search and we found NO products offline, 
        # trigger a background Daraz scrape for this category so next time it works!
        if total_results == 0 and is_category:
            background_tasks.add_task(live_search_and_save, query_str, "Daraz")
        
        # 2. Get paginated results with dynamic sorting
        
        order_clause = "ORDER BY gp.best_score DESC, gp.best_price ASC"
        if sort_by == 'price_asc':
            order_clause = "ORDER BY gp.best_price ASC, gp.best_score DESC"
        elif sort_by == 'price_desc':
            order_clause = "ORDER BY gp.best_price DESC, gp.best_score DESC"
        elif sort_by == 'discount':
            order_clause = "ORDER BY p.discount_percent DESC NULLS LAST, gp.best_score DESC"

        data_sql = sql_base + f"""
        SELECT 
            p.id, p.title, gp.best_price as price, p.original_price, p.discount_percent,
            p.image_url, p.store_name, p.product_url, p.category, gp.store_count, gp.best_score
        FROM grouped_products gp
        JOIN products p ON p.id = gp.best_id
        {order_clause}
        LIMIT $2 OFFSET $3
        """
        
        rows = await db.fetch(data_sql, query_str, limit, offset)
        
        products = [Product(**dict(row)) for row in rows]
        import uuid
        import asyncio
        from app.services.scraper_coordinator import scrape_daraz_background
        from datetime import datetime, timezone
        import json
        
        request_id = str(uuid.uuid4())
        is_complete = True
        
        if page == 1:
            now = datetime.now(timezone.utc)
            from datetime import timedelta
            
            # Check if we already scraped Daraz for this query in the last 24 hours
            recent_cache = await db.fetchrow("""
                SELECT tier2_cached_at, is_complete
                FROM search_cache
                WHERE query = $1 AND tier2_cached_at > $2
            """, query_str, now - timedelta(hours=24))
            
            if recent_cache and recent_cache['is_complete']:
                # Already scraped Daraz recently, no need to scrape again
                # The Daraz products are already in the 'products' table and included in the DB results above
                is_complete = True
            else:
                is_complete = False
                empty_json = json.dumps([])
                
                # Initialize search_cache row for polling (use ON CONFLICT to avoid unique constraint errors during pagination)
                await db.execute("""
                    INSERT INTO search_cache 
                    (query, tier1_results, tier1_cached_at, tier2_results, tier2_cached_at, is_complete, request_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (query) DO UPDATE
                    SET tier2_results = EXCLUDED.tier2_results,
                        tier2_cached_at = EXCLUDED.tier2_cached_at,
                        is_complete = EXCLUDED.is_complete,
                        request_id = EXCLUDED.request_id
                """, query_str, empty_json, now, empty_json, now, False, request_id)
                
                # Spawn background Daraz scraping
                from app.database import postgres
                asyncio.create_task(scrape_daraz_background(postgres.pool, query_str, request_id))
        
        return SearchResponse(
            request_id=request_id if page == 1 and not is_complete else "db-search",
            query=query_str,
            tier="db",
            is_complete=is_complete,  # False only on first page to trigger frontend polling
            results=products,
            results_count=len(products),
            tier1_platforms=[],
            message=f"Found {total_results} total products. Checking Daraz for live results...",
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_results=total_results
        )
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product_detail(
    product_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional)  # Optional authentication
):
    """
    Get detailed information for a specific product by ID or compound string ID.
    
    Automatically adds the product to user's history if user is logged in.
    """
    try:
        product_row = None
        real_product_id = None
        
        if product_id.isdigit():
            real_product_id = int(product_id)
            # Query product from products table (search database)
            product_row = await db.fetchrow("""
                SELECT id, title, price, original_price, discount_percent,
                       image_url, store_name, product_url, category
                FROM products
                WHERE id = $1
            """, real_product_id)
        else:
            # Compound ID (store_name-product_url)
            parts = product_id.split("-", 1)
            if len(parts) == 2:
                store_name, product_url = parts
                product_row = await db.fetchrow("""
                    SELECT id, title, price, original_price, discount_percent,
                           image_url, store_name, product_url, category
                    FROM products
                    WHERE product_url = $1 LIMIT 1
                """, product_url)
                if product_row:
                    real_product_id = product_row['id']
                    
        if not product_row or real_product_id is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Product with ID {product_id} not found"
            )
        
        # Convert to Product model
        product = Product(**dict(product_row))
        
        # Add to user history if user is logged in
        try:
            if current_user:
                user_id = current_user["user_id"]
                await db.execute("""
                    INSERT INTO user_history (
                        user_id, product_id, product_title, product_price,
                        product_image_url, product_url, store_name, category, viewed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                    ON CONFLICT (user_id, product_id) 
                    DO UPDATE SET viewed_at = NOW()
                """, 
                    user_id, real_product_id, product.title, product.price,
                    product.image_url, product.product_url, product.store_name, product.category
                )
        except Exception as e:
            print(f"Failed to record history: {e}")
            pass # Ignore history recording errors
            
        return product
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch product {product_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to load product details"
        )


@router.get("/search/status", response_model=SearchStatusResponse)
async def get_search_status_endpoint(
    query: str,
    request_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Poll for additional search results from Tier 2 platforms.
    
    **Task 7.2: GET /products/search/status?query=<query>&request_id=<id>**
    
    This endpoint supports progressive loading for tiered search by allowing
    the frontend to poll for Tier 2 results after receiving Tier 1 results.
    
    Query Parameters:
    - query: Original search query string (required)
    - request_id: Unique request ID from initial search response (required)
    
    Response:
    - is_complete: Boolean indicating if all platforms finished scraping
    - new_results: Array of products from Tier 2 platforms (if available)
    - new_results_count: Count of new results from Tier 2
    - message: Status message about scraping progress
    
    Performance:
    - Target response time: <100ms
    - Optimized with database indexes on request_id
    
    Frontend Usage:
    1. After receiving Tier 1 results from /products/search, check is_complete
    2. If not complete, poll this endpoint every 2 seconds
    3. Display new results as they arrive
    4. Stop polling when is_complete=true or after max 6 polls (12 seconds)
    
    Requirements:
    - FR5a: Progressive Search Results Polling
    - NFR1: Response time <100ms
    
    Example:
        GET /products/search/status?query=laptop&request_id=uuid-xyz
        
        Response (in progress):
        {
            "request_id": "uuid-xyz",
            "is_complete": false,
            "new_results_count": 0,
            "new_results": [],
            "message": "Tier 2 scraping in progress..."
        }
        
        Response (complete):
        {
            "request_id": "uuid-xyz",
            "is_complete": true,
            "new_results_count": 45,
            "new_results": [...],
            "message": "Tier 2 scraping complete"
        }
    """
    try:
        # Call the coordinator service to get search status
        # This queries search_cache by request_id
        status_result = await get_search_status(db, request_id)
        
        # Convert product dicts to Product models
        new_results_products = []
        for p in status_result.get('new_results', []):
            try:
                new_results_products.append(Product(**p))
            except Exception as e:
                print(f"[WARN] Failed to convert product to model: {e}")
                continue
        
        return SearchStatusResponse(
            request_id=request_id,
            is_complete=status_result.get('is_complete', False),
            new_results_count=status_result.get('new_results_count', 0),
            new_results=new_results_products,
            message=status_result.get('message', 'Status check complete')
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to get search status: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get search status: {str(e)}"
        )


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: Why separate /products/search and /products/search/status endpoints?
A: This implements progressive loading for better UX:
   - /products/search returns fast results immediately (Tier 1)
   - /products/search/status lets frontend poll for additional results (Tier 2)
   - User sees results in 2 seconds instead of waiting 10+ seconds

Q: What is BackgroundTasks in FastAPI?
A: BackgroundTasks allows running functions after returning the response.
   We use it to start Tier 2 scraping after sending Tier 1 results to user.
   The user doesn't wait for Tier 2 - they can see Tier 1 immediately.

Q: Why use Depends(get_db) in endpoints?
A: Depends is FastAPI's dependency injection system. get_db() provides
   a database connection from the connection pool. FastAPI automatically:
   1. Calls get_db() before the endpoint function
   2. Passes the connection to our endpoint
   3. Returns the connection to the pool after the request

Q: How does the tiered search improve performance?
A: Instead of waiting for all 11 platforms (10+ seconds), we:
   1. Scrape 3 fast platforms first (2 seconds) → show results
   2. Scrape 8 slower platforms in background (8 more seconds)
   3. User sees results immediately and can start browsing
   4. More results appear progressively as user scrolls

Q: What happens if Tier 2 scraping fails?
A: User still has Tier 1 results (3 platforms). The cache won't be marked
   complete, so next search will retry. Tier 2 failures don't affect UX
   because user already has results to browse.

Q: Why store results in both cache and return them?
A: Cache is for subsequent searches (same query within 24 hours).
   First search: scrape → return → cache for next time
   Second search (same query): return from cache instantly (<200ms)
"""
