# Technical Design Document

## Overview

This design document specifies the technical architecture and implementation details for comprehensive feature additions to the PricePilot price comparison system. The feature set transforms PricePilot from a basic price comparison tool into a full-featured e-commerce intelligence platform with user authentication, gamification elements (points and referrals), personalized experiences (wishlists and price alerts), analytics dashboards, and admin capabilities.

### System Context

PricePilot is a mobile-first price comparison application with:
- **Frontend**: React Native mobile application
- **Backend**: FastAPI (Python) REST API
- **Databases**: 
  - PostgreSQL (Supabase) for relational data (users, wishlists, alerts, points, referrals)
  - MongoDB for flexible product data and price history
- **Authentication**: JWT token-based authentication
- **Scraping**: Multi-platform product scraper with tiered results

### Design Goals

1. **Extensibility**: Modular architecture supporting future feature additions
2. **Performance**: Sub-2-second API responses for 95% of requests
3. **Security**: Secure authentication, input validation, and data protection
4. **Scalability**: Support for 100+ concurrent users with horizontal scaling capability
5. **Maintainability**: Clear separation of concerns, comprehensive testing
6. **User Experience**: Smooth mobile interactions with progressive data loading

## Architecture

### High-Level Architecture


```mermaid
graph TB
    subgraph "Mobile Frontend"
        RN[React Native App]
        NAV[Bottom Tab Navigation]
        AUTH[Auth Pages]
        HOME[Home & Search]
        PROD[Product Detail]
        WISH[Wishlist]
        NOTIF[Notifications]
        PROF[Profile & Analytics]
        ADMIN[Admin Dashboard]
    end
    
    subgraph "Backend API Layer"
        API[FastAPI Application]
        AUTHM[Auth Middleware]
        LIMITER[Rate Limiter]
        ROUTER[API Routers]
    end
    
    subgraph "Business Logic Layer"
        AUTHSVC[Auth Service]
        PRODSVC[Product Service]
        WISHSVC[Wishlist Service]
        ALERTSVC[Alert Service]
        POINTSSVC[Points Service]
        REFSVC[Referral Service]
        TRACKSVC[Activity Tracker]
        DEALSVC[Deal Score Engine]
        ANALYTICSVC[Analytics Service]
        SCRAPER[Scraper Coordinator]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        MONGO[(MongoDB)]
        CACHE[Redis Cache]
    end
    
    subgraph "Background Jobs"
        SCHEDULER[APScheduler]
        DAILYSCRAPE[Daily Scrape Job]
        ALERTCHECK[Price Alert Checker]
        ANALYTICS[Analytics Generator]
    end
    
    RN --> API
    API --> AUTHM
    API --> LIMITER
    API --> ROUTER
    ROUTER --> AUTHSVC
    ROUTER --> PRODSVC
    ROUTER --> WISHSVC
    ROUTER --> ALERTSVC
    ROUTER --> POINTSSVC
    ROUTER --> REFSVC
    ROUTER --> TRACKSVC
    ROUTER --> DEALSVC
    ROUTER --> ANALYTICSVC
    ROUTER --> SCRAPER
    
    AUTHSVC --> PG
    PRODSVC --> PG
    PRODSVC --> MONGO
    PRODSVC --> CACHE
    WISHSVC --> PG
    ALERTSVC --> PG
    POINTSSVC --> PG
    REFSVC --> PG
    TRACKSVC --> PG
    DEALSVC --> MONGO
    ANALYTICSVC --> PG
    SCRAPER --> MONGO
    SCRAPER --> PG
    
    SCHEDULER --> DAILYSCRAPE
    SCHEDULER --> ALERTCHECK
    SCHEDULER --> ANALYTICS
    DAILYSCRAPE --> SCRAPER
    ALERTCHECK --> ALERTSVC
    ANALYTICS --> ANALYTICSVC
```

### Architectural Patterns

1. **Layered Architecture**: Clear separation between presentation (React Native), API (FastAPI), business logic (services), and data access (repositories)

2. **Repository Pattern**: Database operations encapsulated in repository classes for testability and maintainability

3. **Service Pattern**: Business logic isolated in service classes, keeping routers thin and focused on HTTP concerns

4. **Dependency Injection**: FastAPI's dependency system provides database connections, authentication, and rate limiting

5. **Event-Driven**: Background jobs handle asynchronous tasks (scraping, notifications, analytics)

### Technology Stack

**Frontend:**
- React Native with TypeScript
- React Navigation for routing
- Axios for HTTP requests
- AsyncStorage for token persistence
- React Native Charts for analytics visualization

**Backend:**
- FastAPI (Python 3.9+)
- Pydantic for request/response validation
- asyncpg for async PostgreSQL operations
- Motor for async MongoDB operations
- PyJWT for token generation and validation
- bcrypt for password hashing
- APScheduler for background jobs
- slowapi for rate limiting

**Databases:**
- PostgreSQL (Supabase) for relational data
- MongoDB for document storage
- Redis (optional) for caching

## Components and Interfaces

### 1. Authentication Component

**Purpose**: Handle user registration, login, profile management, and JWT token operations

**API Endpoints:**

```
POST   /auth/register          - Register new user
POST   /auth/login             - Login user
GET    /auth/me                - Get current user profile
PUT    /auth/me                - Update user profile
POST   /auth/refresh           - Refresh access token
POST   /auth/logout            - Logout user (optional token blacklist)
```

**Database Schema:**

