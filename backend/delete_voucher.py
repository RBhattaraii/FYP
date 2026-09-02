import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    await conn.execute("DELETE FROM vouchers WHERE voucher_code = 'SUMMER2026'")
    print("Deleted SUMMER2026")
    await conn.close()
    
if __name__ == "__main__":
    asyncio.run(check())
