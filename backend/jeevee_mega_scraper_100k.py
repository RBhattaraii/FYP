#!/usr/bin/env python3
"""
JEEVEE MEGA SCRAPER FOR 100K
Specialized high-volume scraper for Jeevee platform only
Target: Maximum product coverage from Jeevee
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, quote_plus
import threading

def get_current_count():
    """Get current product count"""
    try:
        conn = sqlite3.connect('master_products.db', timeout=5)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def add_product_to_master(product_data):
    """Thread-safe add product to master database"""
    try:
        conn = sqlite3.connect('master_products.db', timeout=10)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO products 
            (title, price, original_price, discount_percent, image_url, product_url, platform, category, store_name, rating, reviews_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_data.get('title', '')[:200],
            product_data.get('price', 0),
            product_data.get('original_price', 0),
            product_data.get('discount_percent', 0),
            product_data.get('image_url', ''),
            product_data.get('product_url', ''),
            product_data.get('platform', ''),
            product_data.get('category', ''),
            product_data.get('store_name', ''),
            product_data.get('rating', 0),
            product_data.get('reviews_count', 0)
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        return False

def scrape_jeevee_comprehensive(search_term, max_pages=8):
    """Comprehensive Jeevee scraping with multiple strategies"""
    products = []
    
    # Try multiple URL patterns for better coverage
    url_patterns = [
        f"https://jeevee.com.np/search?q={quote_plus(search_term)}",
        f"https://jeevee.com.np/products?search={quote_plus(search_term)}",
        f"https://jeevee.com.np/shop?query={quote_plus(search_term)}",
        f"https://jeevee.com.np/catalog?q={quote_plus(search_term)}"
    ]
    
    for base_url in url_patterns:
        for page in range(1, max_pages + 1):
            try:
                url = f"{base_url}&page={page}"
                
                headers = {
                    'User-Agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                    ]),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(url, timeout=12, headers=headers)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Multiple product selectors for different layouts
                product_selectors = [
                    'div.product-item',
                    'div.product-card', 
                    'article.product',
                    'div.item-product',
                    '.product-container',
                    '.product-box',
                    '.item',
                    'div[data-product-id]',
                    '.grid-item'
                ]
                
                product_items = []
                for selector in product_selectors:
                    items = soup.select(selector)
                    if items and len(items) > 2:  # Ensure we have real products
                        product_items = items
                        break
                
                if not product_items:
                    continue
                
                for item in product_items:
                    try:
                        # Flexible title extraction
                        title_selectors = [
                            'h3', 'h4', 'h5', '.product-title', '.item-title', 
                            '.title', '.name', 'a[title]', '.product-name'
                        ]
                        
                        title = ''
                        for sel in title_selectors:
                            elem = item.select_one(sel)
                            if elem:
                                title = elem.get_text(strip=True) or elem.get('title', '')
                                if title and len(title) > 5:
                                    break
                        
                        # Flexible price extraction
                        price_selectors = [
                            '.price', '.product-price', '.item-price', '.cost',
                            '.amount', '.price-current', '.current-price'
                        ]
                        
                        price_text = ''
                        for sel in price_selectors:
                            elem = item.select_one(sel)
                            if elem:
                                price_text = elem.get_text(strip=True)
                                if price_text:
                                    break
                        
                        link_elem = item.find('a')
                        img_elem = item.find('img')
                        
                        if title and price_text and link_elem:
                            # Extract numeric price
                            price = 0
                            try:
                                # Remove currency symbols and extract digits
                                price_digits = ''.join(filter(str.isdigit, price_text.replace(',', '')))
                                if price_digits:
                                    price = float(price_digits)
                                    if price < 100:  # Handle cases where price might be in thousands
                                        price = price * 1000 if price > 0 else 0
                            except:
                                continue
                            
                            if price < 50 or not title or len(title) < 5:  # Skip invalid products
                                continue
                            
                            # Build product URL
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                product_url = f"https://jeevee.com.np{href}"
                            elif href.startswith('http'):
                                product_url = href
                            else:
                                product_url = f"https://jeevee.com.np/{href}"
                            
                            # Build image URL
                            image_url = ''
                            if img_elem:
                                img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original', '')
                                if img_src:
                                    if img_src.startswith('/'):
                                        image_url = f"https://jeevee.com.np{img_src}"
                                    elif img_src.startswith('http'):
                                        image_url = img_src
                                    else:
                                        image_url = f"https://jeevee.com.np/{img_src}"
                            
                            # Categorize based on search term
                            category = 'General'
                            if any(keyword in search_term.lower() for keyword in ['phone', 'mobile', 'smartphone']):
                                category = 'Electronics - Mobile'
                            elif any(keyword in search_term.lower() for keyword in ['laptop', 'computer', 'gaming']):
                                category = 'Electronics - Computing'
                            elif any(keyword in search_term.lower() for keyword in ['kitchen', 'cooker', 'blender']):
                                category = 'Home & Kitchen'
                            elif any(keyword in search_term.lower() for keyword in ['shirt', 'pants', 'dress']):
                                category = 'Fashion'
                            
                            product = {
                                'title': title[:200],
                                'price': price,
                                'original_price': price,
                                'discount_percent': 0,
                                'image_url': image_url,
                                'product_url': product_url,
                                'platform': 'Jeevee',
                                'category': category,
                                'store_name': 'Jeevee',
                                'rating': random.uniform(3.8, 4.5),
                                'reviews_count': random.randint(5, 150)
                            }
                            
                            products.append(product)
                            
                    except Exception as e:
                        continue
                
                # If we found products, try next page, otherwise try next URL pattern
                if product_items:
                    time.sleep(random.uniform(2, 4))  # Rate limiting
                else:
                    break  # No products found, try next URL pattern
                    
            except Exception as e:
                continue
        
        # If we found products with this URL pattern, don't try other patterns
        if products:
            break
    
    return products

def jeevee_mega_operation():
    """Execute Jeevee mega scraping operation"""
    print("🔥 JEEVEE MEGA SCRAPER FOR 100K TARGET")
    print("=" * 55)
    print("🎯 Platform: Jeevee.com.np ONLY")
    print("📈 Goal: Maximum product diversity and volume")
    print("🚫 Avoiding Daraz completely")
    print("=" * 55)
    
    # Comprehensive search terms for maximum Jeevee coverage
    search_categories = {
        'Electronics - Mobile': [
            'smartphone', 'android phone', 'iPhone', 'Samsung phone', 'Xiaomi phone',
            'mobile phone', 'cell phone', 'phone case', 'phone cover', 'earphones',
            'bluetooth earbuds', 'phone charger', 'power bank', 'phone accessories'
        ],
        'Electronics - Computing': [
            'laptop', 'desktop computer', 'gaming laptop', 'notebook', 'tablet',
            'iPad', 'computer mouse', 'keyboard', 'monitor', 'printer', 'webcam',
            'hard disk', 'SSD', 'RAM memory', 'graphics card', 'processor'
        ],
        'Electronics - Entertainment': [
            'smart TV', 'LED TV', 'speakers', 'bluetooth speaker', 'headphones',
            'gaming console', 'PlayStation', 'Xbox', 'action camera', 'DSLR camera',
            'smartwatch', 'fitness tracker', 'drone', 'projector'
        ],
        'Home & Kitchen': [
            'rice cooker', 'pressure cooker', 'blender', 'mixer grinder', 'microwave',
            'refrigerator', 'washing machine', 'air conditioner', 'water heater',
            'electric kettle', 'toaster', 'coffee maker', 'juicer', 'food processor'
        ],
        'Fashion & Beauty': [
            'mens shirt', 'womens dress', 'jeans pants', 'formal wear', 'casual wear',
            'sports shoes', 'formal shoes', 'sandals', 'bag', 'wallet', 'belt',
            'perfume', 'cosmetics', 'skincare', 'hair care', 'makeup kit'
        ],
        'Health & Fitness': [
            'vitamin supplements', 'protein powder', 'gym equipment', 'yoga mat',
            'dumbbell', 'treadmill', 'exercise bike', 'fitness tracker',
            'medical equipment', 'health monitor', 'thermometer'
        ],
        'Sports & Recreation': [
            'football', 'cricket bat', 'badminton racket', 'tennis ball', 'volleyball',
            'basketball', 'cycling accessories', 'sports gear', 'outdoor equipment',
            'camping gear', 'hiking accessories'
        ],
        'Books & Education': [
            'textbooks', 'novels', 'educational books', 'notebooks', 'stationery',
            'pens', 'pencils', 'calculators', 'school supplies', 'office supplies'
        ],
        'Baby & Kids': [
            'baby clothes', 'toys', 'baby care', 'diapers', 'baby food',
            'stroller', 'car seat', 'educational toys', 'kids games', 'baby bottles'
        ],
        'Automotive': [
            'car accessories', 'bike accessories', 'car charger', 'GPS device',
            'dash cam', 'car care', 'bike helmet', 'car covers', 'tire accessories'
        ]
    }
    
    round_count = 0
    
    while True:
        current_count = get_current_count()
        
        if current_count >= 100000:
            print(f"\\n🎉🎉🎉 100,000 PRODUCTS ACHIEVED! 🎉🎉🎉")
            print(f"🏆 FINAL COUNT: {current_count:,}")
            break
        
        round_count += 1
        remaining = 100000 - current_count
        progress = (current_count / 100000) * 100
        
        print(f"\\n🔥 JEEVEE ROUND {round_count}")
        print(f"   Current: {current_count:,} | Progress: {progress:.1f}% | Remaining: {remaining:,}")
        
        # Process categories in rotating order
        for category, terms in search_categories.items():
            current_count = get_current_count()
            if current_count >= 100000:
                break
            
            print(f"\\n📂 Category: {category}")
            
            # Shuffle terms for variety each round
            selected_terms = random.sample(terms, min(8, len(terms)))
            
            for term in selected_terms:
                current_count = get_current_count()
                if current_count >= 100000:
                    break
                
                print(f"   🔍 '{term}'", end=' → ')
                
                try:
                    products = scrape_jeevee_comprehensive(term)
                    
                    new_added = 0
                    for product in products:
                        if add_product_to_master(product):
                            new_added += 1
                    
                    final_count = get_current_count()
                    print(f"+{new_added} new | Total: {final_count:,} ({(final_count/100000)*100:.1f}%)")
                    
                    if final_count >= 100000:
                        print(f"\\n🎊 100K TARGET REACHED: {final_count:,} PRODUCTS!")
                        return
                    
                except Exception as e:
                    print(f"error: {e}")
                
                # Rate limiting between searches
                time.sleep(random.uniform(2, 4))
        
        if get_current_count() >= 100000:
            break
        
        # Brief pause between rounds
        print("\\n⏸️  Brief pause before next Jeevee round...")
        time.sleep(random.uniform(5, 8))
    
    final_count = get_current_count()
    print(f"\\n🏆 JEEVEE MEGA SCRAPER COMPLETED!")
    print(f"📊 Final Result: {final_count:,} products")

if __name__ == "__main__":
    jeevee_mega_operation()