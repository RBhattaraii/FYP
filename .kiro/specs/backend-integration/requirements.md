# Backend-Frontend Integration Requirements

## Overview
Integrate the PricePilot backend with the React Native frontend using real scraped product data. The system should scrape e-commerce platforms daily to curate best deals for the home screen, and provide real-time search with caching.

## Data Flow Strategy

### Home Screen Data Flow
1. **Daily Scraping**: Scrape homepage of all platforms once per day (e.g., midnight)
2. **Analysis**: Process scraped data to identify best deals and top price drops
3. **Curation**: Store only 30-50 curated products in PostgreSQL
4. **Display**: Home screen fetches curated products from PostgreSQL
5. **Refresh**: Replace curated products with new data on next daily scrape

### Search Data Flow
1. **User Search**: User searches for a product (e.g., "laptop")
2. **Real-time Scraping**: Scrape all platforms for that search query
3. **Caching**: Store search results in PostgreSQL with 24-hour expiry
4. **Subsequent Searches**: Serve from cache if query exists and not expired
5. **Cache Invalidation**: Clear expired cache entries automatically

### MongoDB Usage
MongoDB will store **metadata only**:
- Scraping logs (timestamp, platform, success/failure)
- Scraping statistics (products found, errors encountered)
- NOT storing full product data (to save storage)

## Functional Requirements

### FR1: Daily Homepage Scraping
**Description**: System must scrape homepage/landing page of all e-commerce platforms once per day

