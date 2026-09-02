-- ============================================================================
-- PricePilot Missing Features - Database Schema
-- Run this SQL in Supabase SQL Editor to add all missing feature tables
-- ============================================================================

-- Add phone column to users table if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 100;  -- Start with 100 welcome points
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code TEXT UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_completed BOOLEAN DEFAULT FALSE;

-- Generate referral codes for existing users
UPDATE users SET referral_code = 'REF' || SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8) WHERE referral_code IS NULL;

-- ============================================================================
-- Wishlist Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS wishlist (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    product_title TEXT NOT NULL,
    product_price DECIMAL(10, 2) NOT NULL,
    product_image_url TEXT,
    product_url TEXT NOT NULL,
    store_name TEXT NOT NULL,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_added ON wishlist(added_at);

-- ============================================================================
-- Price Alerts Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    product_title TEXT NOT NULL,
    product_url TEXT NOT NULL,
    store_name TEXT NOT NULL,
    target_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, product_id, is_active)  -- One active alert per user per product
);

CREATE INDEX IF NOT EXISTS idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(is_active);

-- ============================================================================
-- Notifications Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL,  -- 'price_alert', 'system', 'referral'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    product_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

-- ============================================================================
-- Activity Tracking Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL,  -- 'store_visit', 'purchase', 'wishlist_add', 'alert_set'
    product_id INTEGER,
    product_title TEXT,
    product_price DECIMAL(10, 2),
    store_name TEXT,
    savings_amount DECIMAL(10, 2),  -- How much saved vs original price
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_activity_user ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_user_activity_created ON user_activity(created_at);

-- ============================================================================
-- Points Transactions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS points_transactions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL,  -- 'earned_welcome', 'earned_profile', 'earned_purchase', 'earned_referral', 'redeemed_voucher'
    points_change INTEGER NOT NULL,  -- Positive for earning, negative for spending
    description TEXT NOT NULL,
    related_user_id UUID REFERENCES users(id),  -- For referrals
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_points_transactions_user ON points_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_created ON points_transactions(created_at);

