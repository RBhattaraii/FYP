"""
Compare Router
API endpoints for product comparison functionality
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import asyncpg
from datetime import datetime

from app.database.postgres import get_db
from app.auth.jwt_handler import get_current_user
from app.models.compare import (
    ProductComparison,
    ComparisonItem,
    CreateComparisonRequest,
    AddToComparisonRequest,
    ComparisonListResponse,
    ComparisonDetailResponse,
    ComparisonSearchRequest,
    QuickCompareRequest
)
from app.models.product import Product

router = APIRouter(
    prefix="/compare",
    tags=["compare"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_comparison(
    request: CreateComparisonRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new product comparison set.
    Optionally add initial products to the comparison.
    """
    try:
        user_id = current_user["user_id"]
        
        # Create comparison
        comparison_id = await db.fetchval("""
            INSERT INTO product_comparisons (user_id, comparison_name)
            VALUES ($1, $2)
            RETURNING id
        """, user_id, request.comparison_name)
        
        # Add initial products if provided
        added_products = []
        if request.product_ids:
            for product_id in request.product_ids:
                # Get product details
                product = await db.fetchrow("""
                    SELECT title, price, image_url, product_url, store_name, category
                    FROM products WHERE id = $1
                """, product_id)
                
                if product:
                    # Add to comparison
                    await db.execute("""
                        INSERT INTO comparison_items (
                            comparison_id, product_id, product_title, product_price,
                            product_image_url, product_url, store_name, category
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, 
                        comparison_id, product_id, product["title"], product["price"],
                        product["image_url"], product["product_url"], product["store_name"], product["category"]
                    )
                    added_products.append(product_id)
        
        return {
            "comparison_id": comparison_id,
            "comparison_name": request.comparison_name,
            "message": f"Comparison created with {len(added_products)} products",
            "added_products": added_products
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to create comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to create comparison")


@router.get("/", response_model=ComparisonListResponse)
async def get_user_comparisons(
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all comparisons for the current user.
    Includes product count for each comparison.
    """
    try:
        user_id = current_user["user_id"]
        
        # Get comparisons with product counts
        comparisons_data = await db.fetch("""
            SELECT 
                pc.id, pc.user_id, pc.comparison_name, pc.created_at, pc.updated_at,
                COUNT(ci.id) as product_count
            FROM product_comparisons pc
            LEFT JOIN comparison_items ci ON pc.id = ci.comparison_id
            WHERE pc.user_id = $1
            GROUP BY pc.id, pc.user_id, pc.comparison_name, pc.created_at, pc.updated_at
            ORDER BY pc.updated_at DESC
        """, user_id)
        
        comparisons = []
        for comp_data in comparisons_data:
            # Get items for this comparison
            items_data = await db.fetch("""
                SELECT id, product_id, product_title, product_price, product_image_url,
                       product_url, store_name, category, added_at
                FROM comparison_items
                WHERE comparison_id = $1
                ORDER BY added_at ASC
            """, comp_data["id"])
            
            items = [ComparisonItem(**dict(item)) for item in items_data]
            
            comparison = ProductComparison(
                id=comp_data["id"],
                user_id=str(comp_data["user_id"]),
                comparison_name=comp_data["comparison_name"],
                created_at=comp_data["created_at"],
                updated_at=comp_data["updated_at"],
                items=items
            )
            comparisons.append(comparison)
        
        return ComparisonListResponse(
            comparisons=comparisons,
            total_comparisons=len(comparisons)
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch comparisons: {e}")
        raise HTTPException(status_code=500, detail="Failed to load comparisons")


@router.get("/{comparison_id}", response_model=ComparisonDetailResponse)
async def get_comparison_detail(
    comparison_id: int,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed view of a specific comparison.
    Includes structured comparison table for easy display.
    """
    try:
        user_id = current_user["user_id"]
        
        # Verify ownership
        comparison_data = await db.fetchrow("""
            SELECT id, user_id, comparison_name, created_at, updated_at
            FROM product_comparisons 
            WHERE id = $1 AND user_id = $2
        """, comparison_id, user_id)
        
        if not comparison_data:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        # Get comparison items
        items_data = await db.fetch("""
            SELECT id, product_id, product_title, product_price, product_image_url,
                   product_url, store_name, category, added_at
            FROM comparison_items
            WHERE comparison_id = $1
            ORDER BY added_at ASC
        """, comparison_id)
        
        items = [ComparisonItem(**dict(item)) for item in items_data]
        
        comparison = ProductComparison(
            id=comparison_data["id"],
            user_id=str(comparison_data["user_id"]),
            comparison_name=comparison_data["comparison_name"],
            created_at=comparison_data["created_at"],
            updated_at=comparison_data["updated_at"],
            items=items
        )
        
        # Create comparison table for structured display
        comparison_table = create_comparison_table(items)
        
        return ComparisonDetailResponse(
            comparison=comparison,
            comparison_table=comparison_table
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch comparison detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to load comparison")


@router.post("/{comparison_id}/add")
async def add_to_comparison(
    comparison_id: int,
    request: AddToComparisonRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a product to an existing comparison.
    """
    try:
        user_id = current_user["user_id"]
        
        # Verify comparison ownership
        comparison_exists = await db.fetchval("""
            SELECT id FROM product_comparisons 
            WHERE id = $1 AND user_id = $2
        """, comparison_id, user_id)
        
        if not comparison_exists:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        # Check if product already in comparison
        existing = await db.fetchval("""
            SELECT id FROM comparison_items 
            WHERE comparison_id = $1 AND product_id = $2
        """, comparison_id, request.product_id)
        
        if existing:
            raise HTTPException(status_code=400, detail="Product already in comparison")
        
        # Add product to comparison
        await db.execute("""
            INSERT INTO comparison_items (
                comparison_id, product_id, product_title, product_price,
                product_image_url, product_url, store_name, category
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, 
            comparison_id, request.product_id, request.product_title, request.product_price,
            request.product_image_url, request.product_url, request.store_name, request.category
        )
        
        # Update comparison timestamp
        await db.execute("""
            UPDATE product_comparisons SET updated_at = NOW() WHERE id = $1
        """, comparison_id)
        
        return {
            "message": "Product added to comparison",
            "comparison_id": comparison_id,
            "product_id": request.product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to add to comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to add product to comparison")


@router.delete("/{comparison_id}/remove/{product_id}")
async def remove_from_comparison(
    comparison_id: int,
    product_id: int,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a product from a comparison.
    """
    try:
        user_id = current_user["user_id"]
        
        # Verify ownership and remove
        result = await db.execute("""
            DELETE FROM comparison_items 
            WHERE comparison_id = $1 AND product_id = $2
            AND comparison_id IN (
                SELECT id FROM product_comparisons WHERE user_id = $3
            )
        """, comparison_id, product_id, user_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Product not found in comparison")
        
        # Update comparison timestamp
        await db.execute("""
            UPDATE product_comparisons SET updated_at = NOW() WHERE id = $1
        """, comparison_id)
        
        return {
            "message": "Product removed from comparison",
            "comparison_id": comparison_id,
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to remove from comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove product from comparison")


@router.delete("/{comparison_id}")
async def delete_comparison(
    comparison_id: int,
    db: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an entire comparison.
    """
    try:
        user_id = current_user["user_id"]
        
        # Delete comparison (items will be deleted by CASCADE)
        result = await db.execute("""
            DELETE FROM product_comparisons 
            WHERE id = $1 AND user_id = $2
        """, comparison_id, user_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        return {
            "message": "Comparison deleted successfully",
            "comparison_id": comparison_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to delete comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete comparison")


@router.post("/search")
async def search_for_comparison(
    request: ComparisonSearchRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Search for products to add to comparison.
    Excludes products already in the comparison.
    """
    try:
        # Search products (reuse existing search logic)
        rows = await db.fetch("""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM products
            WHERE (
                search_vector @@ websearch_to_tsquery('english', $1)
                OR title ILIKE '%' || $1 || '%'
            )
            AND id != ALL($2)
            ORDER BY 
                CASE WHEN title ILIKE $1 || '%' THEN 1 ELSE 2 END,
                price ASC
            LIMIT $3
        """, request.query, request.exclude_product_ids or [], request.limit)
        
        products = [Product(**dict(row)) for row in rows]
        
        return {
            "query": request.query,
            "results": products,
            "count": len(products)
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to search for comparison: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/quick")
async def quick_compare(
    request: QuickCompareRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Quick comparison between two products without saving.
    Returns structured comparison data.
    """
    try:
        # Get both products
        products_data = await db.fetch("""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM products
            WHERE id IN ($1, $2)
        """, request.product1_id, request.product2_id)
        
        if len(products_data) != 2:
            raise HTTPException(status_code=404, detail="One or both products not found")
        
        # Convert to comparison items format
        items = []
        for product in products_data:
            item = ComparisonItem(
                id=0,  # Not saved to DB
                product_id=product["id"],
                product_title=product["title"],
                product_price=product["price"],
                product_image_url=product["image_url"],
                product_url=product["product_url"],
                store_name=product["store_name"],
                category=product["category"],
                added_at=datetime.now()
            )
            items.append(item)
        
        # Create comparison table
        comparison_table = create_comparison_table(items)
        
        return {
            "product1": items[0],
            "product2": items[1],
            "comparison_table": comparison_table,
            "message": "Quick comparison generated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed quick compare: {e}")
        raise HTTPException(status_code=500, detail="Quick comparison failed")


def create_comparison_table(items: List[ComparisonItem]) -> Dict[str, Any]:
    """
    Create structured comparison table for display.
    Organizes product data for easy side-by-side comparison.
    """
    if not items:
        return {}
    
    # Basic info comparison
    comparison = {
        "products": [
            {
                "id": item.product_id,
                "title": item.product_title,
                "price": float(item.product_price),
                "image_url": item.product_image_url,
                "store": item.store_name,
                "category": item.category,
                "url": item.product_url
            }
            for item in items
        ],
        "price_comparison": {
            "lowest_price": min(float(item.product_price) for item in items),
            "highest_price": max(float(item.product_price) for item in items),
            "price_difference": max(float(item.product_price) for item in items) - min(float(item.product_price) for item in items),
            "savings": max(float(item.product_price) for item in items) - min(float(item.product_price) for item in items)
        },
        "store_comparison": list(set(item.store_name for item in items)),
        "category_comparison": list(set(item.category for item in items if item.category))
    }
    
    return comparison