"""
History models for tracking user product views
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class HistoryItem(BaseModel):
    """Single history item - represents a product the user viewed"""
    id: int
    user_id: str
    product_id: int
    product_title: str
    product_price: Decimal
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str
    category: Optional[str] = None
    viewed_at: datetime
    
    class Config:
        from_attributes = True


class AddToHistoryRequest(BaseModel):
    """Request to add product to user history"""
    product_id: int
    product_title: str
    product_price: float
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str
    category: Optional[str] = None


class HistoryResponse(BaseModel):
    """User history response"""
    items: List[HistoryItem]
    total_items: int
    message: Optional[str] = None


class ClearHistoryRequest(BaseModel):
    """Request to clear specific items from history"""
    product_ids: Optional[List[int]] = None  # If None, clear all history