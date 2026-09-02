"""
Product comparison models
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ComparisonItem(BaseModel):
    """Single product in a comparison"""
    id: int
    product_id: int
    product_title: str
    product_price: Decimal
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str
    category: Optional[str] = None
    added_at: datetime
    
    class Config:
        from_attributes = True


class ProductComparison(BaseModel):
    """A comparison set with multiple products"""
    id: int
    user_id: str
    comparison_name: str
    created_at: datetime
    updated_at: datetime
    items: List[ComparisonItem] = []
    
    class Config:
        from_attributes = True


class CreateComparisonRequest(BaseModel):
    """Request to create a new comparison"""
    comparison_name: str = "My Comparison"
    product_ids: List[int] = []  # Initial products to add


class AddToComparisonRequest(BaseModel):
    """Request to add product to existing comparison"""
    comparison_id: int
    product_id: int
    product_title: str
    product_price: float
    product_image_url: Optional[str] = None
    product_url: str
    store_name: str
    category: Optional[str] = None


class ComparisonListResponse(BaseModel):
    """List of user's comparisons"""
    comparisons: List[ProductComparison]
    total_comparisons: int


class ComparisonDetailResponse(BaseModel):
    """Detailed view of a single comparison"""
    comparison: ProductComparison
    comparison_table: dict  # Structured comparison data for easy display


class ComparisonSearchRequest(BaseModel):
    """Request to search products for comparison"""
    query: str
    exclude_product_ids: List[int] = []  # Products already in comparison
    limit: int = 20


class QuickCompareRequest(BaseModel):
    """Request for quick 2-product comparison"""
    product1_id: int
    product2_id: int