#!/usr/bin/env python3
"""
Monitor Scaled Scrapers Progress - Real-time tracking
"""

import sqlite3
import time
import os
from datetime import datetime

def get_db_stats(db_file):
    """Get product count from database"""
    if not os.path.exists(db_file):
        return 0
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def monitor_progress():
    """Monitor all scaled scraper databases"""
    
    # Define expected database files
    db_files = [
        # Original scrapers
        'quick_working_products.db',
        'fixed_oliz_products.db',
        'fixed_hardwarepasal_products.db',
        
        # Scaled scrapers
        'scaled_oliz_oliz_1.db',
        'scaled_oliz_oliz_2.db', 
        'scaled_oliz_oliz_3.db',
        'scaled_oliz_oliz_4.db',
        'scaled_hardware_hardware_1.db',
        'scaled_hardware_hardware_2.db',
        'scaled_hardware_hardware_3.db',
        'scaled_hardware_hardware_4.db'
    ]
    
    print("🔍 SCALED SCRAPER PROGRESS MONITOR")
    print("=" * 60)
    
    while True:
        try:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - LIVE PROGRESS")
            print("-" * 60)
            
            total_products = 0
            oliz_total = 0
            hardware_total = 0
            
            # Check each database
            for db_file in db_files:
                count = get_db_stats(db_file)
                total_products += count
                
                if count > 0:
                    if 'oliz' in db_file:
                        oliz_total += count
                        platform = "OLIZ"
                    elif 'hardware' in db_file:
                        hardware_total += count  
                        platform = "HARDWARE"
                    else:
                        platform = "MIXED"
                    
                    # Show file size too
                    size_mb = os.path.getsize(db_file) / 1024 / 1024 if os.path.exists(db_file) else 0
                    
                    print(f"  {platform:8} | {db_file:30} | {count:>6,} products | {size_mb:>4.1f}MB")
            
            print("-" * 60)
            print(f"📊 TOTALS:")
            print(f"  Oliz platforms:     {oliz_total:>8,} products")  
            print(f"  Hardware platforms: {hardware_total:>8,} products")
            print(f"  GRAND TOTAL:        {total_products:>8,} products")
            print(f"  Progress to 100k:   {total_products/100000*100:>8.1f}%")
            
            # Progress bar
            progress = min(100, total_products/100000*100)
            filled = int(progress / 2)
            bar = "█" * filled + "░" * (50 - filled)
            print(f"  [{bar}] {progress:.1f}%")
            
            if total_products >= 100000:
                print(f"\n🎉 TARGET ACHIEVED: 100K+ PRODUCTS!")
                break
            else:
                remaining = 100000 - total_products
                print(f"  Remaining:          {remaining:>8,} products")
            
            # Estimate rate if we have previous data
            print(f"\n💡 INSIGHTS:")
            if total_products > 0:
                rate_per_minute = total_products / 5  # Rough estimate
                hours_to_100k = remaining / (rate_per_minute * 60) if rate_per_minute > 0 else float('inf')
                print(f"  Estimated rate:     ~{rate_per_minute:.0f} products/minute")
                if hours_to_100k < 24:
                    print(f"  Time to 100k:       ~{hours_to_100k:.1f} hours")
            
            print(f"  Active databases:   {sum(1 for db in db_files if get_db_stats(db) > 0)}")
            
            time.sleep(30)  # Update every 30 seconds
            
        except KeyboardInterrupt:
            print(f"\n\n📊 FINAL SUMMARY:")
            print(f"   Total Products: {total_products:,}")
            print(f"   Monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_progress()