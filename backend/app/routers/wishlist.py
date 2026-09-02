"""
Wishlist Routes
Handles adding/removing products from wishlist
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg

from app.limiter import limiter
from app.models.wishlist import AddToWishlistRequest, WishlistResponse, WishlistItem
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


async def get_current_user_id(request: Request) -> str:
    """Extract and verify user ID from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )


@router.get("/", response_model=WishlistResponse)
@limiter.limit("30/minute")
async def get_wishlist(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user's wishlist"""
    try:
        user_id = await get_current_user_id(request)
        
        rows = await db.fetch("""
            SELECT id, user_id, product_id, product_title, product_price,
                   product_image_url, product_url, store_name, added_at
            FROM wishlist
            WHERE user_id = $1
            ORDER BY added_at DESC
        """, user_id)
        
        items = [WishlistItem(**dict(row)) for row in rows]
        
        return WishlistResponse(
            items=items,
            total_items=len(items)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get wishlist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wishlist"
        )


@router.post("/add")
@limiter.limit("20/minute")
async def add_to_wishlist(
    request: Request,
    item: AddToWishlistRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Add product to wishlist"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if already in wishlist
        existing = await db.fetchrow("""
            SELECT id FROM wishlist
            WHERE user_id = $1 AND product_id = $2
        """, user_id, item.product_id)
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )
        
        # Add to wishlist
        await db.execute("""
            INSERT INTO wishlist (user_id, product_id, product_title, product_price, 
                                product_image_url, product_url, store_name)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, user_id, item.product_id, item.product_title, item.product_price,
            item.product_image_url, item.product_url, item.store_name)
        
        # Award points for first wishlist add
        wishlist_count = await db.fetchval("""
            SELECT COUNT(*) FROM wishlist WHERE user_id = $1
        """, user_id)
        
        if wishlist_count == 1:  # First wishlist item
            await db.execute("""
                SELECT award_points($1, 5, 'earned_wishlist', 'First product added to wishlist')
            """, user_id)
        
        # Record activity
        await db.execute("""
            INSERT INTO user_activity (user_id, activity_type, product_id, product_title, product_price, store_name)
            VALUES ($1, 'wishlist_add', $2, $3, $4, $5)
        """, user_id, item.product_id, item.product_title, item.product_price, item.store_name)
        
        return {"message": "Added to wishlist successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Add to wishlist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to wishlist"
        )


@router.delete("/{product_id}")
@limiter.limit("20/minute")
async def remove_from_wishlist(
    request: Request,
    product_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """Remove product from wishlist"""
    try:
        user_id = await get_current_user_id(request)
        
        result = await db.execute("""
            DELETE FROM wishlist
            WHERE user_id = $1 AND product_id = $2
        """, user_id, product_id)
        
        if result == "DELETE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in wishlist"
            )
        
        return {"message": "Removed from wishlist successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Remove from wishlist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove from wishlist"
        )


@router.post("/toggle/{product_id}")
@limiter.limit("20/minute")
async def toggle_wishlist(
    request: Request,
    product_id: int,
    item: AddToWishlistRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Toggle product in wishlist (add if not exists, remove if exists)"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if exists
        existing = await db.fetchrow("""
            SELECT id FROM wishlist
            WHERE user_id = $1 AND product_id = $2
        """, user_id, product_id)
        
        if existing:
            # Remove
            await db.execute("""
                DELETE FROM wishlist
                WHERE user_id = $1 AND product_id = $2
            """, user_id, product_id)
            
            return {"message": "Removed from wishlist", "in_wishlist": False}
        else:
            # Add
            await db.execute("""
                INSERT INTO wishlist (user_id, product_id, product_title, product_price, 
                                    product_image_url, product_url, store_name)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, user_id, item.product_id, item.product_title, item.product_price,
                item.product_image_url, item.product_url, item.store_name)
            
            # Award points for first wishlist add
            wishlist_count = await db.fetchval("""
                SELECT COUNT(*) FROM wishlist WHERE user_id = $1
            """, user_id)
            
            if wishlist_count == 1:
                await db.execute("""
                    SELECT award_points($1, 5, 'earned_wishlist', 'First product added to wishlist')
                """, user_id)
            
            # Record activity
            await db.execute("""
                INSERT INTO user_activity (user_id, activity_type, product_id, product_title, product_price, store_name)
                VALUES ($1, 'wishlist_add', $2, $3, $4, $5)
            """, user_id, item.product_id, item.product_title, item.product_price, item.store_name)
            
            return {"message": "Added to wishlist", "in_wishlist": True}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Toggle wishlist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle wishlist"
        )
