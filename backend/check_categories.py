import asyncio
import asyncpg

async def check_categories():
    conn = await asyncpg.connect('postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres')
    
    # Get all categories
    rows = await conn.fetch('''
        SELECT DISTINCT category, COUNT(*) as count 
        FROM products 
        WHERE category IS NOT NULL
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 20
    ''')
    
    print('\nCategories in database:')
    print('-' * 50)
    for row in rows:
        print(f'  {row["category"]}: {row["count"]} products')
    
    print('\n' + '-' * 50)
    print(f'Total categories: {len(rows)}')
    
    await conn.close()

asyncio.run(check_categories())
