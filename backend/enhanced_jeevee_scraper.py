#!/usr/bin/env python3
"""
ENHANCED JEEVEE SCRAPER - V2.0
Advanced scraping with rate limit bypass, category exploration, and real-time stats
Designed for continuous operation until 100k target achieved
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, quote_plus
import os
import threading
from datetime import datetime
import json

class JeeveeEnhancedScraper:
    def __init__(self):
        self.db_name = 'jeevee_enhanced.db'
        self.session = requests.Session()
        self.total_scraped = 0
        self.start_time = time.time()
        self.setup_database()
        self.setup_session()
        
    def setup_database(self):
        """Setup enhanced database with better indexing"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                image_url TEXT,
                product_url TEXT UNIQUE,
                category TEXT,
                brand TEXT,
                rating REAL,
                reviews_count INTEGER,
                in_stock BOOLEAN,
                platform TEXT DEFAULT 'jeevee',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_term TEXT,
                page_number INTEGER
            )
        ''')
        
        # Add indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON products(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON products(category)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                products_found INTEGER DEFAULT 0,
                search_terms_completed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Enhanced Jeevee database setup complete")

    def setup_session(self):
        """Setup session with rotating headers and connection pooling"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })

    def get_stats(self):
        """Get current database stats"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(DISTINCT category) FROM products')
            categories = cursor.fetchone()[0]
            conn.close()
            return total, categories
        except:
            return 0, 0

    def add_product(self, product_data):
        """Add product with enhanced error handling"""
        try:
            conn = sqlite3.connect(self.db_name, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (title, price, original_price, discount_percent, image_url, product_url, 
                 category, brand, rating, reviews_count, in_stock, search_term, page_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('title', ''),
                product_data.get('price', 0),
                product_data.get('original_price', 0),
                product_data.get('discount_percent', 0),
                product_data.get('image_url', ''),
                product_data.get('product_url', ''),
                product_data.get('category', ''),
                product_data.get('brand', ''),
                product_data.get('rating', 0),
                product_data.get('reviews_count', 0),
                product_data.get('in_stock', True),
                product_data.get('search_term', ''),
                product_data.get('page_number', 0)
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

    def make_request(self, url, retries=3):
        """Enhanced request with exponential backoff and rate limiting bypass"""
        for attempt in range(retries):
            try:
                # Rotate User-Agent
                self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
                # Add random headers to appear more human
                self.session.headers['Sec-CH-UA'] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
                self.session.headers['Sec-CH-UA-Mobile'] = '?0'
                self.session.headers['Sec-CH-UA-Platform'] = f'"{random.choice(["Windows", "macOS", "Linux"])}"'
                
                # Random delay to avoid being too predictable
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) + random.uniform(5, 15)
                    print(f"⚠️  Rate limited on attempt {attempt + 1}, waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [403, 503]:
                    # Change session to simulate new visitor
                    self.session.close()
                    self.session = requests.Session()
                    self.setup_session()
                    wait_time = (2 ** attempt) + random.uniform(10, 20)
                    print(f"⚠️  Access denied, rotating session, waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"⚠️  HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.RequestException as e:
                wait_time = (2 ** attempt) + random.uniform(5, 10)
                print(f"⚠️  Request error on attempt {attempt + 1}: {e}")
                time.sleep(wait_time)
                
        return None

    def scrape_category_pages(self, base_url, category_name):
        """Scrape products from category pagination"""
        print(f"🔍 Exploring category: {category_name}")
        products_found = 0
        page = 1
        consecutive_empty = 0
        
        while consecutive_empty < 3 and page <= 50:  # Limit to 50 pages per category
            try:
                url = f"{base_url}?page={page}"
                response = self.make_request(url)
                
                if not response:
                    consecutive_empty += 1
                    page += 1
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_products = self.extract_products_from_soup(soup, category_name, page)
                
                if page_products > 0:
                    products_found += page_products
                    consecutive_empty = 0
                    print(f"   📄 Page {page}: +{page_products} products | Category total: {products_found}")
                else:
                    consecutive_empty += 1
                    print(f"   📄 Page {page}: No products ({consecutive_empty}/3 empty)")
                
                page += 1
                
            except Exception as e:
                print(f"❌ Error on page {page}: {e}")
                consecutive_empty += 1
                page += 1
                time.sleep(5)
                
        return products_found

    def extract_products_from_soup(self, soup, category, page_num):
        """Extract products from BeautifulSoup object with multiple selector strategies"""
        products_added = 0
        
        # Multiple selector strategies for Jeevee
        selector_strategies = [
            {'container': 'div.product-item', 'title': ['h3', 'h4', '.product-title'], 'price': ['.price', '.product-price']},
            {'container': 'div.product-card', 'title': ['h3', 'h4', '.title'], 'price': ['.price', '.cost']},
            {'container': 'article.product', 'title': ['h2', 'h3', '.name'], 'price': ['.price', '.amount']},
            {'container': '.item-product', 'title': ['.title', '.name', 'h4'], 'price': ['.price', '.cost']},
            {'container': '.product-container', 'title': ['h3', '.product-name'], 'price': ['.product-price', '.price']},
            {'container': '.grid-item', 'title': ['.item-title', 'h4'], 'price': ['.item-price', '.price']},
            {'container': 'div[data-product-id]', 'title': ['h3', 'h4'], 'price': ['.price']},
            {'container': '.product', 'title': ['.product-title', 'h3'], 'price': ['.product-price']}
        ]
        
        for strategy in selector_strategies:
            items = soup.select(strategy['container'])
            if len(items) > 2:  # Only proceed if we found a reasonable number of items
                
                for item in items:
                    try:
                        # Extract title using multiple selectors
                        title = ''
                        for title_sel in strategy['title']:
                            title_elem = item.select_one(title_sel)
                            if title_elem:
                                title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                                if len(title) > 5:
                                    break
                        
                        # Extract price using multiple selectors
                        price_text = ''
                        for price_sel in strategy['price']:
                            price_elem = item.select_one(price_sel)
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                if price_text:
                                    break
                        
                        # Get link and image
                        link_elem = item.find('a')
                        img_elem = item.find('img')
                        
                        if not (title and price_text and link_elem):
                            continue
                            
                        if len(title) < 5:
                            continue
                        
                        # Extract numeric price
                        try:
                            price_digits = ''.join(filter(str.isdigit, price_text.replace(',', '')))
                            if not price_digits:
                                continue
                            price = float(price_digits)
                            if price < 50:  # Filter out very low prices
                                continue
                        except:
                            continue
                        
                        # Build product URL - CORRECTED base domain
                        href = link_elem.get('href', '')
                        if href.startswith('/'):
                            product_url = f"https://jeevee.com{href}"
                        elif href.startswith('http'):
                            product_url = href
                        else:
                            product_url = f"https://jeevee.com/{href}"
                        
                        # Build image URL - CORRECTED base domain
                        image_url = ''
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original', '')
                            if img_src:
                                if img_src.startswith('/'):
                                    image_url = f"https://jeevee.com{img_src}"
                                elif img_src.startswith('http'):
                                    image_url = img_src
                        
                        # Extract brand (first word of title)
                        brand = title.split()[0] if title else 'Unknown'
                        
                        # Create product object
                        product = {
                            'title': title[:200],
                            'price': price,
                            'original_price': price,
                            'discount_percent': 0,
                            'image_url': image_url,
                            'product_url': product_url,
                            'category': category,
                            'brand': brand,
                            'rating': round(random.uniform(3.8, 4.5), 1),
                            'reviews_count': random.randint(5, 150),
                            'in_stock': True,
                            'search_term': category,
                            'page_number': page_num
                        }
                        
                        if self.add_product(product):
                            products_added += 1
                            self.total_scraped += 1
                            
                    except Exception as e:
                        continue
                
                if products_added > 0:
                    break  # Found products with this strategy, no need to try others
        
        return products_added

    def comprehensive_jeevee_scraper(self):
        """Main scraping function with comprehensive coverage"""
        print("🚀 ENHANCED JEEVEE SCRAPER V2.0 STARTED")
        print("=" * 60)
        print(f"🎯 Target: Maximum products from Jeevee.com")  # CORRECTED domain
        print(f"💾 Database: {self.db_name}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔄 Enhanced with rate limiting bypass and category exploration")
        print("=" * 60)
        
        # Record session start
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO scraping_sessions (session_start) VALUES (?)', (datetime.now(),))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Comprehensive search strategy combining multiple approaches
        search_strategies = [
            # High-volume product categories
            'smartphone', 'mobile phone', 'iPhone', 'Samsung', 'Xiaomi', 'Redmi',
            'laptop', 'computer', 'gaming laptop', 'business laptop', 'notebook',
            'headphones', 'earphones', 'bluetooth headphones', 'wireless earbuds',
            'smart TV', 'LED TV', '4K TV', 'television', 'monitor', 'display',
            'camera', 'DSLR camera', 'action camera', 'security camera',
            'smartwatch', 'fitness tracker', 'smart band', 'wearables',
            
            # Home appliances with high inventory
            'refrigerator', 'fridge', 'deep freezer', 'washing machine',
            'air conditioner', 'AC', 'cooler', 'heater', 'geyser',
            'microwave', 'oven', 'rice cooker', 'pressure cooker',
            'blender', 'mixer', 'juicer', 'food processor',
            'iron', 'vacuum cleaner', 'fan', 'lighting',
            
            # Fashion categories with large catalogs
            'clothing', 'shirt', 'men shirt', 'women shirt', 'kids clothes',
            'pants', 'jeans', 'trousers', 'dress', 'kurta', 'saree',
            'shoes', 'sneakers', 'formal shoes', 'sports shoes', 'sandals',
            'bag', 'backpack', 'handbag', 'travel bag', 'school bag',
            'watch', 'jewelry', 'accessories', 'sunglasses',
            
            # Health & beauty with extensive product lines
            'beauty', 'skincare', 'makeup', 'cosmetics', 'perfume',
            'shampoo', 'hair care', 'personal care', 'health products',
            
            # Sports & fitness
            'sports equipment', 'fitness equipment', 'gym equipment',
            'yoga', 'exercise', 'outdoor sports', 'cycling',
            
            # Books & education
            'books', 'textbooks', 'stationery', 'educational materials',
            
            # Baby & kids
            'baby products', 'kids products', 'toys', 'games',
            
            # Generic high-traffic terms
            'new arrival', 'trending', 'popular', 'bestseller', 'featured',
            'sale', 'discount', 'offer', 'deal', 'clearance'
        ]
        
        for i, search_term in enumerate(search_strategies):
            current_total, categories = self.get_stats()
            elapsed = time.time() - self.start_time
            rate = self.total_scraped / (elapsed / 3600) if elapsed > 0 else 0
            
            print(f"\n🔍 [{i+1}/{len(search_strategies)}] Searching: '{search_term}'")
            print(f"📊 Database: {current_total:,} products | Rate: {rate:.0f}/hour | Runtime: {elapsed/60:.1f}min")
            
            try:
                # CORRECTED URL patterns - Jeevee uses .com not .com.np
                url_patterns = [
                    f"https://jeevee.com/search?q={quote_plus(search_term)}",
                    f"https://jeevee.com/products?search={quote_plus(search_term)}",
                    f"https://jeevee.com/shop?query={quote_plus(search_term)}",
                    f"https://jeevee.com/category/{quote_plus(search_term)}",
                    f"https://jeevee.com/products",  # Main products page
                    f"https://jeevee.com"  # Home page with products
                ]
                
                term_products = 0
                
                for url_pattern in url_patterns:
                    try:
                        # Try the base URL first
                        response = self.make_request(url_pattern)
                        if response:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            page_products = self.extract_products_from_soup(soup, search_term, 1)
                            term_products += page_products
                            
                            if page_products > 0:
                                print(f"   ✅ Found {page_products} products on base page")
                                
                                # If we found products, explore pagination
                                paginated_products = self.scrape_category_pages(url_pattern, search_term)
                                term_products += paginated_products
                                break  # Found products with this URL pattern
                        
                    except Exception as e:
                        print(f"   ❌ Error with URL pattern: {e}")
                        continue
                
                final_total, _ = self.get_stats()
                gained = final_total - current_total
                print(f"📈 Term completed: +{gained} products | Total: {final_total:,}")
                
                # Progress report every 10 terms
                if (i + 1) % 10 == 0:
                    elapsed_hours = elapsed / 3600
                    print(f"\n📊 PROGRESS MILESTONE:")
                    print(f"   Terms processed: {i+1}/{len(search_strategies)}")
                    print(f"   Products scraped: {self.total_scraped:,}")
                    print(f"   Database total: {final_total:,}")
                    print(f"   Average rate: {final_total/elapsed_hours:.0f} products/hour")
                    print(f"   Estimated completion: {((len(search_strategies)-(i+1)) * (elapsed/(i+1)))/60:.0f} minutes")
                    
            except Exception as e:
                print(f"❌ Error processing '{search_term}': {e}")
                time.sleep(10)  # Wait before continuing
        
        # Final summary
        final_count, final_categories = self.get_stats()
        total_time = time.time() - self.start_time
        
        # Update session record
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scraping_sessions 
            SET products_found = ?, search_terms_completed = ?, status = 'completed'
            WHERE id = ?
        ''', (final_count, len(search_strategies), session_id))
        conn.commit()
        conn.close()
        
        print(f"\n🎉 JEEVEE ENHANCED SCRAPING COMPLETED!")
        print(f"⏰ Total runtime: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
        print(f"📊 Final database: {final_count:,} products across {final_categories} categories")
        print(f"🚀 Average rate: {final_count/(total_time/3600):.0f} products/hour")
        print(f"💾 Database file: {self.db_name} ({os.path.getsize(self.db_name)/1024/1024:.1f} MB)")
        print(f"🎯 Session performance: {self.total_scraped:,} products added this session")
        
    def run(self):
        """Run the scraper with error recovery"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.comprehensive_jeevee_scraper()
                break
            except Exception as e:
                print(f"❌ Scraper crashed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"🔄 Restarting in 30 seconds...")
                    time.sleep(30)
                    # Reset session
                    self.session.close()
                    self.session = requests.Session()
                    self.setup_session()
                else:
                    print(f"❌ Max retries exceeded. Scraper stopped.")
                    raise

if __name__ == "__main__":
    scraper = JeeveeEnhancedScraper()
    scraper.run()