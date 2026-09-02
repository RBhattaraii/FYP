"""
Notifications and Price Alerts models
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class PriceAlert(BaseModel):
    """Price alert model"""
    id: int
    user_id: str
    product_id: int
    product_title: str
    product_url: str
    store_name: str
    product_image_url: Optional[str] = None
    target_price: Decimal
    current_price: Decimal
    is_active: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime
    
    @field_validator('user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string if needed"""
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CreatePriceAlertRequest(BaseModel):
    """Request to create price alert"""
    product_id: int
    product_title: str
    product_url: str
    store_name: str
    target_price: float = Field(gt=0, description="Target price must be positive")
    current_price: float = Field(gt=0, description="Current price must be positive")
    
    @field_validator('target_price', mode='after')
    @classmethod
    def validate_target_price(cls, v, info):
        if 'current_price' in info.data and v >= info.data['current_price']:
            raise ValueError('Target price must be less than current price')
        return v


class UpdatePriceAlertRequest(BaseModel):
    """Request to update price alert"""
    target_price: float = Field(gt=0, description="Target price must be positive")


class Notification(BaseModel):
    """Notification model"""
    id: int
    user_id: str
    notification_type: str  # 'price_alert', 'system', 'referral'
    title: str
    message: str
    product_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    @field_validator('user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string if needed"""
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class NotificationsResponse(BaseModel):
    """Notifications page response"""
    notifications: list[Notification]
    unread_count: int
    total_count: int


class PriceAlertsResponse(BaseModel):
    """Price alerts page response"""
    alerts: list[PriceAlert]
    active_count: int
    total_count: int
