#!/usr/bin/env python3
"""
Comprehensive Acceleration System - All strategies for 100k products
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import threading
from datetime import datetime

# Additional Nepali E-commerce Sites
ADDITIONAL_SITES = [
    {
        'name': 'SastoDeal',
        'base_url': 'https://www.sastodeal.com',
        'selectors': ['div[class*="product"]', '.product-item', '.item-box'],
        'price_selectors': ['.price', '.product-price', '.cost'],
        'active': True
    },
    {
        'name': 'Muncha',  
        'base_url': 'https://muncha.com',
        'selectors': ['div[class*="product"]', '.product-card', '.item'],
        'price_selectors': ['.price', '.amount', '.cost'],
        'active': True
    },
    {
        'name': 'Kaymu', 
        'base_url': 'https://kaymu.com.np',
        'selectors': ['div[class*="product"]', '.product-item', 'article'],
        'price_selectors': ['.price', '.product-price'],
        'active': True
    },
    {
        'name': 'CellPay',
        'base_url': 'https://cellpay.com.np',
        'selectors': ['div[class*="product"]', '.product', '.item'],
        'price_selectors': ['.price', '.cost', '.amount'],
        'active': True
    },
    {
        'name': 'Smartdoko',
        'base_url': 'https://smartdoko.com',
        'selectors': ['div[class*="product"]', '.product-card', '.item-card'],
        'price_selectors': ['.price', '.product-price', '.cost'],
        'active': True
    },
    {
        'name': 'NepalB2B',
        'base_url': 'https://nepalb2b.com',
        'selectors': ['div[class*="product"]', '.product-item', '.listing'],
        'price_selectors': ['.price', '.cost', '.amount'],
        'active': True
    }
]

class ComprehensiveScraperEngine:
    def __init__(self, scraper_id, site_config, category_list):
        self.scraper_id = scraper_id
        self.site_config = site_config
        self.category_list = category_list
        self.db_name = f'comprehensive_{scraper_id}.db'
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
                platform TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        conn.commit()
        conn.close()
        print(f"✅ {self.site_config['name']} scraper {self.scraper_id} ready")

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
            'Connection': 'keep-alive'
        })

    def add_product(self, product_data):
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, price_text, image_url, product_url, category, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data['title'],
                product_data['price'],
                product_data['price_text'],
                product_data['image_url'],
                product_data['product_url'],
                product_data['category'],
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

    def discover_categories(self, base_url):
        """Auto-discover category pages"""
        discovered_urls = []
        
        try:
            response = self.session.get(base_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for category links
                category_patterns = [
                    'a[href*="/category/"]',
                    'a[href*="/categories/"]',
                    'a[href*="/cat/"]',
                    'a[href*="/products/"]',
                    'a[href*="/shop/"]',
                    '.category-link',
                    '.menu-link',
                    'nav a'
                ]
                
                for pattern in category_patterns:
                    links = soup.select(pattern)
                    for link in links[:10]:  # Limit to prevent overload
                        href = link.get('href', '')
                        if href:
                            if href.startswith('/'):
                                full_url = base_url + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            if full_url not in discovered_urls:
                                discovered_urls.append(full_url)
        except:
            pass
            
        return discovered_urls

    def scrape_comprehensive(self):
        """Comprehensive scraping with multiple strategies"""
        site_name = self.site_config['name']
        base_url = self.site_config['base_url']
        
        print(f"🔍 {site_name} SCRAPER {self.scraper_id}: {len(self.category_list)} categories")
        
        # Strategy 1: Category-based searching
        for category in self.category_list:
            print(f"   📂 Category: {category}")
            
            # Multiple URL patterns for each category
            search_urls = [
                f"{base_url}/search?q={category.replace(' ', '+')}",
                f"{base_url}/products?search={category.replace(' ', '+')}",
                f"{base_url}/category/{category.replace(' ', '-')}",
                f"{base_url}/shop?query={category.replace(' ', '+')}",
                f"{base_url}/{category.replace(' ', '-')}",
                base_url  # Also scrape main page
            ]
            
            for search_url in search_urls[:3]:  # Limit to top 3 patterns
                category_products = 0
                
                for page in range(1, 11):  # Up to 10 pages per URL
                    try:
                        if page > 1:
                            if '?' in search_url:
                                url = f"{search_url}&page={page}"
                            else:
                                url = f"{search_url}?page={page}"
                        else:
                            url = search_url
                        
                        response = self.session.get(url, timeout=20)
                        if response.status_code != 200:
                            break
                            
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try different selectors
                        page_products = 0
                        for selector in self.site_config['selectors']:
                            elements = soup.select(selector)
                            
                            if len(elements) > 3:  # Promising selector
                                page_products = self.extract_products_from_elements(
                                    elements, category, site_name, base_url
                                )
                                if page_products > 0:
                                    category_products += page_products
                                    break  # Found working selector
                        
                        if page_products == 0:
                            break  # No products on this page
                            
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception:
                        time.sleep(5)
                        continue
                
                if category_products > 0:
                    current_total = self.get_product_count()
                    print(f"      → {category_products} products | Total: {current_total:,}")
                    break  # Found products with this URL pattern
            
            time.sleep(1)  # Brief delay between categories
        
        # Strategy 2: Auto-discovered category pages
        print(f"   🔍 Discovering category pages...")
        discovered_urls = self.discover_categories(base_url)
        
        for discovered_url in discovered_urls[:10]:  # Limit discoveries
            try:
                response = self.session.get(discovered_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for selector in self.site_config['selectors']:
                        elements = soup.select(selector)
                        if len(elements) > 3:
                            products_found = self.extract_products_from_elements(
                                elements, 'discovered', site_name, base_url
                            )
                            if products_found > 0:
                                break
                
                time.sleep(3)
            except:
                continue

    def extract_products_from_elements(self, elements, category, platform, base_url):
        """Extract products from HTML elements"""
        products_added = 0
        
        for elem in elements:
            try:
                # Get title
                title = ""
                for sel in ['h3', 'h4', 'h2', '.title', '.product-title', '.name', 'a']:
                    title_elem = elem.select_one(sel)
                    if title_elem:
                        title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                        if len(title) > 8:
                            break
                
                # Get price
                price_text = ""
                price = 0
                for sel in self.site_config['price_selectors'] + ['[class*="price"]', '[class*="cost"]']:
                    price_elem = elem.select_one(sel)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if price_text:
                            try:
                                # Extract numbers from price
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
                        'category': category,
                        'platform': platform
                    }
                    
                    if self.add_product(product):
                        products_added += 1
                        self.total_scraped += 1
                        
            except:
                continue
                
        return products_added

    def run(self):
        """Run this comprehensive scraper"""
        start_time = time.time()
        self.scrape_comprehensive()
        runtime = time.time() - start_time
        final_count = self.get_product_count()
        
        print(f"\n✅ {self.site_config['name']} SCRAPER {self.scraper_id} COMPLETE")
        print(f"   Products: {final_count:,}")
        print(f"   Runtime: {runtime/60:.1f} minutes")
        return final_count

def launch_comprehensive_system():
    """Launch comprehensive acceleration system"""
    print("🚀 COMPREHENSIVE ACCELERATION SYSTEM")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Comprehensive category lists for maximum coverage
    comprehensive_categories = [
        # Electronics & Technology  
        'electronics', 'mobile', 'phone', 'smartphone', 'iphone', 'samsung', 'xiaomi',
        'laptop', 'computer', 'tablet', 'headphones', 'earbuds', 'speaker', 'charger',
        'cable', 'power bank', 'smart watch', 'fitness tracker', 'camera', 'gaming',
        
        # Fashion & Apparel
        'clothing', 'fashion', 'shirt', 't-shirt', 'dress', 'pants', 'jeans', 'shoes',
        'sneakers', 'sandals', 'bags', 'backpack', 'handbag', 'watch', 'jewelry',
        'sunglasses', 'belt', 'wallet', 'cap', 'hat', 'scarf', 'gloves',
        
        # Home & Living
        'home', 'furniture', 'decor', 'kitchen', 'cookware', 'appliances', 'lighting',
        'bedding', 'curtains', 'carpet', 'storage', 'organization', 'cleaning',
        'bathroom', 'bedroom', 'living room', 'dining', 'garden', 'outdoor',
        
        # Health & Beauty  
        'beauty', 'skincare', 'makeup', 'cosmetics', 'perfume', 'shampoo', 'soap',
        'cream', 'lotion', 'health', 'fitness', 'supplements', 'medical', 'personal care',
        
        # Sports & Fitness
        'sports', 'fitness', 'gym', 'exercise', 'yoga', 'running', 'cycling', 'swimming',
        'outdoor sports', 'football', 'basketball', 'cricket', 'badminton', 'tennis',
        
        # Books & Education
        'books', 'textbooks', 'novels', 'education', 'stationery', 'pens', 'notebooks',
        'school supplies', 'office supplies', 'art supplies',
        
        # Baby & Kids
        'baby', 'kids', 'children', 'toys', 'games', 'baby care', 'diapers', 'feeding',
        'kids clothing', 'school bags', 'educational toys',
        
        # Automotive
        'automotive', 'car', 'bike', 'motorcycle', 'spare parts', 'accessories',
        'tools', 'maintenance', 'tires', 'batteries'
    ]
    
    # Create scrapers for all sites
    scrapers = []
    threads = []
    
    # Enhanced existing sites with more instances
    existing_enhanced = [
        {
            'name': 'Oliz_Enhanced',
            'base_url': 'https://olizstore.com',
            'selectors': ['div[class*="product"]', '.product-item', '.product-card'],
            'price_selectors': ['.price', '.product-price', '.cost'],
            'active': True
        },
        {
            'name': 'HardwarePasal_Enhanced',
            'base_url': 'https://hardwarepasal.com', 
            'selectors': ['div[class*="product"]', '.product-item', '.cnit-product'],
            'price_selectors': ['.cnit-product-price', '.price', '.product-price'],
            'active': True
        }
    ]
    
    # Combine all sites
    all_sites = existing_enhanced + ADDITIONAL_SITES
    
    # Create multiple instances per site with different category sets
    instance_counter = 0
    
    for site_config in all_sites:
        if not site_config['active']:
            continue
            
        # Split categories into chunks for parallel processing
        categories_per_instance = 15
        category_chunks = [
            comprehensive_categories[i:i+categories_per_instance] 
            for i in range(0, len(comprehensive_categories), categories_per_instance)
        ]
        
        # Create 2-3 instances per site
        for chunk_idx, category_chunk in enumerate(category_chunks[:3]):
            instance_counter += 1
            scraper_id = f"{site_config['name']}_{instance_counter}"
            
            scraper = ComprehensiveScraperEngine(scraper_id, site_config, category_chunk)
            scrapers.append(scraper)
            
            thread = threading.Thread(target=scraper.run)
            threads.append(thread)
    
    print(f"🚀 LAUNCHING {len(threads)} COMPREHENSIVE SCRAPERS")
    print(f"   Sites: {len(all_sites)}")
    print(f"   Categories: {len(comprehensive_categories)}")
    print(f"   Expected massive acceleration!")
    
    # Start all threads with small delays
    for i, thread in enumerate(threads):
        thread.start()
        time.sleep(2)  # 2 second delay between starts
        print(f"   Started scraper {i+1}/{len(threads)}")
    
    # Wait for all to complete
    print(f"\n📊 ALL SCRAPERS RUNNING - Monitor with monitor_scaled_progress.py")
    
    for thread in threads:
        thread.join()
    
    # Final summary
    total_products = sum(scraper.get_product_count() for scraper in scrapers)
    
    print(f"\n🎉 COMPREHENSIVE ACCELERATION COMPLETE!")
    print(f"   Total Products: {total_products:,}")
    print(f"   Active Scrapers: {len(scrapers)}")
    
    if total_products >= 100000:
        print("🎯 TARGET ACHIEVED: 100K+ PRODUCTS!")
    
if __name__ == "__main__":
    launch_comprehensive_system()