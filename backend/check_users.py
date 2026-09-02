import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    users = await conn.fetch('SELECT email FROM users LIMIT 5')
    print('📧 Users in database:')
    for u in users:
        print(f"   - {u['email']}")
    await conn.close()

asyncio.run(check())
