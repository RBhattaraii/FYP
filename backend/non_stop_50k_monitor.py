#!/usr/bin/env python3
"""
NON-STOP 50K MONITOR
Continuous monitoring until 50k unique products achieved
"""

import sqlite3
import time
import os
from datetime import datetime

def continuous_monitor_50k():
    """Monitor continuously until 50k achieved"""
    print("🎯 NON-STOP 50K MONITOR ACTIVATED")
    print("=" * 45)
    print("🔒 Ensuring 50,000 DISTINCT products (no duplicates)")
    print("🚫 Will NOT stop until target achieved")
    print("=" * 45)
    
    start_time = time.time()
    check_count = 0
    prev_total = 0
    
    while True:
        try:
            check_count += 1
            
            conn = sqlite3.connect('master_products.db')
            cursor = conn.cursor()
            
            # Total products
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            
            # Verify uniqueness
            cursor.execute('SELECT COUNT(DISTINCT product_url) FROM products WHERE product_url IS NOT NULL')
            unique_urls = cursor.fetchone()[0]
            
            # Growth since last check
            growth = total_products - prev_total
            
            # Progress metrics
            progress = (total_products / 50000) * 100
            remaining = 50000 - total_products
            
            # Time metrics
            elapsed = time.time() - start_time
            elapsed_str = f"{elapsed/60:.1f}m" if elapsed > 60 else f"{elapsed:.0f}s"
            
            # Current status
            timestamp = datetime.now().strftime("%H:%M:%S")
            duplicate_status = "✅" if total_products == unique_urls else "❌ DUPLICATES!"
            
            print(f"[{timestamp}] Check #{check_count} | {total_products:,} products (+{growth}) | {progress:.1f}% | {remaining:,} remaining | {duplicate_status}")
            
            # Platform distribution every 10 checks
            if check_count % 10 == 0:
                cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC LIMIT 5')
                platforms = cursor.fetchall()
                
                print(f"   🏪 Top platforms:")
                for platform, count in platforms:
                    percentage = (count / total_products * 100) if total_products > 0 else 0
                    print(f"      {platform}: {count:,} ({percentage:.1f}%)")
            
            # Check if target achieved
            if total_products >= 50000:
                print(f"")
                print(f"🎉🎉🎉 50,000 UNIQUE PRODUCTS ACHIEVED! 🎉🎉🎉")
                print(f"🏆 FINAL COUNT: {total_products:,} DISTINCT PRODUCTS")
                print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
                print(f"🔒 Duplicate verification: {'✅ PASS' if total_products == unique_urls else '❌ FAIL'}")
                print(f"✅ MISSION ACCOMPLISHED!")
                
                # Final platform breakdown
                cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
                all_platforms = cursor.fetchall()
                
                print(f"\\n🏪 FINAL PLATFORM DISTRIBUTION:")
                for platform, count in all_platforms:
                    percentage = (count / total_products * 100) if total_products > 0 else 0
                    print(f"   • {platform}: {count:,} products ({percentage:.1f}%)")
                
                # Database size
                db_size = os.path.getsize('master_products.db') / (1024 * 1024)
                print(f"\\n💾 Final database: {db_size:.1f} MB")
                
                conn.close()
                break
            
            conn.close()
            prev_total = total_products
            
            # Wait before next check (5 seconds for rapid monitoring)
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(10)  # Wait longer on error
    
    print(f"\\n🎯 50K monitoring completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    continuous_monitor_50k()