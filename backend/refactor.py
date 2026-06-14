import os

def refactor_scrapers():
    with open('app/services/scraper_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    utils_code = """
import re
import urllib.parse
from datetime import datetime, timezone

BASE_URL = "https://www.daraz.com.np"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

def clean_price(price_text):
    if not price_text:
        return None
    cleaned = price_text.replace("Rs.", "").replace("Rs", "")
    cleaned = re.sub(r"[^\d.]", "", cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None

def calculate_discount(original_price, current_price):
    if original_price and current_price and original_price > current_price:
        discount = ((original_price - current_price) / original_price) * 100
        return round(discount)
    return None
"""

    with open('app/scrapers/utils.py', 'w', encoding='utf-8') as f:
        f.write(utils_code.strip())
        
    daraz_code = """
import time
import asyncio
import re
import urllib.parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from app.scrapers.utils import clean_price, calculate_discount, BASE_URL, USER_AGENT

_executor = ThreadPoolExecutor(max_workers=2)
""" + content[content.find('def _parse_products_from_page'):content.find('async def async_scrape_oliz')]

    with open('app/scrapers/daraz/scraper.py', 'w', encoding='utf-8') as f:
        f.write(daraz_code.strip())
        
    oliz_code = """
import json
import requests
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.scrapers.utils import calculate_discount, USER_AGENT
from app.scrapers.daraz.scraper import _executor

""" + content[content.find('async def async_scrape_oliz'):content.find('async def async_scrape_hukut')]

    with open('app/scrapers/oliz/scraper.py', 'w', encoding='utf-8') as f:
        f.write(oliz_code.strip())
        
    hukut_code = """
import json
import requests
import asyncio
import urllib.parse
from datetime import datetime, timezone
from app.scrapers.utils import calculate_discount, USER_AGENT
from app.scrapers.daraz.scraper import _executor

""" + content[content.find('async def async_scrape_hukut'):]

    with open('app/scrapers/hukut/scraper.py', 'w', encoding='utf-8') as f:
        f.write(hukut_code.strip())
        
    # Now rewrite scraper_service.py to just import them
    new_service_code = """
\"\"\"
Scraper Service for FastAPI Backend
\"\"\"

from app.scrapers.daraz.scraper import async_scrape_daraz
from app.scrapers.oliz.scraper import async_scrape_oliz
from app.scrapers.hukut.scraper import async_scrape_hukut
"""
    with open('app/services/scraper_service.py', 'w', encoding='utf-8') as f:
        f.write(new_service_code.strip())

    print("Refactoring complete.")

if __name__ == '__main__':
    refactor_scrapers()
