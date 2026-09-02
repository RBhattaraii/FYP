#!/usr/bin/env python3
"""
Scraping Progress Monitor
Check progress across all storage systems
"""

import sqlite3
import asyncio
import asyncpg
import os
from datetime import datetime

# Database URLs
SUPABASE_URL = "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

async def check_progress():
    """Check scraping progress across all storage systems"""
    print("🔍 CHECKING SCRAPING PROGRESS")
    print("=" * 50)
    
    total_products = 0
    
    # Check Supabase
    try:
        conn = await asyncpg.connect(SUPABASE_URL)
        supabase_count = await conn.fetchval("SELECT COUNT(*) FROM products")
        await conn.close()
        print(f"📊 Supabase: {supabase_count:,} products")
        total_products += supabase_count
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        supabase_count = 0
    
    # Check local SQLite
    try:
        if os.path.exists('local_products.db'):
            local_conn = sqlite3.connect('local_products.db')
            cursor = local_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            local_count = cursor.fetchone()[0]
            local_conn.close()
            
            # Check file size
            file_size = os.path.getsize('local_products.db')
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"💾 Local SQLite: {local_count:,} products ({file_size_mb:.1f} MB)")
            total_products += local_count
        else:
            print("💾 Local SQLite: No database file found")
            local_count = 0
    except Exception as e:
        print(f"❌ Local SQLite error: {e}")
        local_count = 0
    
    print("=" * 50)
    print(f"🎯 TOTAL PRODUCTS: {total_products:,}")
    
    # Progress toward targets
    min_target = 300000
    max_target = 1000000
    
    min_progress = (total_products / min_target) * 100
    max_progress = (total_products / max_target) * 100
    
    print(f"📈 Progress toward minimum (300k): {min_progress:.1f}%")
    print(f"📈 Progress toward maximum (1M): {max_progress:.1f}%")
    
    if total_products >= max_target:
        print("🏆 MAXIMUM TARGET ACHIEVED!")
    elif total_products >= min_target:
        print("✅ MINIMUM TARGET ACHIEVED!")
    else:
        remaining = min_target - total_products
        print(f"⏳ Need {remaining:,} more products for minimum target")
    
    # Show some recent products if available
    try:
        if os.path.exists('local_products.db'):
            local_conn = sqlite3.connect('local_products.db')
            cursor = local_conn.cursor()
            cursor.execute("""
                SELECT title, price, store_name, platform, category
                FROM products 
                ORDER BY rowid DESC 
                LIMIT 5
            """)
            recent = cursor.fetchall()
            local_conn.close()
            
            if recent:
                print("\n📋 RECENT PRODUCTS SCRAPED:")
                for i, (title, price, store, platform, category) in enumerate(recent, 1):
                    print(f"  {i}. {title[:50]}... - Rs {price} ({platform}/{category})")
    except Exception as e:
        pass
    
    print(f"\n⏰ Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(check_progress())