# Implementation Plan: Admin Dashboard

## Overview

This implementation plan creates a secure admin dashboard for the PricePilot platform, featuring environment-based authentication, comprehensive system metrics, and a mobile interface with role-based access control. The implementation follows a layered approach: backend authentication and API endpoints first, followed by mobile UI components and integration.

## Tasks

- [x] 1. Set up admin authentication infrastructure
  - [x] 1.1 Update environment configuration for admin credentials
    - Add ADMIN_USERNAME and ADMIN_PASSWORD to backend .env file
    - Update .env.example with placeholder admin credentials
    - _Requirements: 1.1_

  - [x] 1.2 Implement admin login endpoint
    - Create POST /auth/admin-login endpoint in app/routers/auth.py
    - Validate credentials against environment variables using constant-time comparison
    - Generate JWT token with role="admin" claim
    - Return AuthResponse with admin user details
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 1.3 Create admin authorization middleware
    - Implement get_current_admin() function in app/routers/admin.py
    - Verify JWT token presence and validity
    - Check role="admin" claim in token payload
    - Return HTTP 401 for missing/invalid tokens
    - Return HTTP 403 for non-admin roles
    - _Requirements: 1.6, 7.1, 7.2, 7.3_

- [~] 2. Checkpoint - Test admin authentication
  - Ensure admin login endpoint works correctly, middleware blocks unauthorized access, ask the user if questions arise.

- [x] 3. Implement dashboard metrics calculation
  - [x] 3.1 Create total products metric query
    - Implement calculate_total_products() function
    - Query COUNT(*) from products table
    - Handle null results by returning 0
    - _Requirements: 3.1, 3.2, 3.5_

  - [x] 3.2 Create category breakdown metric query
    - Implement calculate_category_breakdown() function
    - Query products grouped by category with counts
    - Exclude categories with zero products
    - Sort by count descending and limit to top 10
    - Return array of {category, count} objects
    - _Requirements: 4.1, 4.2, 4.5, 4.6, 4.7_

  - [x] 3.3 Create store distribution metric query
    - Implement calculate_store_distribution() function
    - Query products grouped by store_name with counts
    - Exclude stores with zero products
    - Sort by count descending
    - Return array of {store, count} objects
    - _Requirements: 5.1, 5.2, 5.5, 5.6, 5.7_

  - [x] 3.4 Create scraper status metric query
    - Implement calculate_scraper_status() function
    - Query scrape_metadata for last_scrape_time by store
    - Classify status: "active" (<48h), "stale" (>48h), "inactive" (null)
    - Return array of {store, status, last_scrape} objects
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4. Implement dashboard API endpoint with caching
  - [x] 4.1 Create GET /admin/dashboard endpoint
    - Implement get_admin_dashboard() route in app/routers/admin.py
    - Call get_current_admin() middleware for authorization
    - Execute all metric queries in parallel using asyncio.gather()
    - Handle query exceptions gracefully with fallback values
    - Return DashboardMetrics response with last_updated timestamp
    - _Requirements: 3.2, 4.2, 5.2, 6.5, 9.1_

  - [x] 4.2 Implement 60-second response caching
    - Create in-memory cache dictionary with data and timestamp fields
    - Check cache age before executing queries
    - Return cached data if age < 60 seconds
    - Update cache with fresh data after query execution
    - _Requirements: 9.2, 9.3, 9.4_

  - [x] 4.3 Add rate limiting to admin endpoints
    - Apply @limiter.limit("30/minute") to dashboard endpoint
    - Apply @limiter.limit("3/minute") to admin login endpoint
    - _Requirements: 1.2, 8.7_

- [~] 5. Checkpoint - Test dashboard API
  - Ensure dashboard endpoint returns correct metrics, caching works, rate limiting applies, ask the user if questions arise.

