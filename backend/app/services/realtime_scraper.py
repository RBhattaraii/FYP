"""
Real-time Product Scraper Service
Scrapes individual products on-demand when users view them
"""
import asyncio
import aiohttp
import re
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import asyncpg

class RealtimeProductScraper:
    """
    Scrapes individual product pages in real-time when users view products
    Detects price changes and updates price history
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Store-specific scraping configurations
        self.store_configs = {
            'daraz': {
                'price_selectors': [
                    '.pdp-price_color_orange',
                    '.pdp-price',
                    '[data-testid="price-current"]',
                    '.current-price'
                ],
                'title_selectors': [
                    '[data-testid="product-title"]',
                    '.pdp-product-title',
                    'h1'
                ],
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            },
            'oliz': {
                'price_selectors': [
                    '.price-current',
                    '.product-price',
                    '.price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ],
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            'hukut': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'cgdigital': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'better': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'neostore': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'hardwarepasal': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'jeevee': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'ufonepal': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            },
            'sastodeal': {
                'price_selectors': [
                    '.price-current',
                    '.product-price'
                ],
                'title_selectors': [
                    '.product-title',
                    'h1'
                ]
            }
        }

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10)
            )
        return self.session

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def detect_store_name(self, url: str) -> str:
        """Detect store name from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'daraz' in domain:
            return 'daraz'
        elif 'oliz' in domain:
            return 'oliz'
        elif 'hukut' in domain:
            return 'hukut'
        elif 'cgdigital' in domain:
            return 'cgdigital'
        elif 'better' in domain:
            return 'better'
        elif 'neostore' in domain:
            return 'neostore'
        elif 'hardwarepasal' in domain:
            return 'hardwarepasal'
        elif 'jeevee' in domain:
            return 'jeevee'
        elif 'ufonepal' in domain:
            return 'ufonepal'
        elif 'sastodeal' in domain:
            return 'sastodeal'
        else:
            return 'unknown'

    def extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from text using regex"""
        if not text:
            return None
            
        # Clean the text
        text = text.strip().replace(',', '').replace('Rs.', '').replace('Rs', '').replace('NPR', '')
        
        # Look for price patterns
        price_patterns = [
            r'(\d+(?:\.\d{1,2})?)',  # Basic number
            r'(\d+)',  # Integer only
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    price = float(match.group(1))
                    # Reasonable price range check (1 NPR to 10,000,000 NPR)
                    if 1 <= price <= 10000000:
                        return price
                except ValueError:
                    continue
                    
        return None

    async def scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product page and extract current price and title
        Returns dict with price, title, scraped_at, or None if failed
        """
        try:
            store_name = self.detect_store_name(url)
            config = self.store_configs.get(store_name, self.store_configs['daraz'])
            
            session = await self.get_session()
            
            headers = config.get('headers', {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract price
                current_price = None
                for selector in config['price_selectors']:
                    price_elements = soup.select(selector)
                    for element in price_elements:
                        price_text = element.get_text(strip=True)
                        current_price = self.extract_price_from_text(price_text)
                        if current_price:
                            break
                    if current_price:
                        break
                
                # Extract title
                title = None
                for selector in config['title_selectors']:
                    title_element = soup.select_one(selector)
                    if title_element:
                        title = title_element.get_text(strip=True)
                        if title:
                            break
                
                if not current_price:
                    print(f"Could not extract price from {url}")
                    return None
                
                return {
                    'price': current_price,
                    'title': title or 'Unknown Product',
                    'store_name': store_name,
                    'scraped_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    async def update_product_price_history(self, 
                                         db: asyncpg.Connection,
                                         product_id: int, 
                                         product_url: str, 
                                         current_db_price: float) -> Dict[str, Any]:
        """
        Scrape product page and update price history if price changed
        Returns status and scraped data
        """
        try:
            # Scrape the product page
            scraped_data = await self.scrape_product_page(product_url)
            
            if not scraped_data:
                return {
                    'status': 'failed',
                    'message': 'Failed to scrape product page',
                    'price_changed': False
                }
            
            scraped_price = scraped_data['price']
            
            # Check if price changed (allow small floating point differences)
            price_changed = abs(scraped_price - current_db_price) > 0.01
            
            if price_changed:
                # Update product price in main table
                await db.execute("""
                    UPDATE products 
                    SET price = $1, scraped_at = NOW()
                    WHERE id = $2
                """, scraped_price, product_id)
                
                # Record price history
                await db.execute("""
                    INSERT INTO price_history (product_id, product_title, store_name, price)
                    VALUES ($1, $2, $3, $4)
                """, product_id, scraped_data['title'], scraped_data['store_name'], scraped_price)
                
                print(f"Price updated for product {product_id}: {current_db_price} -> {scraped_price}")
                
                return {
                    'status': 'success',
                    'message': f'Price updated: Rs {current_db_price} → Rs {scraped_price}',
                    'price_changed': True,
                    'old_price': current_db_price,
                    'new_price': scraped_price,
                    'scraped_data': scraped_data
                }
            else:
                # Price is same, just record a data point for tracking
                await db.execute("""
                    INSERT INTO price_history (product_id, product_title, store_name, price)
                    VALUES ($1, $2, $3, $4)
                """, product_id, scraped_data['title'], scraped_data['store_name'], scraped_price)
                
                return {
                    'status': 'success',
                    'message': f'Price unchanged: Rs {current_db_price}',
                    'price_changed': False,
                    'current_price': current_db_price,
                    'scraped_data': scraped_data
                }
                
        except Exception as e:
            print(f"Error updating price history for product {product_id}: {e}")
            return {
                'status': 'error',
                'message': f'Error updating price: {str(e)}',
                'price_changed': False
            }


# Global instance
realtime_scraper = RealtimeProductScraper()

async def scrape_product_on_view(db: asyncpg.Connection, product_id: int) -> Dict[str, Any]:
    """
    Convenience function to scrape product when user views it
    Called from the product detail API endpoint
    """
    try:
        # Get product info from database
        product = await db.fetchrow("""
            SELECT id, title, price, product_url, store_name
            FROM products 
            WHERE id = $1
        """, product_id)
        
        if not product:
            return {
                'status': 'not_found',
                'message': 'Product not found in database'
            }
        
        if not product['product_url']:
            return {
                'status': 'no_url',
                'message': 'Product has no URL to scrape'
            }
        
        # Update price history
        result = await realtime_scraper.update_product_price_history(
            db, 
            product['id'], 
            product['product_url'], 
            float(product['price'])
        )
        
        return result
        
    except Exception as e:
        print(f"Error in scrape_product_on_view: {e}")
        return {
            'status': 'error',
            'message': f'Scraping error: {str(e)}'
        }