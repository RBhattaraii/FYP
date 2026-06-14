import os
import shutil

def reorganize():
    root_scrapers_dir = r"C:\Users\NITOR 5\Desktop\FYP\scrapers"
    backend_scrapers_dir = r"C:\Users\NITOR 5\Desktop\FYP\backend\app\scrapers"
    
    # 1. Create site folders in the root scrapers directory
    for site in ['daraz', 'oliz', 'hukut']:
        site_dir = os.path.join(root_scrapers_dir, site)
        os.makedirs(site_dir, exist_ok=True)
        # Create __init__.py so it can be imported
        open(os.path.join(site_dir, '__init__.py'), 'w').close()
        
        # Copy the refactored scrapers from backend to root scrapers
        src = os.path.join(backend_scrapers_dir, site, 'scraper.py')
        dst = os.path.join(site_dir, f'{site}_scraper.py')
        if os.path.exists(src):
            shutil.copy2(src, dst)
            
    # Copy utils.py
    src_utils = os.path.join(backend_scrapers_dir, 'utils.py')
    dst_utils = os.path.join(root_scrapers_dir, 'utils.py')
    if os.path.exists(src_utils):
        shutil.copy2(src_utils, dst_utils)

    # Make the root scrapers directory a package
    open(os.path.join(root_scrapers_dir, '__init__.py'), 'w').close()
    
    print("Files moved to root scrapers folder.")

if __name__ == '__main__':
    reorganize()
