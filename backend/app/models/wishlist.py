"""
Wishlist and related models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class WishlistItem(BaseModel):
    """Single wishlist item"""
    id: int
    user_id: str
    product_id: int
    product_title: str
    product_price: Decimal
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str
    added_at: datetime
    
    class Config:
        from_attributes = True


class AddToWishlistRequest(BaseModel):
    """Request to add product to wishlist"""
    product_id: int
    product_title: str
    product_price: float
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str


class WishlistResponse(BaseModel):
    """Wishlist page response"""
    items: list[WishlistItem]
    total_items: int
    message: Optional[str] = None
