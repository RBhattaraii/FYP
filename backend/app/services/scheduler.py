"""
Background Scheduler Service
Handles daily homepage scraping at midnight using APScheduler
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
import asyncio
import asyncpg

from app.database.postgres import pool
from app.services.scraper_coordinator import execute_daily_homepage_scraping, cleanup_expired_cache
from app.services.alerts_worker import check_price_alerts_job

# Global scheduler instance
scheduler = None


async def daily_homepage_scraping_job():
    """
    Job that runs daily at midnight to scrape homepage and curate products.
    
    This function:
    1. Gets a database connection from the pool
    2. Checks if scraping is needed (>24 hours since last scrape)
    3. Executes the complete scraping workflow
    4. Logs results
    """
    print(f"[SCHEDULER] Daily homepage scraping job triggered at {datetime.now(timezone.utc)}")
    
    try:
        # Import pool dynamically to get the current value (not the None at module load time)
        from app.database.postgres import pool as db_pool
        
        # Get database connection from pool
        if not db_pool:
            print("[SCHEDULER] ERROR: Database pool not initialized")
            return
        
        async with db_pool.acquire() as db:
            # Check if scraping is needed
            last_scrape = await db.fetchrow("""
                SELECT last_scrape_time
                FROM scrape_metadata
                WHERE scrape_type = $1
                ORDER BY last_scrape_time DESC
                LIMIT 1
            """, 'daily_homepage')
            
            if last_scrape and last_scrape['last_scrape_time']:
                time_since_last = datetime.now(timezone.utc) - last_scrape['last_scrape_time']
                hours_since_last = time_since_last.total_seconds() / 3600
                
                if hours_since_last < 24:
                    print(f"[SCHEDULER] Skipping scrape - last scrape was {hours_since_last:.1f} hours ago")
                    return
            
            # Execute daily scraping workflow
            print("[SCHEDULER] Starting daily homepage scraping...")
            result = await execute_daily_homepage_scraping(db)
            
            print(f"[SCHEDULER] Scraping complete!")
            print(f"  Status: {result.get('status')}")
            print(f"  Total scraped: {result.get('total_scraped', 0)}")
            print(f"  Platforms scraped: {result.get('platforms_scraped', 0)}/{result.get('total_platforms', 0)}")
            print(f"  Best deals: {result.get('best_deals_count', 0)}")
            print(f"  Top price drops: {result.get('top_price_drops_count', 0)}")
            print(f"  Saved to DB: {result.get('saved_to_db', 0)}")
            
    except Exception as e:
        print(f"[SCHEDULER] ERROR during daily scraping: {e}")
        import traceback
        traceback.print_exc()


async def cache_cleanup_job():
    """
    Job that runs daily at 1:00 AM to clean up expired cache entries.
    
    Removes search_cache entries older than 24 hours to keep database clean.
    """
    print(f"[SCHEDULER] Cache cleanup job triggered at {datetime.now(timezone.utc)}")
    
    try:
        # Import pool dynamically to get the current value
        from app.database.postgres import pool as db_pool
        
        # Get database connection from pool
        if not db_pool:
            print("[SCHEDULER] ERROR: Database pool not initialized")
            return
        
        async with db_pool.acquire() as db:
            deleted_count = await cleanup_expired_cache(db)
            print(f"[SCHEDULER] Cache cleanup complete - deleted {deleted_count} entries")
            
    except Exception as e:
        print(f"[SCHEDULER] ERROR during cache cleanup: {e}")


def start_scheduler():
    """
    Start the background scheduler with all scheduled jobs.
    
    Jobs:
    - Daily homepage scraping: Runs at midnight (00:00) every day
    - Cache cleanup: Runs at 1:00 AM every day
    
    This function should be called once when the FastAPI app starts.
    """
    global scheduler
    
    if scheduler is not None:
        print("[SCHEDULER] Scheduler already running")
        return scheduler
    
    # Create AsyncIOScheduler (works with FastAPI's async event loop)
    scheduler = AsyncIOScheduler()
    
    # Job 1: Daily homepage scraping at midnight
    scheduler.add_job(
        daily_homepage_scraping_job,
        trigger=CronTrigger(hour=0, minute=0),  # Every day at 00:00
        id='daily_homepage_scraping',
        name='Daily Homepage Scraping',
        replace_existing=True
    )
    print("[SCHEDULER] Added job: Daily homepage scraping (00:00)")
    
    # Job 2: Cache cleanup at 1:00 AM
    scheduler.add_job(
        cache_cleanup_job,
        trigger=CronTrigger(hour=1, minute=0),  # Every day at 01:00
        id='cache_cleanup',
        name='Cache Cleanup',
        replace_existing=True
    )
    print("[SCHEDULER] Added job: Cache cleanup (01:00)")
    
    # Job 3: Price alert checking every hour
    scheduler.add_job(
        check_price_alerts_job,
        trigger=CronTrigger(hour='*/1'),  # Every hour
        id='check_price_alerts',
        name='Check Price Alerts',
        replace_existing=True
    )
    print("[SCHEDULER] Added job: Check price alerts (hourly)")
    
    # Start the scheduler
    scheduler.start()
    print("[SCHEDULER] Scheduler started successfully")
    print(f"[SCHEDULER] Next scraping run: {scheduler.get_job('daily_homepage_scraping').next_run_time}")
    
    return scheduler


def stop_scheduler():
    """
    Stop the background scheduler.
    
    This function should be called when the FastAPI app shuts down
    to properly stop all scheduled jobs.
    """
    global scheduler
    
    if scheduler is None:
        print("[SCHEDULER] Scheduler not running")
        return
    
    scheduler.shutdown(wait=True)
    print("[SCHEDULER] Scheduler stopped")
    scheduler = None


async def trigger_manual_scraping():
    """
    Manually trigger homepage scraping (for testing or admin endpoint).
    
    This bypasses the 24-hour check and runs scraping immediately.
    
    Returns:
        Dict with scraping results
    """
    print(f"[SCHEDULER] Manual scraping triggered at {datetime.now(timezone.utc)}")
    
    try:
        # Import pool dynamically to get the current value (not the None at module load time)
        from app.database.postgres import pool as db_pool
        
        if not db_pool:
            return {
                'status': 'failed',
                'error': 'Database pool not initialized'
            }
        
        async with db_pool.acquire() as db:
            result = await execute_daily_homepage_scraping(db)
            return result
            
    except Exception as e:
        print(f"[SCHEDULER] ERROR during manual scraping: {e}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is APScheduler?
A: APScheduler (Advanced Python Scheduler) is a library that lets you schedule
   Python functions to run at specific times or intervals.
   
   Like a cron job on Linux, but inside your Python application.
   
   We use it to:
   - Run homepage scraping every day at midnight (00:00)
   - Run cache cleanup every day at 1:00 AM
   
   Benefits over cron:
   - Works on Windows (cron doesn't)
   - Integrated with FastAPI's event loop
   - Easier to test and debug
   - Can trigger jobs manually

Q: What is AsyncIOScheduler?
A: AsyncIOScheduler is the async version of APScheduler that works with
   Python's asyncio event loop.
   
   FastAPI uses asyncio for async/await functions, so we need:
   - AsyncIOScheduler (not BackgroundScheduler)
   - Async job functions (async def)
   - Async database operations (await db.execute)
   
   The scheduler runs in the same event loop as FastAPI, so they can
   share the database connection pool and other resources.

Q: What is CronTrigger?
A: CronTrigger defines when a job should run using cron-like syntax.
   
   Examples:
   - CronTrigger(hour=0, minute=0) → Every day at midnight (00:00)
   - CronTrigger(hour=1, minute=0) → Every day at 1:00 AM
   - CronTrigger(hour=12, minute=30) → Every day at 12:30 PM
   - CronTrigger(day_of_week='mon', hour=9) → Every Monday at 9:00 AM
   
   Parameters:
   - year, month, day, week, day_of_week
   - hour, minute, second
   - Can use ranges: hour='9-17' (9 AM to 5 PM)
   - Can use intervals: minute='*/15' (every 15 minutes)

Q: Why check last_scrape_time before scraping?
A: To prevent duplicate scraping if:
   - Server restarts and scheduler runs again
   - Manual trigger was used recently
   - Multiple instances running (in production)
   
   We only scrape if >24 hours since last scrape, even if scheduler
   triggers multiple times.

Q: How does the scheduler integrate with FastAPI?
A: FastAPI provides startup and shutdown events:
   
   @app.on_event("startup")
   async def startup():
       start_scheduler()  # Start scheduler when app starts
   
   @app.on_event("shutdown")
   async def shutdown():
       stop_scheduler()  # Stop scheduler when app stops
   
   This ensures:
   - Scheduler starts automatically when server starts
   - Scheduler stops cleanly when server stops
   - No orphaned scheduler processes

Q: Why use pool.acquire() instead of Depends(get_db)?
A: Depends(get_db) only works in FastAPI route handlers.
   
   In scheduler jobs (running in background), we need to:
   1. Get the global connection pool
   2. Manually acquire a connection: async with pool.acquire() as db
   3. Use the connection
   4. Connection automatically returned to pool
   
   This is the same pattern as Depends(get_db), but done manually.

Q: What happens if a job fails?
A: APScheduler catches exceptions and logs them, but:
   - The scheduler keeps running
   - Other jobs are not affected
   - Next scheduled run still happens
   
   We wrap our job code in try-except to:
   - Log detailed errors
   - Continue running scheduler
   - Allow manual retry via admin endpoint

Q: Can jobs overlap?
A: By default, no. APScheduler ensures a job doesn't run if:
   - Previous run is still executing
   - This prevents duplicate scraping
   
   If scraping takes >24 hours (unlikely), the next run waits.
   
   You can configure this with:
   - max_instances: Number of concurrent instances allowed
   - coalesce: Whether to run missed jobs
   - misfire_grace_time: How long to wait for a missed job

Q: How to test the scheduler without waiting for midnight?
A: Use the manual trigger function:
   
   POST /scraper/trigger endpoint calls trigger_manual_scraping()
   
   This bypasses the schedule and runs scraping immediately.
   Good for:
   - Testing
   - Admin manual refresh
   - After adding new platforms
"""
