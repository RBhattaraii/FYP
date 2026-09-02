"""
Categories Router - Browse products by category
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import asyncpg

from app.database.postgres import get_db
from app.models.product import Product, SearchResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/")
async def get_categories(db: asyncpg.Connection = Depends(get_db)):
    """Get list of all available categories with product counts"""
    try:
        rows = await db.fetch("""
            SELECT category, COUNT(*) as product_count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY product_count DESC
        """)
        
        categories = [
            {"name": row['category'], "product_count": row['product_count']}
            for row in rows
        ]
        
        return {"categories": categories, "total": len(categories)}
        
    except Exception as e:
        print(f"Get categories error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch categories"
        )


@router.get("/{category_name}", response_model=SearchResponse)
async def get_products_by_category(
    category_name: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query("deal_score", regex="^(price_asc|price_desc|deal_score|newest)$"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    store: Optional[str] = None,
    min_discount: Optional[int] = Query(None, ge=0, le=100),
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Get products in a specific category with filtering and sorting
    
    Parameters:
    - category_name: Category to filter by
    - page: Page number (default: 1)
    - limit: Results per page (default: 20, max: 100)
    - sort_by: Sort order (price_asc, price_desc, deal_score, newest)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - store: Filter by store name
    - min_discount: Minimum discount percentage
    """
    try:
        offset = (page - 1) * limit
        
        # Build WHERE clause
        where_conditions = ["category = $1"]
        params = [category_name]
        param_count = 1
        
        if min_price is not None:
            param_count += 1
            where_conditions.append(f"price >= ${param_count}")
            params.append(min_price)
        
        if max_price is not None:
            param_count += 1
            where_conditions.append(f"price <= ${param_count}")
            params.append(max_price)
        
        if store:
            param_count += 1
            where_conditions.append(f"store_name = ${param_count}")
            params.append(store)
        
        if min_discount is not None:
            param_count += 1
            where_conditions.append(f"discount_percent >= ${param_count}")
            params.append(min_discount)
        
        where_clause = " AND ".join(where_conditions)
        
        # Build ORDER BY clause
        if sort_by == "price_asc":
            order_clause = "ORDER BY price ASC"
        elif sort_by == "price_desc":
            order_clause = "ORDER BY price DESC"
        elif sort_by == "newest":
            order_clause = "ORDER BY scraped_at DESC"
        else:  # deal_score (default)
            order_clause = "ORDER BY discount_percent DESC, price ASC"
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM products WHERE {where_clause}"
        count_row = await db.fetchrow(count_query, *params)
        total_results = count_row['total'] if count_row else 0
        total_pages = (total_results + limit - 1) // limit if total_results > 0 else 1
        
        # Get paginated products
        data_query = f"""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM products
            WHERE {where_clause}
            {order_clause}
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        params.extend([limit, offset])
        
        rows = await db.fetch(data_query, *params)
        products = [Product(**dict(row)) for row in rows]
        
        return SearchResponse(
            request_id=f"category-{category_name}",
            query=category_name,
            tier="all",
            is_complete=True,
            results=products,
            results_count=len(products),
            tier1_platforms=[],
            message=f"Found {total_results} products in {category_name}",
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_results=total_results
        )
        
    except Exception as e:
        print(f"Get category products error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch products: {str(e)}"
        )


@router.get("/{category_name}/filters")
async def get_category_filters(
    category_name: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get available filter options for a category"""
    try:
        # Get price range
        price_range_row = await db.fetchrow("""
            SELECT MIN(price) as min_price, MAX(price) as max_price
            FROM products
            WHERE category = $1
        """, category_name)
        
        # Get available stores
        stores_rows = await db.fetch("""
            SELECT DISTINCT store_name
            FROM products
            WHERE category = $1
            ORDER BY store_name
        """, category_name)
        
        stores = [row['store_name'] for row in stores_rows]
        
        # Get discount ranges
        discount_ranges = [
            {"label": "10% or more", "value": 10},
            {"label": "20% or more", "value": 20},
            {"label": "30% or more", "value": 30},
            {"label": "50% or more", "value": 50},
        ]
        
        return {
            "price_range": {
                "min": float(price_range_row['min_price']) if price_range_row['min_price'] else 0,
                "max": float(price_range_row['max_price']) if price_range_row['max_price'] else 0
            },
            "stores": stores,
            "discount_ranges": discount_ranges,
            "sort_options": [
                {"label": "Best Deal", "value": "deal_score"},
                {"label": "Price: Low to High", "value": "price_asc"},
                {"label": "Price: High to Low", "value": "price_desc"},
                {"label": "Newest First", "value": "newest"}
            ]
        }
        
    except Exception as e:
        print(f"Get category filters error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch category filters"
        )
