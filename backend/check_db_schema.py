import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres.cukfnnjuofbvsrwwkdsh:QWERASDFZXCV12348902567@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres')
    rows = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
    print("User columns:", [r['column_name'] for r in rows])
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
