#!/usr/bin/env python3
"""
CHECK AND CLEAN DUPLICATES FOR 100K TARGET
Analyze duplicates, clean database, and prepare for 100k non-Daraz scraping
"""

import sqlite3
from datetime import datetime

def analyze_duplicates():
    """Analyze and report duplicate products"""
    print("🔍 ANALYZING DUPLICATES FOR 100K TARGET")
    print("=" * 50)
    
    conn = sqlite3.connect('master_products.db')
    cursor = conn.cursor()
    
    # Get total counts
    cursor.execute('SELECT COUNT(*) as total FROM products')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT product_url) as unique_urls FROM products WHERE product_url IS NOT NULL')
    unique_urls = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE product_url IS NULL OR product_url = ""')
    null_urls = cursor.fetchone()[0]
    
    duplicates = total - unique_urls
    
    print(f"📊 CURRENT DATABASE STATUS:")
    print(f"   Total products: {total:,}")
    print(f"   Unique URLs: {unique_urls:,}")
    print(f"   NULL/Empty URLs: {null_urls:,}")
    print(f"   Duplicates found: {duplicates:,}")
    print(f"   Data quality: {(unique_urls/total)*100:.1f}%")
    
    # Platform breakdown
    cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
    platforms = cursor.fetchall()
    
    print(f"\\n🏪 PLATFORM DISTRIBUTION:")
    for platform, count in platforms:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {platform}: {count:,} products ({percentage:.1f}%)")
    
    # Find actual duplicate URLs
    cursor.execute('''
        SELECT product_url, COUNT(*) as count, 
               GROUP_CONCAT(DISTINCT platform) as platforms,
               MAX(title) as sample_title
        FROM products 
        WHERE product_url IS NOT NULL AND product_url != ""
        GROUP BY product_url 
        HAVING COUNT(*) > 1 
        ORDER BY COUNT(*) DESC 
        LIMIT 10
    ''')
    duplicate_details = cursor.fetchall()
    
    if duplicate_details:
        print(f"\\n🚨 SAMPLE DUPLICATE PRODUCTS:")
        for url, count, platforms, title in duplicate_details:
            print(f"   URL: {url[:60]}...")
            print(f"   Appears: {count} times across platforms: {platforms}")
            print(f"   Title: {title[:50]}...")
            print()
    
    # Non-Daraz analysis for 100k target
    cursor.execute('SELECT COUNT(*) FROM products WHERE platform != "Daraz"')
    non_daraz_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT product_url) FROM products WHERE platform != "Daraz" AND product_url IS NOT NULL')
    unique_non_daraz = cursor.fetchone()[0]
    
    print(f"🎯 100K TARGET ANALYSIS (EXCLUDING DARAZ):")
    print(f"   Current non-Daraz products: {non_daraz_count:,}")
    print(f"   Unique non-Daraz URLs: {unique_non_daraz:,}")
    print(f"   Needed for 100k total: {100000 - unique_urls:,}")
    print(f"   Needed non-Daraz for balance: {100000 - unique_non_daraz:,}")
    
    conn.close()
    
    return {
        'total': total,
        'unique_urls': unique_urls,
        'duplicates': duplicates,
        'non_daraz_unique': unique_non_daraz
    }

def clean_duplicates():
    """Remove duplicate products keeping the first occurrence"""
    print(f"\\n🧹 CLEANING DUPLICATES...")
    
    conn = sqlite3.connect('master_products.db')
    cursor = conn.cursor()
    
    # Remove duplicates keeping the lowest ID (first occurrence)
    cursor.execute('''
        DELETE FROM products 
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM products
            WHERE product_url IS NOT NULL AND product_url != ""
            GROUP BY product_url
        ) AND product_url IS NOT NULL AND product_url != ""
    ''')
    
    deleted_count = cursor.rowcount
    conn.commit()
    
    # Also remove products with NULL/empty URLs
    cursor.execute('DELETE FROM products WHERE product_url IS NULL OR product_url = ""')
    null_deleted = cursor.rowcount
    conn.commit()
    
    print(f"   ✅ Removed {deleted_count:,} duplicate products")
    print(f"   ✅ Removed {null_deleted:,} products with invalid URLs")
    
    # Verify cleanup
    cursor.execute('SELECT COUNT(*) FROM products')
    final_total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT product_url) FROM products WHERE product_url IS NOT NULL')
    final_unique = cursor.fetchone()[0]
    
    print(f"   📊 After cleanup: {final_total:,} products (100% unique)")
    print(f"   🎯 Progress toward 100k: {(final_total/100000)*100:.1f}%")
    
    conn.close()
    return final_total

def main():
    print(f"🚀 100K UNIQUE PRODUCTS TARGET - DUPLICATE ANALYSIS & CLEANUP")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Analyze current state
    stats = analyze_duplicates()
    
    # Clean if duplicates found
    if stats['duplicates'] > 0:
        final_count = clean_duplicates()
    else:
        print(f"\\n✅ NO DUPLICATES FOUND - Database is already clean!")
        final_count = stats['unique_urls']
    
    print(f"\\n🎯 READY FOR 100K NON-DARAZ SCRAPING!")
    print(f"   Current unique products: {final_count:,}")
    print(f"   Target: 100,000 products")
    print(f"   Remaining needed: {100000 - final_count:,}")
    print(f"   Strategy: Focus on non-Daraz platforms only")
    print("=" * 70)

if __name__ == "__main__":
    main()