**Acceptance Criteria**:
- Scraping runs automatically at midnight (00:00)
- Scrapes **homepage/landing page ONLY** (featured products, deals section) - NOT entire store catalog
- Supports 11 platforms: Daraz, Better, CGDigital, HardwarePasal, Hukut, Jeevee, NeoStore, Oliz, UfoNepal, Hamrobazar, Sastodeal
- Scraping can be triggered manually via API for testing
- System checks last scrape time before running (don't scrape if already done today)
- Logs scraping results to MongoDB (success/failure, products found, duration)
- Each platform scrapes 20-50 featured products from homepage only

**Priority**: Critical

---

### FR2: Product Curation and Analysis
**Description**: System must analyze scraped products to identify best deals and top price drops

**Acceptance Criteria**:
- Identifies "Best Deals" based on discount percentage (>30% off)
- Identifies "Top Price Drops" based on price reduction from typical price
- Limits curated products to 50 total (25 Best Deals + 25 Top Price Drops)
- Products must have: title, price, original_price, discount_percent, image, store, URL
- Products are categorized (Electronics, Fashion, Home, Beauty, Sports, etc.)
- Duplicate products across platforms are handled intelligently

**Priority**: Critical

---

### FR3: PostgreSQL Storage for Home Screen
**Description**: Store curated products in PostgreSQL for fast home screen loading

**Acceptance Criteria**:
- Table: `home_screen_products` with columns: id, section (best_deals/top_price_drops), title, price, original_price, discount_percent, image_url, store_name, product_url, category, scraped_at
- Table: `scrape_metadata` with columns: id, last_scrape_time, next_scrape_time, status, products_found
- Old curated products are replaced on each daily scrape (not accumulated)
- Data persists until next daily scrape

**Priority**: Critical

---

### FR4: Home Screen API Endpoint
**Description**: Provide API endpoint to fetch curated products for home screen

**Acceptance Criteria**:
- Endpoint: `GET /products/home`
- Returns JSON with two sections: `best_deals` (array) and `top_price_drops` (array)
- Each product includes: id, title, price, original_price, discount_percent, image_url, store_name, product_url, category
- Endpoint is fast (<500ms response time)
- Returns empty arrays if no data available
- No authentication required (public endpoint)

**Priority**: Critical

---

### FR5: Tiered Real-time Search with Progressive Results
**Description**: Provide search functionality with tiered scraping for optimal user experience

**User Story**: As a user, I want to see search results quickly from fast platforms first, then get additional results from other platforms, so that I don't have to wait for all platforms to finish scraping.

**Acceptance Criteria**:
- Endpoint: `GET /products/search?q=laptop`
- **Tiered Search Strategy**:
  - **Tier 1 (Priority)**: Daraz, Sastodeal, Oliz - scrape these first (fastest platforms, 1-2 seconds)
  - **Tier 2 (Background)**: Remaining 8 platforms - scrape concurrently in background
- **Progressive Response Flow**:
  - Step 1: Scrape Tier 1 platforms, return results immediately (~1-2s response time)
  - Step 2: Continue scraping Tier 2 platforms in background
  - Step 3: Frontend polls for additional results or uses WebSocket/SSE for real-time updates
- **Caching**: 
  - First search for a query: scrapes all tiers, returns Tier 1 immediately, updates cache with Tier 2 results
  - Subsequent searches: returns full cached results if query exists and not expired (24 hours)
  - Cache table: `search_cache` with columns: id, query, tier1_results (JSONB), tier2_results (JSONB), tier1_cached_at, tier2_cached_at, is_complete (boolean)
- **Cache Expiration**: Expired cache entries (>24 hours) are cleaned up periodically
- Returns array of products with source platform indicated
- Each tier returns consistent product structure: title, price, original_price, discount_percent, image_url, store_name, product_url, category

**Priority**: Critical

---

### FR5a: Progressive Search Results Polling (Frontend)
**Description**: Frontend polls for additional search results from Tier 2 platforms

**User Story**: As a user, I want to see results from fast platforms immediately, then see more results appear as other platforms finish scraping, so that the app feels responsive.

**Acceptance Criteria**:
- After receiving Tier 1 results, frontend checks if search is complete
- If not complete, frontend polls `GET /products/search/status?query=laptop&requestId=xyz` every 2 seconds
- Status endpoint returns: `{ is_complete: boolean, new_results_count: number }`
- When complete or after 6 polls (12 seconds), stop polling
- Display "Loading more results..." indicator while Tier 2 scraping continues
- New results are appended to existing results list
- User can scroll and interact with Tier 1 results while Tier 2 loads

**Priority**: High

---

### FR6: User Profile API Endpoint
**Description**: Provide endpoint to fetch logged-in user's profile information

**Acceptance Criteria**:
- Endpoint: `GET /auth/me`
- Requires JWT token in Authorization header
- Returns user info: id, email, full_name, created_at
- Returns 401 if token invalid or expired
- Used by home screen to display user's first name in greeting

**Priority**: High

---

### FR7: Frontend Home Screen Integration
**Description**: Update mobile app home screen to display real data from backend

**Acceptance Criteria**:
- Fetches products from `GET /products/home` on screen load
- Displays "Best Deals" section with real products
- Displays "Top Price Drops" section with real products
- Shows loading indicator while fetching data
- Handles errors gracefully (shows error message if API fails)
- Replaces dummy data in `mockData.ts` with API calls

**Priority**: Critical

---

### FR8: Frontend Header Integration
**Description**: Update Header component to display logged-in user's real name

**Acceptance Criteria**:
- Fetches user profile from `GET /auth/me` on home screen load
- Displays first name in greeting (e.g., "Hello, John")
- Falls back to generic greeting if API fails
- Caches user name locally to avoid repeated API calls
- Shows loading state while fetching

**Priority**: Medium

---

### FR9: Manual Scraping Trigger (Testing)
**Description**: Provide endpoint to manually trigger scraping for testing

**Acceptance Criteria**:
- Endpoint: `POST /scraper/trigger`
- Admin-only (requires valid JWT token)
- Triggers immediate scraping of all platforms
- Returns scraping results (success/failure, products found)
- Does not respect 24-hour timer (force scrape)

**Priority**: Low (nice to have for testing)

---

## Non-Functional Requirements

### NFR1: Performance
- Home screen API response time: <500ms
- **Search API Tier 1 response time: <2s** (Daraz, Sastodeal, Oliz)
- **Search API Tier 2 completion time: <10s** (all 11 platforms)
- Cached search results: <200ms response time
- Daily scraping completes within 10 minutes
- Search status polling endpoint: <100ms response time

### NFR2: Reliability
- If one platform scraper fails, others continue
- System recovers gracefully from scraping errors
- Cache prevents overload from repeated searches

### NFR3: Scalability
- System can handle 100 concurrent home screen requests
- Database can store 30 days of scraping logs
- Cache grows proportionally to unique search queries

### NFR4: Maintainability
- Clear separation between scraping logic and API logic
- Easy to add new platforms
- Logs provide debugging information

---

## Platforms to Scrape (11 Total)

### Tier 1 - Priority Platforms (Fast, Scrape First)
1. **Daraz** (daraz.com.np) - Fastest, most reliable
2. **Sastodeal** (sastodeal.com) - Fast API-based
3. **Oliz** (olizstore.com) - Quick response time

### Tier 2 - Background Platforms (Scrape Concurrently)
4. **Better** (better.com.np)
5. **CGDigital** (cgdigital.com.np)
6. **HardwarePasal** (hardwarepasal.com)
7. **Hukut** (hukut.com)
8. **Jeevee** (jeevee.com.np)
9. **NeoStore** (neostore.com.np)
10. **UfoNepal** (ufonepal.com.np)
11. **Hamrobazar** (hamrobazar.com)

**Note**: Tier assignment based on scraper speed and reliability. Can be adjusted based on testing.

---

## Product Categories (10 Total)

1. Electronics
2. Fashion
3. Home
4. Beauty
5. Sports
6. Auto
7. Toys
8. Grocery
9. Books
10. Health

---

## Out of Scope

- Price history tracking (future feature)
- User wishlist functionality (future feature)
- Price alerts (future feature)
- Product comparison (future feature)
- International platforms (Amazon, eBay, AliExpress)
- Advanced search filters (price range, brand, etc.)
- Product recommendations based on user behavior
- Push notifications for price drops

---

## Success Criteria

1. Home screen displays 50 real curated products (25 Best Deals + 25 Top Price Drops)
2. Products are refreshed daily at midnight automatically
3. **Search returns Tier 1 results within 2 seconds** (Daraz, Sastodeal, Oliz)
4. **Search completes all platforms within 10 seconds** (Tier 1 + Tier 2)
5. Cached searches return results within 200ms
6. Header displays logged-in user's first name
7. System runs for 7 consecutive days without errors
8. All 11 platforms are scraped successfully
9. **Users see search results immediately** (progressive loading works)

---

## Assumptions

- Existing scrapers in `scrapers/` directory are functional
- Scrapers return consistent product data structure
- Backend is running on user's local machine (not deployed)
- Mobile app and backend are on same WiFi network
- User has limited storage (MongoDB used minimally)
- Daily scraping at midnight is acceptable (user's computer must be on)

---

## Dependencies

- Existing authentication system (JWT, user registration/login)
- Existing PostgreSQL connection (asyncpg)
- Existing MongoDB connection (pymongo)
- Existing scrapers for 11 platforms
- React Native app with home screen components
- API configuration in `mobile/constants/api.ts`

---

## Risks and Mitigation

### Risk 1: Scraping Failures
**Mitigation**: Each scraper has try-catch, system continues if one fails

### Risk 2: Storage Limitations
**Mitigation**: Store only curated products, clear expired cache, minimal MongoDB usage

### Risk 3: Scraping Takes Too Long
**Mitigation**: Limit to homepage only, scrape concurrently, 10-minute timeout

### Risk 4: Computer Not On at Midnight
**Mitigation**: System checks if scraping missed, runs on next app start

### Risk 5: Network Issues During Scraping
**Mitigation**: Retry logic, log failures, manual trigger endpoint
