# PricePilot Missing Features - Implementation Plan

## Overview
This document outlines the step-by-step implementation of all missing features requested by the user.

## Phase 1: Database Setup ✅
**Status:** COMPLETED
- Created `backend/migrations/add_missing_features.sql` with all required tables
- Tables added:
  - `wishlist` - Save favorite products
  - `price_alerts` - Set target prices
  - `notifications` - Alert inbox
  - `user_activity` - Track user actions
  - `points_transactions` - Points history
  - `vouchers` - Redeemable discount codes
  - `price_history` - 30-60 day price tracking
  - `deal_scores` - Cached Deal Score calculations
  - `admin_metrics` - System performance metrics

**Next Step:** Run the migration in Supabase SQL Editor

## Phase 2: Backend Models ✅
**Status:** COMPLETED
- Created `app/models/wishlist.py` ✅
- Created `app/models/notifications.py` ✅
- Created `app/models/analytics.py` ✅

## Phase 3: Backend API Endpoints (In Progress)
**Status:** 40% COMPLETE

### Completed:
- ✅ Wishlist Router (`app/routers/wishlist.py`)
  - GET /wishlist - Get user's wishlist
  - POST /wishlist/add - Add to wishlist
  - DELETE /wishlist/{id} - Remove from wishlist
  - POST /wishlist/toggle/{id} - Toggle wishlist status

- ✅ Notifications Router (`app/routers/notifications.py`)
  - GET /notifications - Get all notifications
  - POST /notifications/{id}/read - Mark as read
  - POST /notifications/read-all - Mark all as read
  - GET /notifications/alerts - Get price alerts
  - POST /notifications/alerts - Create price alert
  - PUT /notifications/alerts/{id} - Update alert
  - DELETE /notifications/alerts/{id} - Delete alert

### Still Need to Create:
- ❌ Analytics Router (`app/routers/analytics.py`)
  - GET /analytics/dashboard - Smart insights + stats
  - GET /analytics/activity - User activity history
  - POST /analytics/record - Record activity (purchase, visit)
  - GET /analytics/monthly - Monthly statistics
  - GET /analytics/yearly - Yearly statistics

- ❌ Points Router (`app/routers/points.py`)
  - GET /points/balance - Current points
  - GET /points/history - Points transactions
  - GET /points/vouchers - Available vouchers
  - POST /points/redeem - Redeem points for voucher
  - GET /points/referral - Referral stats
  - POST /points/use-referral - Apply referral code

- ❌ Categories Router (`app/routers/categories.py`)
  - GET /categories - List all categories
  - GET /categories/{name} - Get products by category
  - GET /categories/{name}/filters - Get available filters

- ❌ Price History Router (`app/routers/price_history.py`)
  - GET /price-history/{product_id} - Get 30-60 day price history
  - POST /price-history/record - Record price point (background job)

- ❌ Deal Score Router (Update existing `/products` router)
  - Enhance product responses with Deal Score data
  - Add GET /products/{id}/deal-score-explanation
  - Add Trusted Seller Badge indicator

- ❌ Admin Router (`app/routers/admin.py`)
  - GET /admin/dashboard - System metrics
  - GET /admin/users - User statistics
  - GET /admin/scrapers - Scraper status
  - POST /admin/trigger-scraper - Manual scraper trigger
  - GET /admin/searches - Search statistics

## Phase 4: Update Main App
**Status:** NOT STARTED
- ❌ Update `backend/main.py` to include new routers
- ❌ Update `backend/requirements.txt` if needed

## Phase 5: Background Jobs
**Status:** NOT STARTED
- ❌ Create scheduled job to check price alerts every hour
- ❌ Create scheduled job to record price history daily
- ❌ Create scheduled job to calculate deal scores

## Phase 6: Frontend Mobile Pages
**Status:** NOT STARTED

### Authentication Pages (Already exist ✅)
- ✅ Login Page - `mobile/app/(auth)/login.tsx`
- ✅ Register Page - `mobile/app/(auth)/register.tsx`

### Core Pages (Partially exist)
- ✅ Home Page - `mobile/app/(tabs)/home.tsx`
- ✅ Search Results - `mobile/app/search-results.tsx`
- ✅ Product Detail - `mobile/app/product/[id].tsx`
- ❌ Price History Page - `mobile/app/price-history/[id].tsx` (NEW)
- ❌ Category Browse Page - `mobile/app/category/[name].tsx` (NEW)

### Wishlist & Alerts Pages
- ✅ Wishlist Page - `mobile/app/wishlist.tsx` (exists, needs backend integration)
- ❌ Price Alert Settings - `mobile/app/price-alerts.tsx` (NEW)

### User Pages
- ✅ Profile Page - `mobile/app/(tabs)/profile.tsx` (exists, needs enhancement)
- ❌ Notification Center - `mobile/app/notifications.tsx` (NEW)
- ❌ Analytics Page - `mobile/app/analytics.tsx` (NEW)
- ❌ Points & Rewards - `mobile/app/points.tsx` (NEW)

### Admin Pages
- ❌ Admin Dashboard - `mobile/app/admin/dashboard.tsx` (NEW)

### Enhancements Needed:
- ❌ Update Product Detail to show Deal Score explanation
- ❌ Update Product Detail to show Trusted Seller Badge
- ❌ Update Product Detail to add Price Alert button
- ❌ Update Product Detail to add Price History graph
- ❌ Update Home to show new sections
- ❌ Update Profile to show points, referral code, vouchers

## Phase 7: API Service Integration
**Status:** NOT STARTED
- ❌ Create `mobile/services/wishlist.ts`
- ❌ Create `mobile/services/notifications.ts`
- ❌ Create `mobile/services/analytics.ts`
- ❌ Create `mobile/services/points.ts`
- ❌ Create `mobile/services/categories.ts`
- ❌ Create `mobile/services/admin.ts`

## Phase 8: Testing & Verification
**Status:** NOT STARTED
- ❌ Test database migration
- ❌ Test all API endpoints with Postman/curl
- ❌ Test frontend pages with Expo
- ❌ Test points system flow
- ❌ Test referral system flow
- ❌ Test price alerts triggering
- ❌ Test admin dashboard

## Implementation Priority

### 🔥 Critical (Do First)
1. Run database migration
2. Complete remaining backend routers
3. Update main.py to register new routers
4. Test all API endpoints

### ⚡ High Priority (Do Second)
1. Frontend: Notification Center page
2. Frontend: Price Alerts page
3. Frontend: Points & Rewards page
4. Frontend: Analytics page
5. Enhance Product Detail with Deal Score

### ⭐ Medium Priority (Do Third)
1. Frontend: Category Browse page
2. Frontend: Price History graph page
3. Admin Dashboard (backend + frontend)
4. Background jobs for alerts

### 💡 Nice to Have (Do Last)
1. Enhanced analytics visualizations
2. Referral sharing UI improvements
3. Admin advanced features

## Estimated Timeline
- **Phase 1-2:** ✅ DONE (1 hour)
- **Phase 3:** ⏳ IN PROGRESS (2 hours remaining)
- **Phase 4-5:** 1 hour
- **Phase 6-7:** 4 hours
- **Phase 8:** 2 hours
- **Total:** ~10 hours of implementation

## Next Steps (Immediate Actions)
1. ✅ Complete analytics router
2. ✅ Complete points router
3. ✅ Complete categories router
4. ✅ Complete price history router
5. ✅ Update products router for Deal Score
6. ✅ Create admin router
7. Update main.py to register all routers
8. Run database migration
9. Test backend APIs
10. Start frontend implementation

