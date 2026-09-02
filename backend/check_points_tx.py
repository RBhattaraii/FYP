import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from app.models.analytics import PointsTransaction

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    rows = await conn.fetch("SELECT * FROM points_transactions LIMIT 5")
    for row in rows:
        d = dict(row)
        print("Dict:", d)
        try:
            pt = PointsTransaction(**d)
            print("Success:", pt)
        except Exception as e:
            print("Error:", e)
    await conn.close()
    
if __name__ == "__main__":
    asyncio.run(check())
