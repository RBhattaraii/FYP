"""
Analytics Router - User activity tracking and smart insights
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg
from decimal import Decimal
from datetime import datetime, timedelta

from app.limiter import limiter
from app.models.analytics import (
    RecordActivityRequest,
    AnalyticsResponse,
    PurchaseStatistics,
    SmartInsights,
    PointsTransaction
)
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
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


@router.get("/dashboard", response_model=AnalyticsResponse)
@limiter.limit("30/minute")
async def get_analytics_dashboard(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get complete analytics dashboard"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get current points
        user_row = await db.fetchrow("SELECT points FROM users WHERE id = $1", user_id)
        current_points = user_row['points'] if user_row else 0
        
        # Monthly statistics
        monthly_purchases = await db.fetch("""
            SELECT product_id, product_title, product_price, store_name, savings_amount, created_at
            FROM user_activity
            WHERE user_id = $1 
            AND activity_type = 'purchase'
            AND created_at >= date_trunc('month', CURRENT_DATE)
        """, user_id)
        
        monthly_stats = PurchaseStatistics(
            period="month",
            product_count=len(monthly_purchases),
            total_spent=sum(row['product_price'] or 0 for row in monthly_purchases),
            total_savings=sum(row['savings_amount'] or 0 for row in monthly_purchases)
        )
        
        # Yearly statistics
        yearly_purchases = await db.fetch("""
            SELECT product_id, product_title, product_price, store_name, savings_amount, created_at
            FROM user_activity
            WHERE user_id = $1 
            AND activity_type = 'purchase'
            AND created_at >= date_trunc('year', CURRENT_DATE)
        """, user_id)
        
        yearly_stats = PurchaseStatistics(
            period="year",
            product_count=len(yearly_purchases),
            total_spent=sum(row['product_price'] or 0 for row in yearly_purchases),
            total_savings=sum(row['savings_amount'] or 0 for row in yearly_purchases)
        )
        
        # Points history
        points_rows = await db.fetch("""
            SELECT id, user_id, transaction_type, points_change, description, related_user_id, created_at
            FROM points_transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 50
        """, user_id)
        
        points_history = [PointsTransaction(**dict(row)) for row in points_rows]
        
        # Smart Insights
        # 1. Total savings
        total_savings = yearly_stats.total_savings
        
        # 2. Missed products (products viewed but not purchased when price dropped)
        missed_products_rows = await db.fetch("""
            WITH viewed_products AS (
                SELECT DISTINCT product_id, product_title, MIN(product_price) as viewed_price
                FROM user_activity
                WHERE user_id = $1 AND activity_type = 'store_visit'
                GROUP BY product_id, product_title
            ),
            lowest_prices AS (
                SELECT product_id, MIN(price) as lowest_price
                FROM price_history
                WHERE recorded_at >= NOW() - INTERVAL '30 days'
                GROUP BY product_id
            )
            SELECT vp.product_id, vp.product_title, vp.viewed_price, lp.lowest_price,
                   (vp.viewed_price - lp.lowest_price) as potential_savings
            FROM viewed_products vp
            JOIN lowest_prices lp ON vp.product_id = lp.product_id
            WHERE lp.lowest_price < vp.viewed_price * 0.9
            AND NOT EXISTS (
                SELECT 1 FROM user_activity ua
                WHERE ua.user_id = $1 
                AND ua.activity_type = 'purchase'
                AND ua.product_id = vp.product_id
            )
            ORDER BY potential_savings DESC
            LIMIT 5
        """, user_id)
        
        missed_products = [dict(row) for row in missed_products_rows]
        
        # 3. Category spending
        category_spending_rows = await db.fetch("""
            SELECT p.category, SUM(ua.product_price) as total_spent
            FROM user_activity ua
            JOIN products p ON ua.product_id = p.id
            WHERE ua.user_id = $1 
            AND ua.activity_type = 'purchase'
            AND ua.created_at >= NOW() - INTERVAL '1 year'
            GROUP BY p.category
            ORDER BY total_spent DESC
        """, user_id)
        
        category_spending = {row['category']: float(row['total_spent']) for row in category_spending_rows}
        
        # 4. Monthly spending trend (last 6 months)
        monthly_trend_rows = await db.fetch("""
            SELECT 
                date_trunc('month', created_at) as month,
                COUNT(*) as purchase_count,
                SUM(product_price) as total_spent
            FROM user_activity
            WHERE user_id = $1 
            AND activity_type = 'purchase'
            AND created_at >= NOW() - INTERVAL '6 months'
            GROUP BY date_trunc('month', created_at)
            ORDER BY month ASC
        """, user_id)
        
        monthly_spending_trend = [
            {
                "month": row['month'].strftime("%Y-%m"),
                "purchase_count": row['purchase_count'],
                "total_spent": float(row['total_spent'])
            }
            for row in monthly_trend_rows
        ]
        
        # 5. Average discount
        avg_discount_row = await db.fetchrow("""
            SELECT AVG(
                CASE 
                    WHEN ua.savings_amount IS NOT NULL AND ua.product_price > 0
                    THEN (ua.savings_amount / ua.product_price) * 100
                    ELSE 0
                END
            ) as avg_discount
            FROM user_activity ua
            WHERE ua.user_id = $1 AND ua.activity_type = 'purchase'
        """, user_id)
        
        avg_discount = float(avg_discount_row['avg_discount'] or 0)
        
        # 6. Suggested products (categories user browses but hasn't purchased)
        suggested_rows = await db.fetch("""
            WITH browsed_categories AS (
                SELECT DISTINCT p.category
                FROM user_activity ua
                JOIN products p ON ua.product_id = p.id
                WHERE ua.user_id = $1 AND ua.activity_type = 'store_visit'
            ),
            purchased_categories AS (
                SELECT DISTINCT p.category
                FROM user_activity ua
                JOIN products p ON ua.product_id = p.id
                WHERE ua.user_id = $1 AND ua.activity_type = 'purchase'
            )
            SELECT p.id, p.title, p.price, p.discount_percent, p.image_url, p.store_name
            FROM products p
            WHERE p.category IN (SELECT category FROM browsed_categories)
            AND p.category NOT IN (SELECT category FROM purchased_categories)
            AND p.discount_percent > 10
            ORDER BY p.discount_percent DESC
            LIMIT 5
        """, user_id)
        
        suggested_products = [dict(row) for row in suggested_rows]
        
        smart_insights = SmartInsights(
            total_savings=total_savings,
            missed_products_count=len(missed_products),
            missed_products=missed_products,
            category_spending=category_spending,
            monthly_spending_trend=monthly_spending_trend,
            average_discount=avg_discount,
            suggested_products=suggested_products
        )
        
        return AnalyticsResponse(
            current_points=current_points,
            monthly_stats=monthly_stats,
            yearly_stats=yearly_stats,
            points_history=points_history,
            smart_insights=smart_insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )


@router.post("/record")
@limiter.limit("60/minute")
async def record_activity(
    request: Request,
    activity: RecordActivityRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Record user activity (purchase, store visit, etc.)"""
    try:
        user_id = await get_current_user_id(request)
        
        await db.execute("""
            INSERT INTO user_activity (user_id, activity_type, product_id, product_title, 
                                      product_price, store_name, savings_amount)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, user_id, activity.activity_type, activity.product_id, activity.product_title,
            activity.product_price, activity.store_name, activity.savings_amount)
        
        # Award points for purchases
        if activity.activity_type == 'purchase':
            await db.execute("""
                SELECT award_points($1, 10, 'earned_purchase', 'Product purchase')
            """, user_id)
        
        return {"message": "Activity recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Record activity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record activity"
        )
