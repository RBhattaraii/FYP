#!/usr/bin/env python3
"""
Check Scraper Status - See which scrapers are actively collecting data
"""

import sqlite3
import os
import glob
import time
from datetime import datetime

def check_scraper_status():
    print('🔍 CHECKING SCRAPER STATUS AND PLATFORM DATA')
    print('=' * 60)

    # Get all database files
    db_files = glob.glob('*.db')
    db_files.sort()

    total_products = 0
    platform_data = {}
    active_scrapers = []

    for db_file in db_files:
        try:
            if not os.path.exists(db_file):
                continue
                
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if products table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if not cursor.fetchone():
                conn.close()
                continue
            
            # Get product count
            cursor.execute('SELECT COUNT(*) FROM products')
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Get platform info
                cursor.execute('SELECT DISTINCT platform FROM products WHERE platform IS NOT NULL')
                platforms = [p[0] for p in cursor.fetchall() if p[0]]
                
                if not platforms:
                    # Try to determine platform from filename
                    if 'oliz' in db_file.lower():
                        platforms = ['Oliz Store']
                    elif 'hardware' in db_file.lower():
                        platforms = ['Hardware Pasal']
                    elif 'jeevee' in db_file.lower():
                        platforms = ['Jeevee']
                    elif 'cgdigital' in db_file.lower():
                        platforms = ['CG Digital']
                    elif 'hukut' in db_file.lower():
                        platforms = ['Hukut']
                    elif 'better' in db_file.lower():
                        platforms = ['Better']
                    else:
                        platforms = [db_file.replace('.db', '').replace('_', ' ').title()]
                
                size_mb = os.path.getsize(db_file) / 1024 / 1024
                
                print(f'{db_file:40} | {count:>6,} products | {size_mb:>5.1f}MB | {", ".join(platforms)}')
                total_products += count
                
                for platform in platforms:
                    if platform in platform_data:
                        platform_data[platform] += count
                    else:
                        platform_data[platform] = count
            
            conn.close()
            
        except Exception as e:
            print(f'{db_file:40} | ERROR: {str(e)[:30]}...')

    print('=' * 60)        
    print(f'TOTAL PRODUCTS ACROSS ALL DATABASES: {total_products:,}')
    print()
    
    print('📊 PLATFORM BREAKDOWN:')
    for platform, count in sorted(platform_data.items(), key=lambda x: x[1], reverse=True):
        print(f'  {platform:25}: {count:>6,} products')

    print()
    print('🕐 RECENT DATABASE ACTIVITY (Last 30 minutes):')
    
    current_time = time.time()
    recent_activity = False

    for db_file in sorted(db_files):
        if os.path.exists(db_file):
            mod_time = os.path.getmtime(db_file)
            age_minutes = (current_time - mod_time) / 60
            
            if age_minutes < 30:  # Modified in last 30 minutes
                size_mb = os.path.getsize(db_file) / 1024 / 1024
                print(f'  📝 {db_file:35} | Modified {age_minutes:>4.1f} min ago | {size_mb:>5.1f}MB')
                recent_activity = True

    if not recent_activity:
        print('  ⚠️  No databases modified in the last 30 minutes')
        print('  🔍 Scrapers may have stopped or completed')

    print()
    print('🎯 EXPECTED PLATFORMS (excluding Daraz):')
    expected = ['Jeevee', 'CG Digital', 'Hukut', 'Oliz Store', 'Better', 'Hardware Pasal']
    for platform in expected:
        if any(platform.lower() in p.lower() for p in platform_data.keys()):
            status = '✅'
        else:
            status = '❌'
        print(f'  {status} {platform}')

if __name__ == "__main__":
    check_scraper_status()