```sql
-- Users table (PostgreSQL)
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT,
    phone           TEXT,
    role            TEXT NOT NULL DEFAULT 'user',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    points_balance  INTEGER NOT NULL DEFAULT 100,  -- Welcome bonus
    referral_code   TEXT UNIQUE NOT NULL,
    referred_by     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_referred_by ON users(referred_by);
```

**Service Methods:**

```python
class AuthService:
    async def register_user(email: str, password: str, full_name: str, referral_code: str) -> User
    async def login_user(email: str, password: str) -> AuthResponse
    async def get_user_by_id(user_id: UUID) -> User
    async def update_user_profile(user_id: UUID, updates: dict) -> User
    def generate_referral_code(user_id: UUID) -> str
    def create_jwt_token(user_id: UUID) -> str
    def verify_jwt_token(token: str) -> dict
```

**Key Design Decisions:**

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens expire after 24 hours
- Referral codes are 8-character alphanumeric strings
- Welcome bonus of 100 points awarded on registration
- Phone validation: 10-15 digits only

### 2. Product & Search Component

**Purpose**: Handle product display, search, and deal scoring

**API Endpoints:**

```
GET    /products/home          - Get home page products (best deals, top drops)
GET    /products/search        - Search products with tiered results
GET    /products/search/status - Poll for additional search results
GET    /products/{id}          - Get product details
GET    /products/{id}/history  - Get price history
GET    /categories             - List all categories
GET    /categories/{name}      - Browse category with filtering
POST   /products/{id}/track    - Track "Go to Store" click
```

**Database Schema:**

```sql
-- Products table (PostgreSQL for search index)
CREATE TABLE products (
    id                SERIAL PRIMARY KEY,
    title             TEXT NOT NULL,
    price             DECIMAL(10, 2) NOT NULL,
    original_price    DECIMAL(10, 2),
    discount_percent  INTEGER,
    image_url         TEXT,
    store_name        TEXT NOT NULL,
    product_url       TEXT NOT NULL UNIQUE,
    category          TEXT,
    mongo_id          TEXT,
    deal_score        INTEGER,
    scraped_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    search_vector     tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(category, '')), 'B')
    ) STORED
);

CREATE INDEX idx_products_search ON products USING GIN(search_vector);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_deal_score ON products(deal_score DESC);
```

**MongoDB Collections:**

```javascript
// products collection
{
  _id: ObjectId,
  product_url: String,
  title: String,
  current_price: Number,
  original_price: Number,
  store_name: String,
  image_url: String,
  description: String,
  specifications: Object,
  seller_rating: Number,
  review_count: Number,
  review_score: Number,
  price_history: [
    {
      price: Number,
      timestamp: Date
    }
  ],
  last_updated: Date
}
```

**Service Methods:**

```python
class ProductService:
    async def get_home_products() -> HomeScreenResponse
    async def search_products(query: str, tier: int) -> SearchResponse
    async def get_product_details(product_id: int) -> Product
    async def get_price_history(product_id: int) -> List[PricePoint]
    async def get_category_products(category: str, filters: dict) -> List[Product]
    
class DealScoreEngine:
    def calculate_deal_score(product: Product) -> int
    def get_price_competitiveness_score(price: float, category_avg: float) -> float
    def get_seller_rating_score(rating: float) -> float
    def get_review_score(review_count: int, review_rating: float) -> float
```

**Deal Score Algorithm:**

```python
deal_score = (
    price_competitiveness * 0.50 +
    seller_rating_score * 0.30 +
    review_score * 0.20
) * 100

# Price competitiveness: How much below category average
price_competitiveness = max(0, (category_avg - product_price) / category_avg)

# Seller rating: Normalize 0-5 rating to 0-1
seller_rating_score = min(seller_rating / 5.0, 1.0)

# Review score: Weighted by count (more reviews = more reliable)
review_score = (review_rating / 5.0) * min(review_count / 100, 1.0)
```

### 3. Wishlist Component

**Purpose**: Manage user's saved products and track price changes

**API Endpoints:**

```
GET    /wishlist               - Get user's wishlist
POST   /wishlist/{product_id}  - Add product to wishlist
DELETE /wishlist/{product_id}  - Remove product from wishlist
GET    /wishlist/price-drops   - Get products with recent price drops
```

**Database Schema:**

```sql
CREATE TABLE wishlists (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    added_price     DECIMAL(10, 2),
    current_price   DECIMAL(10, 2),
    last_checked    TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_wishlist_user ON wishlists(user_id);
CREATE INDEX idx_wishlist_product ON wishlists(product_id);
```

**Service Methods:**

```python
class WishlistService:
    async def add_to_wishlist(user_id: UUID, product_id: int) -> bool
    async def remove_from_wishlist(user_id: UUID, product_id: int) -> bool
    async def get_user_wishlist(user_id: UUID) -> List[WishlistItem]
    async def check_price_drops(user_id: UUID) -> List[WishlistItem]
    async def update_wishlist_prices() -> int  # Background job
```

### 4. Price Alerts Component

**Purpose**: Manage price alerts and send notifications

**API Endpoints:**

```
GET    /alerts                 - Get user's active alerts
POST   /alerts                 - Create price alert
PUT    /alerts/{id}            - Update alert target price
DELETE /alerts/{id}            - Delete alert
GET    /notifications          - Get user notifications
PUT    /notifications/{id}/read - Mark notification as read
```

**Database Schema:**

