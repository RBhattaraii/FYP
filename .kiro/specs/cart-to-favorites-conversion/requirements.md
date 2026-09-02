# Requirements Document

## Introduction

This document defines the requirements for converting the PricePilot shopping cart system to a Favorites/Saved Products feature. PricePilot is a price comparison platform that aggregates product data from multiple stores (Jeevee, Oliz, Daraz, Hukut, Neostore, Hardwarepasal). Users do not purchase products through the app; instead, they save products to compare prices across stores. The current "Shopping Cart" metaphor is misleading and needs to be replaced with a "Favorites" system that better reflects the platform's purpose.

## Glossary

- **Favorites_System**: The new feature that allows users to save products for later comparison
- **Mobile_App**: The React Native (Expo) mobile application
- **Backend_API**: The Python FastAPI server
- **Database**: PostgreSQL database hosted on Supabase
- **Cart_Context**: React context managing cart state in mobile app
- **Storage_Layer**: AsyncStorage for local persistence in mobile app
- **Store**: External e-commerce website (Jeevee, Oliz, Daraz, etc.)
- **Product_Item**: A product from a specific store with price and availability information
- **User**: Authenticated user of the PricePilot platform

## Requirements

### Requirement 1: Rename Database Table and Columns

**User Story:** As a developer, I want the database schema to reflect the Favorites feature, so that the codebase is semantically accurate.

#### Acceptance Criteria

1. THE Backend_API SHALL rename the shopping_cart table to favorites (if exists)
2. THE Backend_API SHALL rename cart_items table to favorite_items (if exists)
3. THE Database SHALL maintain all existing foreign key relationships after renaming
4. THE Database SHALL preserve all existing data during table rename operation
5. WHEN tables do not exist, THE Backend_API SHALL create new favorites table with columns: id, user_id, created_at, updated_at
6. WHEN tables do not exist, THE Backend_API SHALL create new favorite_items table with columns: id, favorite_id, product_id, store_name, product_url, product_title, product_image, price, added_at

### Requirement 2: Update Backend API Endpoints

**User Story:** As a mobile developer, I want REST API endpoints that reflect Favorites terminology, so that the API is intuitive and self-documenting.

#### Acceptance Criteria

1. THE Backend_API SHALL rename POST /cart/add endpoint to POST /favorites/add
2. THE Backend_API SHALL rename DELETE /cart/remove endpoint to DELETE /favorites/remove
3. THE Backend_API SHALL rename GET /cart endpoint to GET /favorites
4. THE Backend_API SHALL rename PUT /cart/update endpoint to PUT /favorites/update (if exists)
5. THE Backend_API SHALL return 200 OK with favorites list when GET /favorites is called with valid auth token
6. THE Backend_API SHALL return 201 Created when POST /favorites/add successfully adds a product
7. THE Backend_API SHALL return 200 OK when DELETE /favorites/remove successfully removes a product
8. THE Backend_API SHALL return 401 Unauthorized when requests lack valid authentication token
9. THE Backend_API SHALL return 404 Not Found when attempting to remove non-existent favorite
10. THE Backend_API SHALL maintain backward compatibility with old cart endpoints for 2 weeks (deprecation period)

### Requirement 3: Remove Quantity Management from Backend

**User Story:** As a product manager, I want quantity controls removed from the Favorites system, so that users understand this is for comparison not purchasing.

#### Acceptance Criteria

1. THE Backend_API SHALL remove quantity field from favorite_items table
2. THE Backend_API SHALL remove quantity parameter from POST /favorites/add endpoint
3. THE Backend_API SHALL remove PUT /favorites/update endpoint (if it only updates quantity)
4. THE Backend_API SHALL return favorite items without quantity field in response payload
5. WHEN existing data contains quantity values, THE Backend_API SHALL ignore those values during migration

### Requirement 4: Remove Checkout Functionality from Backend

**User Story:** As a product manager, I want checkout functionality removed, so that users cannot mistakenly attempt to purchase through PricePilot.

#### Acceptance Criteria

1. THE Backend_API SHALL remove POST /cart/checkout endpoint (if exists)
2. THE Backend_API SHALL remove GET /cart/total endpoint (if exists)
3. THE Backend_API SHALL remove any payment processing integration code
4. THE Backend_API SHALL return 410 Gone when deprecated checkout endpoints are called

