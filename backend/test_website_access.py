#!/usr/bin/env python3
"""
Website Accessibility Tester
Quick test to check if target websites are accessible
"""

import requests
import time
from datetime import datetime

def test_website(name, url, timeout=10):
    """Test if a website is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"Testing {name}... ", end="")
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            print(f"✅ OK ({response.status_code}) - {len(response.content)} bytes")
            return True
        else:
            print(f"⚠️  HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)[:50]}...")
        return False

def main():
    print("🔍 WEBSITE ACCESSIBILITY TEST")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    websites = [
        ("Jeevee", "https://jeevee.com.np"),
        ("CGDigital", "https://cgdigital.com.np"),
        ("Hukut", "https://hukut.com"),
        ("Oliz Store", "https://olizstore.com"),
        ("Better", "https://better.com.np"),
        ("Hardware Pasal", "https://hardwarepasal.com")
    ]
    
    accessible = 0
    total = len(websites)
    
    for name, url in websites:
        if test_website(name, url):
            accessible += 1
        time.sleep(1)  # Brief delay between tests
    
    print("=" * 40)
    print(f"📊 Results: {accessible}/{total} websites accessible")
    
    if accessible == total:
        print("🎉 All websites are accessible - ready to scrape!")
    elif accessible > total // 2:
        print("⚠️  Some websites unavailable - partial scraping possible")
    else:
        print("❌ Many websites unavailable - check network/VPN")
    
    print("\n💡 If websites are blocked:")
    print("   • Try using a VPN")
    print("   • Wait and retry later")
    print("   • Check if sites are down: downforeveryoneorjustme.com")

if __name__ == "__main__":
    main()