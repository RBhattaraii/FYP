import requests

urls = [
    "https://www.jeevee.com/products/ultima-rapid-75w-pd+qc-car-charger-adapter-with-dual-port-137862",
    "https://hukut.com/product/nothing-phone-(3a)-pro",
    "https://www.neostore.com.np/product/ant-esports-690-af-projector-home-projector-1080p-native-4k-decoding-android-13-wifi-8000-lumens-auto-focus-ott-apps-portable-home-cinema-voice-remote"
]

for url in urls:
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        print(f"Status {r.status_code} for {url}")
        if r.status_code == 404:
            print("  This is actually a 404 page!")
    except Exception as e:
        print(f"Error {url}: {e}")
