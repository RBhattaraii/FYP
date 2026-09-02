# PricePilot - System Context Document

This document serves as the absolute "source of truth" for the PricePilot architecture, database schema, and core business logic. Feed this to any AI chatbot to give it complete context on the project.

## 1. Project Overview
**Name:** PricePilot
**Goal:** A smart, cloud-based mobile application that aggregates, normalizes, and compares online product prices in real-time across Nepalese e-commerce platforms (e.g., Daraz, Hukut, Jeevee).
**Key Value Proposition:** Provides ultimate price transparency, calculates a "Deal Score" to identify fake discounts, and gamifies the shopping experience through a points and voucher system.

## 2. Technology Stack
*   **Frontend (Mobile):** React Native (Expo framework), TypeScript, NativeWind (Tailwind CSS for React Native layout).
*   **Backend (API):** Python, FastAPI, Uvicorn (ASGI server).
*   **Databases (Hybrid Architecture):**
    *   **PostgreSQL:** Handles highly structured, relational data (User Authentication, Financial Points, Vouchers, Search Caching). Provides ACID compliance.
    *   **MongoDB:** Handles massive, unstructured/semi-structured data (Raw Scraped HTML, Daily Price Histories, Millions of Product Listings).
*   **Scraping Engine:** Python (BeautifulSoup4 / httpx / Motor async MongoDB).

## 3. Database Schema (Hybrid ERD)

### PostgreSQL Tables (Relational / Core Logic)
1.  **User:** `user_id` (PK), `role`, `first_name`, `last_name`, `email`, `password_hash`, `points` (balance), `referral_code`, `referred_by`, `created_at`.
2.  **Points_Transaction:** `transaction_id` (PK), `user_id` (FK), `transaction_type`, `points_change`, `description`, `created_at`.
3.  **Voucher:** `voucher_id` (PK), `user_id` (FK), `code`, `discount_amount`, `is_redeemed`, `expires_at`.
4.  **Wishlist:** `wishlist_id` (PK), `user_id` (FK), `product_id` (FK bridging to MongoDB), `added_date`.
5.  **Search_Cache:** `id` (PK), `query`, `tier1_results` (JSON), `is_complete`, `cached_at`.
6.  **Home_Screen_Products:** `id` (PK), `section`, `title`, `price`, `store_name`, `scraped_at`.

### MongoDB Collections (NoSQL / Big Data)
7.  **Product:** `_id` (PK), `name`, `category`, `image_url`, `normalized_title`.
8.  **Store_Listing:** `_id` (PK), `product_id` (FK to Product), `store_name`, `url`, `current_price`, `last_scraped`.
9.  **Price_History:** `_id` (PK), `listing_id` (FK to Store_Listing), `price`, `recorded_at`.
10. **Scraping_Log:** `_id` (PK), `store_name`, `items_scraped`, `status`, `start_time`, `end_time`.

## 4. Core System Architectures & Algorithms

### A. The Scraping & Normalization Engine
*   **Background Workers:** Asynchronous Python workers scrape e-commerce category pages without blocking the main FastAPI application.
*   **Data Normalization:** Extracts raw, messy titles (e.g., "Apple iPhone 15 Pro Max 256GB - Blue Titanium [Official]") and normalizes them into standard query strings ("iPhone 15 Pro Max 256GB"). This allows products scraped from entirely different stores to be perfectly linked under the same core `Product` entity.
*   **Upsert Logic:** If a product exists, the scraper updates the `current_price` in the `Store_Listing` and pushes a new timestamped record to `Price_History`. If new, it creates the entire tree.

### B. Tiered Search & Caching System
To provide instantaneous search results while scraping massive datasets:
*   **Tier 1 (Instant):** Checks the `Search_Cache` (PostgreSQL). If a query was searched recently, it returns the JSON results immediately (O(1) lookup).
*   **Tier 2 (Deep Search):** If cache misses, the backend queries MongoDB using advanced text vector indexes on the `normalized_title`, aggregates the results, and asynchronously saves them to the PostgreSQL `Search_Cache` for the next user who searches that exact phrase.

### C. Deal Score Algorithm
*   Calculates the true legitimacy of a discount.
*   *Factors:* Current price vs. Historical average price across the last 30 days, cross-referencing prices across multiple competitor stores.
*   *Output:* Generates a visual score. A high score means the product is currently cheaper than historical averages and beats competitor pricing (a genuine deal).

### D. Gamification (Points & Vouchers)
*   **Earning:** Users earn points by registering, completing profiles, inviting friends (referral codes), or daily activity.
*   **Redemption:** Users can convert a specific balance (e.g., 500 points) into a unique Voucher code. The transaction checks the PostgreSQL `points` balance, deducts it securely (ACID compliance prevents overdrafts), logs the exact change to `Points_Transaction`, and mints a secure `Voucher`.

### E. Security & Validation Best Practices
*   **Auth:** JWT (JSON Web Tokens) Bearer authentication for session management. Passwords hashed securely using Bcrypt.
*   **Strict Pydantic Validation:** Models enforce strict rules (e.g., first/last name cannot be empty, passwords must contain >8 chars, 1 uppercase, 1 special character).
*   **Anti-Enumeration:** Login endpoints return identical generic error messages ("Invalid Credentials") for both incorrect emails and incorrect passwords to prevent hackers from scraping registered emails.
