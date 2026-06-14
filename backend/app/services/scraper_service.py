"""
Scraper Service for FastAPI Backend
"""
import sys
import os

# Add the root FYP directory to sys.path so we can import the scrapers module
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from scrapers.daraz.daraz_scraper import async_scrape_daraz
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee