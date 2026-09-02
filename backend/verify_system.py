#!/usr/bin/env python3
"""
System Verification Script
Checks that all enhanced scraper files are in place and ready
"""

import os
import sqlite3
from datetime import datetime

def check_file_exists(filename, description):
    """Check if a file exists and show status"""
    exists = os.path.exists(filename)
    size = f" ({os.path.getsize(filename)} bytes)" if exists else ""
    status = "✅" if exists else "❌"
    print(f"   {status} {filename:35} - {description}{size}")
    return exists

def verify_system():
    """Verify all system components are ready"""
    print("🔍 ENHANCED SCRAPING SYSTEM VERIFICATION")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directory: {os.getcwd()}")
    print("=" * 50)
    
    # Check enhanced scrapers
    print("\n🚀 ENHANCED SCRAPERS:")
    scrapers = [
        ("enhanced_jeevee_scraper.py", "Jeevee marketplace scraper"),
        ("enhanced_cgdigital_scraper.py", "CGDigital electronics scraper"),
        ("enhanced_hukut_scraper.py", "Hukut marketplace scraper"),
        ("enhanced_oliz_scraper.py", "Oliz fashion scraper"),
        ("enhanced_better_scraper.py", "Better products scraper"),
        ("enhanced_hardwarepasal_scraper.py", "HardwarePasal hardware scraper")
    ]
    
    scraper_count = 0
    for filename, description in scrapers:
        if check_file_exists(filename, description):
            scraper_count += 1
    
    # Check management tools
    print("\n📊 MANAGEMENT TOOLS:")
    tools = [
        ("scraper_monitor.py", "Real-time progress monitor"),
        ("enhanced_master_consolidator.py", "Database consolidator"),
        ("test_website_access.py", "Website accessibility tester"),
        ("verify_system.py", "System verification script")
    ]
    
    tool_count = 0
    for filename, description in tools:
        if check_file_exists(filename, description):
            tool_count += 1
    
    # Check launchers
    print("\n🚀 LAUNCHERS:")
    launchers = [
        ("run_all_scrapers.bat", "Windows batch launcher"),
        ("run_all_scrapers.sh", "Linux/Mac shell launcher")
    ]
    
    launcher_count = 0
    for filename, description in launchers:
        if check_file_exists(filename, description):
            launcher_count += 1
    
    # Check documentation
    print("\n📚 DOCUMENTATION:")
    docs = [
        ("SCRAPER_INSTRUCTIONS.md", "User instructions"),
        ("COMPLETE_SYSTEM_SUMMARY.md", "Complete system overview")
    ]
    
    doc_count = 0
    for filename, description in docs:
        if check_file_exists(filename, description):
            doc_count += 1
    
    # Check existing databases
    print("\n💾 EXISTING DATABASES:")
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    if db_files:
        for db_file in sorted(db_files):
            size_mb = os.path.getsize(db_file) / 1024 / 1024
            print(f"   📄 {db_file:35} - {size_mb:.1f} MB")
    else:
        print("   (No existing databases - will be created when scrapers run)")
    
    # Test Python imports
    print("\n🐍 PYTHON DEPENDENCIES:")
    dependencies = [
        ("requests", "HTTP client library"),
        ("beautifulsoup4", "HTML parsing library"),
        ("sqlite3", "Database library")
    ]
    
    import_count = 0
    for module, description in dependencies:
        try:
            if module == "beautifulsoup4":
                import bs4
            else:
                __import__(module)
            print(f"   ✅ {module:35} - {description}")
            import_count += 1
        except ImportError:
            print(f"   ❌ {module:35} - {description} (MISSING)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY:")
    print(f"   Scrapers: {scraper_count}/6 ✅")
    print(f"   Tools: {tool_count}/4 ✅")
    print(f"   Launchers: {launcher_count}/2 ✅")
    print(f"   Documentation: {doc_count}/2 ✅")
    print(f"   Dependencies: {import_count}/3 ✅")
    
    total_score = scraper_count + tool_count + launcher_count + doc_count + import_count
    max_score = 17
    percentage = (total_score / max_score) * 100
    
    print(f"\n🎯 OVERALL READINESS: {percentage:.1f}% ({total_score}/{max_score})")
    
    if percentage == 100:
        print("🎉 SYSTEM FULLY READY!")
        print("   • All files present and accounted for")
        print("   • All dependencies available")
        print("   • Ready to launch scrapers")
        print("\n💡 NEXT STEPS:")
        print("   1. Run: python test_website_access.py")
        print("   2. Run: run_all_scrapers.bat (Windows) or ./run_all_scrapers.sh (Linux/Mac)")
        print("   3. Monitor progress in real-time")
        print("   4. Consolidate databases when complete")
        
    elif percentage >= 90:
        print("✅ SYSTEM MOSTLY READY!")
        print("   • Minor issues detected")
        print("   • Should work with reduced functionality")
        
    elif percentage >= 75:
        print("⚠️  SYSTEM PARTIALLY READY")
        print("   • Some components missing")
        print("   • May have reduced functionality")
        
    else:
        print("❌ SYSTEM NOT READY")
        print("   • Major components missing")
        print("   • Please check file locations")

    # Quick functionality test
    if scraper_count >= 3 and import_count == 3:
        print(f"\n🧪 QUICK FUNCTIONALITY TEST:")
        try:
            # Test database creation
            test_db = "test_verification.db"
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
            conn.close()
            os.remove(test_db)
            print("   ✅ Database operations working")
            
            # Test HTTP client
            import requests
            print("   ✅ HTTP client ready")
            
            # Test HTML parsing
            from bs4 import BeautifulSoup
            soup = BeautifulSoup("<html><body>test</body></html>", 'html.parser')
            print("   ✅ HTML parsing ready")
            
            print("   🎉 All core functionality verified!")
            
        except Exception as e:
            print(f"   ❌ Functionality test failed: {e}")

if __name__ == "__main__":
    verify_system()