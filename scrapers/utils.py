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