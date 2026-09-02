import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def clear():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    await conn.execute('DELETE FROM home_screen_products')
    await conn.execute("DELETE FROM scrape_metadata WHERE scrape_type = 'daily_homepage'")
    await conn.close()
    print("Cleared home screen products")

if __name__ == "__main__":
    asyncio.run(clear())