```sql
CREATE TABLE price_alerts (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    target_price    DECIMAL(10, 2) NOT NULL,
    current_price   DECIMAL(10, 2) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    triggered_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, product_id, is_active)
);

CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL,  -- 'price_alert', 'system', 'referral'
    title           TEXT NOT NULL,
    message         TEXT NOT NULL,
    product_id      INTEGER REFERENCES products(id),
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
```

**Service Methods:**

```python
class PriceAlertService:
    async def create_alert(user_id: UUID, product_id: int, target_price: Decimal) -> PriceAlert
    async def update_alert(alert_id: int, target_price: Decimal) -> PriceAlert
    async def delete_alert(alert_id: int) -> bool
    async def get_user_alerts(user_id: UUID) -> List[PriceAlert]
    async def check_price_alerts() -> int  # Background job - check all active alerts
    
class NotificationService:
    async def send_price_alert_notification(user_id: UUID, product: Product, target_price: Decimal)
    async def send_referral_notification(user_id: UUID, referee_name: str, points: int)
    async def get_user_notifications(user_id: UUID, unread_only: bool) -> List[Notification]
    async def mark_as_read(notification_id: int) -> bool
```

### 5. Points & Rewards Component

**Purpose**: Implement gamification through points and voucher system

**API Endpoints:**

```
GET    /points                 - Get user's point balance and history
GET    /points/history         - Get detailed point transaction history
GET    /rewards                - List available vouchers for redemption
POST   /rewards/{id}/redeem    - Redeem points for voucher
GET    /rewards/my-vouchers    - Get user's active vouchers
```

**Database Schema:**

```sql
CREATE TABLE point_transactions (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL,  -- 'registration', 'profile_complete', 'purchase', 
                                     -- 'wishlist_add', 'alert_set', 'referral_given', 
                                     -- 'referral_received', 'voucher_redemption'
    amount          INTEGER NOT NULL,  -- Positive for credit, negative for debit
    balance_after   INTEGER NOT NULL,
    description     TEXT,
    reference_id    TEXT,  -- Optional: product_id, alert_id, voucher_id, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE vouchers (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,
    discount_amount DECIMAL(10, 2) NOT NULL,
    point_cost      INTEGER NOT NULL,
    expiry_days     INTEGER NOT NULL DEFAULT 30,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE user_vouchers (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    voucher_id      INTEGER NOT NULL REFERENCES vouchers(id),
    voucher_code    TEXT UNIQUE NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    is_used         BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at      TIMESTAMPTZ NOT NULL,
    used_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_points_user ON point_transactions(user_id);
CREATE INDEX idx_points_created ON point_transactions(created_at DESC);
CREATE INDEX idx_user_vouchers_user ON user_vouchers(user_id);
CREATE INDEX idx_user_vouchers_active ON user_vouchers(user_id, is_used, expires_at) 
    WHERE is_used = FALSE;
```

**Service Methods:**

```python
class PointsService:
    async def award_points(user_id: UUID, transaction_type: str, amount: int, 
                          description: str, reference_id: str) -> PointTransaction
    async def deduct_points(user_id: UUID, amount: int, description: str) -> PointTransaction
    async def get_balance(user_id: UUID) -> int
    async def get_transaction_history(user_id: UUID, limit: int) -> List[PointTransaction]
    
class RewardsService:
    async def get_available_vouchers() -> List[Voucher]
    async def redeem_voucher(user_id: UUID, voucher_id: int) -> UserVoucher
    async def get_user_vouchers(user_id: UUID, active_only: bool) -> List[UserVoucher]
    def generate_voucher_code() -> str
```

**Points Allocation Rules:**

- Registration: 100 points
- Complete profile (name + phone): 50 points
- Add to wishlist (first time): 5 points
- Set price alert: 5 points
- Mark purchase: 10 points
- Referral (referrer): 50 points
- Referral (new user): 25 points

### 6. Referral Component

**Purpose**: Enable user growth through referral rewards

**API Endpoints:**

```
GET    /referrals              - Get user's referral stats
GET    /referrals/code         - Get user's referral code
POST   /referrals/validate     - Validate referral code (used during registration)
```

**Service Methods:**

```python
class ReferralService:
    async def generate_unique_code(user_id: UUID) -> str
    async def validate_code(code: str) -> Optional[UUID]
    async def process_referral(referrer_id: UUID, referee_id: UUID) -> bool
    async def get_referral_stats(user_id: UUID) -> ReferralStats
```

**Integration Points:**

- During registration, validate and apply referral code
- Award points to both referrer and referee
- Send notification to referrer about successful referral
- Track referral hierarchy for analytics

### 7. Activity Tracking Component

**Purpose**: Track user actions and generate purchase statistics

**API Endpoints:**

```
POST   /activity/store-visit   - Record store visit click
POST   /activity/purchase      - Mark product as purchased
GET    /activity/stats         - Get purchase statistics
GET    /activity/history       - Get detailed purchase history
```

**Database Schema:**

```sql
CREATE TABLE activity_events (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type      TEXT NOT NULL,  -- 'store_visit', 'purchase'
    product_id      INTEGER REFERENCES products(id),
    store_name      TEXT,
    price           DECIMAL(10, 2),
    savings_amount  DECIMAL(10, 2),
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON activity_events(user_id);
CREATE INDEX idx_activity_type ON activity_events(event_type);
CREATE INDEX idx_activity_created ON activity_events(created_at DESC);
```

**Service Methods:**

