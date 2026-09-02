"""
Test price alerts database and API
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def test_database():
    """Test database connection and price_alerts table"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check if price_alerts table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'price_alerts'
            )
        """)
        
        if table_exists:
            print("✅ price_alerts table exists")
            
            # Get table schema
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'price_alerts'
                ORDER BY ordinal_position
            """)
            
            print("\nTable Schema:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
            
            # Count alerts
            count = await conn.fetchval("SELECT COUNT(*) FROM price_alerts")
            print(f"\n📊 Total alerts in database: {count}")
            
            if count > 0:
                # Show sample
                sample = await conn.fetchrow("""
                    SELECT id, product_title, store_name, target_price, current_price, is_active 
                    FROM price_alerts 
                    LIMIT 1
                """)
                print("\nSample alert:")
                print(f"  ID: {sample['id']}")
                print(f"  Product: {sample['product_title']}")
                print(f"  Store: {sample['store_name']}")
                print(f"  Target: Rs {sample['target_price']}")
                print(f"  Current: Rs {sample['current_price']}")
                print(f"  Active: {sample['is_active']}")
        else:
            print("❌ price_alerts table does NOT exist")
            print("   Run: python apply_missing_features.py")
            await conn.close()
            return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    exit(0 if success else 1)
