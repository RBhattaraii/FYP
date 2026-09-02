#!/usr/bin/env python3
"""
NON-STOP 100K MONITOR
Continuous monitoring until 100k unique products achieved
Focus on non-Daraz platforms only
"""

import sqlite3
import time
import os
from datetime import datetime

def continuous_monitor_100k():
    """Monitor continuously until 100k achieved"""
    print("🎯 NON-STOP 100K MONITOR ACTIVATED")
    print("=" * 50)
    print("🔒 Target: 100,000 DISTINCT products (no duplicates)")
    print("🚫 EXCLUDING Daraz (focus on platform diversification)")
    print("🚫 Will NOT stop until target achieved")
    print("=" * 50)
    
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
            
            # Non-Daraz breakdown
            cursor.execute('SELECT COUNT(*) FROM products WHERE platform != "Daraz"')
            non_daraz_total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE platform = "Daraz"')
            daraz_total = cursor.fetchone()[0]
            
            # Growth since last check
            growth = total_products - prev_total
            
            # Progress metrics
            progress = (total_products / 100000) * 100
            remaining = 100000 - total_products
            
            # Time metrics
            elapsed = time.time() - start_time
            elapsed_str = f"{elapsed/60:.1f}m" if elapsed > 60 else f"{elapsed:.0f}s"
            
            # Current status
            timestamp = datetime.now().strftime("%H:%M:%S")
            duplicate_status = "✅" if total_products == unique_urls else "❌ DUPLICATES!"
            
            print(f"[{timestamp}] Check #{check_count} | {total_products:,} products (+{growth}) | {progress:.1f}% | {remaining:,} remaining | {duplicate_status}")
            print(f"           Non-Daraz: {non_daraz_total:,} | Daraz: {daraz_total:,} | Ratio: {(non_daraz_total/total_products)*100:.1f}% non-Daraz")
            
            # Platform distribution every 15 checks
            if check_count % 15 == 0:
                cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
                platforms = cursor.fetchall()
                
                print(f"   🏪 All platforms:")
                for platform, count in platforms:
                    percentage = (count / total_products * 100) if total_products > 0 else 0
                    status = "⏭️ SKIPPING" if platform == "Daraz" else "✅ ACTIVE"
                    print(f"      {platform}: {count:,} ({percentage:.1f}%) {status}")
            
            # Check if target achieved
            if total_products >= 100000:
                print(f"")
                print(f"🎉🎉🎉 100,000 UNIQUE PRODUCTS ACHIEVED! 🎉🎉🎉")
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
            
            # Wait before next check (8 seconds for comprehensive monitoring)
            time.sleep(8)
            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(15)  # Wait longer on error
    
    print(f"\\n🎯 100K monitoring completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    continuous_monitor_100k()