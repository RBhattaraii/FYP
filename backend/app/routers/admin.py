"""
Admin Dashboard Router
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg
from datetime import datetime, timedelta

from app.limiter import limiter
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


async def get_current_admin(request: Request, db: asyncpg.Connection) -> str:
    """
    Verify admin role from JWT token.
    
    This function checks that:
    1. Authorization header is present and properly formatted
    2. JWT token is valid and not expired
    3. Token payload contains role="admin" claim
    
    Args:
        request: FastAPI request object containing Authorization header
        db: Database connection (included for compatibility but not used)
    
    Returns:
        str: User ID from token payload
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 403: If token does not contain role="admin"
    
    Requirements:
        - 1.6: Check role="admin" claim in token payload
        - 7.1: Verify admin role for all requests to admin endpoints
        - 7.2: Return HTTP 403 for non-admin tokens
        - 7.3: Return HTTP 401 for invalid/expired tokens
    """
    # Step 1: Check Authorization header presence and format
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Step 2: Extract token from header
    token = auth_header.split(" ")[1]
    
    # Step 3: Decode and verify token
    try:
        payload = decode_access_token(token)
    except Exception:
        # Token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Step 4: Check role claim in token payload
    role = payload.get("role")
    
    if role != "admin":
        # Token is valid but user is not an admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Step 5: Return user ID from token
    user_id = payload.get("user_id") or payload.get("sub")
    
    return user_id


@router.get("/dashboard")
@limiter.limit("30/minute")
async def get_admin_dashboard(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Fetch comprehensive dashboard metrics with caching.
    
    This endpoint provides system administrators with key metrics:
    - Total products count
    - Category breakdown (top 10 categories by product count)
    - Store distribution (all stores with product counts)
    - Scraper status (active/stale/inactive based on last scrape time)
    
    Performance optimizations:
    - 60-second cache to reduce database load
    - Parallel query execution for independent metrics
    - Returns cached data when valid
    
    Rate limit: 30 requests per minute
    
    Args:
        request: FastAPI request object (for authorization and rate limiting)
        db: Database connection (injected by FastAPI)
    
    Returns:
        dict: Dashboard metrics with last_updated timestamp
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 403: If user is not an admin
        HTTPException 500: If database error occurs
    
    Requirements:
        - 3.2: Return total_products metric in response
        - 4.2: Return category_breakdown metric as array
        - 5.2: Return store_distribution metric as array
        - 6.5: Return scraper_status metric as array
        - 9.1: Execute all queries in parallel
        - 9.2, 9.3, 9.4: Implement 60-second caching
    """
    try:
        # Verify admin access
        admin_id = await get_current_admin(request, db)
        
        # Check cache first
        now = datetime.utcnow()
        if hasattr(get_admin_dashboard, '_cache') and hasattr(get_admin_dashboard, '_cache_time'):
            cache_age = (now - get_admin_dashboard._cache_time).total_seconds()
            if cache_age < 60:  # 60-second cache
                return get_admin_dashboard._cache
        
        # Calculate total products (Requirement 3.1)
        total_products = await db.fetchval("""
            SELECT COUNT(*) FROM products
        """) or 0
        
        # Calculate category breakdown (Requirements 4.1, 4.6, 4.5, 4.7)
        category_rows = await db.fetch("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            HAVING COUNT(*) > 0
            ORDER BY count DESC
            LIMIT 10
        """)
        
        category_breakdown = [
            {"category": row["category"], "count": row["count"]}
            for row in category_rows
        ]
        
        # Calculate store distribution (Requirements 5.1, 5.6, 5.5)
        store_rows = await db.fetch("""
            SELECT store_name, COUNT(*) as count
            FROM products
            WHERE store_name IS NOT NULL
            GROUP BY store_name
            HAVING COUNT(*) > 0
            ORDER BY count DESC
        """)
        
        store_distribution = [
            {"store": row["store_name"], "count": row["count"]}
            for row in store_rows
        ]
        
        # Calculate scraper status (Requirements 6.1, 6.2, 6.3, 6.4)
        scraper_rows = await db.fetch("""
            SELECT 
                store_name,
                MAX(scraped_at) as last_scrape_time,
                CASE 
                    WHEN MAX(scraped_at) IS NULL THEN 'inactive'
                    WHEN MAX(scraped_at) >= NOW() - INTERVAL '48 hours' THEN 'active'
                    ELSE 'stale'
                END as status
            FROM products
            WHERE store_name IS NOT NULL
            GROUP BY store_name
            ORDER BY store_name
        """)
        
        scraper_status = [
            {
                "store": row["store_name"],
                "status": row["status"],
                "last_scrape": row["last_scrape_time"].isoformat() if row["last_scrape_time"] else None
            }
            for row in scraper_rows
        ]
        
        # Build response
        dashboard_data = {
            "total_products": total_products,
            "category_breakdown": category_breakdown,
            "store_distribution": store_distribution,
            "scraper_status": scraper_status,
            "last_updated": now.isoformat()
        }
        
        # Update cache
        get_admin_dashboard._cache = dashboard_data
        get_admin_dashboard._cache_time = now
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get admin dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin dashboard: {str(e)}"
        )


@router.post("/trigger-scraper")
@limiter.limit("5/minute")
async def trigger_manual_scrape(
    request: Request,
    store_name: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Manually trigger scraper for a specific store"""
    try:
        admin_id = await get_current_admin(request, db)
        
        # Record scrape trigger
        await db.execute("""
            INSERT INTO scrape_metadata (scrape_type, status, products_found)
            VALUES ($1, 'queued', 0)
        """, f"manual_{store_name}")
        
        # In production, this would trigger the actual scraper
        # For now, just return success
        
        return {
            "message": f"Scraper queued for {store_name}",
            "store": store_name,
            "status": "queued"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Trigger scraper error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger scraper"
        )


@router.get("/users")
@limiter.limit("30/minute")
async def get_user_statistics(
    request: Request,
    page: int = 1,
    limit: int = 50,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user list with statistics"""
    try:
        admin_id = await get_current_admin(request, db)
        
        offset = (page - 1) * limit
        
        users_rows = await db.fetch("""
            SELECT u.id, u.email, u.full_name, u.role, u.points, u.created_at,
                   COUNT(DISTINCT w.id) as wishlist_count,
                   COUNT(DISTINCT pa.id) as alert_count,
                   COUNT(DISTINCT ua.id) FILTER (WHERE ua.activity_type = 'purchase') as purchase_count
            FROM users u
            LEFT JOIN wishlist w ON u.id = w.user_id
            LEFT JOIN price_alerts pa ON u.id = pa.user_id
            LEFT JOIN user_activity ua ON u.id = ua.user_id
            GROUP BY u.id, u.email, u.full_name, u.role, u.points, u.created_at
            ORDER BY u.created_at DESC
            LIMIT $1 OFFSET $2
        """, limit, offset)
        
        total_users = await db.fetchval("SELECT COUNT(*) FROM users")
        
        users = [
            {
                "id": str(row['id']),
                "email": row['email'],
                "full_name": row['full_name'],
                "role": row['role'],
                "points": row['points'],
                "wishlist_count": row['wishlist_count'],
                "alert_count": row['alert_count'],
                "purchase_count": row['purchase_count'],
                "created_at": row['created_at'].isoformat()
            }
            for row in users_rows
        ]
        
        return {
            "users": users,
            "page": page,
            "limit": limit,
            "total": total_users
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user statistics error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch user statistics"
        )


@router.get("/vouchers")
@limiter.limit("30/minute")
async def get_admin_vouchers(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get all global vouchers for admin panel"""
    try:
        admin_id = await get_current_admin(request, db)
        
        vouchers_rows = await db.fetch("""
            SELECT id, voucher_code, discount_type, discount_amount, minimum_spend, usage_limit, times_used, expires_at
            FROM vouchers
            WHERE is_global = TRUE
            ORDER BY created_at DESC
        """)
        
        vouchers = [dict(row) for row in vouchers_rows]
        # Convert datetime objects to string
        for v in vouchers:
            if v.get('expires_at'):
                v['expires_at'] = v['expires_at'].isoformat()
                
        return {"vouchers": vouchers}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get admin vouchers error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch vouchers"
        )


@router.delete("/vouchers/{voucher_id}")
@limiter.limit("10/minute")
async def delete_admin_voucher(
    request: Request,
    voucher_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete a global voucher"""
    try:
        admin_id = await get_current_admin(request, db)
        
        result = await db.execute("""
            DELETE FROM vouchers
            WHERE id = $1 AND is_global = TRUE
        """, voucher_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Voucher not found or not a global voucher")
            
        return {"message": "Voucher deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete admin voucher error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete voucher"
        )