```python
class ActivityTracker:
    async def record_store_visit(user_id: UUID, product_id: int, store_name: str)
    async def record_purchase(user_id: UUID, product_id: int, price: Decimal, 
                             original_price: Decimal)
    async def get_monthly_stats(user_id: UUID, year: int, month: int) -> PurchaseStats
    async def get_yearly_stats(user_id: UUID, year: int) -> PurchaseStats
    async def get_purchase_history(user_id: UUID, limit: int) -> List[Purchase]
```

### 8. Analytics Component

**Purpose**: Generate personalized insights and spending analytics

**API Endpoints:**

```
GET    /analytics/insights     - Get smart insights summary
GET    /analytics/savings      - Get total savings calculations
GET    /analytics/missed       - Get missed deal opportunities
GET    /analytics/categories   - Get category spending breakdown
GET    /analytics/trends       - Get spending trends over time
```

**Service Methods:**

```python
class AnalyticsService:
    async def calculate_total_savings(user_id: UUID) -> Decimal
    async def find_missed_opportunities(user_id: UUID) -> List[MissedDeal]
    async def get_category_breakdown(user_id: UUID) -> Dict[str, CategoryStats]
    async def get_spending_trends(user_id: UUID, months: int) -> List[MonthlyTrend]
    async def get_average_discount(user_id: UUID) -> float
    async def generate_product_suggestions(user_id: UUID) -> List[Product]
```

### 9. Admin Dashboard Component

**Purpose**: Provide system monitoring and management for administrators

**API Endpoints:**

```
GET    /admin/stats            - Get system statistics
GET    /admin/users            - List all users with filters
GET    /admin/scrapers         - Get scraper status
POST   /admin/scrapers/trigger - Manually trigger scraper
GET    /admin/products/count   - Get product counts by store
GET    /admin/logs             - Get system logs
```

**Authorization:**

- All endpoints protected by admin role check
- JWT token must have `role: "admin"`

**Service Methods:**

```python
class AdminService:
    async def get_system_stats() -> SystemStats
    async def get_user_list(filters: dict, page: int) -> PaginatedUsers
    async def get_scraper_status() -> List[ScraperStatus]
    async def trigger_scraper(store_name: str) -> bool
    async def get_product_counts() -> Dict[str, int]
```

## Data Models

### Core Pydantic Models

