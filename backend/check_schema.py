import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    rows = await conn.fetch("SELECT column_name, is_nullable, data_type FROM information_schema.columns WHERE table_name = 'vouchers'")
    for row in rows:
        print(dict(row))
    await conn.close()
    
if __name__ == "__main__":
    asyncio.run(check())
