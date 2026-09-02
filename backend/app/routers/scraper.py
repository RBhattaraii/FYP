"""
Scraper Router
Admin endpoints for manual scraping control
"""
from fastapi import APIRouter, HTTPException, Request, status

from app.services.scheduler import trigger_manual_scraping

router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
    responses={404: {"description": "Not found"}},
)


@router.post("/trigger")
async def manual_trigger_scraping(request: Request):
    """
    Manually trigger homepage scraping (Admin only).
    
    This endpoint:
    - Bypasses the 24-hour timer
    - Runs complete scraping workflow immediately
    - Returns scraping results
    
    Use cases:
    - Testing scraping functionality
    - Manual refresh after adding new platforms
    - Emergency data update
    
    **Note:** In production, this should require admin authentication.
    For now, it's open for testing purposes.
    
    Returns:
        Scraping results with status, counts, and timing
    """
    try:
        print("[API] Manual scraping triggered via /scraper/trigger")
        
        # Execute scraping
        result = await trigger_manual_scraping()
        
        if result.get('status') == 'failed':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Scraping failed')
            )
        
        return {
            'status': 'success',
            'message': 'Homepage scraping completed',
            'results': {
                'total_scraped': result.get('total_scraped', 0),
                'platforms_scraped': result.get('platforms_scraped', 0),
                'platforms_failed': result.get('platforms_failed', 0),
                'best_deals_count': result.get('best_deals_count', 0),
                'top_price_drops_count': result.get('top_price_drops_count', 0),
                'saved_to_db': result.get('saved_to_db', 0),
                'scraped_at': result.get('scraped_at')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error in manual trigger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger scraping: {str(e)}"
        )


@router.get("/status")
async def get_scraping_status():
    """
    Get status of last scraping run.
    
    Returns information about:
    - When last scraping occurred
    - When next scraping is scheduled
    - How many products are currently in database
    
    Returns:
        Status information dict
    """
    try:
        from app.database.postgres import pool
        
        if not pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not connected"
            )
        
        async with pool.acquire() as db:
            # Get last scrape metadata
            last_scrape = await db.fetchrow("""
                SELECT last_scrape_time, next_scrape_time, status, products_found
                FROM scrape_metadata
                WHERE scrape_type = $1
                ORDER BY last_scrape_time DESC
                LIMIT 1
            """, 'daily_homepage')
            
            # Count current products in database
            product_counts = await db.fetchrow("""
                SELECT 
                    COUNT(*) FILTER (WHERE section = 'best_deals') as best_deals_count,
                    COUNT(*) FILTER (WHERE section = 'top_price_drops') as top_price_drops_count,
                    COUNT(*) as total_count
                FROM home_screen_products
            """)
            
            if last_scrape:
                return {
                    'last_scrape_time': last_scrape['last_scrape_time'].isoformat() if last_scrape['last_scrape_time'] else None,
                    'next_scrape_time': last_scrape['next_scrape_time'].isoformat() if last_scrape['next_scrape_time'] else None,
                    'last_scrape_status': last_scrape['status'],
                    'last_scrape_products_found': last_scrape['products_found'],
                    'current_products': {
                        'best_deals': product_counts['best_deals_count'],
                        'top_price_drops': product_counts['top_price_drops_count'],
                        'total': product_counts['total_count']
                    }
                }
            else:
                return {
                    'last_scrape_time': None,
                    'next_scrape_time': None,
                    'last_scrape_status': 'never_scraped',
                    'last_scrape_products_found': 0,
                    'current_products': {
                        'best_deals': product_counts['best_deals_count'],
                        'top_price_drops': product_counts['top_price_drops_count'],
                        'total': product_counts['total_count']
                    }
                }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting scraping status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping status"
        )


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: Why have a manual trigger endpoint?
A: Several reasons:
   1. Testing: Test scraping without waiting for midnight
   2. Development: Populate database with test data quickly
   3. Admin control: Manually refresh data if needed
   4. Debugging: Trigger scraping to check if it works
   5. Emergency: Update data outside normal schedule

Q: Should this endpoint be protected?
A: Yes! In production, this should require:
   - Admin JWT token
   - API key
   - IP whitelist
   - Rate limiting (very strict - maybe 1/hour)
   
   For development/testing, it's open but should be secured before deployment.
   
   Example protection:
   ```python
   @router.post("/trigger")
   async def manual_trigger(
       request: Request,
       db: Connection = Depends(get_db),
       current_user = Depends(get_current_admin_user)  # Admin only!
   ):
       ...
   ```

Q: What's the difference between /trigger and scheduled scraping?
A: 
   Scheduled (automatic at midnight):
   - Checks if >24 hours since last scrape
   - Skips if recently scraped
   - Runs automatically without human intervention
   
   Manual trigger (/scraper/trigger):
   - Bypasses 24-hour check
   - Runs immediately regardless of last scrape
   - Requires human action (API call)
   - Good for testing and emergency updates

Q: What does the /status endpoint show?
A: It shows:
   - last_scrape_time: When scraping last ran
   - next_scrape_time: When next scheduled run is
   - last_scrape_status: Success/failed/running
   - last_scrape_products_found: How many products scraped
   - current_products: Current counts in database
   
   This helps:
   - Monitor if scraping is working
   - Debug issues
   - Check data freshness
   - Verify scheduler is running

Q: Why use FILTER in the SQL query?
A: FILTER is PostgreSQL's way to count subsets efficiently:
   
   ```sql
   COUNT(*) FILTER (WHERE section = 'best_deals')
   ```
   
   This counts only rows where section='best_deals' in a single query.
   
   Alternative (less efficient):
   ```sql
   SELECT 
       (SELECT COUNT(*) FROM products WHERE section='best_deals'),
       (SELECT COUNT(*) FROM products WHERE section='top_price_drops')
   ```
   
   FILTER is faster because it scans the table once, not twice.

Q: What if scraping is already running when /trigger is called?
A: Two possibilities:
   1. Current implementation: Second call starts another scrape (might cause issues)
   2. Better implementation: Check if scraping is running, return error if yes
   
   To prevent concurrent scraping:
   ```python
   # Check scrape_metadata for status='running'
   running = await db.fetchrow(
       "SELECT * FROM scrape_metadata WHERE status = 'running'"
   )
   if running:
       raise HTTPException(409, "Scraping already in progress")
   ```

Q: How would you add authentication to this endpoint?
A: Step-by-step:
   1. Create admin check function:
      ```python
      async def get_current_admin(request: Request, db: Connection = Depends(get_db)):
          token = request.headers.get("Authorization")
          user = decode_token_and_get_user(token, db)
          if user['role'] != 'admin':
              raise HTTPException(403, "Admin access required")
          return user
      ```
   
   2. Add to endpoint:
      ```python
      @router.post("/trigger")
      async def trigger(
          admin = Depends(get_current_admin)  # Requires admin!
      ):
          ...
      ```
   
   3. Test:
      - Regular user → 403 Forbidden
      - Admin user → 200 Success

Q: What happens if database is down when /trigger is called?
A: The try-except catches the error and returns:
   ```json
   {
       "detail": "Failed to trigger scraping: connection refused"
   }
   ```
   
   With HTTP status 500 Internal Server Error.
   
   Client should:
   - Show error message to admin
   - Allow retry
   - Log the error for debugging
"""
