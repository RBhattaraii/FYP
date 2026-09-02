-- ============================================================================
-- Compare and History Tables for PricePilot
-- Add these tables to support product comparison and user history features
-- ============================================================================

-- Product History Table
-- Tracks products viewed by users for history feature
CREATE TABLE IF NOT EXISTS user_history (
    id                SERIAL PRIMARY KEY,
    user_id          UUID NOT NULL,
    product_id       INTEGER NOT NULL,
    product_title    TEXT NOT NULL,
    product_price    DECIMAL(10, 2) NOT NULL,
    product_image_url TEXT,
    product_url      TEXT NOT NULL,
    store_name       TEXT NOT NULL,
    category         TEXT,
    viewed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint (if users table exists)
    -- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate entries for same user+product
    UNIQUE(user_id, product_id)
);

-- Product Comparisons Table
-- Stores product comparison sets created by users
CREATE TABLE IF NOT EXISTS product_comparisons (
    id               SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL,
    comparison_name TEXT NOT NULL DEFAULT 'My Comparison',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Comparison Items Table
-- Links products to comparison sets (many-to-many relationship)
CREATE TABLE IF NOT EXISTS comparison_items (
    id              SERIAL PRIMARY KEY,
    comparison_id   INTEGER NOT NULL REFERENCES product_comparisons(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL,
    product_title   TEXT NOT NULL,
    product_price   DECIMAL(10, 2) NOT NULL,
    product_image_url TEXT,
    product_url     TEXT NOT NULL,
    store_name      TEXT NOT NULL,
    category        TEXT,
    added_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Prevent duplicate products in same comparison
    UNIQUE(comparison_id, product_id)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_history_viewed_at ON user_history(viewed_at);
CREATE INDEX IF NOT EXISTS idx_product_comparisons_user_id ON product_comparisons(user_id);
CREATE INDEX IF NOT EXISTS idx_comparison_items_comparison_id ON comparison_items(comparison_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for product_comparisons table
CREATE TRIGGER IF NOT EXISTS trigger_comparisons_updated_at
BEFORE UPDATE ON product_comparisons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- Example Usage and Queries
-- ============================================================================

-- Add product to user history (upsert - update viewed_at if exists)
/*
INSERT INTO user_history (user_id, product_id, product_title, product_price, product_image_url, product_url, store_name, category)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 12345, 'Lenovo IdeaPad 3', 85000.00, 'https://example.com/image.jpg', 'https://hukut.com/product/laptop', 'Hukut', 'laptop')
ON CONFLICT (user_id, product_id) 
DO UPDATE SET viewed_at = NOW();
*/

-- Get user history (latest 50 products)
/*
SELECT * FROM user_history 
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000' 
ORDER BY viewed_at DESC 
LIMIT 50;
*/

-- Create new comparison
/*
INSERT INTO product_comparisons (user_id, comparison_name)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Laptop Comparison')
RETURNING id;
*/

-- Add products to comparison
/*
INSERT INTO comparison_items (comparison_id, product_id, product_title, product_price, product_image_url, product_url, store_name, category)
VALUES 
    (1, 12345, 'Lenovo IdeaPad 3', 85000.00, 'https://example.com/image1.jpg', 'https://hukut.com/product/laptop1', 'Hukut', 'laptop'),
    (1, 12346, 'Acer Aspire 3', 75000.00, 'https://example.com/image2.jpg', 'https://jeevee.com/product/laptop2', 'Jeevee', 'laptop');
*/

-- Get comparison with products
/*
SELECT 
    pc.id as comparison_id,
    pc.comparison_name,
    pc.created_at,
    ci.product_id,
    ci.product_title,
    ci.product_price,
    ci.product_image_url,
    ci.product_url,
    ci.store_name,
    ci.category,
    ci.added_at
FROM product_comparisons pc
LEFT JOIN comparison_items ci ON pc.id = ci.comparison_id
WHERE pc.user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY pc.created_at DESC, ci.added_at ASC;
*/