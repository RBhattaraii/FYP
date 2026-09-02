import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def fix_schema():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        await conn.execute("ALTER TABLE vouchers ALTER COLUMN user_id DROP NOT NULL")
        print("Schema updated successfully. user_id is now nullable.")
    except Exception as e:
        print("Failed to update schema:", e)
    finally:
        await conn.close()
    
if __name__ == "__main__":
    asyncio.run(fix_schema())
