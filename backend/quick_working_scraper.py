#!/usr/bin/env python3
"""
Quick Working Scraper - Focus on sites that actually work
Start with Oliz and HardwarePasal since they have the most products
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime

class QuickWorkingScraper:
    def __init__(self):
        self.db_name = 'quick_working_products.db'
        self.session = requests.Session()
        self.total_scraped = 0
        self.setup_database()
        self.setup_session()
        
    def setup_database(self):
        """Setup database"""
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
                platform TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON products(platform)')
        
        conn.commit()
        conn.close()
        print("✅ Quick Working database setup complete")

    def setup_session(self):
        """Setup session"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })

    def get_stats(self):
        """Get stats by platform"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform')
            results = cursor.fetchall()
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            conn.close()
            return dict(results), total
        except:
            return {}, 0

    def add_product(self, product_data):
        """Add product"""
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, price_text, image_url, product_url, platform)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('title', ''),
                product_data.get('price', 0),
                product_data.get('price_text', ''),
                product_data.get('image_url', ''),
                product_data.get('product_url', ''),
                product_data.get('platform', '')
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except:
            return False

    def scrape_oliz(self):
        """Scrape Oliz - we know this works"""
        print("\n🔍 SCRAPING OLIZ STORE")
        print("=" * 40)
        
        urls_to_scrape = [
            "https://olizstore.com/products",  # 389 products
            "https://olizstore.com",           # 84 products
        ]
        
        for base_url in urls_to_scrape:
            print(f"📱 {base_url}")
            
            for page in range(1, 11):  # Try up to 10 pages
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
                            
                            # Get price - try multiple approaches
                            price_text = ""
                            price = 0
                            for sel in ['.price', '.product-price', '.cost', '.amount', '[class*="price"]']:
                                price_elem = elem.select_one(sel)
                                if price_elem:
                                    price_text = price_elem.get_text(strip=True)
                                    if price_text:
                                        try:
                                            # Extract numbers from price
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
                                    'platform': 'oliz'
                                }
                                
                                if self.add_product(product):
                                    page_products += 1
                                    self.total_scraped += 1
                                    
                        except Exception:
                            continue
                    
                    print(f"   Page {page}: +{page_products} products")
                    
                    if page_products == 0:
                        break  # No more products
                        
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"   Page {page}: Error - {e}")
                    break

    def scrape_hardwarepasal(self):
        """Scrape HardwarePasal - lots of products available"""
        print("\n🔍 SCRAPING HARDWARE PASAL")
        print("=" * 40)
        
        for page in range(1, 21):  # Try up to 20 pages
            try:
                url = f"https://hardwarepasal.com?page={page}" if page > 1 else "https://hardwarepasal.com"
                
                response = self.session.get(url, timeout=20)
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
                                'product_url': product_url,
                                'platform': 'hardwarepasal'
                            }
                            
                            if self.add_product(product):
                                page_products += 1
                                self.total_scraped += 1
                                
                    except Exception:
                        continue
                
                print(f"Page {page}: +{page_products} products")
                
                if page_products == 0:
                    break  # No more products
                    
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"Page {page}: Error - {e}")
                break

    def run(self):
        """Run the working scrapers"""
        print("🚀 QUICK WORKING SCRAPER STARTED")
        print("Focusing on sites that actually work...")
        print("=" * 50)
        
        start_time = time.time()
        
        # Scrape working sites
        self.scrape_oliz()
        
        stats, total = self.get_stats()
        print(f"\n📊 OLIZ COMPLETE: {stats.get('oliz', 0)} products")
        
        self.scrape_hardwarepasal()
        
        # Final stats
        final_stats, final_total = self.get_stats()
        runtime = time.time() - start_time
        
        print(f"\n🎉 SCRAPING COMPLETE!")
        print(f"⏰ Runtime: {runtime/60:.1f} minutes")
        print(f"📊 Total products: {final_total:,}")
        
        for platform, count in final_stats.items():
            print(f"   {platform.title()}: {count:,} products")
            
        print(f"💾 Database: {self.db_name} ({os.path.getsize(self.db_name)/1024/1024:.1f} MB)")

if __name__ == "__main__":
    scraper = QuickWorkingScraper()
    scraper.run()