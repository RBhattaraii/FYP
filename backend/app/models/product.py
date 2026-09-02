"""
Product models for API responses
Pydantic models for product data validation
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, HttpUrl


class Product(BaseModel):
    """
    Product model representing a scraped product
    
    Fields:
        id: Product ID (optional for search results, required for home screen)
        title: Product name/title
        price: Current selling price
        original_price: Original price before discount (optional)
        discount_percent: Discount percentage (optional)
        image_url: URL to product image
        store_name: Name of the e-commerce platform (e.g., "Daraz", "Sastodeal")
        product_url: Direct URL to product page
        category: Product category (e.g., "Electronics", "Fashion")
    """
    id: Optional[int] = None
    title: str
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[int] = None
    image_url: Optional[str] = None
    store_name: str
    product_url: Optional[str] = None
    category: Optional[str] = None
    store_count: int = 1
    alternative_offers: Optional[List[Dict[str, Any]]] = None


class HomeScreenResponse(BaseModel):
    """
    Response model for home screen endpoint (GET /products/home)
    
    Fields:
        best_deals: Array of products with highest discounts (>30% off)
        top_price_drops: Array of products with largest price reductions
    """
    best_deals: List[Product]
    top_price_drops: List[Product]
    tech_gadgets: List[Product] = []
    audio_essentials: List[Product] = []
    home_appliances: List[Product] = []


class SearchResponse(BaseModel):
    """
    Response model for search endpoint (GET /products/search)
    
    Fields:
        request_id: Unique identifier for this search request (for polling)
        query: The search query string
        tier: Current tier (1 = immediate results, 2 = all results)
        is_complete: Whether all platforms have been scraped
        results: Array of product results
        results_count: Total number of results in this response
        tier1_platforms: List of Tier 1 platforms (fast platforms)
        message: Status message for the user
    """
    request_id: str
    query: str
    tier: Union[int, str]
    is_complete: bool
    results: List[Product]
    results_count: int
    tier1_platforms: Optional[List[str]] = None
    message: str
    
    # Pagination metadata
    page: int = 1
    limit: int = 50
    total_pages: int = 1
    total_results: int = 0


class SearchStatusResponse(BaseModel):
    """
    Response model for search status polling endpoint (GET /products/search/status)
    
    Fields:
        request_id: The search request ID being polled
        is_complete: Whether all platforms have been scraped
        new_results_count: Number of new results available since last poll
        new_results: Array of new product results (empty if none)
        message: Status message for the user
    """
    request_id: str
    is_complete: bool
    new_results_count: int
    new_results: List[Product]
    message: str


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is the purpose of these Pydantic models?
A: These models define the structure of API responses. They ensure that
   all responses from the backend have consistent format and types.
   FastAPI uses these models to automatically generate API documentation
   and validate response data.

Q: Why is id Optional in Product model?
A: Search results may not have database IDs (they're scraped in real-time),
   but home screen products are stored in PostgreSQL and have IDs.
   Making it Optional allows the same model to be used for both cases.

Q: What is the difference between SearchResponse and SearchStatusResponse?
A: SearchResponse is returned immediately when user searches (Tier 1 results).
   SearchStatusResponse is used for polling - it returns additional results
   as they become available from slower platforms (Tier 2).

Q: Why separate best_deals and top_price_drops in HomeScreenResponse?
A: The home screen has two distinct sections with different sorting logic:
   - best_deals: Sorted by discount percentage (highest % off)
   - top_price_drops: Sorted by absolute price reduction (largest Rs drop)
   Separating them makes it easy for frontend to display each section.

Q: What is HttpUrl type?
A: HttpUrl is a Pydantic type that validates URLs. It ensures the URL
   is properly formatted (starts with http:// or https://).
   Note: We're using str for now for simplicity, but could use HttpUrl.

Q: Why do we need tier and is_complete fields?
A: These fields implement the progressive loading strategy:
   - tier tells frontend which platforms were scraped (1 = fast, 2 = all)
   - is_complete tells frontend if it should keep polling for more results
   This creates a better UX - users see fast results immediately, then
   additional results load progressively.
"""
