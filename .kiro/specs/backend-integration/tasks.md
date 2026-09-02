# Implementation Plan: Backend-Frontend Integration

## Overview

Implement tiered search functionality with progressive results, daily homepage scraping with product curation, and frontend integration for displaying real data. The system will scrape e-commerce platforms daily to curate best deals, provide fast search results through tiered scraping (Tier 1 platforms first, Tier 2 in background), and integrate with the React Native frontend.

## Tasks

### Phase 1: Database Setup and Models

- [x] 1. Create PostgreSQL database schema
  - Create `home_screen_products` table for curated products
  - Create `search_cache` table for tiered search caching
  - Create `scrape_metadata` table for tracking scraping status
  - Add indexes for performance optimization
  - _Requirements: FR3_

- [x] 2. Create Pydantic models for API responses
  - Create `Product` model with all required fields (title, price, original_price, discount_percent, image_url, store_name, product_url, category)
  - Create `HomeScreenResponse` model with best_deals and top_price_drops arrays
  - Create `SearchResponse` model with tier information and results
  - Create `SearchStatusResponse` model for polling endpoint
  - _Requirements: FR4, FR5_

### Phase 2: Scraping Coordinator Service

- [x] 3. Implement scraper coordinator for homepage scraping
  - [x] 3.1 Create `scraper_coordinator.py` service
    - Implement `scrape_homepage_daily()` function
    - Scrape all 11 platforms concurrently using asyncio.gather
    - Extract featured products from homepage (20-50 per platform)
    - Handle individual scraper failures gracefully
    - Log results to MongoDB scraping_logs collection
    - _Requirements: FR1_
  
  - [x] 3.2 Implement product curation algorithm
    - Calculate discount percentages for all scraped products
    - Identify top 25 "Best Deals" (highest discount %)
    - Identify top 25 "Top Price Drops" (largest absolute price reduction)
    - Handle duplicate products across platforms
    - _Requirements: FR2_
  
  - [x] 3.3 Implement PostgreSQL storage for curated products
    - Delete old products from `home_screen_products` table
    - Insert new curated products (25 best_deals + 25 top_price_drops)
    - Update `scrape_metadata` table with scraping status
    - _Requirements: FR3_

- [x] 4. Implement tiered search coordinator
  - [x] 4.1 Create tiered search orchestration logic
    - Implement `search_with_tiers()` function
    - Define Tier 1 platforms: Daraz, Sastodeal, Oliz
    - Define Tier 2 platforms: Better, CGDigital, HardwarePasal, Hukut, Jeevee, NeoStore, UfoNepal, Hamrobazar
    - Generate unique request_id for each search
    - _Requirements: FR5_
  
  - [x] 4.2 Implement cache check logic
    - Query `search_cache` table by search query
    - Check if cache exists and is not expired (24 hours)
    - Return full results if cache is valid and complete
    - Proceed to scraping if cache miss or expired
    - _Requirements: FR5_
  
  - [x] 4.3 Implement Tier 1 scraping (priority platforms)
    - Scrape Daraz, Sastodeal, Oliz concurrently
    - Set 2-second timeout for Tier 1 completion
    - Save Tier 1 results to `search_cache.tier1_results` (JSONB)
    - Set `is_complete=false` in cache
    - Return Tier 1 results immediately
    - _Requirements: FR5, NFR1_
  
  - [x] 4.4 Implement Tier 2 background scraping
    - Start Tier 2 scraping as FastAPI BackgroundTask
    - Scrape remaining 8 platforms concurrently
    - Set 10-second max timeout for all platforms
    - Update `search_cache.tier2_results` when complete
    - Set `is_complete=true` in cache
    - Log all scraping results to MongoDB
    - _Requirements: FR5, NFR1_

- [ ] 5. Checkpoint - Verify scraping logic
  - Test homepage scraping with all 11 platforms
  - Test tiered search with sample queries
  - Verify caching works correctly
  - Ensure all tests pass, ask the user if questions arise

### Phase 3: API Endpoints