```python
# Auth Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]
    referral_code: Optional[str]
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    full_name: Optional[str]
    phone: Optional[str]
    points_balance: int
    referral_code: str

# Product Models  
class Product(BaseModel):
    id: int
    title: str
    price: Decimal
    original_price: Optional[Decimal]
    discount_percent: Optional[int]
    image_url: Optional[str]
    store_name: str
    product_url: str
    category: Optional[str]
    deal_score: Optional[int]
    
class PricePoint(BaseModel):
    price: Decimal
    timestamp: datetime
    
# Wishlist Models
class WishlistItem(BaseModel):
    id: int
    product: Product
    added_price: Decimal
    current_price: Decimal
    price_drop: Optional[Decimal]
    added_at: datetime
    
# Alert Models
class PriceAlert(BaseModel):
    id: int
    product_id: int
    target_price: Decimal
    current_price: Decimal
    is_active: bool
    created_at: datetime
    
class Notification(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    product_id: Optional[int]
    is_read: bool
    created_at: datetime
    
# Points Models
class PointTransaction(BaseModel):
    id: int
    transaction_type: str
    amount: int
    balance_after: int
    description: str
    created_at: datetime
    
class Voucher(BaseModel):
    id: int
    name: str
    description: str
    discount_amount: Decimal
    point_cost: int
    expiry_days: int
    
class UserVoucher(BaseModel):
    id: int
    voucher_code: str
    discount_amount: Decimal
    expires_at: datetime
    is_used: bool
    
# Activity Models
class PurchaseStats(BaseModel):
    total_purchases: int
    total_spent: Decimal
    total_saved: Decimal
    average_discount: float
    
class Purchase(BaseModel):
    product_title: str
    store_name: str
    price: Decimal
    original_price: Decimal
    savings: Decimal
    purchased_at: datetime
    
# Analytics Models
class MissedDeal(BaseModel):
    product: Product
    viewed_at: datetime
    lowest_price_reached: Decimal
    potential_savings: Decimal
    
class CategoryStats(BaseModel):
    category: str
    purchase_count: int
    total_spent: Decimal
    average_price: Decimal
    
class MonthlyTrend(BaseModel):
    month: str
    total_spent: Decimal
    purchase_count: int
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

After reviewing the prework analysis and identifying redundancies, the following correctness properties capture the essential behaviors that must be verified through property-based testing:

### Property 1: User Registration Creates Valid Account with Token

*For any* valid email and password (meeting validation rules), registering a user SHALL create an account in the database, hash the password with bcrypt, generate a unique referral code, award 100 welcome points, and return a valid JWT token containing user_id, email, and role.

**Validates: Requirements 1.2, 1.3, 1.4, 1.9, 1.10**

### Property 2: User Login Returns Token for Valid Credentials

*For any* registered user with valid credentials, login SHALL return a JWT token containing the correct user_id, email, and role, and the token SHALL be decodable to retrieve the same information.

**Validates: Requirements 1.7, 1.10**

### Property 3: Invalid Credentials Return Consistent Error

*For any* invalid credentials (unregistered email OR wrong password), login SHALL return the same error message "Invalid email or password" without revealing which credential was incorrect.

**Validates: Requirements 1.8**

### Property 4: Password Hashing is One-Way and Verifiable

*For any* password, hashing the password SHALL produce a different string than the original, and verifying the original password against the hash SHALL return true, while any other password SHALL return false.

**Validates: Requirements 1.9**

### Property 5: JWT Token Contains Required Payload Fields

*For any* generated JWT token, decoding the token SHALL extract a payload containing user_id, email, and role fields.

**Validates: Requirements 1.10**

### Property 6: Deal Score Calculation is Bounded and Consistent

*For any* product with valid price, seller rating (0-5), and review data, the Deal_Score calculation SHALL produce a value between 0 and 100, and calculating the score multiple times for the same input SHALL produce the same result.

**Validates: Requirements 3.7, 10.1, 10.2, 10.3**

### Property 7: Wishlist Add is Idempotent

*For any* user and product, adding a product to the wishlist twice SHALL result in only one wishlist entry, and adding then immediately removing SHALL result in zero wishlist entries.

**Validates: Requirements 5.2, 5.3**

### Property 8: Price Alert Validation Enforces Positive Target Below Current

*For any* price alert, the target price SHALL be validated as a positive number less than the current price, and invalid values (negative, zero, or greater than current) SHALL be rejected.

**Validates: Requirements 6.3**

### Property 9: Price Alert Triggers on Price Drop

*For any* active price alert with target price T and product with current price P, when P drops to or below T, the alert SHALL trigger a notification and deactivate the alert to prevent duplicates.

**Validates: Requirements 6.5, 6.13**

### Property 10: Activity Recording Persists Events

*For any* user action (store visit or purchase), recording the activity SHALL persist the event with user_id, product_id, timestamp, and metadata, and retrieving the user's activity history SHALL include the recorded event.

**Validates: Requirements 7.1, 7.2, 7.4**

### Property 11: Purchase Statistics Calculate Correctly

*For any* set of purchase events for a user, calculating monthly and yearly statistics SHALL correctly sum the product counts, total spending, and savings amounts from those events.

**Validates: Requirements 7.5, 7.6**

### Property 12: Points Award Correctly for Actions

*For any* valid point-earning action (registration, profile completion, purchase, wishlist add, alert set), awarding points SHALL credit the correct amount (100, 50, 10, 5, 5 respectively), update the user's balance, and record a transaction.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 13: Points Redemption Validates Sufficient Balance

*For any* voucher redemption attempt, the system SHALL validate that the user has sufficient points, and SHALL reject redemption if points are insufficient OR deduct points and generate voucher if sufficient.

**Validates: Requirements 8.11**

### Property 14: Referral Codes are Unique Per User

*For any* registered users, each user SHALL have a unique referral code, and generating codes for multiple users SHALL never produce duplicate codes.

**Validates: Requirements 9.1**

### Property 15: Referral Rewards Award Correct Points

*For any* valid referral (new user registers with referrer's code), the system SHALL award 50 points to the referrer and 25 points to the new user, and SHALL prevent users from using their own referral codes.

**Validates: Requirements 9.5, 9.6, 9.9**

### Property 16: Referral Code Validation is Accurate

*For any* referral code, validation SHALL return true if the code exists and belongs to an active user, and SHALL return false for non-existent, expired, or self-referral codes.

**Validates: Requirements 9.8**

### Property 17: Analytics Total Savings Calculation is Correct

*For any* set of purchases, calculating total savings SHALL sum (original_price - paid_price) for all purchases where original_price exists, and SHALL return 0 for empty purchase history.

**Validates: Requirements 11.2**

### Property 18: Phone Number Validation Enforces Format

*For any* phone number input, validation SHALL accept strings containing only digits with length 10-15, and SHALL reject strings with non-digit characters or length outside the range.

**Validates: Requirements 12.6**

### Property 19: JWT Token Validation Detects Invalid Tokens

*For any* JWT token (valid, expired, malformed, or tampered), token validation SHALL correctly identify valid tokens and reject invalid ones with appropriate error messages.

**Validates: Requirements 16.2**

### Property 20: Input Sanitization Prevents SQL Injection

*For any* user input containing SQL injection patterns (e.g., `'; DROP TABLE users; --`), parameterized queries SHALL treat the input as data and NOT execute it as SQL commands.

**Validates: Requirements 16.5**

### Property 21: Input Sanitization Prevents XSS Attacks

*For any* user input containing XSS attack patterns (e.g., `<script>alert('XSS')</script>`), the system SHALL escape or strip the malicious content before storage or display.

**Validates: Requirements 16.6**


## Error Handling

### Error Response Format

All API errors follow a consistent JSON format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource successfully created
- **400 Bad Request**: Invalid input or validation error
- **401 Unauthorized**: Missing, invalid, or expired authentication token
- **403 Forbidden**: Authenticated but lacking required permissions
- **404 Not Found**: Requested resource does not exist
- **409 Conflict**: Resource conflict (e.g., duplicate email)
- **422 Unprocessable Entity**: Validation error from Pydantic
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error

### Error Handling Strategy

**Client Errors (4xx):**
- Return specific error messages that help users correct their input
- Never expose sensitive information (e.g., whether email exists)
- Log for monitoring but don't alert

**Server Errors (5xx):**
- Return generic error message to client
- Log detailed error with stack trace
- Alert operations team for critical errors
- Include request ID for troubleshooting

**Database Errors:**
```python
try:
    result = await db.fetchrow(query, *params)
except asyncpg.UniqueViolationError:
    raise HTTPException(status_code=409, detail="Resource already exists")
except asyncpg.PostgresError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database operation failed")
```

