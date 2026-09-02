"""
Price Alert Worker Service
Queries active price alerts, scrapes current product prices using Playwright coordinators,
creates user notifications, and updates trigger states.
"""
import asyncpg

async def check_price_alerts_job() -> dict:
    """
    Check all active price alerts against the current product prices.
    If the current price is less than or equal to the target price,
    create a notification and mark the alert as inactive.
    """
    print("[ALERT-WORKER] Checking price alerts...")
    
    from app.database.postgres import pool as db_pool
    from app.services.realtime_scraper import scrape_product_on_view
    
    if not db_pool:
        print("[ALERT-WORKER] ERROR: Database pool not initialized")
        return {
            "status": "failed",
            "error": "Database pool not initialized"
        }
        
    try:
        async with db_pool.acquire() as db:
            # Get all active alerts
            alerts = await db.fetch("""
                SELECT id, user_id, product_id, product_title, target_price, current_price, store_name, product_url
                FROM price_alerts
                WHERE is_active = TRUE
            """)
            
            if not alerts:
                print("[ALERT-WORKER] No active price alerts to check.")
                return {
                    "status": "success",
                    "checked": 0,
                    "triggered": 0
                }
                
            checked_count = 0
            triggered_count = 0
            
            for alert in alerts:
                alert_id = alert['id']
                product_id = alert['product_id']
                user_id = alert['user_id']
                target_price = alert['target_price']
                product_title = alert['product_title']
                store_name = alert['store_name']
                product_url = alert['product_url']
                
                # Check live price by triggering the scrape
                # (This updates the products table and writes price_history)
                if product_url:
                    try:
                        await scrape_product_on_view(db, product_id)
                    except Exception as scrape_err:
                        print(f"[ALERT-WORKER] Scrape failed for product {product_id} during alert check: {scrape_err}")
                
                # Get the updated product price from DB
                current_price = await db.fetchval("""
                    SELECT price FROM products WHERE id = $1
                """, product_id)
                
                if current_price is None:
                    current_price = alert['current_price']
                
                checked_count += 1
                
                # Compare new price with target price
                if float(current_price) <= float(target_price):
                    # Create notification
                    await db.execute("""
                        INSERT INTO notifications (user_id, notification_type, title, message, product_id, is_read, created_at)
                        VALUES ($1, 'price_drop', $2, $3, $4, FALSE, NOW())
                    """, 
                        user_id, 
                        f"Price Drop Alert: {product_title}",
                        f"Great news! The price of {product_title} has dropped to Rs {current_price} (your target was: Rs {target_price}) at {store_name}.",
                        product_id
                    )
                    
                    # Update alert status
                    await db.execute("""
                        UPDATE price_alerts
                        SET is_active = FALSE, triggered_at = NOW(), current_price = $1
                        WHERE id = $2
                    """, current_price, alert_id)
                    
                    triggered_count += 1
                    print(f"[ALERT-WORKER] Alert TRIGGERED for '{product_title}' (ID: {product_id}). Price dropped to Rs {current_price}.")
                    
            print(f"[ALERT-WORKER] Alert check completed. Checked: {checked_count}, Triggered: {triggered_count}")
            return {
                "status": "success",
                "checked": checked_count,
                "triggered": triggered_count
            }
            
    except Exception as e:
        print(f"[ALERT-WORKER] ERROR checking price alerts: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
