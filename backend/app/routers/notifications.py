"""
Notifications and Price Alerts Routes
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg
import logging

from app.limiter import limiter
from app.models.notifications import (
    CreatePriceAlertRequest,
    UpdatePriceAlertRequest,
    PriceAlertsResponse,
    NotificationsResponse,
    PriceAlert,
    Notification
)
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


async def get_current_user_id(request: Request) -> str:
    """Extract and verify user ID from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            logger.warning("Token payload missing user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed. Please log in again."
        )


# ============================================================================
# Notifications Endpoints
# ============================================================================

@router.get("/", response_model=NotificationsResponse)
@limiter.limit("30/minute")
async def get_notifications(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get all notifications for current user"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Fetching notifications for user: {user_id}")
        
        rows = await db.fetch("""
            SELECT id, user_id, notification_type, title, message, 
                   product_id, is_read, created_at
            FROM notifications
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 100
        """, user_id)
        
        notifications = [Notification(**dict(row)) for row in rows]
        
        unread_count = await db.fetchval("""
            SELECT COUNT(*) FROM notifications
            WHERE user_id = $1 AND is_read = FALSE
        """, user_id)
        
        logger.info(f"Successfully fetched {len(notifications)} notifications for user {user_id}")
        return NotificationsResponse(
            notifications=notifications,
            unread_count=unread_count or 0,
            total_count=len(notifications)
        )
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in get_notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in get_notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching notifications. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications. Please try again."
        )


@router.post("/{notification_id}/read")
@limiter.limit("30/minute")
async def mark_notification_read(
    request: Request,
    notification_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """Mark notification as read"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Marking notification {notification_id} as read for user {user_id}")
        
        result = await db.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = $1 AND user_id = $2
        """, notification_id, user_id)
        
        if result == "UPDATE 0":
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        logger.info(f"Successfully marked notification {notification_id} as read")
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in mark_notification_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in mark_notification_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating notification. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in mark_notification_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read. Please try again."
        )


