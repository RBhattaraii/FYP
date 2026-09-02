"""
populate_database.py
====================
Populates the Supabase products table with scraped data.

Strategy:
- Hukut:   Full catalog via empty search + offset pagination (~3,000+ products)
- Jeevee:  100+ search terms × full pagination (~20,000+ unique products)
- Oliz:    Key search terms
- CGDigital: Key search terms
- Daraz:   Key search terms WITH rate limiting (1.5s delay between requests)
- Others:  Standard search terms

Run this script periodically (e.g. weekly) to keep the database fresh.
"""
import asyncio
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.services.scraper_coordinator import execute_global_scraping
from app.database.mongo import connect_mongodb


async def populate_db():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("DATABASE_URL not found in .env")
        return

    print("Connecting to database...")

    try:
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        print("Connected successfully to PostgreSQL!")

        # Connect to mongo
        connect_mongodb()

        # Run the global scraper
        result = await execute_global_scraping(conn)

        print("\n=== Scraping Summary ===")
        print(f"Status: {result['status']}")
        print(f"Total Scraped: {result['total_scraped']}")
        print(f"Unique Products: {result['unique_products']}")
        print(f"Saved to DB: {result['saved_to_db']}")
        print(f"Time Taken: {result['duration_ms'] / 1000:.1f} seconds")

        await conn.close()

    except Exception as e:
        print(f"Failed to populate database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(populate_db())
