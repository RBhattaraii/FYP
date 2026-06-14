import os
import sys

def fix_imports():
    root_scrapers_dir = r"C:\Users\NITOR 5\Desktop\FYP\scrapers"
    
    files_to_fix = [
        os.path.join(root_scrapers_dir, 'daraz', 'daraz_scraper.py'),
        os.path.join(root_scrapers_dir, 'oliz', 'oliz_scraper.py'),
        os.path.join(root_scrapers_dir, 'hukut', 'hukut_scraper.py')
    ]
    
    for file in files_to_fix:
        if not os.path.exists(file):
            continue
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace("from app.scrapers.utils", "from scrapers.utils")
        content = content.replace("from app.scrapers.daraz.scraper", "from scrapers.daraz.daraz_scraper")
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # Fix backend/app/services/scraper_service.py
    backend_service = r"C:\Users\NITOR 5\Desktop\FYP\backend\app\services\scraper_service.py"
    
    new_content = """
\"\"\"
Scraper Service for FastAPI Backend
\"\"\"
import sys
import os

# Add the root FYP directory to sys.path so we can import the scrapers module
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from scrapers.daraz.daraz_scraper import async_scrape_daraz
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
"""
    with open(backend_service, 'w', encoding='utf-8') as f:
        f.write(new_content.strip())
        
    print("Imports fixed.")

if __name__ == '__main__':
    fix_imports()