-- ============================================================================
-- Vouchers Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS vouchers (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    voucher_code TEXT UNIQUE NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    points_cost INTEGER NOT NULL,
    is_redeemed BOOLEAN DEFAULT FALSE,
    redeemed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vouchers_user ON vouchers(user_id);
CREATE INDEX IF NOT EXISTS idx_vouchers_code ON vouchers(voucher_code);
CREATE INDEX IF NOT EXISTS idx_vouchers_active ON vouchers(is_redeemed, expires_at);

-- ============================================================================
-- Price History Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_title TEXT NOT NULL,
    store_name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_recorded ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_price_history_product_store ON price_history(product_id, store_name);

-- ============================================================================
-- Deal Scores Table (Cached calculations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS deal_scores (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    product_title TEXT NOT NULL,
    store_name TEXT NOT NULL,
    deal_score INTEGER NOT NULL,  -- 0-100
    price_score DECIMAL(5, 2),  -- Price competitiveness (50% weight)
    seller_score DECIMAL(5, 2),  -- Seller rating (30% weight)
    review_score DECIMAL(5, 2),  -- Product reviews (20% weight)
    is_trusted_seller BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deal_scores_product ON deal_scores(product_id);
CREATE INDEX IF NOT EXISTS idx_deal_scores_score ON deal_scores(deal_score);

-- ============================================================================
-- Admin Metrics Table (For dashboard)
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_metrics (
    id SERIAL PRIMARY KEY,
    metric_type TEXT NOT NULL,  -- 'user_count', 'product_count', 'search_count', etc.
    metric_value INTEGER NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_metrics_type ON admin_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_admin_metrics_recorded ON admin_metrics(recorded_at);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to award points
CREATE OR REPLACE FUNCTION award_points(
    p_user_id UUID,
    p_points INTEGER,
    p_transaction_type TEXT,
    p_description TEXT
)
RETURNS VOID AS $$
BEGIN
    -- Add points to user
    UPDATE users SET points = points + p_points WHERE id = p_user_id;
    
    -- Record transaction
    INSERT INTO points_transactions (user_id, transaction_type, points_change, description)
    VALUES (p_user_id, p_transaction_type, p_points, p_description);
END;
$$ LANGUAGE plpgsql;

-- Function to check and trigger price alerts
CREATE OR REPLACE FUNCTION check_price_alerts()
RETURNS VOID AS $$
DECLARE
    alert_record RECORD;
BEGIN
    -- Find active alerts where current price dropped to or below target
    FOR alert_record IN 
        SELECT pa.*, p.price as latest_price
        FROM price_alerts pa
        JOIN products p ON p.id = pa.product_id
        WHERE pa.is_active = TRUE
        AND p.price <= pa.target_price
    LOOP
        -- Create notification
        INSERT INTO notifications (user_id, notification_type, title, message, product_id)
        VALUES (
            alert_record.user_id,
            'price_alert',
            'Price Drop Alert!',
            format('%s is now %s (target: %s)', alert_record.product_title, alert_record.latest_price, alert_record.target_price),
            alert_record.product_id
        );
        
        -- Deactivate alert
        UPDATE price_alerts 
        SET is_active = FALSE, triggered_at = NOW()
        WHERE id = alert_record.id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate deal score
CREATE OR REPLACE FUNCTION calculate_deal_score(
    p_product_id INTEGER,
    p_price DECIMAL,
    p_original_price DECIMAL,
    p_seller_rating DECIMAL DEFAULT 4.0,
    p_review_count INTEGER DEFAULT 50
)
RETURNS INTEGER AS $$
DECLARE
    v_price_score DECIMAL;
    v_seller_score DECIMAL;
    v_review_score DECIMAL;
    v_deal_score INTEGER;
    v_is_trusted BOOLEAN;
BEGIN
    -- Price score (0-100) based on discount
    IF p_original_price IS NOT NULL AND p_original_price > p_price THEN
        v_price_score := ((p_original_price - p_price) / p_original_price) * 100;
    ELSE
        v_price_score := 0;
    END IF;
    
    -- Seller score (0-100) based on rating
    v_seller_score := (p_seller_rating / 5.0) * 100;
    
    -- Review score (0-100) based on review count
    v_review_score := LEAST((p_review_count::DECIMAL / 100) * 100, 100);
    
    -- Weighted total: price 50%, seller 30%, reviews 20%
    v_deal_score := ROUND(
        (v_price_score * 0.5) + 
        (v_seller_score * 0.3) + 
        (v_review_score * 0.2)
    );
    
    -- Trusted seller badge if rating >= 4.5 and reviews >= 100
    v_is_trusted := (p_seller_rating >= 4.5 AND p_review_count >= 100);
    
    -- Upsert deal score
    INSERT INTO deal_scores (product_id, product_title, store_name, deal_score, price_score, seller_score, review_score, is_trusted_seller, calculated_at)
    SELECT p_product_id, title, store_name, v_deal_score, v_price_score, v_seller_score, v_review_score, v_is_trusted, NOW()
    FROM products WHERE id = p_product_id
    ON CONFLICT (product_id) 
    DO UPDATE SET 
        deal_score = v_deal_score,
        price_score = v_price_score,
        seller_score = v_seller_score,
        review_score = v_review_score,
        is_trusted_seller = v_is_trusted,
        calculated_at = NOW();
    
    RETURN v_deal_score;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Initial Data Setup
-- ============================================================================

-- Create welcome notifications for existing users
INSERT INTO notifications (user_id, notification_type, title, message)
SELECT id, 'system', 'Welcome to PricePilot!', 'You have received 100 welcome points. Start tracking prices and earn more rewards!'
FROM users
WHERE NOT EXISTS (SELECT 1 FROM notifications WHERE user_id = users.id AND notification_type = 'system');

-- Record initial welcome points transactions
INSERT INTO points_transactions (user_id, transaction_type, points_change, description)
SELECT id, 'earned_welcome', 100, 'Welcome bonus'
FROM users
WHERE NOT EXISTS (SELECT 1 FROM points_transactions WHERE user_id = users.id AND transaction_type = 'earned_welcome');

COMMIT;
