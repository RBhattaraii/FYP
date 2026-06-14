import requests
import time

def test_search():
    url = "http://localhost:8000/products/search?q=samsung+s24"
    
    print("--- FIRST REQUEST (Should be LIVE) ---")
    start = time.time()
    response = requests.get(url)
    end = time.time()
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Source: {data.get('source')}")
    print(f"Time taken: {end - start:.2f} seconds")
    print(f"Results found: {data.get('results_count')}")
    if data.get('data'):
        print(f"First result: {data['data'][0].get('product_name')}")
    
    print("\n--- SECOND REQUEST (Should be CACHE) ---")
    start = time.time()
    response = requests.get(url)
    end = time.time()
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Source: {data.get('source')}")
    print(f"Time taken: {end - start:.2f} seconds")
    print(f"Results found: {data.get('results_count')}")
    
if __name__ == "__main__":
    test_search()
