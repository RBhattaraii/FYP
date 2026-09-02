#!/usr/bin/env python3
"""
Run Working Scrapers - Launch multiple scrapers that actually work
"""

import subprocess
import time
import os
import threading
from datetime import datetime

class ScraperLauncher:
    def __init__(self):
        self.results = {}
        
    def run_scraper(self, scraper_name, script_file):
        """Run a single scraper and capture results"""
        print(f"🚀 Starting {scraper_name}...")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                ['python', script_file], 
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True, 
                text=True, 
                timeout=3600  # 1 hour timeout
            )
            
            runtime = time.time() - start_time
            
            if result.returncode == 0:
                self.results[scraper_name] = {
                    'status': 'SUCCESS',
                    'runtime': runtime,
                    'output': result.stdout[-500:] if result.stdout else ""  # Last 500 chars
                }
                print(f"✅ {scraper_name} completed in {runtime/60:.1f} minutes")
            else:
                self.results[scraper_name] = {
                    'status': 'FAILED', 
                    'runtime': runtime,
                    'error': result.stderr[-500:] if result.stderr else ""
                }
                print(f"❌ {scraper_name} failed after {runtime/60:.1f} minutes")
                
        except subprocess.TimeoutExpired:
            self.results[scraper_name] = {
                'status': 'TIMEOUT',
                'runtime': 3600,
                'error': 'Scraper timed out after 1 hour'
            }
            print(f"⏰ {scraper_name} timed out after 1 hour")
            
        except Exception as e:
            self.results[scraper_name] = {
                'status': 'ERROR',
                'runtime': 0,
                'error': str(e)
            }
            print(f"💥 {scraper_name} crashed: {e}")

    def launch_all_scrapers(self):
        """Launch all working scrapers in parallel"""
        print("🚀 LAUNCHING ALL WORKING SCRAPERS")
        print("=" * 50)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Define working scrapers
        scrapers = [
            ("Quick Working", "quick_working_scraper.py"),
            # Add more as we fix them
        ]
        
        # Launch in separate threads for parallel execution
        threads = []
        
        for scraper_name, script_file in scrapers:
            if os.path.exists(script_file):
                thread = threading.Thread(
                    target=self.run_scraper, 
                    args=(scraper_name, script_file)
                )
                threads.append(thread)
                thread.start()
                time.sleep(2)  # Small delay between starts
            else:
                print(f"⚠️  {script_file} not found, skipping {scraper_name}")
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        self.show_final_results()

    def show_final_results(self):
        """Show final results summary"""
        print(f"\n🎉 ALL SCRAPERS COMPLETED!")
        print("=" * 50)
        
        total_runtime = 0
        successful = 0
        failed = 0
        
        for scraper_name, result in self.results.items():
            status = result['status']
            runtime = result['runtime']
            total_runtime += runtime
            
            if status == 'SUCCESS':
                successful += 1
                print(f"✅ {scraper_name:20}: SUCCESS ({runtime/60:.1f}min)")
            else:
                failed += 1
                print(f"❌ {scraper_name:20}: {status} ({runtime/60:.1f}min)")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Total runtime: {total_runtime/60:.1f} minutes")
        
        # Check database sizes
        db_files = [
            'quick_working_products.db',
            'oliz_enhanced.db',
            'hardwarepasal_enhanced.db',
            'jeevee_enhanced.db',
            'hukut_enhanced.db'
        ]
        
        print(f"\n💾 DATABASE SIZES:")
        total_size = 0
        for db_file in db_files:
            if os.path.exists(db_file):
                size_mb = os.path.getsize(db_file) / 1024 / 1024
                total_size += size_mb
                print(f"   {db_file:25}: {size_mb:.1f} MB")
        
        print(f"   Total DB size: {total_size:.1f} MB")
        
        print(f"\n💡 NEXT STEPS:")
        print("   1. Check individual database files for product counts")
        print("   2. Run enhanced_master_consolidator.py to merge all data")
        print("   3. Use scraper_monitor.py to track overall progress")

if __name__ == "__main__":
    launcher = ScraperLauncher()
    launcher.launch_all_scrapers()