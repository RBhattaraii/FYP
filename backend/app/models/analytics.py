"""
Analytics, Points, Activity Tracking models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserActivity(BaseModel):
    """User activity model"""
    id: int
    user_id: str
    activity_type: str  # 'store_visit', 'purchase', 'wishlist_add', 'alert_set'
    product_id: Optional[int] = None
    product_title: Optional[str] = None
    product_price: Optional[Decimal] = None
    store_name: Optional[str] = None
    savings_amount: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecordActivityRequest(BaseModel):
    """Request to record user activity"""
    activity_type: str = Field(..., pattern="^(store_visit|purchase|wishlist_add|alert_set)$")
    product_id: Optional[int] = None
    product_title: Optional[str] = None
    product_price: Optional[float] = None
    store_name: Optional[str] = None
    savings_amount: Optional[float] = None


class PointsTransaction(BaseModel):
    """Points transaction model"""
    id: int
    user_id: str
    transaction_type: str
    points_change: int
    description: str
    related_user_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseStatistics(BaseModel):
    """Purchase statistics"""
    period: str  # 'month' or 'year'
    product_count: int
    total_spent: Decimal
    total_savings: Decimal


class SmartInsights(BaseModel):
    """Smart insights for analytics"""
    total_savings: Decimal
    missed_products_count: int
    missed_products: List[dict]  # Products user viewed but didn't buy when price dropped
    category_spending: dict  # Category -> amount
    monthly_spending_trend: List[dict]  # Last 6 months
    average_discount: float
    suggested_products: List[dict]


class AnalyticsResponse(BaseModel):
    """Complete analytics response"""
    current_points: int
    monthly_stats: PurchaseStatistics
    yearly_stats: PurchaseStatistics
    points_history: List[PointsTransaction]
    smart_insights: SmartInsights


class Voucher(BaseModel):
    """Voucher model"""
    id: int
    user_id: Optional[str] = None
    voucher_code: str
    discount_type: str = "fixed_amount"
    discount_amount: Decimal
    minimum_spend: Decimal = Decimal('0')
    usage_limit: int = 1
    times_used: int = 0
    is_global: bool = False
    points_cost: int = 0
    is_redeemed: bool = False
    redeemed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RedeemPointsRequest(BaseModel):
    """Request to redeem points for voucher"""
    points_to_redeem: int = Field(ge=1, description="Minimum 1 points")
    discount_amount: float = Field(gt=0, description="Discount amount must be positive")
    global_voucher_id: Optional[int] = None


class ReferralStats(BaseModel):
    """Referral statistics"""
    referral_code: str
    total_referrals: int
    pending_referrals: int
    points_earned_from_referrals: int

class AdminCreateVoucherRequest(BaseModel):
    voucher_code: str
    discount_type: str = Field(pattern="^(fixed_amount|percentage)$", default="fixed_amount")
    discount_amount: Decimal
    minimum_spend: Decimal = Decimal('0')
    usage_limit: int = 1
    expires_in_days: int = 30
    points_cost: int = 0

class ValidateVoucherRequest(BaseModel):
    voucher_code: str
    order_total: Decimal

class ValidateVoucherResponse(BaseModel):
    is_valid: bool
    message: str
    discount_amount: Decimal
    new_total: Decimal
    voucher_id: Optional[int] = None

class RedeemCheckoutRequest(BaseModel):
    voucher_code: str
    order_total: Decimal

