import re
from collections import Counter

with open('ufonepal_dump.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find class attributes
classes = re.findall(r'class="([^"]+)"', content)
product_classes = [c for c in classes if 'product' in c.lower()]
counts = Counter(product_classes)
print('Product-related classes (top 20):')
for cls, cnt in counts.most_common(20):
    print(f'  {cnt:3d}x  {cls}')

print()
print('Snippet around first "product" occurrence:')
idx = content.lower().find('product')
if idx > 0:
    print(content[max(0, idx-100):idx+300])
