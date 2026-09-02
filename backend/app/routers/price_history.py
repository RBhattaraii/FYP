"""
Price History Router - Track product prices over time
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import asyncpg
from typing import List
from datetime import datetime

from app.database.postgres import get_db
from app.services.realtime_scraper import scrape_product_on_view
from app.services.forecasting import generate_price_forecast

router = APIRouter(
    prefix="/price-history",
    tags=["Price History"]
)


@router.post("/scrape/{product_id}")
async def trigger_realtime_scrape(
    product_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Manually trigger real-time scraping for a specific product
    
    This endpoint:
    1. Scrapes the product page immediately 
    2. Updates price if changed
    3. Records price history entry
    4. Returns scraping results
    
    Use when user wants to check current price manually
    """
    try:
        result = await scrape_product_on_view(db, product_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        elif result['status'] == 'not_found':
            raise HTTPException(status_code=404, detail=result['message'])
        elif result['status'] == 'no_url':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return {
            'status': 'success',
            'product_id': product_id,
            'message': result['message'],
            'price_changed': result['price_changed'],
            'scraped_at': datetime.now().isoformat(),
            **{k: v for k, v in result.items() if k not in ['status', 'message', 'price_changed']}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Manual scrape error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape product: {str(e)}"
        )


@router.get("/{product_id}")
async def get_price_history(
    product_id: int,
    days: int = 60,
    db: asyncpg.Connection = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Get price history for a product (default: last 60 days)
    
    This endpoint now includes real-time price checking:
    1. Triggers background scraping of the product page
    2. Updates price if it has changed
    3. Returns historical price data with any new updates
    
    Parameters:
    - product_id: Product ID
    - days: Number of days to look back (default: 60, max: 365)
    """
    try:
        if days > 365:
            days = 365
        
        # Get current product info
        product_row = await db.fetchrow("""
            SELECT id, title, price, original_price, discount_percent, 
                   store_name, category, product_url
            FROM products
            WHERE id = $1
        """, product_id)
        
        if not product_row:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Trigger real-time price check in background (only if product has URL)
        if product_row['product_url']:
            background_tasks.add_task(scrape_product_on_view, db, product_id)
        
        # Get price history
        history_rows = await db.fetch("""
            SELECT price, recorded_at
            FROM price_history
            WHERE product_id = $1
            AND recorded_at >= NOW() - INTERVAL '1 day' * $2
            ORDER BY recorded_at ASC
        """, product_id, days)
        
        price_history = [
            {
                "price": float(row['price']),
                "date": row['recorded_at'].isoformat()
            }
            for row in history_rows
        ]
        
        # Calculate statistics
        if price_history:
            prices = [p['price'] for p in price_history]
            lowest_price = min(prices)
            highest_price = max(prices)
            average_price = sum(prices) / len(prices)
            
            # Price trend (up, down, stable)
            if len(prices) >= 2:
                recent_avg = sum(prices[-7:]) / min(len(prices), 7)
                older_avg = sum(prices[:7]) / min(len(prices), 7)
                
                if recent_avg < older_avg * 0.95:
                    trend = "down"
                elif recent_avg > older_avg * 1.05:
                    trend = "up"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
        else:
            lowest_price = float(product_row['price'])
            highest_price = float(product_row['price'])
            average_price = float(product_row['price'])
            trend = "no_history"
        
        # Generate price forecast
        forecast = generate_price_forecast(price_history, float(product_row['price']))
        
        return {
            "product_id": product_id,
            "product_title": product_row['title'],
            "current_price": float(product_row['price']),
            "original_price": float(product_row['original_price']) if product_row['original_price'] else None,
            "store_name": product_row['store_name'],
            "price_history": price_history,
            "statistics": {
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "average_price": round(average_price, 2),
                "price_trend": trend,
                "data_points": len(price_history)
            },
            "forecast": forecast,
            "realtime_scraping": product_row['product_url'] is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get price history error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch price history: {str(e)}"
        )


@router.post("/record")
async def record_price_point(
    product_id: int,
    price: float,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Record a price point (called by background scraper job)
    Internal endpoint - should be protected in production
    """
    try:
        # Get product info
        product_row = await db.fetchrow("""
            SELECT title, store_name FROM products WHERE id = $1
        """, product_id)
        
        if not product_row:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Record price point
        await db.execute("""
            INSERT INTO price_history (product_id, product_title, store_name, price)
            VALUES ($1, $2, $3, $4)
        """, product_id, product_row['title'], product_row['store_name'], price)
        
        return {"message": "Price point recorded", "product_id": product_id, "price": price}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Record price point error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to record price point"
        )


@router.get("/product/{product_id}/comparison")
async def get_price_comparison_history(
    product_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get price history across all stores selling the same product"""
    try:
        # Get product title for matching
        product_row = await db.fetchrow("""
            SELECT title FROM products WHERE id = $1
        """, product_id)
        
        if not product_row:
            raise HTTPException(status_code=404, detail="Product not found")
        
        title = product_row['title']
        
        # Find similar products (same title, different stores)
        similar_products = await db.fetch("""
            SELECT id, store_name, price
            FROM products
            WHERE title ILIKE $1
            ORDER BY price ASC
        """, f"%{title}%")
        
        # Get price history for each store
        store_histories = {}
        for prod in similar_products:
            history = await db.fetch("""
                SELECT price, recorded_at
                FROM price_history
                WHERE product_id = $1
                AND recorded_at >= NOW() - INTERVAL '60 days'
                ORDER BY recorded_at ASC
            """, prod['id'])
            
            store_histories[prod['store_name']] = [
                {"price": float(h['price']), "date": h['recorded_at'].isoformat()}
                for h in history
            ]
        
        return {
            "product_title": title,
            "stores": store_histories
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get price comparison history error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch price comparison history"
        )