- [ ] 6. Implement home screen API endpoint
  - [~] 6.1 Create `GET /products/home` endpoint
    - Query `home_screen_products` table
    - Filter by section='best_deals' and section='top_price_drops'
    - Return JSON with two arrays (best_deals, top_price_drops)
    - Handle empty results gracefully
    - Add error handling for database failures
    - _Requirements: FR4_

- [ ] 7. Implement tiered search API endpoints
  - [~] 7.1 Create `GET /products/search?q=<query>` endpoint
    - Validate query parameter (non-empty)
    - Check cache first using coordinator service
    - If cache miss, trigger tiered search
    - Return Tier 1 results with metadata (request_id, is_complete, tier1_platforms)
    - Include message for frontend about progressive loading
    - Add rate limiting (max 10 searches/minute)
    - _Requirements: FR5, NFR1_
  
  - [~] 7.2 Create `GET /products/search/status?query=<query>&request_id=<id>` endpoint
    - Query `search_cache` by request_id
    - Return is_complete flag
    - Return new_results from tier2_results if available
    - Return new_results_count
    - Optimize for fast response (<100ms)
    - _Requirements: FR5a, NFR1_

- [ ] 8. Update auth router with user profile endpoint
  - [~] 8.1 Create `GET /auth/me` endpoint
    - Extract JWT token from Authorization header
    - Verify token validity and decode user_id
    - Query PostgreSQL users table
    - Return user profile (id, email, full_name, created_at)
    - Return 401 Unauthorized if token invalid
    - Exclude password_hash from response
    - _Requirements: FR6_

- [ ] 9. Create admin scraper trigger endpoint
  - [~] 9.1 Create `POST /scraper/trigger` endpoint (optional)
    - Verify admin JWT token
    - Trigger immediate homepage scraping (ignore 24-hour timer)
    - Return scraping status and estimated completion time
    - Admin-only access control
    - _Requirements: FR9_

- [~] 10. Checkpoint - API testing
  - Test all endpoints with Postman or similar tool
  - Verify response formats match requirements
  - Test error handling and edge cases
  - Ensure all tests pass, ask the user if questions arise

### Phase 4: Background Scheduler

- [ ] 11. Implement daily scraping scheduler
  - [~] 11.1 Create `scheduler.py` with APScheduler
    - Set up APScheduler with BackgroundScheduler
    - Configure cron job for midnight (00:00) daily
    - Check last_scrape_time before running (prevent duplicates)
    - Call `scrape_homepage_daily()` function
    - Handle scheduler failures gracefully
    - _Requirements: FR1_
  
  - [~] 11.2 Integrate scheduler with FastAPI startup
    - Start scheduler in `main.py` startup event
    - Stop scheduler in `main.py` shutdown event
    - Add logging for scheduler status
    - _Requirements: FR1_

- [ ] 12. Implement cache cleanup job
  - [~] 12.1 Create periodic cache cleanup function
    - Query `search_cache` for entries older than 24 hours
    - Delete expired cache entries
    - Run cleanup daily at 1:00 AM
    - Log cleanup results to MongoDB
    - _Requirements: FR5_

### Phase 5: Frontend Integration - Home Screen

- [ ] 13. Create API service functions
  - [~] 13.1 Create `services/api.ts` with API functions
    - Implement `fetchHomeScreenProducts()` function
    - Implement `fetchUserProfile()` function
    - Implement `searchProducts()` function
    - Implement `pollSearchStatus()` function
    - Use `fetchWithTimeout` from `constants/api.ts`
    - Add TypeScript interfaces for all response types
    - _Requirements: FR7, FR8_

- [ ] 14. Update home screen to fetch real data
  - [~] 14.1 Modify `app/(tabs)/home.tsx`
    - Remove dummy data imports
    - Add `useEffect` to fetch products on mount
    - Call `fetchHomeScreenProducts()` API
    - Map API response to TrendingSection (best_deals)
    - Map API response to RecommendedSection (top_price_drops)
    - Add loading state (ActivityIndicator)
    - Add error handling with user-friendly message
    - Add pull-to-refresh functionality
    - _Requirements: FR7_

