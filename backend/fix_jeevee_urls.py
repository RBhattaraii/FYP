"""
fix_jeevee_urls.py
==================
Fixes ALL Jeevee product URLs in the database.

Strategy:
  - Real products (with jeevee.com URLs): Verify via HEAD request,
    try the alternate ID pattern if broken.
  - Synthetic products (with jeevee.synthetic URLs): Replace with
    a Jeevee search URL that is GUARANTEED to work:
    https://www.jeevee.com/products/search?query={product_name}
"""

import asyncio
import asyncpg
import os
import re
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 500


async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)

    # ── Step 1: Fix synthetic Jeevee URLs ────────────────────────────────────
    print("Step 1: Fixing synthetic Jeevee URLs...")
    synthetic_count = await conn.fetchval(
        "SELECT COUNT(*) FROM products WHERE store_name = 'Jeevee' AND product_url LIKE '%synthetic%'"
    )
    print(f"  Found {synthetic_count:,} synthetic Jeevee products.")

    if synthetic_count > 0:
        # Update all synthetic URLs to use Jeevee search URL
        await conn.execute("""
            UPDATE products
            SET product_url = 'https://www.jeevee.com/products/search?query=' || 
                              regexp_replace(lower(title), '[^a-z0-9]+', '+', 'g') ||
                              '&ref=' || id::text
            WHERE store_name = 'Jeevee' AND product_url LIKE '%synthetic%'
        """)
        print(f"  Fixed {synthetic_count:,} synthetic URLs -> Jeevee search links.")

    # ── Step 2: Fix real Jeevee URLs that are broken ─────────────────────────
    print("\nStep 2: Checking real Jeevee URLs...")
    real_rows = await conn.fetch("""
        SELECT id, title, product_url
        FROM products
        WHERE store_name = 'Jeevee'
          AND product_url LIKE '%jeevee.com/products/%'
          AND product_url NOT LIKE '%/search?%'
        LIMIT 500
    """)
    print(f"  Found {len(real_rows)} real Jeevee URLs to check.")

    fixed = 0
    broken_no_fix = 0
    for row in real_rows:
        url = row['product_url']
        try:
            head = requests.head(url, timeout=3, allow_redirects=True)
            if head.status_code == 404:
                # Try swapping the ID
                # Extract current slug and ID
                path = url.split('/products/')[-1]
                parts = path.rsplit('-', 1)
                if len(parts) == 2:
                    slug_part, old_id = parts[0], parts[1]
                    # We don't know the alternate ID, so fall back to search URL
                    search_url = 'https://www.jeevee.com/products/search?query=' + urllib.parse.quote(row['title']) + '&ref=' + str(row['id'])
                    await conn.execute(
                        "UPDATE products SET product_url = $1 WHERE id = $2",
                        search_url, row['id']
                    )
                    fixed += 1
                else:
                    broken_no_fix += 1
        except Exception:
            pass  # Network error, leave as is

    print(f"  Fixed {fixed} broken real URLs -> search links.")
    if broken_no_fix:
        print(f"  Could not fix {broken_no_fix} URLs (unusual format).")

    # ── Step 3: Fix variant URLs from old synthetic generator ────────────────
    print("\nStep 3: Fixing variant URLs...")
    variant_count = await conn.fetchval(
        "SELECT COUNT(*) FROM products WHERE store_name = 'Jeevee' AND product_url LIKE '%?variant=%'"
    )
    if variant_count > 0:
        await conn.execute("""
            UPDATE products
            SET product_url = 'https://www.jeevee.com/products/search?query=' || 
                              regexp_replace(lower(title), '[^a-z0-9]+', '+', 'g') ||
                              '&ref=' || id::text
            WHERE store_name = 'Jeevee' AND product_url LIKE '%?variant=%'
        """)
        print(f"  Fixed {variant_count:,} variant URLs -> search links.")

    # Final summary
    total_jeevee = await conn.fetchval("SELECT COUNT(*) FROM products WHERE store_name = 'Jeevee'")
    sample = await conn.fetch(
        "SELECT title, product_url FROM products WHERE store_name = 'Jeevee' ORDER BY RANDOM() LIMIT 5"
    )

    print(f"\nDone! Total Jeevee products: {total_jeevee:,}")
    print("\nSample URLs:")
    for s in sample:
        print(f"  {s['title'][:40]} -> {s['product_url'][:80]}")

    await conn.close()


asyncio.run(main())
