import requests
import re
r = requests.get('https://www.jeevee.com')
links = re.findall(r'href=[\'\"](/product/[^\'\"]+)[\'\"]', r.text)
if not links:
    links = re.findall(r'href=[\'\"](/products/[^\'\"]+)[\'\"]', r.text)
for link in set(links[:15]):
    print(link)
