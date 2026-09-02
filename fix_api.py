import sys
with open('mobile/services/api.ts', 'r') as f:
    content = f.read()

content = content.replace('\\${API_URL}/compare/search\\', '`${API_URL}/compare/search`')
content = content.replace("'Authorization': Bearer ,", "'Authorization': `Bearer ${token}`,\n")
content = content.replace("throw new Error(HTTP : );", "throw new Error(`HTTP ${response.status}: ${response.statusText}`);")
content = content.replace('\\${API_URL}/compare/create\\', '`${API_URL}/compare/create`')
content = content.replace('\\${API_URL}/compare/\\', '`${API_URL}/compare/`')
content = content.replace('\\${API_URL}/price-history/?days=\\', '`${API_URL}/price-history/${productId}?days=${days}`')

with open('mobile/services/api.ts', 'w') as f:
    f.write(content)
