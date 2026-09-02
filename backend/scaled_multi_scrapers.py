#!/usr/bin/env python3
"""
Scaled Multi-Scrapers - Multiple instances for 100k products
Create separate scrapers for different categories and sections
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import threading
from datetime import datetime

class ScaledOlizScraper:
    def __init__(self, instance_id, search_categories):
        self.instance_id = instance_id
        self.search_categories = search_categories
        self.db_name = f'scaled_oliz_{instance_id}.db'
        self.session = requests.Session()
        self.total_scraped = 0
        self.setup_database()
        self.setup_session()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                price_text TEXT,
                image_url TEXT,
                product_url TEXT UNIQUE,
                category TEXT,
                platform TEXT DEFAULT 'oliz',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        conn.commit()
        conn.close()
        print(f"✅ Scaled Oliz {self.instance_id} database ready")

    def setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def add_product(self, product_data):
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, price_text, image_url, product_url, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_data['title'],
                product_data['price'],
                product_data['price_text'],
                product_data['image_url'],
                product_data['product_url'],
                product_data['category']
            ))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except:
            return False

    def get_product_count(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

    def scrape_oliz_categories(self):
        """Scrape Oliz using category-specific search"""
        print(f"🔍 OLIZ INSTANCE {self.instance_id}: {len(self.search_categories)} categories")
        
        for category in self.search_categories:
            print(f"   📂 Searching: {category}")
            
            # Try multiple URL patterns for each category
            url_patterns = [
                f"https://olizstore.com/search?q={category.replace(' ', '+')}",
                f"https://olizstore.com/products?search={category.replace(' ', '+')}",
                f"https://olizstore.com/category/{category.replace(' ', '-')}",
                f"https://olizstore.com/{category.replace(' ', '-')}",
                # Also try the main pages with different page numbers
                "https://olizstore.com/products",
                "https://olizstore.com"
            ]
            
            for base_url in url_patterns[:2]:  # Focus on first 2 patterns
                
                for page in range(1, 21):  # Up to 20 pages per category
                    try:
                        url = f"{base_url}&page={page}" if page > 1 else base_url
                        
                        response = self.session.get(url, timeout=20)
                        if response.status_code != 200:
                            break
                            
                        soup = BeautifulSoup(response.content, 'html.parser')
                        elements = soup.select('div[class*="product"]')
                        
                        page_products = 0
                        
                        for elem in elements:
                            try:
                                # Get title
                                title = ""
                                for sel in ['h3', 'h4', 'h2', '.title', '.product-title', 'a']:
                                    title_elem = elem.select_one(sel)
                                    if title_elem:
                                        title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                                        if len(title) > 8:
                                            break
                                
                                # Get price
                                price_text = ""
                                price = 0
                                for sel in ['.price', '.product-price', '.cost', '.amount', '[class*="price"]']:
                                    price_elem = elem.select_one(sel)
                                    if price_elem:
                                        price_text = price_elem.get_text(strip=True)
                                        if price_text:
                                            try:
                                                price_digits = ''.join(c for c in price_text if c.isdigit() or c == '.')
                                                if price_digits:
                                                    price = float(price_digits)
                                                    break
                                            except:
                                                continue
                                
                                # Get link
                                link_elem = elem.select_one('a')
                                if not link_elem:
                                    continue
                                    
                                product_url = link_elem.get('href', '')
                                if product_url.startswith('/'):
                                    product_url = f"https://olizstore.com{product_url}"
                                elif not product_url.startswith('http'):
                                    continue
                                
                                # Get image
                                image_url = ""
                                img_elem = elem.select_one('img')
                                if img_elem:
                                    img_src = img_elem.get('src') or img_elem.get('data-src', '')
                                    if img_src:
                                        if img_src.startswith('/'):
                                            image_url = f"https://olizstore.com{img_src}"
                                        elif img_src.startswith('http'):
                                            image_url = img_src
                                
                                if title and product_url and len(title) > 5:
                                    product = {
                                        'title': title[:200],
                                        'price': price,
                                        'price_text': price_text,
                                        'image_url': image_url,
                                        'product_url': product_url,
                                        'category': category
                                    }
                                    
                                    if self.add_product(product):
                                        page_products += 1
                                        self.total_scraped += 1
                                        
                            except:
                                continue
                        
                        if page_products > 0:
                            current_total = self.get_product_count()
                            print(f"      Page {page}: +{page_products} | Total: {current_total:,}")
                        else:
                            break  # No products on this page
                            
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception:
                        time.sleep(5)
                        continue
                
                # Small delay between URL patterns
                time.sleep(1)
            
            # Delay between categories
            time.sleep(2)

    def run(self):
        """Run this Oliz instance"""
        start_time = time.time()
        self.scrape_oliz_categories()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ OLIZ INSTANCE {self.instance_id} COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        return final_count

class ScaledHardwarePasalScraper:
    def __init__(self, instance_id, page_range):
        self.instance_id = instance_id
        self.page_start, self.page_end = page_range
        self.db_name = f'scaled_hardware_{instance_id}.db'
        self.session = requests.Session()
        self.total_scraped = 0
        self.setup_database()
        self.setup_session()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                price_text TEXT,
                image_url TEXT,
                product_url TEXT UNIQUE,
                platform TEXT DEFAULT 'hardwarepasal',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        conn.commit()
        conn.close()
        print(f"✅ Scaled HardwarePasal {self.instance_id} database ready")

    def setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def add_product(self, product_data):
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, price_text, image_url, product_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                product_data['title'],
                product_data['price'],
                product_data['price_text'],
                product_data['image_url'],
                product_data['product_url']
            ))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except:
            return False

    def get_product_count(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

    def scrape_hardware_pages(self):
        """Scrape HardwarePasal pages in assigned range"""
        print(f"🔍 HARDWARE INSTANCE {self.instance_id}: Pages {self.page_start}-{self.page_end}")
        
        for page in range(self.page_start, self.page_end + 1):
            try:
                url = f"https://hardwarepasal.com?page={page}" if page > 1 else "https://hardwarepasal.com"
                
                response = self.session.get(url, timeout=25)
                if response.status_code != 200:
                    print(f"   Page {page}: HTTP {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.select('div[class*="product"]')
                
                page_products = 0
                
                for elem in elements:
                    try:
                        # Get title
                        title = ""
                        for sel in ['h3', 'h4', 'h2', '.title', '.product-title', 'a']:
                            title_elem = elem.select_one(sel)
                            if title_elem:
                                title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                                if len(title) > 8:
                                    break
                        
                        # Get price
                        price_text = ""
                        price = 0
                        for sel in ['.cnit-product-price', '.price', '.product-price', '.cost']:
                            price_elem = elem.select_one(sel)
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                if price_text and any(c.isdigit() for c in price_text):
                                    try:
                                        price_clean = price_text.replace('Rs.', '').replace(',', '').strip()
                                        price_digits = ''.join(c for c in price_clean if c.isdigit() or c == '.')
                                        if price_digits:
                                            price = float(price_digits)
                                            break
                                    except:
                                        continue
                        
                        # Get link
                        link_elem = elem.select_one('a')
                        if not link_elem:
                            continue
                            
                        product_url = link_elem.get('href', '')
                        if product_url.startswith('/'):
                            product_url = f"https://hardwarepasal.com{product_url}"
                        elif not product_url.startswith('http'):
                            continue
                        
                        # Get image
                        image_url = ""
                        img_elem = elem.select_one('img')
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src', '')
                            if img_src:
                                if img_src.startswith('/'):
                                    image_url = f"https://hardwarepasal.com{img_src}"
                                elif img_src.startswith('http'):
                                    image_url = img_src
                        
                        if title and product_url and len(title) > 5:
                            product = {
                                'title': title[:200],
                                'price': price,
                                'price_text': price_text,
                                'image_url': image_url,
                                'product_url': product_url
                            }
                            
                            if self.add_product(product):
                                page_products += 1
                                self.total_scraped += 1
                                
                    except:
                        continue
                
                current_total = self.get_product_count()
                print(f"   Page {page}: +{page_products} | Total: {current_total:,}")
                    
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"   Page {page}: Error - {e}")
                time.sleep(10)
                continue

    def run(self):
        """Run this HardwarePasal instance"""
        start_time = time.time()
        self.scrape_hardware_pages()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ HARDWARE INSTANCE {self.instance_id} COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        return final_count

def main():
    """Launch multiple scraper instances"""
    print("🚀 SCALED MULTI-SCRAPERS FOR 100K PRODUCTS")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Define category groups for Oliz instances
    oliz_categories = [
        # Instance 1: Electronics & Tech
        ['electronics', 'phone', 'mobile', 'smartphone', 'iphone', 'samsung', 'laptop', 'computer', 'tablet', 'headphones', 'speaker', 'charger', 'cable', 'accessories'],
        
        # Instance 2: Fashion & Clothing  
        ['clothing', 'fashion', 'shirt', 't-shirt', 'dress', 'pants', 'jeans', 'shoes', 'sneakers', 'bag', 'backpack', 'watch', 'jewelry', 'sunglasses'],
        
        # Instance 3: Home & Living
        ['home', 'decor', 'furniture', 'kitchen', 'bedroom', 'bathroom', 'lighting', 'storage', 'curtains', 'bedding', 'cushions', 'carpet'],
        
        # Instance 4: Health & Beauty
        ['beauty', 'skincare', 'makeup', 'cosmetics', 'perfume', 'shampoo', 'cream', 'moisturizer', 'soap', 'health', 'fitness', 'yoga']
    ]
    
    # Define page ranges for HardwarePasal instances
    hardware_ranges = [
        (1, 25),    # Instance 1: Pages 1-25
        (26, 50),   # Instance 2: Pages 26-50  
        (51, 75),   # Instance 3: Pages 51-75
        (76, 100)   # Instance 4: Pages 76-100
    ]
    
    # Create and start all scrapers
    scrapers = []
    threads = []
    
    # Create Oliz scrapers
    for i, categories in enumerate(oliz_categories):
        scraper = ScaledOlizScraper(f"oliz_{i+1}", categories)
        scrapers.append(scraper)
        thread = threading.Thread(target=scraper.run)
        threads.append(thread)
    
    # Create HardwarePasal scrapers  
    for i, page_range in enumerate(hardware_ranges):
        scraper = ScaledHardwarePasalScraper(f"hardware_{i+1}", page_range)
        scrapers.append(scraper)
        thread = threading.Thread(target=scraper.run)
        threads.append(thread)
    
    # Start all threads with delays
    for i, thread in enumerate(threads):
        thread.start()
        time.sleep(3)  # 3 second delay between starts
        print(f"🚀 Started scraper {i+1}/8")
    
    print(f"\n📊 ALL 8 SCRAPERS RUNNING IN PARALLEL")
    print("   - 4 Oliz instances (different categories)")  
    print("   - 4 HardwarePasal instances (different page ranges)")
    print("   This should dramatically increase product collection rate!")
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    # Calculate final results
    total_products = 0
    oliz_total = 0
    hardware_total = 0
    
    for scraper in scrapers:
        count = scraper.get_product_count()
        total_products += count
        
        if 'oliz' in scraper.db_name:
            oliz_total += count
        else:
            hardware_total += count
    
    print(f"\n🎉 ALL SCALED SCRAPERS COMPLETE!")
    print(f"   Oliz Total: {oliz_total:,} products")
    print(f"   Hardware Total: {hardware_total:,} products") 
    print(f"   GRAND TOTAL: {total_products:,} products")
    print(f"   Progress to 100k: {total_products/100000*100:.1f}%")
    
    if total_products >= 100000:
        print("🎯 TARGET ACHIEVED: 100K+ PRODUCTS!")
    else:
        remaining = 100000 - total_products
        print(f"   Remaining for 100k: {remaining:,} products")
        print(f"💡 Run more instances or explore additional sites to reach 100k")

if __name__ == "__main__":
    main()