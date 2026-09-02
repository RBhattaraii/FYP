#!/usr/bin/env python3
"""
PROGRESS MONITOR
Real-time tracking of master database growth
"""

import sqlite3
import time
import os
from datetime import datetime

def monitor_progress():
    """Monitor master database progress"""
    print("📊 MASTER DATABASE PROGRESS MONITOR")
    print("=" * 45)
    
    prev_count = 0
    
    for i in range(20):  # Monitor for 20 checks
        try:
            conn = sqlite3.connect('master_products.db')
            cursor = conn.cursor()
            
            # Current total
            cursor.execute('SELECT COUNT(*) FROM products')
            current_count = cursor.fetchone()[0]
            
            # Growth since last check
            growth = current_count - prev_count
            
            # Progress metrics
            progress_50k = (current_count / 50000) * 100
            remaining_50k = 50000 - current_count
            
            # Platform distribution
            cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
            platforms = cursor.fetchall()
            
            # Display update
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] UPDATE #{i+1}")
            print(f"📈 Total: {current_count:,} (+{growth:,})")
            print(f"🎯 50k: {progress_50k:.1f}% ({remaining_50k:,} remaining)")
            
            # Top platforms
            print("🏪 Top platforms:")
            for platform, count in platforms[:4]:
                percentage = (count / current_count * 100) if current_count > 0 else 0
                print(f"   • {platform}: {count:,} ({percentage:.1f}%)")
            
            # Database size
            if os.path.exists('master_products.db'):
                size_mb = os.path.getsize('master_products.db') / (1024 * 1024)
                print(f"💾 Size: {size_mb:.1f} MB")
            
            # Check if target reached
            if current_count >= 50000:
                print(f"\n🎉 50K MILESTONE ACHIEVED!")
                print(f"✅ Final count: {current_count:,} unique products")
                break
            
            prev_count = current_count
            conn.close()
            
            # Wait before next check
            if i < 19:
                print("⏳ Next update in 30 seconds...")
                time.sleep(30)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
    
    print(f"\n📊 Monitoring complete at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    monitor_progress()