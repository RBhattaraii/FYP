# PricePilot / Fashion - Full Stack System Overview

This document provides a comprehensive overview of the PricePilot (also referred to as Fashion) platform. It is a full-stack price comparison and e-commerce aggregator tailored primarily for the Nepalese market (aggregating from stores like Daraz, Oliz Store, Jeevee, Hukut, CG Digital, etc.). 

This file is intended to be used as a context prompt for AI assistants to understand the architecture, tech stack, feature set, routing, and database design of the repository.

---

## 1. System Architecture & Tech Stack

The repository is divided into three main components:

### A. Backend (`/backend`)
*   **Framework**: Python with FastAPI.
*   **Database**: PostgreSQL (interacted with asynchronously using `asyncpg`).
*   **Core Responsibilities**: 
    *   RESTful API for the mobile app and admin web panel.
    *   Running web scrapers to fetch product data from various e-commerce sites.
    *   Entity resolution (matching similar products across different stores).
    *   Managing user authentication, history, points, vouchers, and price alerts.
    *   Cron jobs / background tasks for price monitoring and sending push notifications.

### B. Mobile App (`/mobile`)
*   **Framework**: React Native using Expo and Expo Router (file-based routing).
*   **Language**: TypeScript.
*   **Styling**: Custom styles adhering to a "premium brown aesthetic" (`#704F38`, `#6E4B3A`).
*   **Core Responsibilities**:
    *   User-facing application available on iOS and Android.
    *   Browsing products, searching, and viewing detailed product comparisons.
    *   Managing the user's Wishlist (Favorites) and Price Alerts.
    *   Onboarding, Auth, and Profile management.
    *   Handling Push Notifications (via `expo-notifications`).

### C. Admin Web Panel (`/admin-web`)
*   **Framework**: React (Vite) / TypeScript.
*   **Core Responsibilities**:
    *   Dashboard for platform administrators.
    *   Triggering manual scrapes and viewing scraping statistics.
    *   Managing global vouchers, reward tiers, and user points.
    *   Moderating products and resolving categorization issues.

---

## 2. Deep Dive: Mobile App (`/mobile`)

### Routing Structure (`/mobile/app/`)
The app uses `expo-router` for file-based routing:
*   `_layout.tsx`: The root layout. Handles global notification listeners and splash screen logic.
*   `index.tsx`: The entry point. It evaluates the user's Auth token, Profile Completion status, and Notification Opt-in status, then redirects accordingly.
*   **(auth)/**:
    *   `login.tsx`, `register.tsx`, `welcome.tsx`
    *   `complete-profile.tsx`: Forced if user registers without full info.
    *   `notifications-prompt.tsx`: Forced on login if user hasn't opted into notifications.
*   **(tabs)/**: The main bottom tab bar containing `home.tsx`, `explore.tsx`, `favorites.tsx`, `offers.tsx`, and `profile.tsx`.
*   **product/[id].tsx**: The Product Details Page. Handles dynamic IDs (both integer DB IDs and compound string IDs for freshly scraped items).
*   **category/[name].tsx**: Category filtering page.
*   **Other Pages**: `price-alerts.tsx`, `points.tsx`, `compare-search.tsx`, `my-comparisons.tsx`, `search-results.tsx`.

### State & Context
*   **FavoritesContext**: Manages wishlist globally.
*   **authStorage.ts**: Wrapper around `expo-secure-store` to handle tokens and string flags like `notifications_opt_in`.
*   **API Services**: `/services/api.ts` exports `fetchWithTimeout` to handle backend requests.

---

## 3. Deep Dive: Backend (`/backend`)

### Routers (`/backend/app/routers/`)
The FastAPI application splits its endpoints into routers:
*   `auth.py`: Login, Register, Me.
*   `products.py`: `GET /products`, `GET /products/{id}`, Search, sorting.
*   `scraper.py`: Triggering scrapers.
*   `notifications.py`: Price alerts (`GET /notifications/alerts`, `POST /notifications/alerts`).
*   `compare.py`: Fetching similar items for the compare feature.
*   `points.py`: Referral system, point redemption, generating vouchers.
*   `wishlist.py`, `categories.py`, `analytics.py`, `history.py`.

### Database Entities (PostgreSQL via asyncpg)
*   **users**: ID, email, password_hash, full_name, role.
*   **products**: Original products scraped from sites. Fields: title, price, original_price, discount_percent, image_url, product_url, store_name, category.
*   **price_history**: Tracks historical prices for a `product_id`.
*   **price_alerts**: Links `user_id`, `product_id`, and `target_price`.
*   **points**: Tracks a user's reward points balance.
*   **vouchers**: 
    *   Admin-created templates (Global Vouchers like `ROYA`).
    *   User-redeemed instances (Unique codes generated when users spend points).

### Unique Architectural Details
*   **Compound IDs**: When searching, scrapers might return products that are not yet saved in the database. The backend generates a temporary string ID (e.g., `storeName-https://product.url`). The frontend uses `encodeURIComponent` when passing these IDs to `[id].tsx`. The backend's `/products/{id}` endpoint natively detects if the ID is an integer (DB fetch) or a compound string (live fetch using the URL).
*   **Notification Push Tokens**: The app registers for Expo Push Notifications and saves the token to the backend `/auth/push-token`.

---

## 4. Key Design Patterns & UX Guidelines

*   **Premium Aesthetic**: The mobile app strictly adheres to a luxurious, clean design. It avoids default blue/red colors, heavily favoring curated palettes like `#704F38` (brown), white, and sleek grays. 
*   **Error Handling**: User-friendly error messages (e.g., Modals or clean alert screens) are preferred over raw system alerts.
*   **Speed**: Caching mechanisms are heavily utilized on the backend. The frontend passes heavy data via Route Params where possible to avoid redundant API calls on navigation.

---

## 5. Common Scripts / Commands
*   **Backend**: `uvicorn main:app --host 0.0.0.0 --reload` (Runs on port 8000)
*   **Mobile**: `npx expo start` (Runs on port 8081)
*   **Admin Web**: `npm run dev` (Runs on port 3000/5173)

---

*End of Document. Use this context to understand the relationships between the backend endpoints, the mobile UI, and the database schema.*
