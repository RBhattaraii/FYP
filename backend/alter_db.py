import asyncio
import asyncpg
import os

async def main():
    conn = await asyncpg.connect('postgresql://postgres.cukfnnjuofbvsrwwkdsh:QWERASDFZXCV12348902567@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres')
    try:
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS expo_push_token TEXT;")
        print("Successfully added expo_push_token to users table.")
    except Exception as e:
        print("Error altering table:", e)
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
