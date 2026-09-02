import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres.cukfnnjuofbvsrwwkdsh:QWERASDFZXCV12348902567@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres')
    await conn.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid != pg_backend_pid() AND state = 'active'")
    print("Terminated active queries")
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
