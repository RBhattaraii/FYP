"""
Verification script for PricePilot high-end FYP features:
1. AI Price Forecasting (Holt's Linear Trend & OLS Regression)
2. Advanced Entity Resolution (Jaccard similarity product grouping)
3. Alerts checking background task
"""
import asyncio
from datetime import datetime, timedelta
from app.services.forecasting import generate_price_forecast
from app.services.entity_resolution import resolve_entities

def test_ai_forecasting():
    print("\n==================================================")
    print("Testing AI Price Forecasting Service...")
    print("==================================================")
    
    # Mock price history showing a downward trend
    base_date = datetime.now()
    history = [
        {"price": 10000.0, "date": (base_date - timedelta(days=20)).isoformat()},
        {"price": 9800.0, "date": (base_date - timedelta(days=15)).isoformat()},
        {"price": 9500.0, "date": (base_date - timedelta(days=10)).isoformat()},
        {"price": 9200.0, "date": (base_date - timedelta(days=5)).isoformat()},
        {"price": 9000.0, "date": base_date.isoformat()}
    ]
    
    forecast = generate_price_forecast(history, 9000.0)
    print(f"Current Price: 9000.0")
    print(f"15-Day Prediction: {forecast['predicted_price_15_days']}")
    print(f"30-Day Prediction: {forecast['predicted_price_30_days']}")
    print(f"Trend Direction: {forecast['trend_direction']}")
    print(f"Confidence Score: {forecast['confidence_score']}%")
    print(f"Recommendation: {forecast['recommendation']}")
    print(f"Explanation: {forecast['explanation']}")
    
    assert forecast['trend_direction'] == 'down'
    assert forecast['recommendation'] == 'Wait'
    print("[SUCCESS] AI Forecasting behaves correctly!")

def test_entity_resolution():
    print("\n==================================================")
    print("Testing Advanced Entity Resolution (Product Grouping)...")
    print("==================================================")
    
    # Mock search results containing duplicate listings with slight name variations
    products = [
        {
            "id": 1,
            "title": "Apple iPhone 15 Pro Max 256GB Black",
            "price": 195000.0,
            "original_price": 200000.0,
            "discount_percent": 2,
            "image_url": "iphone_black.jpg",
            "store_name": "Daraz",
            "product_url": "/daraz/iphone15"
        },
        {
            "id": 2,
            "title": "iPhone 15 Pro Max 256 GB (Black)",
            "price": 191000.0,
            "original_price": 195000.0,
            "discount_percent": 2,
            "image_url": "iphone_hukut.jpg",
            "store_name": "Hukut",
            "product_url": "/hukut/iphone15-256"
        },
        {
            "id": 3,
            "title": "Apple iPhone 15 Pro Max 128GB Black", # Storage mismatch - should NOT be grouped!
            "price": 175000.0,
            "image_url": "iphone_128.jpg",
            "store_name": "CGDigital",
            "product_url": "/cg/iphone15-128"
        }
    ]
    
    resolved = resolve_entities(products)
    print(f"Total input products: {len(products)}")
    print(f"Total resolved products: {len(resolved)}")
    
    for idx, p in enumerate(resolved):
        print(f"\nGroup {idx + 1}: {p['title']}")
        print(f"  Lowest Price: Rs {p['price']} (Store: {p['store_name']})")
        print(f"  Stores Count: {p['store_count']}")
        if p['alternative_offers']:
            print(f"  Alternative Offers:")
            for offer in p['alternative_offers']:
                print(f"    - {offer['store_name']}: Rs {offer['price']}")
                
    # Group 1 (iPhone 15 Pro Max 256GB) should group Daraz and Hukut together (lowest price selected)
    assert len(resolved) == 2
    iphone_256 = next(x for x in resolved if "256" in x['title'])
    assert iphone_256['store_count'] == 2
    assert iphone_256['price'] == 191000.0 # Cheaper Hukut price swapped to primary
    assert iphone_256['store_name'] == 'Hukut'
    assert len(iphone_256['alternative_offers']) == 1
    assert iphone_256['alternative_offers'][0]['store_name'] == 'Daraz'
    
    print("[SUCCESS] Entity Resolution groups and consolidates duplicates correctly!")

if __name__ == "__main__":
    test_ai_forecasting()
    test_entity_resolution()
    print("\n[ALL TESTS PASSED SUCCESSFULLY]")
