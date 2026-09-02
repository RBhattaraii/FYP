"""
Add phone column to users table if it doesn't exist
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def add_phone_column():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    try:
        # Check if phone column exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='users' 
                AND column_name='phone'
            );
        """)
        
        if column_exists:
            print("✓ Phone column already exists in users table")
        else:
            # Add phone column
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN phone VARCHAR(20);
            """)
            print("✓ Added phone column to users table")
        
        # Check if updated_at column exists
        updated_at_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='users' 
                AND column_name='updated_at'
            );
        """)
        
        if updated_at_exists:
            print("✓ Updated_at column already exists in users table")
        else:
            # Add updated_at column
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
            """)
            print("✓ Added updated_at column to users table")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_phone_column())