**Validation Errors:**
```python
# Pydantic automatically validates and returns 422 with field-level errors
class RegisterRequest(BaseModel):
    email: EmailStr  # Auto-validates email format
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
```

**Authentication Errors:**
```python
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Rate Limiting:**
```python
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    # If limit exceeded, slowapi automatically returns 429
    pass
```

### Graceful Degradation

**Cache Failures:**
- If Redis cache is unavailable, fallback to database queries
- Log warning but continue serving requests

**External Service Failures:**
- If scraper fails, return cached results
- If notification service fails, queue for retry

**Database Connection Pool Exhaustion:**
- Return 503 Service Unavailable
- Alert operations team
- Implement circuit breaker pattern

## Testing Strategy

### Testing Approach

PricePilot comprehensive features require a multi-layered testing strategy:

1. **Property-Based Testing (PBT)**: Verify universal properties across randomized inputs
2. **Example-Based Unit Testing**: Test specific scenarios and edge cases
3. **Integration Testing**: Test component interactions and database operations
4. **API Testing**: Test HTTP endpoints with real requests
5. **Performance Testing**: Verify response time and scalability requirements

### Property-Based Testing Configuration

**Library**: [Hypothesis](https://hypothesis.readthedocs.io/) for Python

**Configuration:**
```python
from hypothesis import given, strategies as st, settings

# Run each property test with minimum 100 iterations
@settings(max_examples=100, deadline=2000)  # 2 second timeout per example
@given(
    email=st.emails(),
    password=st.text(min_size=8).filter(lambda p: any(c.isdigit() for c in p))
)
def test_property_user_registration_creates_valid_account(email, password):
    """
    Property 1: User Registration Creates Valid Account with Token
    Feature: pricepilot-comprehensive-features, Property 1
    """
    # Test implementation
    pass
```

**Tag Format**: Each property test includes a comment with:
```python
"""
Property {number}: {property_title}
Feature: pricepilot-comprehensive-features, Property {number}: {property_text}
"""
```

### Unit Testing Strategy

**Example-Based Tests:**
- Test specific edge cases (empty strings, boundary values, null handling)
- Test error conditions (invalid input, missing required fields)
- Test business logic with concrete examples

**Test Organization:**
```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_points_service.py
│   ├── test_deal_score_engine.py
│   ├── test_activity_tracker.py
│   └── ...
├── properties/
│   ├── test_auth_properties.py
│   ├── test_points_properties.py
│   ├── test_analytics_properties.py
│   └── ...
├── integration/
│   ├── test_auth_flow.py
│   ├── test_wishlist_integration.py
│   ├── test_alert_system.py
│   └── ...
└── api/
    ├── test_auth_endpoints.py
    ├── test_product_endpoints.py
    └── ...
```

**Key Unit Tests:**

1. **Authentication:**
   - Valid registration creates account
   - Duplicate email returns error
   - Invalid password format rejected
   - Login with wrong password fails
   - JWT token generation and verification

2. **Points System:**
   - Each action type awards correct points
   - Insufficient balance prevents redemption
   - Point transactions recorded correctly
   - Balance calculations accurate

3. **Deal Score:**
   - Score bounded between 0-100
   - Weighted formula applied correctly
   - Missing data handled gracefully

4. **Referrals:**
   - Unique code generation
   - Code validation
   - Points awarded to both parties
   - Self-referral prevented

5. **Analytics:**
   - Savings calculation correct
   - Category breakdown accurate
   - Trend calculations handle missing data

### Integration Testing

**Database Integration:**
```python
@pytest.fixture
async def test_db():
    """Provide test database connection"""
    pool = await create_test_pool()
    yield pool
    await pool.close()

async def test_wishlist_integration(test_db):
    """Test complete wishlist add/remove flow"""
    # Create test user
    user = await create_test_user(test_db)
    # Create test product
    product = await create_test_product(test_db)
    # Add to wishlist
    result = await wishlist_service.add_to_wishlist(user.id, product.id)
    assert result == True
    # Verify in database
    wishlist = await wishlist_service.get_user_wishlist(user.id)
    assert len(wishlist) == 1
    # Remove from wishlist
    result = await wishlist_service.remove_from_wishlist(user.id, product.id)
    assert result == True
    # Verify removed
    wishlist = await wishlist_service.get_user_wishlist(user.id)
    assert len(wishlist) == 0
```

**Background Job Testing:**
```python
async def test_price_alert_checker():
    """Test price alert background job"""
    # Create alert with target $100
    alert = await create_test_alert(target_price=100.00)
    # Update product price to $95
    await update_product_price(alert.product_id, 95.00)
    # Run background job
    triggered_count = await price_alert_service.check_price_alerts()
    assert triggered_count == 1
    # Verify notification created
    notifications = await notification_service.get_user_notifications(alert.user_id)
    assert len(notifications) == 1
    # Verify alert deactivated
    updated_alert = await price_alert_service.get_alert(alert.id)
    assert updated_alert.is_active == False
```

### API Testing

**FastAPI TestClient:**
```python
from fastapi.testclient import TestClient

def test_register_endpoint():
    """Test POST /auth/register"""
    client = TestClient(app)
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["email"] == "test@example.com"
    assert data["points_balance"] == 100  # Welcome bonus

def test_protected_endpoint_requires_auth():
    """Test authentication middleware"""
    client = TestClient(app)
    response = client.get("/wishlist")
    assert response.status_code == 401
```

### Performance Testing

**Load Testing with Locust:**
```python
from locust import HttpUser, task, between

class PricePilotUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before running tasks"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["token"]
    
    @task(3)
    def view_home(self):
        self.client.get("/products/home", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(2)
    def search_products(self):
        self.client.get("/products/search?q=laptop", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def view_wishlist(self):
        self.client.get("/wishlist", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

**Performance Goals:**
- 95% of requests respond within 2 seconds
- Support 100+ concurrent users
- Home page loads within 1 second
- Search tier 1 results within 3 seconds

### Test Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Property Tests**: All identified properties (21 properties)
- **Integration Tests**: All critical user flows
- **API Tests**: All endpoints with happy path and error cases

### Continuous Integration

**GitHub Actions Workflow:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      
      mongodb:
        image: mongo:6
        options: >-
          --health-cmd "mongosh --eval 'db.runCommand({ping:1})'"
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov hypothesis
      
      - name: Run unit tests
        run: pytest tests/unit --cov=app --cov-report=xml
      
      - name: Run property tests
        run: pytest tests/properties --hypothesis-profile=ci
      
      - name: Run integration tests
        run: pytest tests/integration
      
      - name: Run API tests
        run: pytest tests/api
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```


## Security Considerations

### Authentication & Authorization

**JWT Token Security:**
- Tokens signed with HS256 algorithm using strong secret key (256-bit minimum)
- Token expiry set to 24 hours
- Payload includes only necessary claims: user_id, email, role, exp, iat
- Token refresh mechanism for seamless user experience
- Optional token blacklist for logout (using Redis with TTL)

**Password Security:**
- Bcrypt hashing with cost factor 12 (2^12 = 4096 rounds)
- Passwords never stored in plain text
- Minimum 8 characters with at least one number requirement
- Rate limiting on login (5 attempts/minute) and registration (3 attempts/minute)

**Role-Based Access Control (RBAC):**
```python
def require_role(required_role: str):
    """Decorator to enforce role-based access control"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            token = extract_token(request)
            payload = decode_token(token)
            if payload.get("role") != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@router.get("/admin/stats")
@require_role("admin")
async def get_admin_stats():
    pass
```

### Input Validation & Sanitization

**SQL Injection Prevention:**
- Always use parameterized queries with asyncpg
- Never concatenate user input into SQL strings
- Use Pydantic models for automatic type validation

```python
# ✅ SAFE - Parameterized query
await db.fetchrow("SELECT * FROM users WHERE email = $1", user_email)

# ❌ UNSAFE - String concatenation
await db.fetchrow(f"SELECT * FROM users WHERE email = '{user_email}'")
```

**XSS Prevention:**
- Escape HTML in user-generated content before display
- Use Content Security Policy (CSP) headers
- Validate and sanitize all string inputs

```python
import html

def sanitize_text(text: str) -> str:
    """Escape HTML to prevent XSS"""
    return html.escape(text)
```

**CORS Configuration:**
```python
# Production: Restrict to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pricepilot.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

**SlowAPI Configuration:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Per-endpoint limits:
# /auth/register: 3/minute (prevent spam)
# /auth/login: 5/minute (prevent brute force)
# /products/search: 20/minute (prevent scraper abuse)
# Default: 100/minute (general protection)
```

### Data Privacy

**PII Handling:**
- Email addresses encrypted at rest (optional)
- Phone numbers stored with minimal access
- User data deletion on account closure (GDPR compliance)
- Activity tracking anonymized for analytics

**Logging:**
- Never log passwords, tokens, or sensitive data
- Log request IDs for troubleshooting
- Implement log retention policy (90 days)

**Data Retention:**
- Inactive accounts (2 years no login) flagged for deletion
- Soft delete with 30-day recovery window
- Automated purge of deleted accounts after recovery period

## Performance Optimization

### Database Optimization

**Indexing Strategy:**
```sql
-- Frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_wishlists_user ON wishlists(user_id);
CREATE INDEX idx_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_products_search ON products USING GIN(search_vector);

-- Composite indexes for common queries
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) 
    WHERE is_read = FALSE;
CREATE INDEX idx_activity_user_date ON activity_events(user_id, created_at DESC);
```

**Query Optimization:**
- Use EXPLAIN ANALYZE to identify slow queries
- Avoid SELECT * (fetch only needed columns)
- Use LIMIT for pagination
- Implement database connection pooling (5-20 connections)

**Connection Pooling:**
```python
async def create_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        command_timeout=60,
        max_cached_statement_lifetime=0,
        max_cacheable_statement_size=1024
    )
```

### Caching Strategy

**Redis Caching:**
```python
# Home page products (cache for 1 hour)
cache_key = "home:products:v1"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

products = await fetch_home_products()
await redis.setex(cache_key, 3600, json.dumps(products))
return products

# Search results (cache for 24 hours)
cache_key = f"search:{query}:tier1"
# Similar pattern
```

**Cache Invalidation:**
- Time-based expiry (TTL)
- Manual invalidation on data updates
- Cache warming for frequently accessed data

### API Response Optimization

**Pagination:**
```python
@router.get("/products/search")
async def search_products(
    query: str,
    page: int = 1,
    limit: int = 20  # Default 20, max 50
):
    if limit > 50:
        limit = 50
    offset = (page - 1) * limit
    
    results = await db.fetch(
        "SELECT * FROM products WHERE ... LIMIT $1 OFFSET $2",
        limit, offset
    )
    return PaginatedResponse(results=results, page=page, limit=limit)
```

**Response Compression:**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Async Operations:**
- Use async/await throughout for non-blocking I/O
- Parallel database queries where possible
- Background job processing for heavy tasks

### Image Optimization

**Image Handling:**
- Serve images via CDN (Cloudinary, AWS S3 + CloudFront)
- Lazy loading on mobile app
- Thumbnail generation for list views
- WebP format for modern browsers

## Monitoring & Observability

### Logging

**Structured Logging:**
```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log with context
logger.info("User registered", extra={
    "user_id": user_id,
    "email": email,
    "referral_code": referral_code
})
```

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Something unexpected but handled
- ERROR: Errors that need attention
- CRITICAL: System-level failures

### Metrics

**Key Metrics to Track:**

**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx errors)
- Active users (current connections)

**Business Metrics:**
- User registrations per day
- Daily active users (DAU)
- Searches performed
- Wishlists created
- Price alerts set
- Points awarded/redeemed
- Referrals successful

**System Metrics:**
- CPU usage
- Memory usage
- Database connection pool utilization
- Query execution time
- Cache hit rate

### Health Checks

```python
@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow()}

@router.get("/health/detailed")
async def detailed_health_check(db: asyncpg.Connection = Depends(get_db)):
    """Detailed health check with dependency verification"""
    checks = {
        "api": "ok",
        "postgres": "unknown",
        "mongodb": "unknown",
        "redis": "unknown"
    }
    
    # Check PostgreSQL
    try:
        await db.fetchval("SELECT 1")
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)}"
    
    # Check MongoDB
    try:
        mongo_db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
    
    overall_status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow()
    }
```

### Alerting

**Alert Conditions:**
- API error rate > 5% for 5 minutes
- Response time p95 > 5 seconds for 5 minutes
- Database connection pool > 90% utilization
- Failed scraper jobs (critical stores down)
- Disk space < 10% free

**Alert Channels:**
- Slack/Discord notifications
- Email for critical alerts
- PagerDuty for on-call rotation

## Deployment Architecture

### Environment Configuration

**Environments:**
1. **Development**: Local development with Docker Compose
2. **Staging**: Pre-production testing environment
3. **Production**: Live user-facing environment

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
MONGODB_URL=mongodb://user:pass@host:27017/dbname
REDIS_URL=redis://host:6379

# JWT
JWT_SECRET_KEY=<256-bit-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://pricepilot.app

# Rate Limiting
RATE_LIMIT_ENABLED=true

# Background Jobs
SCHEDULER_ENABLED=true
DAILY_SCRAPE_HOUR=0  # Midnight UTC

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=<sentry-url>
```

### Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/pricepilot
      - MONGODB_URL=mongodb://mongo:27017/pricepilot
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - mongo
      - redis
  
  postgres:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: pricepilot
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

### Deployment Process

**CI/CD Pipeline:**
1. Run tests (unit, property, integration)
2. Build Docker image
3. Push to container registry
4. Deploy to staging
5. Run smoke tests
6. Deploy to production (blue-green or rolling)
7. Monitor for errors

**Zero-Downtime Deployment:**
- Use health checks in load balancer
- Rolling updates with Kubernetes or ECS
- Database migrations run before deployment
- Rollback plan for failed deployments

## Future Enhancements

### Phase 1 (Current Scope)
- ✅ Authentication and user management
- ✅ Wishlist and price alerts
- ✅ Points and referral system
- ✅ Activity tracking and analytics
- ✅ Admin dashboard

### Phase 2 (Future)
- Push notifications (Firebase Cloud Messaging)
- Social sharing (share deals on social media)
- Product comparison tool (side-by-side)
- Advanced filters (brand, specifications)
- Price prediction ML model

### Phase 3 (Advanced)
- User reviews and ratings
- Community features (forums, discussions)
- Personalized recommendations (collaborative filtering)
- Browser extension for price tracking
- API for third-party integrations

## Appendix

### Database Migration Plan

**Migration Strategy:**
1. Create new tables for features
2. Add columns to existing users table
3. Create indexes
4. Backfill data where needed
5. Test rollback procedures

**Migration Script Example:**
```sql
-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS points_balance INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS referral_code TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES users(id);

-- Create index on referral_code
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);

-- Award welcome bonus to existing users
UPDATE users SET points_balance = 100 WHERE points_balance = 0;

-- Generate referral codes for existing users
-- (Run Python script to generate unique codes)
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/pricepilot-backend
cd pricepilot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Run database migrations
python migrations/run_migrations.py

# Start development server
uvicorn main:app --reload

# Run tests
pytest
```

### Technology Decisions Rationale

**Why FastAPI?**
- High performance (async/await support)
- Automatic API documentation
- Built-in data validation (Pydantic)
- Modern Python features

**Why PostgreSQL for relational data?**
- ACID compliance for critical data (users, transactions)
- Rich indexing capabilities (GIN for full-text search)
- Strong consistency guarantees
- Excellent async support with asyncpg

**Why MongoDB for product data?**
- Flexible schema for varying product attributes
- Efficient time-series storage (price history)
- Horizontal scaling capability
- Good performance for read-heavy workloads

**Why JWT for authentication?**
- Stateless (no server-side session storage)
- Scalable across multiple API servers
- Industry standard
- Easy to implement and verify

**Why Hypothesis for property testing?**
- Most mature property testing library for Python
- Intelligent test case generation
- Shrinking to minimal failing examples
- Good integration with pytest

---

*This design document provides a comprehensive technical specification for implementing the PricePilot comprehensive features. It should be reviewed and updated as the implementation progresses and new insights are gained.*

