"""
History Router
API endpoints for user product viewing history
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncpg
from datetime import datetime

from app.database.postgres import get_db
from app.auth.jwt_handler import get_current_user
from app.models.history import (
    HistoryItem,
    AddToHistoryRequest,
    HistoryResponse,
    ClearHistoryRequest
)

router = APIRouter(
    prefix="/history",
    tags=["history"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add")
async def add_to_history(
    request: AddToHistoryRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a product to user's viewing history.
    Uses UPSERT - if product already exists in history, updates viewed_at timestamp.
    
    This should be called whenever a user views a product detail page.
    """
    try:
        user_id = current_user["user_id"]
        
        # Insert or update history record
        await db.execute("""
            INSERT INTO user_history (
                user_id, product_id, product_title, product_price,
                product_image_url, product_url, store_name, category, viewed_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            ON CONFLICT (user_id, product_id) 
            DO UPDATE SET viewed_at = NOW()
        """, 
            user_id, request.product_id, request.product_title, request.product_price,
            request.product_image_url, request.product_url, request.store_name, request.category
        )
        
        return {"message": "Product added to history", "product_id": request.product_id}
        
    except Exception as e:
        print(f"[ERROR] Failed to add to history: {e}")
        raise HTTPException(status_code=500, detail="Failed to add product to history")


@router.get("/", response_model=HistoryResponse)
async def get_user_history(
    limit: int = 50,
    page: int = 1,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's product viewing history with pagination.
    Returns most recently viewed products first.
    
    Query Parameters:
    - limit: Number of items per page (default: 50, max: 100)
    - page: Page number (default: 1)
    """
    try:
        user_id = current_user["user_id"]
        
        # Cap limit for safety
        if limit > 100:
            limit = 100
        if page < 1:
            page = 1
            
        offset = (page - 1) * limit
        
        # Get total count
        total_count = await db.fetchval("""
            SELECT COUNT(*) FROM user_history WHERE user_id = $1
        """, user_id)
        
        # Get history items
        rows = await db.fetch("""
            SELECT id, user_id, product_id, product_title, product_price,
                   product_image_url, product_url, store_name, category, viewed_at
            FROM user_history 
            WHERE user_id = $1
            ORDER BY viewed_at DESC
            LIMIT $2 OFFSET $3
        """, user_id, limit, offset)
        
        # Convert to models
        items = [HistoryItem(**dict(row)) for row in rows]
        
        return HistoryResponse(
            items=items,
            total_items=total_count,
            message=f"Found {len(items)} items in your history"
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch history: {e}")
        raise HTTPException(status_code=500, detail="Failed to load history")


@router.delete("/clear")
async def clear_history(
    request: ClearHistoryRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Clear user's history.
    
    Request body:
    - product_ids: List of specific product IDs to remove (optional)
    - If product_ids is empty/null, clears entire history
    """
    try:
        user_id = current_user["user_id"]
        
        if request.product_ids and len(request.product_ids) > 0:
            # Clear specific products
            result = await db.execute("""
                DELETE FROM user_history 
                WHERE user_id = $1 AND product_id = ANY($2)
            """, user_id, request.product_ids)
            
            # Extract affected row count from result
            affected_rows = int(result.split()[-1]) if result.startswith("DELETE") else 0
            
            return {
                "message": f"Removed {affected_rows} items from history",
                "cleared_product_ids": request.product_ids
            }
        else:
            # Clear entire history
            result = await db.execute("""
                DELETE FROM user_history WHERE user_id = $1
            """, user_id)
            
            # Extract affected row count
            affected_rows = int(result.split()[-1]) if result.startswith("DELETE") else 0
            
            return {
                "message": f"Cleared entire history ({affected_rows} items)",
                "cleared_all": True
            }
            
    except Exception as e:
        print(f"[ERROR] Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")


@router.get("/stats")
async def get_history_stats(
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's history statistics.
    Returns total items, most viewed categories, etc.
    """
    try:
        user_id = current_user["user_id"]
        
        # Get basic stats
        stats = await db.fetchrow("""
            SELECT 
                COUNT(*) as total_items,
                COUNT(DISTINCT category) as unique_categories,
                COUNT(DISTINCT store_name) as unique_stores,
                MIN(viewed_at) as first_viewed,
                MAX(viewed_at) as last_viewed
            FROM user_history 
            WHERE user_id = $1
        """, user_id)
        
        # Get top categories
        top_categories = await db.fetch("""
            SELECT category, COUNT(*) as count
            FROM user_history 
            WHERE user_id = $1 AND category IS NOT NULL
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        """, user_id)
        
        # Get top stores
        top_stores = await db.fetch("""
            SELECT store_name, COUNT(*) as count
            FROM user_history 
            WHERE user_id = $1
            GROUP BY store_name 
            ORDER BY count DESC 
            LIMIT 5
        """, user_id)
        
        return {
            "total_items": stats["total_items"],
            "unique_categories": stats["unique_categories"],
            "unique_stores": stats["unique_stores"],
            "first_viewed": stats["first_viewed"],
            "last_viewed": stats["last_viewed"],
            "top_categories": [{"category": row["category"], "count": row["count"]} for row in top_categories],
            "top_stores": [{"store": row["store_name"], "count": row["count"]} for row in top_stores]
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get history stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to load history statistics")