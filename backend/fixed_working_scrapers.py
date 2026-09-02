#!/usr/bin/env python3
"""
Fixed Working Scrapers - Direct approach for 100k products
Based on successful testing, focus on sites that actually work
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime
import threading

class FixedOlizScraper:
    def __init__(self):
        self.db_name = 'fixed_oliz_products.db'
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
                platform TEXT DEFAULT 'oliz',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        conn.commit()
        conn.close()
        print("✅ Fixed Oliz database ready")

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

    def scrape_oliz_pages(self):
        """Scrape Oliz using direct page approach"""
        print("🔍 SCRAPING OLIZ STORE")
        
        # Start with known working URLs
        base_urls = [
            "https://olizstore.com/products",  # 389 products found
            "https://olizstore.com"           # 84 products found
        ]
        
        for base_url in base_urls:
            print(f"\n📱 {base_url}")
            
            for page in range(1, 51):  # Try up to 50 pages
                try:
                    url = f"{base_url}?page={page}" if page > 1 else base_url
                    
                    response = self.session.get(url, timeout=20)
                    if response.status_code != 200:
                        print(f"   Page {page}: HTTP {response.status_code}")
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
                                    'product_url': product_url
                                }
                                
                                if self.add_product(product):
                                    page_products += 1
                                    self.total_scraped += 1
                                    
                        except:
                            continue
                    
                    current_total = self.get_product_count()
                    print(f"   Page {page}: +{page_products} products | Total: {current_total:,}")
                    
                    if page_products == 0:
                        print(f"   No more products found, stopping at page {page}")
                        break
                        
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"   Page {page}: Error - {e}")
                    time.sleep(5)
                    continue

    def run(self):
        """Run Oliz scraper"""
        start_time = time.time()
        self.scrape_oliz_pages()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ OLIZ SCRAPING COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        print(f"   Rate: {final_count/(runtime/60):.0f} products/minute")

class FixedHardwarePasalScraper:
    def __init__(self):
        self.db_name = 'fixed_hardwarepasal_products.db'
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
        print("✅ Fixed HardwarePasal database ready")

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

    def scrape_hardwarepasal_pages(self):
        """Scrape HardwarePasal using direct page approach"""
        print("🔍 SCRAPING HARDWARE PASAL")
        
        for page in range(1, 101):  # Try up to 100 pages (they had 597 products on page 1)
            try:
                url = f"https://hardwarepasal.com?page={page}" if page > 1 else "https://hardwarepasal.com"
                
                response = self.session.get(url, timeout=25)
                if response.status_code != 200:
                    print(f"Page {page}: HTTP {response.status_code}")
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
                        
                        # Get price - HardwarePasal specific
                        price_text = ""
                        price = 0
                        for sel in ['.cnit-product-price', '.price', '.product-price', '.cost']:
                            price_elem = elem.select_one(sel)
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                if price_text and any(c.isdigit() for c in price_text):
                                    try:
                                        # Extract price from "Rs. 12,345" format
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
                print(f"Page {page}: +{page_products} products | Total: {current_total:,}")
                
                if page_products == 0:
                    print(f"No more products found, stopping at page {page}")
                    break
                    
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"Page {page}: Error - {e}")
                time.sleep(10)
                continue

    def run(self):
        """Run HardwarePasal scraper"""
        start_time = time.time()
        self.scrape_hardwarepasal_pages()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ HARDWAREPASAL SCRAPING COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        print(f"   Rate: {final_count/(runtime/60):.0f} products/minute")

def main():
    """Run both scrapers"""
    print("🚀 FIXED WORKING SCRAPERS - TARGETING 100K PRODUCTS")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run both scrapers in parallel
    oliz_scraper = FixedOlizScraper()
    hardware_scraper = FixedHardwarePasalScraper()
    
    # Start threads
    oliz_thread = threading.Thread(target=oliz_scraper.run)
    hardware_thread = threading.Thread(target=hardware_scraper.run)
    
    oliz_thread.start()
    time.sleep(5)  # Small delay
    hardware_thread.start()
    
    # Wait for completion
    oliz_thread.join()
    hardware_thread.join()
    
    # Final summary
    oliz_count = oliz_scraper.get_product_count()
    hardware_count = hardware_scraper.get_product_count()
    total_products = oliz_count + hardware_count
    
    print(f"\n🎉 ALL SCRAPERS COMPLETE!")
    print(f"   Oliz Store: {oliz_count:,} products")
    print(f"   Hardware Pasal: {hardware_count:,} products")
    print(f"   TOTAL: {total_products:,} products")
    print(f"   Progress to 100k: {total_products/100000*100:.1f}%")
    
    if total_products >= 100000:
        print("🎯 TARGET ACHIEVED: 100K+ PRODUCTS!")
    else:
        remaining = 100000 - total_products
        print(f"   Remaining for 100k: {remaining:,} products")

if __name__ == "__main__":
    main()