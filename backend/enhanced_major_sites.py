#!/usr/bin/env python3
"""
Enhanced Major Sites Scraper - Target large Nepali e-commerce sites
Focus on sites with known large product catalogs
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import threading
from datetime import datetime

# Major Nepali E-commerce Sites with Large Product Catalogs
MAJOR_SITES = [
    {
        'name': 'NepBay',
        'urls': [
            'https://nepbay.com',
            'https://nepbay.com/products',
            'https://nepbay.com/categories'
        ],
        'selectors': ['div[class*="product"]', '.product-item', '.product-card', 'article.product'],
        'active': True
    },
    {
        'name': 'Thulo',
        'urls': [
            'https://thulo.com',
            'https://thulo.com/products', 
            'https://thulo.com/categories'
        ],
        'selectors': ['div[class*="product"]', '.item', '.product-box'],
        'active': True
    },
    {
        'name': 'MeroShopping', 
        'urls': [
            'https://meroshopping.com',
            'https://meroshopping.com/products',
            'https://meroshopping.com/shop'
        ],
        'selectors': ['div[class*="product"]', '.product-item', '.shop-item'],
        'active': True
    },
    {
        'name': 'NepMart',
        'urls': [
            'https://nepmart.com',
            'https://nepmart.com/products'
        ],
        'selectors': ['div[class*="product"]', '.product-card', '.item-card'],
        'active': True
    },
    {
        'name': 'Gyapu', 
        'urls': [
            'https://gyapu.com',
            'https://gyapu.com/products'
        ],
        'selectors': ['div[class*="product"]', '.product-item', '.listing'],
        'active': True
    }
]

class MajorSiteScraper:
    def __init__(self, site_config, scraper_id):
        self.site_config = site_config
        self.scraper_id = scraper_id
        self.db_name = f'major_{site_config["name"]}_{scraper_id}.db'
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
                platform TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        conn.commit()
        conn.close()
        print(f"✅ Major {self.site_config['name']} scraper {self.scraper_id} ready")

    def setup_session(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def add_product(self, product_data):
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, price_text, image_url, product_url, platform)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_data['title'],
                product_data['price'],
                product_data['price_text'],
                product_data['image_url'],
                product_data['product_url'],
                product_data['platform']
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

    def extract_products(self, soup, base_url):
        """Extract products from page content"""
        products_added = 0
        
        for selector in self.site_config['selectors']:
            elements = soup.select(selector)
            
            if len(elements) > 3:  # Found products
                for elem in elements:
                    try:
                        # Get title
                        title = ""
                        for title_sel in ['h3', 'h4', 'h2', '.title', '.product-title', '.name', 'a']:
                            title_elem = elem.select_one(title_sel)
                            if title_elem:
                                title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                                if len(title) > 8:
                                    break
                        
                        # Get price
                        price_text = ""
                        price = 0
                        for price_sel in ['.price', '.product-price', '.cost', '.amount', '[class*="price"]']:
                            price_elem = elem.select_one(price_sel)
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                if price_text:
                                    try:
                                        # Extract price
                                        price_clean = price_text.replace('Rs.', '').replace('NPR', '').replace(',', '').strip()
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
                            product_url = base_url + product_url
                        elif not product_url.startswith('http'):
                            continue
                        
                        # Get image
                        image_url = ""
                        img_elem = elem.select_one('img')
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src', '')
                            if img_src:
                                if img_src.startswith('/'):
                                    image_url = base_url + img_src
                                elif img_src.startswith('http'):
                                    image_url = img_src
                        
                        if title and product_url and len(title) > 5:
                            product = {
                                'title': title[:200],
                                'price': price,
                                'price_text': price_text,
                                'image_url': image_url,
                                'product_url': product_url,
                                'platform': self.site_config['name']
                            }
                            
                            if self.add_product(product):
                                products_added += 1
                                self.total_scraped += 1
                                
                    except:
                        continue
                        
                if products_added > 0:
                    break  # Found working selector
                    
        return products_added

    def scrape_major_site(self):
        """Scrape major site comprehensively"""
        site_name = self.site_config['name']
        print(f"🔍 {site_name} MAJOR SCRAPER {self.scraper_id}")
        
        for base_url in self.site_config['urls']:
            print(f"   📱 {base_url}")
            
            # Test base URL first
            try:
                response = self.session.get(base_url, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    base_products = self.extract_products(soup, base_url)
                    
                    if base_products > 0:
                        print(f"      → {base_products} products from base page")
                        
                        # Try pagination on this URL
                        for page in range(2, 101):  # Try up to 100 pages
                            try:
                                if '?' in base_url:
                                    page_url = f"{base_url}&page={page}"
                                else:
                                    page_url = f"{base_url}?page={page}"
                                
                                response = self.session.get(page_url, timeout=20)
                                if response.status_code != 200:
                                    break
                                
                                soup = BeautifulSoup(response.content, 'html.parser')
                                page_products = self.extract_products(soup, base_url)
                                
                                if page_products > 0:
                                    current_total = self.get_product_count()
                                    print(f"      Page {page}: +{page_products} | Total: {current_total:,}")
                                else:
                                    break  # No products on this page
                                    
                                time.sleep(random.uniform(3, 6))
                                
                            except:
                                time.sleep(10)
                                continue
                    
                    # Also try category discovery
                    category_links = soup.select('a[href*="category"]')[:10]
                    category_links += soup.select('a[href*="shop"]')[:10]
                    
                    for link in category_links:
                        try:
                            href = link.get('href', '')
                            if href.startswith('/'):
                                cat_url = base_url + href
                            elif href.startswith('http'):
                                cat_url = href
                            else:
                                continue
                            
                            response = self.session.get(cat_url, timeout=15)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                cat_products = self.extract_products(soup, base_url)
                                if cat_products > 0:
                                    print(f"      Category: +{cat_products} products")
                            
                            time.sleep(random.uniform(2, 4))
                            
                        except:
                            continue
                
                time.sleep(5)
                
            except Exception as e:
                print(f"      ❌ Error with {base_url}: {str(e)[:50]}...")
                time.sleep(10)
                continue

    def run(self):
        """Run this major site scraper"""
        start_time = time.time()
        self.scrape_major_site()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ {self.site_config['name']} SCRAPER {self.scraper_id} COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        return final_count

def launch_major_sites():
    """Launch scrapers for major sites"""
    print("🚀 ENHANCED MAJOR SITES SCRAPER")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    scrapers = []
    threads = []
    
    # Create 2 instances per major site
    for site_config in MAJOR_SITES:
        if site_config['active']:
            for instance in range(1, 3):  # 2 instances per site
                scraper = MajorSiteScraper(site_config, instance)
                scrapers.append(scraper)
                thread = threading.Thread(target=scraper.run)
                threads.append(thread)
    
    print(f"🚀 LAUNCHING {len(threads)} MAJOR SITE SCRAPERS")
    
    # Start all threads
    for i, thread in enumerate(threads):
        thread.start()
        time.sleep(3)  # 3 second delay
        print(f"   Started scraper {i+1}/{len(threads)}")
    
    print(f"\n📊 ALL MAJOR SITE SCRAPERS RUNNING")
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Final summary
    total_products = sum(scraper.get_product_count() for scraper in scrapers)
    
    print(f"\n🎉 MAJOR SITES SCRAPING COMPLETE!")
    print(f"   Total Products: {total_products:,}")
    print(f"   Active Scrapers: {len(scrapers)}")

if __name__ == "__main__":
    launch_major_sites()