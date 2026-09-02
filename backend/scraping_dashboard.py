#!/usr/bin/env python3
"""
COMPREHENSIVE SCRAPING DASHBOARD
Real-time monitoring of all scraping operations
"""

import sqlite3
import asyncio
import asyncpg
import os
import time
from datetime import datetime

# Database URLs
SUPABASE_URL = "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

async def get_comprehensive_stats():
    """Get comprehensive statistics from all databases"""
    stats = {
        'supabase': 0,
        'main_local': 0,
        'turbo_local': 0,
        'total': 0,
        'file_sizes': {},
        'recent_products': []
    }
    
    # Check Supabase
    try:
        conn = await asyncpg.connect(SUPABASE_URL)
        stats['supabase'] = await conn.fetchval("SELECT COUNT(*) FROM products")
        await conn.close()
    except Exception:
        stats['supabase'] = 0
    
    # Check main local database
    try:
        if os.path.exists('local_products.db'):
            conn = sqlite3.connect('local_products.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['main_local'] = cursor.fetchone()[0]
            conn.close()
            stats['file_sizes']['main'] = os.path.getsize('local_products.db') / (1024 * 1024)
    except Exception:
        stats['main_local'] = 0
    
    # Check turbo database
    try:
        if os.path.exists('turbo_products.db'):
            conn = sqlite3.connect('turbo_products.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['turbo_local'] = cursor.fetchone()[0]
            
            # Get recent products from turbo
            cursor.execute("""
                SELECT title, price, store_name, search_term, turbo_batch
                FROM products 
                ORDER BY rowid DESC 
                LIMIT 3
            """)
            stats['recent_products'] = cursor.fetchall()
            
            conn.close()
            stats['file_sizes']['turbo'] = os.path.getsize('turbo_products.db') / (1024 * 1024)
    except Exception:
        stats['turbo_local'] = 0
    
    # Calculate total
    stats['total'] = stats['supabase'] + stats['main_local'] + stats['turbo_local']
    
    return stats

def display_dashboard(stats, iteration):
    """Display comprehensive dashboard"""
    clear_screen()
    
    print("🚀 PRICEPILOT MASS SCRAPING DASHBOARD")
    print("=" * 70)
    print(f"📊 Real-time Update #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Storage breakdown
    print("💾 STORAGE DISTRIBUTION:")
    print(f"  📡 Supabase PostgreSQL: {stats['supabase']:,} products")
    if stats['main_local'] > 0:
        size_info = f" ({stats['file_sizes'].get('main', 0):.1f} MB)" if 'main' in stats['file_sizes'] else ""
        print(f"  🗄️  Main Scraper (SQLite): {stats['main_local']:,} products{size_info}")
    if stats['turbo_local'] > 0:
        size_info = f" ({stats['file_sizes'].get('turbo', 0):.1f} MB)" if 'turbo' in stats['file_sizes'] else ""
        print(f"  ⚡ Turbo Scraper (SQLite): {stats['turbo_local']:,} products{size_info}")
    
    print("=" * 70)
    
    # Total progress
    total = stats['total']
    print(f"🎯 TOTAL PRODUCTS COLLECTED: {total:,}")
    
    # Progress bars
    min_target = 300000
    max_target = 1000000
    
    min_progress = min((total / min_target) * 100, 100)
    max_progress = (total / max_target) * 100
    
    # Visual progress bars
    min_bar_length = 50
    min_filled = int((min_progress / 100) * min_bar_length)
    min_bar = "█" * min_filled + "░" * (min_bar_length - min_filled)
    
    max_bar_length = 50
    max_filled = int((max_progress / 100) * max_bar_length)
    max_bar = "█" * max_filled + "░" * (max_bar_length - max_filled)
    
    print(f"\n📈 MINIMUM TARGET (300k): {min_progress:.1f}%")
    print(f"   [{min_bar}]")
    
    print(f"\n📈 MAXIMUM TARGET (1M): {max_progress:.1f}%")
    print(f"   [{max_bar}]")
    
    # Status messages
    if total >= max_target:
        print("\n🏆 MAXIMUM TARGET ACHIEVED! INCREDIBLE SUCCESS!")
    elif total >= min_target:
        print("\n✅ MINIMUM TARGET ACHIEVED! READY FOR PRODUCTION!")
    else:
        remaining = min_target - total
        print(f"\n⏳ {remaining:,} more products needed for minimum target")
    
    # Performance metrics
    if iteration > 1:
        # Estimate rate (this is approximate)
        estimated_rate = total / (iteration * 10)  # 10 seconds per iteration
        if estimated_rate > 0:
            eta_seconds = remaining / estimated_rate if remaining > 0 else 0
            eta_hours = eta_seconds / 3600
            print(f"🚀 Current Rate: ~{estimated_rate:.0f} products/second")
            if eta_hours > 0:
                print(f"⏰ ETA to 300k: ~{eta_hours:.1f} hours")
    
    # Recent activity
    if stats['recent_products']:
        print("\n📋 LATEST TURBO SCRAPER ACTIVITY:")
        for i, (title, price, store, term, batch) in enumerate(stats['recent_products'], 1):
            print(f"  {i}. {title[:45]}... - Rs {price} ({term})")
    
    print("\n" + "=" * 70)
    print("🔥 ACTIVE SCRAPERS: Main Scraper + Turbo Scraper")
    print("💡 Press Ctrl+C to stop monitoring")
    print("=" * 70)

async def run_dashboard():
    """Run the monitoring dashboard"""
    iteration = 0
    
    try:
        while True:
            iteration += 1
            stats = await get_comprehensive_stats()
            display_dashboard(stats, iteration)
            
            # Check if we've reached maximum target
            if stats['total'] >= 1000000:
                print("\n🎉 MAXIMUM TARGET REACHED! MISSION ACCOMPLISHED!")
                break
            
            # Wait 10 seconds before next update
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n📊 Dashboard monitoring stopped.")
        final_stats = await get_comprehensive_stats()
        print(f"\n🎯 Final Count: {final_stats['total']:,} products collected")

if __name__ == "__main__":
    asyncio.run(run_dashboard())