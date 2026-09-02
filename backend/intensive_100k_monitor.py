#!/usr/bin/env python3
"""
INTENSIVE 100K MONITOR - REAL-TIME PROGRESS TRACKING
High-frequency monitoring with rate calculations
"""

import sqlite3
import time
from datetime import datetime

def intensive_monitor():
    print("⚡ INTENSIVE 100K MONITOR - MAXIMUM FREQUENCY")
    print("=" * 60)
    print("📊 Real-time tracking every 2 seconds")
    print("🎯 Target: 100,000 products in 60 minutes")
    print("=" * 60)
    
    start_time = time.time()
    check_count = 0
    prev_count = 0
    target_rate = 1000  # products per minute
    
    while True:
        try:
            check_count += 1
            
            conn = sqlite3.connect('master_products.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM products')
            current_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE platform != "Daraz"')
            non_daraz = cursor.fetchone()[0]
            
            elapsed = time.time() - start_time
            elapsed_min = elapsed / 60
            
            # Calculate rates
            growth = current_count - prev_count
            current_rate = (current_count - 40724) / elapsed_min if elapsed_min > 0 else 0  # Rate since start (40724 was starting count)
            instant_rate = growth * 30 if growth > 0 else 0  # Instant rate (checks every 2s, so *30 for per minute)
            
            remaining = 100000 - current_count
            eta_min = remaining / current_rate if current_rate > 0 else float('inf')
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Progress indicators
            progress = (current_count / 100000) * 100
            rate_status = "🔥" if current_rate >= target_rate else "⚡" if current_rate >= 500 else "🐌"
            
            print(f"[{timestamp}] {current_count:,}/100k ({progress:.1f}%) | +{growth} | Rate: {current_rate:.0f}/min {rate_status} | ETA: {eta_min:.1f}min | Non-Daraz: {non_daraz:,}")
            
            # Platform breakdown every 30 checks (1 minute)
            if check_count % 30 == 0:
                cursor.execute('SELECT platform, COUNT(*) FROM products WHERE platform != "Daraz" GROUP BY platform ORDER BY COUNT(*) DESC')
                platforms = cursor.fetchall()
                
                print(f"   📊 Non-Daraz platforms:")
                for platform, count in platforms[:8]:
                    print(f"      {platform}: {count:,}")
                
                # Performance analysis
                if current_rate < target_rate:
                    deficit = target_rate - current_rate
                    print(f"   ⚠️  Rate deficit: -{deficit:.0f}/min (need {target_rate}/min for 1hr target)")
            
            # Check if target achieved
            if current_count >= 100000:
                total_time = elapsed / 60
                avg_rate = (current_count - 40724) / total_time
                
                print(f"")
                print(f"🎉🎉🎉 100,000 PRODUCTS ACHIEVED! 🎉🎉🎉")
                print(f"⏱️  Completion time: {total_time:.1f} minutes")
                print(f"📈 Average rate: {avg_rate:.0f} products/minute")
                print(f"🏆 Total scraped: {current_count - 40724:,} new products")
                
                cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
                final_platforms = cursor.fetchall()
                
                print(f"\\n🏪 FINAL PLATFORM DISTRIBUTION:")
                for platform, count in final_platforms:
                    percentage = (count / current_count * 100)
                    print(f"   {platform}: {count:,} products ({percentage:.1f}%)")
                
                conn.close()
                break
            
            conn.close()
            prev_count = current_count
            
            # High frequency monitoring - check every 2 seconds
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(5)
    
    print(f"\\n⚡ Intensive monitoring completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    intensive_monitor()