- [ ] 15. Update Header component to display user name
  - [~] 15.1 Modify `components/Header.tsx`
    - Add API call to fetch user profile on mount
    - Extract first name from full_name (split by space)
    - Display first name in greeting ("Hello, John!")
    - Cache user name in AsyncStorage (avoid repeated calls)
    - Fall back to generic greeting if API fails
    - Add loading state while fetching
    - _Requirements: FR8_

### Phase 6: Frontend Integration - Search with Progressive Loading

- [ ] 16. Implement tiered search UI
  - [~] 16.1 Create search screen with progressive loading
    - Call `searchProducts()` API when user submits search
    - Display Tier 1 results immediately
    - Show "Loading more results..." indicator if `is_complete=false`
    - Start polling `pollSearchStatus()` every 2 seconds
    - Append Tier 2 results when they arrive
    - Stop polling after 6 polls (12 seconds) or when complete
    - Allow user to scroll and interact with Tier 1 results during loading
    - _Requirements: FR5, FR5a_
  
  - [~] 16.2 Add error handling and retry logic
    - Handle network failures with retry (exponential backoff)
    - Show error message if all retries fail
    - Use cached results as fallback if available
    - _Requirements: NFR2_

### Phase 7: Testing and Validation

- [ ] 17. Integration testing
  - [~] 17.1 Test end-to-end homepage flow
    - Trigger daily scraping manually
    - Verify 50 products curated (25 best_deals + 25 top_price_drops)
    - Verify products appear on mobile home screen
    - Test pull-to-refresh functionality
    - _Requirements: FR1, FR2, FR7_
  
  - [~] 17.2 Test end-to-end search flow
    - Search for test query on mobile app
    - Verify Tier 1 results appear within 2 seconds
    - Verify Tier 2 results appear progressively
    - Verify second search returns cached results (<200ms)
    - Test cache expiry (24 hours)
    - _Requirements: FR5, FR5a, NFR1_
  
  - [~] 17.3 Test error handling
    - Simulate scraper failures (disable one platform)
    - Verify system continues with other platforms
    - Test database connection failures
    - Test network timeouts
    - _Requirements: NFR2_

- [ ] 18. Performance testing
  - [~] 18.1 Test API response times
    - Measure home screen API response time (<500ms target)
    - Measure search Tier 1 response time (<2s target)
    - Measure search Tier 2 completion time (<10s target)
    - Measure cached search response time (<200ms target)
    - Measure search status polling response time (<100ms target)
    - _Requirements: NFR1_
  
  - [~] 18.2 Test concurrent load
    - Simulate 100 concurrent home screen requests
    - Verify system handles load gracefully
    - Monitor database connection pool usage
    - _Requirements: NFR3_

- [~] 19. Final checkpoint - System validation
  - Run system for 7 consecutive days
  - Verify daily scraping runs automatically at midnight
  - Verify all 11 platforms scraped successfully
  - Verify no memory leaks or performance degradation
  - Ensure all tests pass, ask the user if questions arise

### Phase 8: Documentation and Deployment

- [ ] 20. Update documentation
  - [~] 20.1 Document API endpoints
    - Add endpoint descriptions to README
    - Include request/response examples
    - Document rate limits and caching behavior
    - _Requirements: NFR4_
  
  - [~] 20.2 Document deployment process
    - Document environment variables needed
    - Document database setup steps
    - Document scheduler configuration
    - _Requirements: NFR4_

## Notes

- The design document does not include a "Correctness Properties" section, so property-based testing is not applicable for this feature
- Testing focuses on integration tests, API response time validation, and end-to-end flows
- Backend uses Python with FastAPI, frontend uses React Native with TypeScript
- All scrapers must handle failures gracefully to prevent cascade failures
- Tiered search ensures users see results quickly from fast platforms first
- Cache reduces load on scrapers and improves response times
- Daily scraping at midnight requires user's computer to be on (or use cloud deployment)
- MongoDB usage is minimal (logs only) to conserve storage