- [ ] 6. Create mobile authentication infrastructure
  - [ ] 6.1 Extend useAuth hook with admin support
    - Add isAdmin state to useAuth hook in mobile/hooks/useAuth.ts
    - Add loginAdmin() function that calls /auth/admin-login
    - Set isAdmin=true when role="admin" in token payload
    - Store admin token in expo-secure-store
    - _Requirements: 2.4, 7.6_

  - [~] 6.2 Create admin login screen
    - Create mobile/app/(auth)/admin-login.tsx screen
    - Add email and password input fields with validation
    - Add password visibility toggle
    - Display loading indicator during authentication
    - Show error message for invalid credentials
    - Navigate to admin dashboard on successful login
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [ ] 7. Implement admin tab navigation
  - [~] 7.1 Add conditional admin tab to bottom navigation
    - Update mobile/app/(tabs)/_layout.tsx
    - Add admin tab with shield icon (Ionicons shield/shield-outline)
    - Conditionally render tab only when isAdmin=true
    - Use warningOrange color for active state
    - Route to admin screen on tap
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 8. Create admin dashboard screen
  - [~] 8.1 Implement dashboard screen layout and data fetching
    - Create mobile/app/(tabs)/admin.tsx screen
    - Implement fetchMetrics() function to call /admin/dashboard
    - Add loading state with skeleton UI
    - Add error handling with retry capability
    - Cache metrics locally using expo-secure-store for offline viewing
    - Auto-refresh on screen focus using useFocusEffect
    - _Requirements: 8.6, 8.7, 9.5, 9.6, 9.7_

  - [~] 8.2 Implement pull-to-refresh functionality
    - Add ScrollView with RefreshControl component
    - Trigger fetchMetrics(true) on pull-to-refresh
    - Show refreshing indicator during data fetch
    - Update all metrics on successful refresh
    - Display error banner on refresh failure
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [~] 8.3 Create total products metric card
    - Display "Total Products" card with large number display
    - Format numbers with comma separators using toLocaleString()
    - Handle zero products without error state
    - _Requirements: 3.3, 3.4, 3.5_

  - [~] 8.4 Create category breakdown visualization
    - Display "Category Breakdown (Top 10)" card with list
    - Show category names with product counts
    - Sort and display top 10 categories
    - Format counts with comma separators
    - _Requirements: 4.3, 4.4, 4.5, 4.7_

  - [~] 8.5 Create store distribution visualization
    - Display "Store Distribution" card with list
    - Show store names with product counts
    - Sort stores by count descending
    - Format counts with comma separators
    - _Requirements: 5.3, 5.4, 5.5, 5.7_

  - [~] 8.6 Create scraper status visualization
    - Display "Scraper Status" card with store list
    - Show store name, status badge, and last scrape time
    - Use color coding: green (active), yellow (stale), red (inactive)
    - Format timestamps as relative time ("2 hours ago", "3 days ago")
    - _Requirements: 6.6, 6.7, 6.8_

  - [~] 8.7 Add last updated timestamp display
    - Display "Last updated: X ago" at bottom of dashboard
    - Format timestamp as relative time
    - _Requirements: 8.7_

- [ ] 9. Implement authentication state management
  - [~] 9.1 Add token expiry handling
    - Check JWT token expiry in useAuth hook
    - Clear admin state when token expires
    - Redirect to admin login on expiry
    - _Requirements: 7.4, 7.5_

- [~] 10. Final checkpoint - End-to-end testing
  - Ensure all tests pass, verify admin login flow works, dashboard displays all metrics correctly, refresh works, tab navigation functions properly, ask the user if questions arise.

## Notes

- Tasks focus on implementing secure admin authentication and comprehensive dashboard metrics
- Environment-based credentials ensure admin access is separate from user database
- 60-second caching optimizes dashboard performance and reduces database load
- Parallel query execution minimizes API response time
- Mobile UI provides pull-to-refresh and auto-refresh for current data
- Offline caching allows viewing cached metrics without network connection
- Role-based tab rendering ensures admin features are hidden from regular users
- All timestamps use ISO 8601 format for consistency
- Rate limiting prevents abuse of authentication and dashboard endpoints

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3", "3.4"] },
    { "id": 3, "tasks": ["4.1", "4.2", "4.3"] },
    { "id": 4, "tasks": ["6.1"] },
    { "id": 5, "tasks": ["6.2", "7.1"] },
    { "id": 6, "tasks": ["8.1"] },
    { "id": 7, "tasks": ["8.2", "8.3", "8.4", "8.5", "8.6", "8.7"] },
    { "id": 8, "tasks": ["9.1"] }
  ]
}
```