### Requirement 5: Update Mobile App Context and State Management

**User Story:** As a mobile developer, I want the CartContext renamed to FavoritesContext, so that the code reflects the correct business domain.

#### Acceptance Criteria

1. THE Mobile_App SHALL rename CartContext.tsx to FavoritesContext.tsx
2. THE Mobile_App SHALL rename CartProvider to FavoritesProvider
3. THE Mobile_App SHALL rename useCart hook to useFavorites
4. THE Mobile_App SHALL rename CartItem interface to FavoriteItem
5. THE Mobile_App SHALL remove quantity property from FavoriteItem interface
6. THE Mobile_App SHALL remove updateQuantity function from FavoritesContext
7. THE Mobile_App SHALL rename STORAGE_KEY from 'pricepilot_cart' to 'pricepilot_favorites'
8. WHEN Storage_Layer contains old 'pricepilot_cart' data, THE Mobile_App SHALL migrate data to 'pricepilot_favorites' key on first launch
9. THE Mobile_App SHALL update all import statements referencing CartContext to FavoritesContext
10. THE Mobile_App SHALL maintain addItem, removeItem, and clearFavorites functions

### Requirement 6: Update Mobile Screen and Navigation

**User Story:** As a user, I want the navigation and screens to say "Favorites" instead of "Cart", so that the purpose is clear.

#### Acceptance Criteria

1. THE Mobile_App SHALL rename cart.tsx screen file to favorites.tsx
2. THE Mobile_App SHALL update tab navigation label from "Cart" to "Favorites"
3. THE Mobile_App SHALL update tab navigation icon from "cart" to "heart" (or "bookmark")
4. THE Mobile_App SHALL update screen header from "Shopping Cart" to "Favorites"
5. THE Mobile_App SHALL update empty state icon from "cart-outline" to "heart-outline"
6. THE Mobile_App SHALL update empty state message to "Your favorites list is empty"
7. WHEN zero items exist, THE Mobile_App SHALL display message "Save products to compare prices later"

### Requirement 7: Update Mobile UI Components

**User Story:** As a user, I want UI elements to reflect the Favorites concept, so that I understand the feature's purpose.

#### Acceptance Criteria

1. THE Mobile_App SHALL rename "Add to Cart" buttons to "Save" or "Add to Favorites"
2. THE Mobile_App SHALL update button icons from "cart-outline" to "heart-outline" or "bookmark-outline"
3. THE Mobile_App SHALL remove quantity increment/decrement controls (+/-) from favorite items
4. THE Mobile_App SHALL remove quantity display from favorite items
5. THE Mobile_App SHALL update DealCard component button text from "Add to Cart" to "Save"
6. THE Mobile_App SHALL update product detail page button text from "Add to Cart" to "Add to Favorites"
7. THE Mobile_App SHALL display "Saved!" or "Added to Favorites!" toast message when product is saved
8. THE Mobile_App SHALL display heart icon in filled state when product is already in favorites

### Requirement 8: Remove Checkout UI and Total Calculation

**User Story:** As a product manager, I want checkout UI removed, so that users focus on price comparison not purchasing.

#### Acceptance Criteria

1. THE Mobile_App SHALL remove "Check Out" button from favorites screen
2. THE Mobile_App SHALL remove subtotal calculation display
3. THE Mobile_App SHALL remove total price display
4. THE Mobile_App SHALL remove item selection checkboxes (used for checkout)
5. THE Mobile_App SHALL remove "Select All" checkbox functionality
6. THE Mobile_App SHALL maintain "Remove" button for each favorite item
7. THE Mobile_App SHALL display product count "X items saved" instead of total price

### Requirement 9: Update API Service Layer in Mobile

**User Story:** As a mobile developer, I want API service functions renamed to match Favorites terminology, so that the codebase is consistent.

#### Acceptance Criteria

