"""
Apply missing features migration
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def apply_migration():
    """Apply the missing features migration"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected to database")
        
        # Read migration file
        with open('migrations/add_missing_features.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        await conn.execute(migration_sql)
        print("✅ Migration applied successfully!")
        
        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('price_alerts', 'notifications')
        """)
        
        print("\nVerified tables:")
        for row in tables:
            print(f"  ✓ {row['table_name']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")

if __name__ == "__main__":
    asyncio.run(apply_migration())