@router.post("/read-all")
@limiter.limit("10/minute")
async def mark_all_read(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Marking all notifications as read for user {user_id}")
        
        await db.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = $1 AND is_read = FALSE
        """, user_id)
        
        logger.info(f"Successfully marked all notifications as read for user {user_id}")
        return {"message": "All notifications marked as read"}
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in mark_all_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in mark_all_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating notifications. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in mark_all_read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read. Please try again."
        )


# ============================================================================
# Price Alerts Endpoints
# ============================================================================

@router.get("/alerts", response_model=PriceAlertsResponse)
@limiter.limit("30/minute")
async def get_price_alerts(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get all price alerts for current user"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Fetching price alerts for user: {user_id}")
        
        rows = await db.fetch("""
            SELECT pa.id, pa.user_id, pa.product_id, pa.product_title, pa.product_url, pa.store_name,
                   pa.target_price, pa.current_price, pa.is_active, pa.triggered_at, pa.created_at,
                   p.image_url as product_image_url
            FROM price_alerts pa
            LEFT JOIN products p ON pa.product_id = p.id
            WHERE pa.user_id = $1
            ORDER BY pa.created_at DESC
        """, user_id)
        
        alerts = [PriceAlert(**dict(row)) for row in rows]
        active_count = sum(1 for alert in alerts if alert.is_active)
        
        logger.info(f"Successfully fetched {len(alerts)} price alerts for user {user_id}")
        return PriceAlertsResponse(
            alerts=alerts,
            active_count=active_count,
            total_count=len(alerts)
        )
        
    except HTTPException:
        raise
    except asyncpg.exceptions.UndefinedTableError as e:
        # If the price_alerts table doesn't exist (e.g. migrations not applied),
        # return an empty response so the frontend can continue working.
        logger.warning(f"Price alerts table not found - returning empty response: {str(e)}")
        return PriceAlertsResponse(alerts=[], active_count=0, total_count=0)
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in get_price_alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in get_price_alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching price alerts. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_price_alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price alerts. Please try again."
        )


@router.post("/alerts", response_model=PriceAlert)
@limiter.limit("20/minute")
async def create_price_alert(
    request: Request,
    alert_data: CreatePriceAlertRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Create a new price alert"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Creating price alert for user {user_id}, product {alert_data.product_id}")
        
        # Check if active alert already exists for this product
        existing = await db.fetchrow("""
            SELECT id FROM price_alerts
            WHERE user_id = $1 AND product_id = $2 AND is_active = TRUE
        """, user_id, alert_data.product_id)
        
        if existing:
            logger.warning(f"Duplicate alert attempt for user {user_id}, product {alert_data.product_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert Already Exists - You already have an active price alert for this product."
            )
        
        # Create alert
        row = await db.fetchrow("""
            INSERT INTO price_alerts (user_id, product_id, product_title, product_url, 
                                     store_name, target_price, current_price, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
            RETURNING id, user_id, product_id, product_title, product_url, store_name,
                      target_price, current_price, is_active, triggered_at, created_at
        """, user_id, alert_data.product_id, alert_data.product_title, alert_data.product_url,
            alert_data.store_name, alert_data.target_price, alert_data.current_price)
        
        # Award points for setting alert
        try:
            await db.execute("""
                SELECT award_points($1, 5, 'earned_alert', 'Price alert set')
            """, user_id)
        except Exception as points_error:
            # Don't fail the entire request if points award fails
            logger.warning(f"Failed to award points for alert creation: {str(points_error)}")
        
        # Record activity
        try:
            await db.execute("""
                INSERT INTO user_activity (user_id, activity_type, product_id, product_title, product_price, store_name)
                VALUES ($1, 'alert_set', $2, $3, $4, $5)
            """, user_id, alert_data.product_id, alert_data.product_title, alert_data.target_price, alert_data.store_name)
        except Exception as activity_error:
            # Don't fail the entire request if activity recording fails
            logger.warning(f"Failed to record activity for alert creation: {str(activity_error)}")
        
        logger.info(f"Successfully created price alert {row['id']} for user {user_id}")
        
        return PriceAlert(**dict(row))
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in create_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.exceptions.UniqueViolationError as e:
        logger.warning(f"Duplicate alert constraint violation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert Already Exists - You already have an active price alert for this product."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in create_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating price alert. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create price alert. Please try again."
        )


@router.put("/alerts/{alert_id}")
@limiter.limit("20/minute")
async def update_price_alert(
    request: Request,
    alert_id: int,
    alert_data: UpdatePriceAlertRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Update target price for an existing alert"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Updating price alert {alert_id} for user {user_id}")
        
        result = await db.execute("""
            UPDATE price_alerts
            SET target_price = $1
            WHERE id = $2 AND user_id = $3 AND is_active = TRUE
        """, alert_data.target_price, alert_id, user_id)
        
        if result == "UPDATE 0":
            logger.warning(f"Alert {alert_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active alert not found"
            )
        
        logger.info(f"Successfully updated price alert {alert_id}")
        return {"message": "Price alert updated successfully"}
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in update_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in update_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating price alert. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update price alert. Please try again."
        )


@router.delete("/alerts/{alert_id}")
@limiter.limit("20/minute")
async def delete_price_alert(
    request: Request,
    alert_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete a price alert"""
    try:
        user_id = await get_current_user_id(request)
        logger.info(f"Deleting price alert {alert_id} for user {user_id}")
        
        result = await db.execute("""
            DELETE FROM price_alerts
            WHERE id = $1 AND user_id = $2
        """, alert_id, user_id)
        
        if result == "DELETE 0":
            logger.warning(f"Alert {alert_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        logger.info(f"Successfully deleted price alert {alert_id}")
        return {"message": "Price alert deleted successfully"}
        
    except HTTPException:
        raise
    except asyncpg.exceptions.PostgresConnectionError as e:
        logger.error(f"Database connection error in delete_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in delete_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting price alert. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_price_alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete price alert. Please try again."
        )


@router.post("/alerts/check")
async def manual_check_price_alerts(
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Manually trigger price alert checking worker.
    Fires the background scraping verification and alerts trigger.
    """
    from app.services.alerts_worker import check_price_alerts_job
    try:
        result = await check_price_alerts_job()
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        return result
    except Exception as e:
        logger.error(f"Manual alert check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Manual alerts check failed: {str(e)}"
        )
