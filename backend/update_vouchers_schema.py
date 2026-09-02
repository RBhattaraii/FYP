import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def run_migration():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set")
        return
        
    conn = await asyncpg.connect(url)
    
    try:
        # Add new columns to vouchers table
        await conn.execute("""
            ALTER TABLE vouchers 
            ADD COLUMN IF NOT EXISTS discount_type VARCHAR(20) DEFAULT 'fixed_amount',
            ADD COLUMN IF NOT EXISTS minimum_spend DECIMAL(10, 2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS usage_limit INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS times_used INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS is_global BOOLEAN DEFAULT FALSE
        """)
        
        # Modify existing discount_amount column to act as discount_value (so we don't break existing code immediately)
        # We will keep the name `discount_amount` but it can represent percentage or fixed based on `discount_type`
        
        print("Successfully updated vouchers table schema.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
