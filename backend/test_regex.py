import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_regex():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Test if accessory penalty applies
    q1 = """
    SELECT 
        'apple iphone 17 silicone case' ~ '\\y(case|cover)\\y' as match1,
        'iphone' !~ '\\y(case|cover)\\y' as match2
    """
    res = await conn.fetchrow(q1)
    print(dict(res))
    await conn.close()

asyncio.run(test_regex())
