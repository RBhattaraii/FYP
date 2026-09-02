import requests

url = "https://cgdigital.com.np/api/web-search?keywords=laptop"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://cgdigital.com.np",
    "Referer": "https://cgdigital.com.np/search/laptop"
}

try:
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    print(res.text[:500])
except Exception as e:
    print(e)
