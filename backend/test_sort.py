from app.services.scraper_coordinator import sort_search_results

products = [
    {'title': 'UNIQ HYBRID IPHONE 17 PRO MAX MAGCLICK CHARGING CAMERAS', 'price': 2400, 'platform': 'jeevee'},
    {'title': 'Apple iPhone 17 Pro Max 256GB', 'price': 210000, 'platform': 'daraz'},
    {'title': 'UNIQ HYBRID IPHONE 17 PRO CLARION TINT', 'price': 2000, 'platform': 'jeevee'}
]

sorted_res = sort_search_results('iphone 17', products)
for p in sorted_res:
    print(f"{p['title']} - Rs {p['price']}")
