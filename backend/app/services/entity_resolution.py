"""
Advanced Entity Resolution Service for PricePilot
Performs string normalization, tokenization, Jaccard similarity scoring, brand alignment, 
and numerical specification matching to group identical products from different online stores.
"""
from typing import List, Dict, Any
import re

def normalize_title(title: str) -> str:
    """
    Clean and normalize product title for accurate token comparison.
    """
    # Lowercase
    title = title.lower()
    # Remove punctuation/symbols except spaces and alphanumeric characters
    title = re.sub(r'[^\w\s]', ' ', title)
    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def extract_numbers(title: str) -> set:
    """
    Extract numbers with optional units (like 128gb, 8gb, v8, etc.) to prevent matching mismatches.
    """
    # Remove space between digits and units, e.g. "256 gb" -> "256gb"
    title_clean = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title.lower())
    tokens = re.findall(r'\b\d+(?:gb|tb|mb|ram|hz|v|w|mah|ah|k|s|pro|pro\smax)?\b|\b(?:i3|i5|i7|i9|ryzen\s\d|m1|m2|m3)\b', title_clean)
    return set(tokens)

def calculate_jaccard_similarity(title_a: str, title_b: str) -> float:
    """
    Compute word-level Jaccard similarity index: Intersection(A, B) / Union(A, B)
    """
    # Normalize space around units in titles
    clean_a = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title_a.lower())
    clean_b = re.sub(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b', r'\1\2', title_b.lower())
    
    words_a = set(normalize_title(clean_a).split())
    words_b = set(normalize_title(clean_b).split())
    
    # Remove common stopwords to focus on distinctive keywords
    stopwords = {'for', 'with', 'and', 'of', 'in', 'the', 'nepal', 'buy', 'online', 'genuine', 'brand', 'new', 'official', 'warranty'}
    words_a = words_a - stopwords
    words_b = words_b - stopwords
    
    if not words_a or not words_b:
        return 0.0
        
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    
    return len(intersection) / len(union)

def match_products(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> bool:
    """
    Determines if two products are identical based on text similarity and specs.
    """
    title_a = prod_a.get('title', '')
    title_b = prod_b.get('title', '')
    
    # Calculate text Jaccard similarity
    jaccard_score = calculate_jaccard_similarity(title_a, title_b)
    
    # Check if numerical values (storage, RAM, CPU tier) match
    nums_a = extract_numbers(title_a)
    nums_b = extract_numbers(title_b)
    
    # If they have mismatched specs (e.g. 128gb vs 256gb), they are not the same product
    spec_mismatch = False
    if nums_a and nums_b:
        # Check if they have contrasting digits with same unit
        # e.g., A has "128gb" and B has "256gb"
        for spec in nums_a:
            if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_b:
                spec_mismatch = True
                break
        for spec in nums_b:
            if ('gb' in spec or 'tb' in spec or 'ram' in spec) and spec not in nums_a:
                spec_mismatch = True
                break
                
    if spec_mismatch:
        return False
        
    # High similarity threshold + matching specs
    return jaccard_score >= 0.40

def resolve_entities(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Consolidates a flat list of products into an entity-resolved list, grouping
    identical items from different stores under a single product profile.
    
    Optimized to run in O(N log N) average time by pre-computing features
    and partitioning comparisons using brand buckets.
    """
    if not products:
        return []
        
    # Step 1: Pre-compute features (regex, splits, sets) for all products ONCE
    stopwords = {'for', 'with', 'and', 'of', 'in', 'the', 'nepal', 'buy', 'online', 'genuine', 'brand', 'new', 'official', 'warranty'}
    unit_pattern = re.compile(r'(\d+)\s*(gb|tb|mb|ram|mah|hz|v|w|ah|k|s)\b')
    word_pattern = re.compile(r'[^\w\s]')
    space_pattern = re.compile(r'\s+')
    spec_pattern = re.compile(r'\b\d+(?:gb|tb|mb|ram|hz|v|w|mah|ah|k|s|pro|pro\smax)?\b|\b(?:i3|i5|i7|i9|ryzen\s\d|m1|m2|m3)\b')
    
    common_brands = {
        'apple', 'iphone', 'macbook', 'samsung', 'xiaomi', 'redmi', 'poco', 'oneplus', 'realme', 'oppo', 'vivo',
        'huawei', 'honor', 'nokia', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'sony',
        'lg', 'panasonic', 'philips', 'canon', 'nikon', 'gopro', 'dji', 'bose', 'jbl', 'boat', 'anker'
    }
    
    accessory_keywords = {
        "cover", "case", "protector", "glass", "cable", "charger", "adapter",
        "strap", "band", "mount", "remote", "stand", "skin", "decal", "sticker",
        "hybrid", "magsafe", "magnetic", "silicone", "leather", "wallet",
        "tempered", "lens", "guard", "ring", "holder", "tripod", "pouch", "sleeve",
        "screen", "film", "back", "bumper", "grip", "clip", "dock", "hub",
        "pendrive", "usb", "ram", "memory", "sodimm", "dimm", "ddr4", "ddr5", "ssd",
        "hard drive", "hdd", "mouse", "keyboard", "battery", "backpack", "bag", "stylus", "pen"
    }
    
    model_modifiers = {"pro", "max", "plus", "mini", "ultra", "lite", "se", "e", "neo", "play", "air"}
    
    precomputed = []
    for p in products:
        title = (p.get('title') or '').lower()
        # Normalize
        clean_title = unit_pattern.sub(r'\1\2', title)
        norm_title = word_pattern.sub(' ', clean_title)
        norm_title = space_pattern.sub(' ', norm_title).strip()
        
        words = set(norm_title.split())
        words_without_stopwords = words - stopwords
        specs = set(spec_pattern.findall(clean_title))
        
        # Precompute features
        is_accessory = any(keyword in title for keyword in accessory_keywords)
        modifiers = {mod for mod in model_modifiers if mod in words}
        
        p_copy = dict(p)
        p_copy['_resolved_words'] = words_without_stopwords
        p_copy['_resolved_numbers'] = specs
        p_copy['_resolved_is_accessory'] = is_accessory
        p_copy['_resolved_modifiers'] = modifiers
        p_copy['store_count'] = 1
        p_copy['alternative_offers'] = []
        precomputed.append(p_copy)
        
    # Step 2: Canopy / Brand grouping to restrict matching pairs
    buckets = {}
    for idx, p in enumerate(precomputed):
        title = (p.get('title') or '').lower()
        brand = 'generic'
        for b in common_brands:
            if b in title:
                # Group related brands/sub-brands together
                if b in ('apple', 'iphone', 'macbook'):
                    brand = 'apple'
                elif b in ('xiaomi', 'redmi', 'poco'):
                    brand = 'xiaomi'
                else:
                    brand = b
                break
        if brand == 'generic' and title.split():
            brand = title.split()[0]
            
        p['_resolved_brand'] = brand
        buckets.setdefault(brand, []).append(idx)
        
    # Step 3: Run grouping in the original sorted order
    resolved = []
    used_indices = set()
    
    for i in range(len(precomputed)):
        if i in used_indices:
            continue
            
        primary = precomputed[i]
        brand = primary['_resolved_brand']
        brand_bucket = buckets.get(brand, [])
        
        # Look for matches in the same brand bucket
        for j in brand_bucket:
            if j <= i or j in used_indices:
                continue
                
            candidate = precomputed[j]
            if primary.get('store_name') == candidate.get('store_name'):
                continue
                
            # Guard: Accessories and non-accessories never match
            if primary['_resolved_is_accessory'] != candidate['_resolved_is_accessory']:
                continue
                
            # Guard: Model modifiers must match exactly (e.g. Pro vs Max)
            if primary['_resolved_modifiers'] != candidate['_resolved_modifiers']:
                continue
                
            # Guard: Price ratio must be at least 0.50 (i.e. not more than 2x price difference)
            price_a = float(primary.get('price') or 0)
            price_b = float(candidate.get('price') or 0)
            if price_a and price_b:
                ratio = min(price_a, price_b) / max(price_a, price_b)
                if ratio < 0.50:
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
            
        # Post process primary alternative offers list
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
        
        # Clean up internal fields
        primary.pop('_resolved_words', None)
        primary.pop('_resolved_numbers', None)
        primary.pop('_resolved_brand', None)
        primary.pop('_resolved_is_accessory', None)
        primary.pop('_resolved_modifiers', None)
        resolved.append(primary)
        used_indices.add(i)
        
    return resolved
