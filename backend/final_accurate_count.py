#!/usr/bin/env python3
"""
Final Accurate Count - Proper platform naming and unique product count
"""

import sqlite3
import os
import glob

def get_accurate_count():
    print("🎯 FINAL ACCURATE PRODUCT COUNT")
    print("=" * 60)
    
    # Create temporary database for unique products
    temp_db = 'temp_unique_count.db'
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Create table for unique products with proper platform mapping
        cursor.execute('''
            CREATE TABLE unique_products (
                product_url TEXT PRIMARY KEY,
                title TEXT,
                price REAL,
                platform TEXT,
                source_db TEXT
            )
        ''')
        
        # Platform name mapping to standardize names
        platform_mapping = {
            'oliz': 'Oliz Store',
            'oliz_store': 'Oliz Store', 
            'Oliz': 'Oliz Store',
            'Oliz_Enhanced': 'Oliz Store',
            'hardwarepasal': 'Hardware Pasal',
            'HardwarePasal': 'Hardware Pasal',
            'HardwarePasal_Enhanced': 'Hardware Pasal',
            'cgdigital': 'CG Digital',
            'CGDigital': 'CG Digital',
            'jeevee': 'Jeevee',
            'Jeevee': 'Jeevee',
            'hukut': 'Hukut',
            'Hukut': 'Hukut',
            'better': 'Better',
            'Better': 'Better',
            'daraz': 'Daraz',
            'Daraz': 'Daraz'
        }
        
        # Get all database files
        db_files = glob.glob('*.db')
        db_files = [db for db in db_files if 'temp_' not in db and 'monitor' not in db]
        
        total_processed = 0
        
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
                
                # Get products with platform info
                source_cursor.execute('''
                    SELECT DISTINCT product_url, title, price, platform 
                    FROM products 
                    WHERE product_url IS NOT NULL AND product_url != ""
                ''')
                
                products = source_cursor.fetchall()
                source_conn.close()
                
                print(f"📂 {db_file:40} | {len(products):>6,} products")
                
                for product_url, title, price, platform in products:
                    # Determine platform
                    if platform:
                        # Map platform name
                        mapped_platform = platform_mapping.get(platform, platform)
                    else:
                        # Infer from filename
                        filename_lower = db_file.lower()
                        if 'oliz' in filename_lower:
                            mapped_platform = 'Oliz Store'
                        elif 'hardware' in filename_lower:
                            mapped_platform = 'Hardware Pasal'
                        elif 'jeevee' in filename_lower:
                            mapped_platform = 'Jeevee'
                        elif 'cgdigital' in filename_lower or 'cg' in filename_lower:
                            mapped_platform = 'CG Digital'
                        elif 'hukut' in filename_lower:
                            mapped_platform = 'Hukut'
                        elif 'better' in filename_lower:
                            mapped_platform = 'Better'
                        elif 'daraz' in filename_lower:
                            mapped_platform = 'Daraz'
                        else:
                            mapped_platform = 'Unknown'
                    
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO unique_products 
                            (product_url, title, price, platform, source_db)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (product_url, title, price, mapped_platform, db_file))
                        total_processed += 1
                    except:
                        continue
                        
            except Exception as e:
                print(f"❌ Error processing {db_file}: {str(e)[:50]}...")
                continue
        
        conn.commit()
        
        # Get final counts
        cursor.execute('SELECT COUNT(*) FROM unique_products')
        total_unique = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT platform, COUNT(*) 
            FROM unique_products 
            GROUP BY platform 
            ORDER BY COUNT(*) DESC
        ''')
        platform_stats = cursor.fetchall()
        
        # Exclude Daraz count
        cursor.execute('''
            SELECT COUNT(*) 
            FROM unique_products 
            WHERE platform != "Daraz"
        ''')
        non_daraz_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("=" * 60)
        print(f"📊 FINAL ACCURATE RESULTS:")
        print(f"   Total unique products: {total_unique:,}")
        print(f"   Non-Daraz products: {non_daraz_count:,}")
        print(f"   Products processed: {total_processed:,}")
        
        print(f"\n🏆 PLATFORM BREAKDOWN:")
        target_platforms = ['Jeevee', 'CG Digital', 'Hukut', 'Oliz Store', 'Better', 'Hardware Pasal']
        
        for platform, count in platform_stats:
            if platform == 'Daraz':
                print(f"   🚫 {platform:20}: {count:>6,} products (excluded)")
            elif platform in target_platforms:
                print(f"   ✅ {platform:20}: {count:>6,} products")
            else:
                print(f"   📝 {platform:20}: {count:>6,} products")
        
        print(f"\n🎯 TARGET ANALYSIS:")
        if total_unique >= 100000:
            print(f"   🎉 TARGET ACHIEVED: {total_unique:,} products!")
            print(f"   📈 Exceeded by: {total_unique - 100000:,} products")
        else:
            print(f"   📊 Progress: {total_unique/100000*100:.1f}% ({total_unique:,}/100,000)")
            print(f"   📋 Remaining: {100000 - total_unique:,} products")
        
        if non_daraz_count >= 100000:
            print(f"   🎉 NON-DARAZ TARGET: {non_daraz_count:,} products (achieved!)")
        else:
            print(f"   📊 Non-Daraz progress: {non_daraz_count/100000*100:.1f}%")
        
        print(f"\n📂 EXPECTED PLATFORMS STATUS:")
        for platform in target_platforms:
            found = any(p[0] == platform for p in platform_stats)
            count = next((p[1] for p in platform_stats if p[0] == platform), 0)
            if found and count > 0:
                print(f"   ✅ {platform}: {count:,} products")
            else:
                print(f"   ❌ {platform}: Not found or 0 products")
        
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

if __name__ == "__main__":
    get_accurate_count()