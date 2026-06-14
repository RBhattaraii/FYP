import re
from collections import Counter

with open('search_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

links = re.findall(r'<a[^>]*class="([^"]+)"[^>]*href="[^"]*/products/[^"]+"', html)
print(Counter(links).most_common(5))
