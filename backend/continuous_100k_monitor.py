#!/usr/bin/env python3
"""
Continuous 100k Monitor - Real-time tracking until 100k achieved
"""

import sqlite3
import time
import os
import glob
from datetime import datetime

def get_total_products():
    """Get total unique products across all databases"""
    
    # Create temporary consolidation
    temp_db = 'temp_monitor.db'
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TEMPORARY TABLE temp_products (
                product_url TEXT PRIMARY KEY,
                title TEXT,
                platform TEXT
            )
        ''')
        
        # Get all database files
        db_files = glob.glob('*.db')
        db_files = [db for db in db_files if 'temp_' not in db and 'monitor' not in db]
        
        total_added = 0
        active_dbs = 0
        
        for db_file in db_files:
            try:
                if not os.path.exists(db_file):
                    continue
                    
                source_conn = sqlite3.connect(db_file)
                source_cursor = source_conn.cursor()
                
                # Check if products table exists
                source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                if not source_cursor.fetchone():
                    source_conn.close()
                    continue
                
                # Get products
                source_cursor.execute("SELECT DISTINCT product_url, title, COALESCE(platform, ?) FROM products WHERE product_url IS NOT NULL", (db_file.replace('.db', ''),))
                
                products = source_cursor.fetchall()
                source_conn.close()
                
                if products:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO temp_products (product_url, title, platform) 
                        VALUES (?, ?, ?)
                    ''', products)
                    
                    added = cursor.rowcount
                    total_added += len(products)  # Count all products processed
                    active_dbs += 1
                    
            except Exception:
                continue
        
        # Get unique count
        cursor.execute('SELECT COUNT(*) FROM temp_products')
        unique_count = cursor.fetchone()[0]
        
        # Get platform breakdown
        cursor.execute('SELECT platform, COUNT(*) FROM temp_products GROUP BY platform ORDER BY COUNT(*) DESC')
        platform_stats = cursor.fetchall()
        
        conn.close()
        
        return unique_count, platform_stats, active_dbs
        
    except Exception:
        return 0, [], 0
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def monitor_continuously():
    """Monitor progress continuously until 100k reached"""
    
    print("🎯 CONTINUOUS 100K PRODUCT MONITOR")
    print("=" * 60)
    print("Real-time tracking until 100,000 products achieved")
    print("=" * 60)
    
    start_time = time.time()
    last_count = 0
    
    while True:
        try:
            current_count, platform_stats, active_dbs = get_total_products()
            current_time = datetime.now()
            elapsed_hours = (time.time() - start_time) / 3600
            
            # Calculate growth rate
            growth_since_start = current_count - last_count if last_count > 0 else 0
            rate_per_hour = current_count / elapsed_hours if elapsed_hours > 0 else 0
            
            # Clear screen for live update effect
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🎯 LIVE 100K PRODUCT TRACKER")
            print("=" * 60)
            print(f"⏰ Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🕐 Runtime: {elapsed_hours:.1f} hours")
            print("=" * 60)
            
            # Progress display
            progress_pct = (current_count / 100000) * 100
            progress_bar_filled = int(progress_pct / 2)  # 50 chars max
            progress_bar = "█" * progress_bar_filled + "░" * (50 - progress_bar_filled)
            
            print(f"📊 PROGRESS TO 100K:")
            print(f"   Current Products: {current_count:,}")
            print(f"   Target: 100,000")
            print(f"   Progress: {progress_pct:.1f}%")
            print(f"   [{progress_bar}] {progress_pct:.1f}%")
            
            if current_count >= 100000:
                excess = current_count - 100000
                print(f"\n🎉 🎉 🎉 TARGET ACHIEVED! 🎉 🎉 🎉")
                print(f"🎯 100,000 products reached!")
                print(f"✨ Excess products: {excess:,}")
                print(f"⏰ Time to achieve: {elapsed_hours:.1f} hours")
                break
            
            remaining = 100000 - current_count
            print(f"   Remaining: {remaining:,} products")
            
            # Rate and time estimation
            print(f"\n🚀 COLLECTION RATE:")
            print(f"   Current rate: {rate_per_hour:.0f} products/hour")
            
            if rate_per_hour > 0:
                hours_remaining = remaining / rate_per_hour
                if hours_remaining < 1:
                    print(f"   Estimated completion: {hours_remaining * 60:.0f} minutes")
                else:
                    print(f"   Estimated completion: {hours_remaining:.1f} hours")
            
            # Database status
            print(f"\n💾 DATABASE STATUS:")
            print(f"   Active databases: {active_dbs}")
            
            # Top platforms
            print(f"\n🏆 TOP PLATFORMS:")
            for platform, count in platform_stats[:8]:
                platform_name = platform[:20]
                print(f"   {platform_name:20}: {count:>6,} products")
            
            # Database files summary
            db_files = glob.glob('*.db')
            total_db_size = sum(os.path.getsize(db) for db in db_files if os.path.exists(db)) / (1024 * 1024)
            print(f"\n📂 STORAGE:")
            print(f"   Database files: {len(db_files)}")
            print(f"   Total size: {total_db_size:.1f} MB")
            
            print(f"\n💡 TIPS:")
            print("   • Multiple scrapers are running in parallel")
            print("   • Progress updates every 60 seconds")
            print("   • Press Ctrl+C to stop monitoring")
            
            last_count = current_count
            time.sleep(60)  # Update every minute
            
        except KeyboardInterrupt:
            print(f"\n\n📊 MONITORING STOPPED BY USER")
            print(f"   Final count: {current_count:,} products")
            print(f"   Total runtime: {elapsed_hours:.1f} hours")
            break
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_continuously()