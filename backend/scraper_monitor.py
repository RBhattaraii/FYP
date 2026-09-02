#!/usr/bin/env python3
"""
SCRAPER PROGRESS MONITOR
Real-time monitoring of all scraping progress with live statistics
"""

import sqlite3
import os
import time
from datetime import datetime
import json
from collections import defaultdict

class ScraperMonitor:
    def __init__(self):
        self.platform_dbs = {
            'jeevee': 'jeevee_enhanced.db',
            'cgdigital': 'cgdigital_enhanced.db', 
            'hukut': 'hukut_enhanced.db',
            'oliz': 'oliz_enhanced.db',
            'better': 'better_enhanced.db',
            'hardwarepasal': 'hardwarepasal_enhanced.db'
        }
        self.master_db = 'master_enhanced_products.db'
        self.target = 100000
        
    def get_db_stats(self, db_file):
        """Get statistics from a database"""
        if not os.path.exists(db_file):
            return {
                'total': 0,
                'brands': 0,
                'categories': 0,
                'avg_price': 0,
                'latest_scraped': None,
                'file_size_mb': 0
            }
            
        try:
            conn = sqlite3.connect(db_file, timeout=5)
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT brand) FROM products WHERE brand IS NOT NULL')
            brands = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT category) FROM products WHERE category IS NOT NULL')
            categories = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(price) FROM products WHERE price > 0')
            avg_price = cursor.fetchone()[0] or 0
            
            # Latest scraped time
            cursor.execute('SELECT MAX(scraped_at) FROM products')
            latest_scraped = cursor.fetchone()[0]
            
            conn.close()
            
            file_size_mb = os.path.getsize(db_file) / 1024 / 1024
            
            return {
                'total': total,
                'brands': brands,
                'categories': categories,
                'avg_price': avg_price,
                'latest_scraped': latest_scraped,
                'file_size_mb': file_size_mb
            }
            
        except Exception as e:
            return {
                'total': 0,
                'brands': 0,
                'categories': 0,
                'avg_price': 0,
                'latest_scraped': None,
                'file_size_mb': 0,
                'error': str(e)
            }

    def get_scraping_rate(self, db_file, minutes=30):
        """Calculate products scraped per hour in last N minutes"""
        if not os.path.exists(db_file):
            return 0
            
        try:
            conn = sqlite3.connect(db_file, timeout=5)
            cursor = conn.cursor()
            
            # Count products scraped in last N minutes
            cursor.execute('''
                SELECT COUNT(*) FROM products 
                WHERE scraped_at >= datetime('now', '-{} minutes')
            '''.format(minutes))
            
            recent_count = cursor.fetchone()[0]
            conn.close()
            
            # Calculate hourly rate
            rate_per_hour = (recent_count / minutes) * 60
            return rate_per_hour
            
        except Exception:
            return 0

    def show_live_dashboard(self):
        """Display live dashboard with real-time statistics"""
        # Clear screen for live update effect
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🚀 ENHANCED SCRAPER MONITORING DASHBOARD")
        print("=" * 80)
        print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: {self.target:,} products")
        print("=" * 80)
        
        # Individual platform statistics
        total_all_platforms = 0
        platform_stats = {}
        
        print("\n📊 INDIVIDUAL PLATFORM PROGRESS:")
        print("-" * 80)
        print(f"{'PLATFORM':<15} {'PRODUCTS':<12} {'RATE/HR':<10} {'BRANDS':<8} {'SIZE':<8} {'STATUS'}")
        print("-" * 80)
        
        for platform, db_file in self.platform_dbs.items():
            stats = self.get_db_stats(db_file)
            rate = self.get_scraping_rate(db_file, 30)  # Last 30 minutes
            
            total_all_platforms += stats['total']
            platform_stats[platform] = stats
            
            # Determine status
            if stats['total'] == 0:
                status = "❌ NOT STARTED"
            elif rate > 10:
                status = "🟢 ACTIVE"
            elif rate > 0:
                status = "🟡 SLOW"
            else:
                status = "🔴 STOPPED"
            
            print(f"{platform.upper():<15} {stats['total']:,>11} {rate:>8.0f} {stats['brands']:>7} "
                  f"{stats['file_size_mb']:>6.1f}MB {status}")
        
        # Master database stats
        master_stats = self.get_db_stats(self.master_db)
        
        print("-" * 80)
        print(f"{'MASTER DB':<15} {master_stats['total']:,>11} {'N/A':<10} {master_stats['brands']:>7} "
              f"{master_stats['file_size_mb']:>6.1f}MB")
        
        # Progress summary
        progress_pct = (total_all_platforms / self.target) * 100 if self.target > 0 else 0
        remaining = max(0, self.target - total_all_platforms)
        
        print(f"\n🎯 OVERALL PROGRESS:")
        print(f"   Individual Platforms: {total_all_platforms:,} products")
        print(f"   Master Database: {master_stats['total']:,} products")
        print(f"   Progress: {progress_pct:.1f}% ({total_all_platforms:,} / {self.target:,})")
        print(f"   Remaining: {remaining:,} products")
        
        # Progress bar
        bar_length = 50
        filled_length = int(bar_length * progress_pct / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"   [{bar}] {progress_pct:.1f}%")
        
        # Estimated completion time
        total_rate = sum(self.get_scraping_rate(db_file, 60) for db_file in self.platform_dbs.values())
        if total_rate > 0 and remaining > 0:
            hours_remaining = remaining / total_rate
            completion_time = datetime.now().timestamp() + (hours_remaining * 3600)
            completion_str = datetime.fromtimestamp(completion_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   Estimated completion: {hours_remaining:.1f} hours ({completion_str})")
        
        # Top performing platforms
        active_platforms = [(p, self.get_scraping_rate(self.platform_dbs[p], 30)) 
                           for p in self.platform_dbs.keys()]
        active_platforms.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n⚡ SCRAPING RATES (products/hour):")
        for platform, rate in active_platforms:
            if rate > 0:
                print(f"   {platform.upper():<15}: {rate:>6.0f}/hr")
        
        # Recent activity
        print(f"\n🕐 RECENT ACTIVITY:")
        for platform, db_file in self.platform_dbs.items():
            stats = platform_stats[platform]
            if stats['latest_scraped']:
                try:
                    last_time = datetime.fromisoformat(stats['latest_scraped'].replace('Z', '+00:00'))
                    time_ago = datetime.now() - last_time.replace(tzinfo=None)
                    if time_ago.total_seconds() < 3600:  # Less than 1 hour
                        minutes_ago = int(time_ago.total_seconds() / 60)
                        print(f"   {platform.upper():<15}: {minutes_ago} minutes ago")
                except:
                    pass
        
        # Health warnings
        warnings = []
        for platform, stats in platform_stats.items():
            if stats.get('error'):
                warnings.append(f"❌ {platform.upper()}: Database error")
            elif stats['total'] == 0:
                warnings.append(f"⚠️  {platform.upper()}: No products found")
            elif self.get_scraping_rate(self.platform_dbs[platform], 60) == 0 and stats['total'] > 0:
                warnings.append(f"🔴 {platform.upper()}: Scraping stopped")
        
        if warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
        
        print(f"\n💡 TIPS:")
        print(f"   • Run each scraper in a separate terminal for parallel processing")
        print(f"   • Monitor for rate limiting and adjust delays if needed")
        print(f"   • Use enhanced_master_consolidator.py to merge databases")
        print(f"   • Press Ctrl+C to exit monitor")

    def monitor_continuously(self, interval=30):
        """Monitor scrapers continuously with auto-refresh"""
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)...")
        
        try:
            while True:
                self.show_live_dashboard()
                print(f"\n🔄 Refreshing in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n👋 Monitoring stopped by user")
            print(f"📊 Final summary:")
            self.show_summary()

    def show_summary(self):
        """Show final summary statistics"""
        total = sum(self.get_db_stats(db_file)['total'] for db_file in self.platform_dbs.values())
        master = self.get_db_stats(self.master_db)['total']
        
        print(f"   Individual platforms: {total:,} products")
        print(f"   Master database: {master:,} products")
        print(f"   Target progress: {(total/self.target)*100:.1f}%")

    def export_stats(self, filename=None):
        """Export current statistics to JSON file"""
        if not filename:
            filename = f"scraper_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'target': self.target,
            'platforms': {}
        }
        
        total_products = 0
        for platform, db_file in self.platform_dbs.items():
            stats = self.get_db_stats(db_file)
            rate = self.get_scraping_rate(db_file, 60)
            
            stats_data['platforms'][platform] = {
                'products': stats['total'],
                'brands': stats['brands'],
                'categories': stats['categories'],
                'avg_price': stats['avg_price'],
                'rate_per_hour': rate,
                'file_size_mb': stats['file_size_mb'],
                'latest_scraped': stats['latest_scraped']
            }
            
            total_products += stats['total']
        
        # Master database stats
        master_stats = self.get_db_stats(self.master_db)
        stats_data['master_database'] = {
            'products': master_stats['total'],
            'brands': master_stats['brands'],
            'file_size_mb': master_stats['file_size_mb']
        }
        
        stats_data['summary'] = {
            'total_individual_products': total_products,
            'progress_percentage': (total_products / self.target) * 100,
            'remaining_products': max(0, self.target - total_products)
        }
        
        with open(filename, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        print(f"📊 Statistics exported to: {filename}")
        return filename

if __name__ == "__main__":
    import sys
    
    monitor = ScraperMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            monitor.show_live_dashboard()
        elif sys.argv[1] == '--export':
            monitor.export_stats()
        elif sys.argv[1] == '--summary':
            monitor.show_summary()
        else:
            print("Usage: python scraper_monitor.py [--once|--export|--summary]")
    else:
        # Default: continuous monitoring
        monitor.monitor_continuously(30)