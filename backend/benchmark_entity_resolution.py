import time
import re
from typing import List, Dict, Any

def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

# Original implementation
def extract_numbers_old(title: str) -> set:
    title_clean = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title.lower())
    tokens = re.findall(r'\b\d+(?:gb|tb|mb|ram|hz|v|w|mah|ah|k|s|pro|pro\smax)?\b|\b(?:i3|i5|i7|i9|ryzen\s\d|m1|m2|m3)\b', title_clean)
    return set(tokens)

def calculate_jaccard_similarity_old(title_a: str, title_b: str) -> float:
    clean_a = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title_a.lower())
    clean_b = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title_b.lower())
    
    words_a = set(normalize_title(clean_a).split())
    words_b = set(normalize_title(clean_b).split())
    
    stopwords = {'for', 'with', 'and', 'of', 'in', 'the', 'nepal', 'buy', 'online', 'genuine', 'brand', 'new', 'official', 'warranty'}
    words_a = words_a - stopwords
    words_b = words_b - stopwords
    
    if not words_a or not words_b:
        return 0.0
    return len(words_a.intersection(words_b)) / len(words_a.union(words_b))

def match_products_old(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> bool:
    title_a = prod_a.get('title', '')
    title_b = prod_b.get('title', '')
    jaccard_score = calculate_jaccard_similarity_old(title_a, title_b)
    nums_a = extract_numbers_old(title_a)
    nums_b = extract_numbers_old(title_b)
    
    spec_mismatch = False
    if nums_a and nums_b:
        for spec in nums_a:
            if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_b:
                spec_mismatch = True
                break
        if not spec_mismatch:
            for spec in nums_b:
                if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_a:
                    spec_mismatch = True
                    break
    if spec_mismatch:
        return False
    return jaccard_score >= 0.40


# Optimized implementation
def resolve_entities_optimized(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not products:
        return []
        
    t0 = time.time()
    
    # Step 1: Pre-compute features (regex, splits, sets) for all products ONCE
    stopwords = {'for', 'with', 'and', 'of', 'in', 'the', 'nepal', 'buy', 'online', 'genuine', 'brand', 'new', 'official', 'warranty'}
    unit_pattern = re.compile(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b')
    word_pattern = re.compile(r'[^\w\s]')
    space_pattern = re.compile(r'\s+')
    spec_pattern = re.compile(r'\b\d+(?:gb|tb|mb|ram|hz|v|w|mah|ah|k|s|pro|pro\smax)?\b|\b(?:i3|i5|i7|i9|ryzen\s\d|m1|m2|m3)\b')
    
    precomputed = []
    for p in products:
        title = p.get('title') or ''
        # Normalize
        clean_title = unit_pattern.sub(r'\1\2', title.lower())
        norm_title = word_pattern.sub(' ', clean_title)
        norm_title = space_pattern.sub(' ', norm_title).strip()
        
        words = set(norm_title.split()) - stopwords
        specs = set(spec_pattern.findall(clean_title))
        
        p_copy = dict(p)
        p_copy['_resolved_words'] = words
        p_copy['_resolved_numbers'] = specs
        p_copy['store_count'] = 1
        p_copy['alternative_offers'] = []
        precomputed.append(p_copy)
        
    print(f"Precompute took {(time.time() - t0)*1000:.2f}ms")
    
    # Step 2: Canopy / Brand grouping to restrict matching pairs
    # Group by first word of clean title as a bucket key (candidate generator)
    buckets = {}
    for idx, p in enumerate(precomputed):
        title = p.get('title', '').lower()
        # Find brand/prefix word
        first_word = title.split()[0] if title.split() else 'generic'
        # Group similar brands
        if first_word in ('apple', 'iphone'):
            brand = 'apple'
        elif first_word in ('dell', 'inspiron', 'latitude', 'xps'):
            brand = 'dell'
        elif first_word in ('hp', 'pavilion', 'elitebook', 'probook'):
            brand = 'hp'
        elif first_word in ('lenovo', 'thinkpad', 'ideapad', 'yoga'):
            brand = 'lenovo'
        elif first_word in ('asus', 'zenbook', 'vivobook', 'rog'):
            brand = 'asus'
        elif first_word in ('acer', 'aspire', 'predator', 'spin'):
            brand = 'acer'
        else:
            brand = first_word
            
        buckets.setdefault(brand, []).append(idx)
        
    # Step 3: Run grouping per bucket
    resolved = []
    used_indices = set()
    
    t1 = time.time()
    for brand_bucket in buckets.values():
        for i_idx in range(len(brand_bucket)):
            i = brand_bucket[i_idx]
            if i in used_indices:
                continue
                
            primary = precomputed[i]
            
            # Look for matches in the same brand bucket
            for j_idx in range(i_idx + 1, len(brand_bucket)):
                j = brand_bucket[j_idx]
                if j in used_indices:
                    continue
                    
                candidate = precomputed[j]
                if primary.get('store_name') == candidate.get('store_name'):
                    continue
                    
                # Match check (optimized using precomputed fields)
                words_a = primary['_resolved_words']
                words_b = candidate['_resolved_words']
                
                jaccard_score = 0.0
                if words_a and words_b:
                    jaccard_score = len(words_a & words_b) / len(words_a | words_b)
                    
                if jaccard_score < 0.40:
                    continue
                    
                nums_a = primary['_resolved_numbers']
                nums_b = candidate['_resolved_numbers']
                
                spec_mismatch = False
                if nums_a and nums_b:
                    for spec in nums_a:
                        if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_b:
                            spec_mismatch = True
                            break
                    if not spec_mismatch:
                        for spec in nums_b:
                            if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_a:
                                spec_mismatch = True
                                break
                                
                if spec_mismatch:
                    continue
                    
                # Found match!
                primary['alternative_offers'].append({
                    'store_name': candidate.get('store_name'),
                    'price': float(candidate.get('price')),
                    'original_price': float(candidate['original_price']) if candidate.get('original_price') else None,
                    'discount_percent': candidate.get('discount_percent'),
                    'product_url': candidate.get('product_url'),
                    'image_url': candidate.get('image_url'),
                })
                primary['store_count'] += 1
                used_indices.add(j)
                
            # Post process primary
            if primary['alternative_offers']:
                primary['alternative_offers'].sort(key=lambda x: x['price'])
                cheapest_alt = primary['alternative_offers'][0]
                if cheapest_alt['price'] < primary['price']:
                    old_primary_offer = {
                        'store_name': primary['store_name'],
                        'price': float(primary['price']),
                        'original_price': float(primary['original_price']) if primary.get('original_price') else None,
                        'discount_percent': primary.get('discount_percent'),
                        'product_url': primary['product_url'],
                        'image_url': primary['image_url'],
                    }
                    primary['alternative_offers'].append(old_primary_offer)
                    primary['price'] = cheapest_alt['price']
                    primary['original_price'] = cheapest_alt['original_price']
                    primary['discount_percent'] = cheapest_alt['discount_percent']
                    primary['store_name'] = cheapest_alt['store_name']
                    primary['product_url'] = cheapest_alt['product_url']
                    primary['image_url'] = cheapest_alt['image_url']
                    
                    primary['alternative_offers'] = [o for o in primary['alternative_offers'] if o['product_url'] != cheapest_alt['product_url']]
                    primary['alternative_offers'].sort(key=lambda x: x['price'])
            
            # Clean up internal fields to keep return footprint small
            primary.pop('_resolved_words', None)
            primary.pop('_resolved_numbers', None)
            resolved.append(primary)
            used_indices.add(i)
            
    print(f"Loop matching took {(time.time() - t1)*1000:.2f}ms")
    return resolved

# Run benchmark
if __name__ == "__main__":
    # Generate 2500 products
    mock_products = []
    brands = ['Apple', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Samsung', 'Generic']
    for idx in range(2500):
        brand = brands[idx % len(brands)]
        mock_products.append({
            'title': f"{brand} Laptop 15.6 inch {128 * (1 + (idx%3))}GB SSD 8GB RAM",
            'price': 50000.0 + (idx % 20) * 1000.0,
            'store_name': f"Store {idx % 4}",
            'product_url': f"https://store{idx % 4}.com/product/{idx}",
            'image_url': 'image.jpg'
        })
        
    print(f"Running Entity Resolution on {len(mock_products)} products...")
    resolved = resolve_entities_optimized(mock_products)
    print(f"Total resolved: {len(resolved)}")