1. THE Mobile_App SHALL rename addToCart API function to addToFavorites
2. THE Mobile_App SHALL rename removeFromCart API function to removeFromFavorites
3. THE Mobile_App SHALL rename getCart API function to getFavorites
4. THE Mobile_App SHALL update API endpoint URLs from /cart/* to /favorites/*
5. THE Mobile_App SHALL remove quantity parameter from addToFavorites request body
6. THE Mobile_App SHALL handle 410 Gone responses from deprecated endpoints gracefully

### Requirement 10: Maintain Grouped Display by Store

**User Story:** As a user, I want my saved products grouped by store, so that I can easily compare prices across stores.

#### Acceptance Criteria

1. WHEN favorites screen is displayed, THE Mobile_App SHALL group products by storeName
2. THE Mobile_App SHALL display store name as section header for each group
3. THE Mobile_App SHALL show store logo or icon next to store name (if available)
4. THE Mobile_App SHALL maintain alphabetical ordering of stores
5. THE Mobile_App SHALL display product count for each store "(3 items)"
6. WHEN multiple products from same store exist, THE Mobile_App SHALL display them under single store header

### Requirement 11: Add Compare Functionality

**User Story:** As a user, I want a "Compare Prices" button, so that I can quickly view price differences across stores for saved products.

#### Acceptance Criteria

1. WHEN 2 or more products are saved, THE Mobile_App SHALL display "Compare Prices" button at bottom of favorites screen
2. THE Mobile_App SHALL disable "Compare Prices" button when fewer than 2 products exist
3. WHEN "Compare Prices" button is tapped, THE Mobile_App SHALL navigate to price comparison screen
4. THE Mobile_App SHALL pass all favorite items to comparison screen
5. THE Mobile_App SHALL display button with indigo background and white text
6. THE Mobile_App SHALL show button height of 48px with full width (minus padding)

### Requirement 12: Preserve Product Data Structure

**User Story:** As a developer, I want existing product data structure maintained, so that minimal refactoring is required.

#### Acceptance Criteria

1. THE Favorites_System SHALL maintain product fields: id, productId, title, price, storeName, storeLogoUrl, imageUrl, productUrl
2. THE Favorites_System SHALL remove quantity field from data structure
3. THE Database SHALL preserve created_at and updated_at timestamps for favorites
4. THE Database SHALL preserve added_at timestamp for individual favorite items
5. THE Backend_API SHALL continue returning product data in same JSON structure (minus quantity)

### Requirement 13: Migration Script for Existing Data

**User Story:** As a developer, I want a migration script that converts cart data to favorites, so that existing users don't lose their saved products.

#### Acceptance Criteria

1. THE Backend_API SHALL provide migration script rename_cart_to_favorites.py
2. WHEN migration script is executed, THE Backend_API SHALL rename tables atomically (single transaction)
3. WHEN migration script is executed, THE Backend_API SHALL drop quantity column from favorite_items table
4. WHEN migration script encounters errors, THE Backend_API SHALL rollback all changes
5. THE migration script SHALL log all operations to migration.log file
6. THE migration script SHALL create backup of cart tables before modification
7. WHEN migration completes successfully, THE migration script SHALL output "Migration completed: X users, Y items migrated"

### Requirement 14: Update Mobile Storage Migration

**User Story:** As a user, I want my locally saved cart items automatically migrated to favorites, so that I don't lose my saved products after the update.

#### Acceptance Criteria

1. WHEN Mobile_App launches after update, THE Storage_Layer SHALL check for 'pricepilot_cart' key
2. WHEN 'pricepilot_cart' key exists, THE Mobile_App SHALL read cart items from AsyncStorage
3. WHEN cart items are read, THE Mobile_App SHALL remove quantity field from each item
4. WHEN quantity field is removed, THE Mobile_App SHALL write items to 'pricepilot_favorites' key
5. WHEN write completes successfully, THE Mobile_App SHALL delete 'pricepilot_cart' key
6. WHEN migration fails, THE Mobile_App SHALL retry on next app launch
7. THE Mobile_App SHALL log migration status to console for debugging

### Requirement 15: Update Documentation and Comments

**User Story:** As a developer, I want code comments and documentation updated, so that new team members understand the Favorites system.

#### Acceptance Criteria

1. THE Mobile_App SHALL update all code comments referencing "cart" to "favorites"
2. THE Backend_API SHALL update all code comments referencing "cart" to "favorites"
3. THE Backend_API SHALL update API documentation (if using OpenAPI/Swagger)
4. THE Backend_API SHALL update README files with new endpoint names
5. THE Mobile_App SHALL update component JSDoc comments with Favorites terminology

## Non-Functional Requirements

### NFR1: Backward Compatibility

**Priority:** High  
**Description:** The system must maintain temporary backward compatibility to prevent breaking existing mobile app versions.

#### Acceptance Criteria

1. WHEN old cart endpoints are called, THE Backend_API SHALL forward requests to favorites endpoints
2. THE Backend_API SHALL return 200 OK with deprecation warning header for old endpoints
3. THE Backend_API SHALL maintain old endpoints for minimum 14 days after deployment
4. WHEN deprecation period ends, THE Backend_API SHALL return 410 Gone for old endpoints
5. THE Backend_API SHALL log usage of deprecated endpoints for monitoring

### NFR2: Data Integrity

**Priority:** High  
**Description:** The migration must preserve all existing user data without loss or corruption.

#### Acceptance Criteria

1. THE migration script SHALL complete in single database transaction
2. WHEN migration fails at any step, THE Database SHALL rollback all changes
3. THE migration script SHALL verify row count before and after migration
4. THE migration script SHALL create timestamped backup before starting
5. WHEN data validation fails, THE migration script SHALL abort and report errors

### NFR3: Performance

**Priority:** High  
**Description:** The Favorites system must maintain or improve current performance.

#### Acceptance Criteria

1. THE Backend_API SHALL respond to GET /favorites in less than 500ms
2. THE Backend_API SHALL respond to POST /favorites/add in less than 300ms
3. THE Mobile_App SHALL render favorites screen in less than 200ms
4. THE Mobile_App SHALL update UI optimistically when adding/removing favorites
5. THE Mobile_App SHALL maintain 60 FPS scroll performance on favorites screen

### NFR4: Testing

**Priority:** High  
**Description:** All changes must be thoroughly tested before deployment.

#### Acceptance Criteria

1. THE Backend_API SHALL have unit tests for all favorites endpoints
2. THE Backend_API SHALL have integration tests for database migration
3. THE Mobile_App SHALL have unit tests for FavoritesContext
4. THE Mobile_App SHALL have integration tests for favorites screen
5. THE Mobile_App SHALL have E2E tests for add/remove favorites flow
6. THE migration script SHALL be tested on copy of production database
7. WHEN all tests pass, THE development team SHALL approve for deployment

### NFR5: User Experience

**Priority:** High  
**Description:** The transition from Cart to Favorites must be seamless for users.

#### Acceptance Criteria

1. WHEN user updates app, THE Mobile_App SHALL migrate local storage automatically
2. WHEN user opens favorites screen, THE Mobile_App SHALL display all previously saved items
3. THE Mobile_App SHALL show one-time tooltip explaining new Favorites feature (optional)
4. THE Mobile_App SHALL maintain familiar UI layout and interactions
5. WHEN user taps "Save" button, THE Mobile_App SHALL provide immediate visual feedback

### NFR6: Accessibility

**Priority:** Medium  
**Description:** The Favorites system must be accessible to users with disabilities.

#### Acceptance Criteria

1. THE Mobile_App SHALL provide screen reader labels for all favorites buttons
2. THE Mobile_App SHALL use "Add to favorites" and "Remove from favorites" accessibility labels
3. THE Mobile_App SHALL maintain 44px minimum touch target size for all buttons
4. THE Mobile_App SHALL maintain WCAG AA color contrast ratios
5. THE Mobile_App SHALL announce "Added to favorites" via screen reader

## Data Requirements

### DR1: Favorites Table Schema

**Table Name:** favorites  
**Description:** Stores user favorites collection

**Columns:**
- `id`: UUID, primary key
- `user_id`: UUID, foreign key to users table, NOT NULL
- `created_at`: timestamp, default NOW()
- `updated_at`: timestamp, default NOW()

**Indexes:**
- Primary key on `id`
- Index on `user_id`
- Index on `created_at`

### DR2: Favorite Items Table Schema

**Table Name:** favorite_items  
**Description:** Stores individual products in favorites

**Columns:**
- `id`: UUID, primary key
- `favorite_id`: UUID, foreign key to favorites table, NOT NULL
- `product_id`: UUID, foreign key to products table, NULLABLE
- `store_name`: VARCHAR(100), NOT NULL
- `product_url`: TEXT, NOT NULL
- `product_title`: VARCHAR(500), NOT NULL
- `product_image`: TEXT, NULLABLE
- `price`: DECIMAL(10,2), NOT NULL
- `added_at`: timestamp, default NOW()

**Indexes:**
- Primary key on `id`
- Index on `favorite_id`
- Index on `product_id`
- Index on `added_at`

**Removed Fields:**
- `quantity` (removed - not needed for comparison)

### DR3: Mobile FavoriteItem Interface

**Interface Name:** FavoriteItem  
**Location:** mobile/context/FavoritesContext.tsx

**Fields:**
```typescript
interface FavoriteItem {
  id: string;              // unique key: `${store_name}-${product_url}`
  productId?: number;      // from DB if available
  title: string;
  price: number;
  storeName: string;
  storeLogoUrl?: string;
  imageUrl?: string;
  productUrl: string;
  // quantity field REMOVED
}
```

## API Requirements

### API1: Add Product to Favorites

**Endpoint:** POST /favorites/add  
**Authentication:** Required (JWT Bearer token)

**Request Body:**
```json
{
  "product_id": "uuid",          // optional
  "store_name": "Jeevee",
  "product_url": "https://...",
  "product_title": "Product Name",
  "product_image": "https://...", // optional
  "price": 99.99
}
```

**Response:** 201 Created
```json
{
  "success": true,
  "message": "Product added to favorites",
  "favorite_item_id": "uuid"
}
```

**Error Responses:**
- 400 Bad Request: Invalid request body
- 401 Unauthorized: Missing or invalid token
- 409 Conflict: Product already in favorites
- 500 Internal Server Error

### API2: Remove Product from Favorites

**Endpoint:** DELETE /favorites/remove  
**Authentication:** Required (JWT Bearer token)

**Request Body:**
```json
{
  "favorite_item_id": "uuid"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Product removed from favorites"
}
```

**Error Responses:**
- 400 Bad Request: Invalid favorite_item_id
- 401 Unauthorized: Missing or invalid token
- 404 Not Found: Favorite item not found
- 500 Internal Server Error

### API3: Get User Favorites

**Endpoint:** GET /favorites  
**Authentication:** Required (JWT Bearer token)

**Query Parameters:**
- `user_id`: UUID (optional, defaults to authenticated user)

**Response:** 200 OK
```json
{
  "favorites": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "store_name": "Jeevee",
      "product_url": "https://...",
      "product_title": "Product Name",
      "product_image": "https://...",
      "price": 99.99,
      "added_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 15
}
```

**Error Responses:**
- 401 Unauthorized: Missing or invalid token
- 500 Internal Server Error

### API4: Deprecated Cart Endpoints (Temporary)

**Endpoints:** POST /cart/add, DELETE /cart/remove, GET /cart  
**Deprecation Period:** 14 days  
**Behavior:** Forward to /favorites/* endpoints

**Response Headers:**
```
Deprecation: true
Sunset: Wed, 31 Jan 2024 23:59:59 GMT
Link: </favorites/*>; rel="successor-version"
```

## Dependencies

### Backend Dependencies
- PostgreSQL (Supabase) - Database
- FastAPI - Web framework
- SQLAlchemy - ORM for database operations
- Alembic - Database migration tool
- python-dotenv - Environment variables

### Mobile Dependencies
- React Native (Expo) - Mobile framework
- AsyncStorage - Local storage
- expo-router - Navigation
- Ionicons - Icon library
- TypeScript - Type safety

### Migration Dependencies
- psycopg2 - PostgreSQL adapter for Python
- Alembic - Migration script execution

## Constraints

### Technical Constraints
- Must work with existing PostgreSQL database on Supabase
- Must maintain compatibility with React Native 0.72+
- Must use Expo SDK 54
- Must not break existing authentication flow
- Migration must be reversible (rollback capability)

### Business Constraints
- Must complete migration during low-traffic window
- Must not lose any user data
- Must maintain app functionality during transition
- Must support users on old app version for 14 days
- Must complete feature in single sprint (2 weeks)

### Design Constraints
- Must maintain existing indigo color scheme
- Must keep familiar UI layout
- Must use heart or bookmark icon (consistent with favorites concept)
- Must not introduce new navigation patterns

## Success Metrics

### User Adoption
- **Target:** 90% of active users successfully migrate to Favorites
- **Target:** Zero data loss during migration
- **Target:** Less than 5% user confusion reports

### Technical Performance
- **Target:** API response times maintain current performance (≤500ms)
- **Target:** Mobile app performance maintains 60 FPS
- **Target:** Zero downtime during deployment
- **Target:** Migration script completes in less than 5 minutes

### Code Quality
- **Target:** 100% of deprecated cart references removed from codebase
- **Target:** 90% test coverage for new favorites code
- **Target:** Zero critical bugs reported in first week

## Out of Scope

The following features are explicitly out of scope for this refactoring:

1. **Price History Tracking**: Tracking price changes over time
2. **Price Drop Alerts**: Notifications when favorited products go on sale
3. **Favorites Sharing**: Sharing favorites list with other users
4. **Favorites Categories**: Organizing favorites into custom categories
5. **Bulk Actions**: Select multiple favorites for bulk operations
6. **Favorites Export**: Exporting favorites list to CSV or PDF
7. **Favorites Limit**: Maximum number of items per user
8. **Social Features**: Comments, likes, or ratings on favorites
9. **Smart Recommendations**: ML-based suggestions based on favorites
10. **Comparison Screen**: Detailed side-by-side price comparison UI (separate feature)

## Assumptions

1. **Existing cart functionality works:** Current cart system is functional and tested
2. **Database access:** Development team has full access to Supabase database
3. **Testing environment:** Staging environment mirrors production database structure
4. **User base size:** Migration script can handle current user base (<10,000 users)
5. **No concurrent cart operations:** Migration runs during low-traffic window
6. **Mobile app update:** Users will update app within 14-day deprecation period
7. **No external cart integrations:** No third-party services depend on cart endpoints
8. **Single favorites list per user:** Users have one favorites collection (not multiple lists)

## Risks & Mitigations

### Risk 1: Data Loss During Migration

**Impact:** High - Users lose saved products  
**Probability:** Low  
**Mitigation:**
- Create database backup before migration
- Run migration in single transaction with rollback capability
- Test migration on copy of production database
- Verify row counts before and after migration
- Keep backup for 30 days post-migration

### Risk 2: Mobile Storage Migration Failure

**Impact:** Medium - Users lose locally saved items  
**Probability:** Medium  
**Mitigation:**
- Keep old 'pricepilot_cart' data until successful migration
- Retry migration on next app launch if first attempt fails
- Log migration errors for debugging
- Provide manual sync button if automatic migration fails

### Risk 3: Breaking Old App Versions

**Impact:** High - Users on old version cannot use app  
**Probability:** Low  
**Mitigation:**
- Maintain deprecated cart endpoints for 14 days
- Return clear deprecation headers
- Force update notification after 7 days
- Gradual rollout (10% → 50% → 100%)

### Risk 4: API Endpoint Confusion

**Impact:** Low - Developers use wrong endpoints  
**Probability:** Medium  
**Mitigation:**
- Update API documentation immediately
- Add code comments with new endpoint names
- Update example queries in README
- Announce change in team communication channels

### Risk 5: User Confusion About Feature Change

**Impact:** Medium - Users don't understand new terminology  
**Probability:** Medium  
**Mitigation:**
- Show one-time tooltip explaining Favorites on first launch
- Use familiar heart/bookmark icons
- Maintain similar UI layout and interactions
- Include change in app update notes
- Provide in-app help text

### Risk 6: Performance Degradation

**Impact:** High - Slow favorites loading  
**Probability:** Low  
**Mitigation:**
- Maintain existing database indexes on renamed tables
- Test API performance with realistic data volume
- Implement client-side caching (AsyncStorage)
- Monitor API response times post-deployment
- Optimize queries if needed
