"""
Script to populate sample price history data for testing
"""
import asyncio
import asyncpg
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_sample_price_history():
    """Create sample price history data for existing products"""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected to database")
        
        # Get first 10 products to add price history
        products = await conn.fetch("""
            SELECT id, title, price, store_name
            FROM products
            ORDER BY id
            LIMIT 10
        """)
        
        if not products:
            print("No products found in database")
            return
        
        print(f"Found {len(products)} products to add price history")
        
        # Create price history table if it doesn't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                product_title TEXT NOT NULL,
                store_name TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                recorded_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Clear existing price history
        await conn.execute("DELETE FROM price_history")
        print("Cleared existing price history")
        
        # Generate price history for each product
        for product in products:
            product_id = product['id']
            title = product['title']
            current_price = float(product['price'])
            store_name = product['store_name']
            
            print(f"Generating price history for: {title}")
            
            # Generate 60 days of price history
            for day in range(60, 0, -1):
                # Calculate date
                date = datetime.now() - timedelta(days=day)
                
                # Generate realistic price variations
                # Base price varies ±20% from current price
                variation = random.uniform(-0.2, 0.2)
                price_on_date = current_price * (1 + variation)
                
                # Add some seasonal patterns
                if day < 15:  # Recent prices closer to current
                    price_on_date = current_price * (1 + random.uniform(-0.1, 0.1))
                
                # Ensure price is positive
                price_on_date = max(price_on_date, current_price * 0.5)
                
                # Round to 2 decimal places
                price_on_date = round(price_on_date, 2)
                
                # Insert price history record
                await conn.execute("""
                    INSERT INTO price_history (product_id, product_title, store_name, price, recorded_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, product_id, title, store_name, price_on_date, date)
            
            print(f"  Added 60 days of price history for product {product_id}")
        
        print("\n✅ Sample price history data created successfully!")
        print("You can now test the price history feature in the mobile app.")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    asyncio.run(create_sample_price_history())