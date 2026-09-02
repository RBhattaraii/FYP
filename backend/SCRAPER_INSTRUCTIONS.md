# 🚀 ENHANCED SCRAPER SYSTEM - INSTRUCTIONS

## Overview
This enhanced scraper system is designed to collect 100,000+ products from 6 Nepalese e-commerce platforms:
- **Jeevee.com.np** - General marketplace
- **CGDigital.com.np** - Electronics specialist
- **Hukut.com** - General marketplace
- **OlizStore.com** - Fashion & lifestyle
- **Better.com.np** - General products
- **HardwarePasal.com** - Hardware & electronics

## 📁 Files Overview

### Individual Scrapers (Enhanced V2.0)
- `enhanced_jeevee_scraper.py` - Jeevee scraper with rate limiting bypass
- `enhanced_cgdigital_scraper.py` - CGDigital with electronics focus
- `enhanced_hukut_scraper.py` - Hukut general marketplace scraper
- `enhanced_oliz_scraper.py` - Oliz fashion & lifestyle scraper  
- `enhanced_better_scraper.py` - Better general products scraper
- `enhanced_hardwarepasal_scraper.py` - HardwarePasal hardware scraper

### Management Scripts
- `scraper_monitor.py` - Real-time progress monitoring dashboard
- `enhanced_master_consolidator.py` - Combines all databases into master
- `run_all_scrapers.bat` - Windows launcher (all scrapers at once)
- `run_all_scrapers.sh` - Linux/Mac launcher (all scrapers at once)

## 🚀 Quick Start

### Option 1: Launch All Scrapers (Recommended)

**Windows:**
```bash
# Double-click or run:
run_all_scrapers.bat
```

**Linux/Mac:**
```bash
chmod +x run_all_scrapers.sh
./run_all_scrapers.sh
```

This will:
- ✅ Open 6 scraper windows (one per platform)
- ✅ Open 1 monitor window (real-time progress)
- ✅ Run all scrapers in parallel until completion

### Option 2: Manual Individual Launch

Open **7 separate terminals** and run:

```bash
# Terminal 1 - Jeevee
python enhanced_jeevee_scraper.py

# Terminal 2 - CGDigital  
python enhanced_cgdigital_scraper.py

# Terminal 3 - Hukut
python enhanced_hukut_scraper.py

# Terminal 4 - Oliz
python enhanced_oliz_scraper.py

# Terminal 5 - Better
python enhanced_better_scraper.py

# Terminal 6 - HardwarePasal
python enhanced_hardwarepasal_scraper.py

# Terminal 7 - Monitor
python scraper_monitor.py
```

## 📊 Monitoring Progress

### Real-time Dashboard
The monitor shows:
- ✅ Products scraped per platform
- ⚡ Scraping rates (products/hour)
- 📈 Progress toward 100k target
- 🕐 Latest activity timestamps
- ⚠️ Health warnings and status

### Manual Progress Check
```bash
# Quick stats
python scraper_monitor.py --once

# Export JSON report
python scraper_monitor.py --export

# Just summary numbers
python scraper_monitor.py --summary
```

## 💾 Database Management

### Individual Databases
Each scraper creates its own database:
- `jeevee_enhanced.db`
- `cgdigital_enhanced.db`  
- `hukut_enhanced.db`
- `oliz_enhanced.db`
- `better_enhanced.db`
- `hardwarepasal_enhanced.db`

### Consolidate Into Master Database
```bash
# Merge all individual databases into master
python enhanced_master_consolidator.py
```

This creates: `master_enhanced_products.db` with all unique products.

## 🔧 Enhanced Features

### Rate Limiting Bypass
- ✅ Exponential backoff retry logic
- ✅ User-Agent rotation
- ✅ Smart delay randomization
- ✅ Session reset on blocks
- ✅ Multiple URL pattern attempts

### Comprehensive Coverage
- ✅ 50-150 search terms per platform
- ✅ Multi-page exploration (up to 50 pages)
- ✅ Multiple CSS selector strategies
- ✅ Brand detection and categorization
- ✅ Price validation and filtering

### Error Recovery
- ✅ Automatic retry on failures
- ✅ Graceful error handling
- ✅ Progress preservation
- ✅ Session restart capability

## 📈 Expected Performance

### Typical Results per Platform:
- **Jeevee**: 8,000-15,000 products
- **CGDigital**: 5,000-12,000 products  
- **Hukut**: 6,000-10,000 products
- **Oliz**: 4,000-8,000 products
- **Better**: 3,000-6,000 products
- **HardwarePasal**: 4,000-7,000 products

### Estimated Runtime:
- **Fast**: 2-4 hours (good network, minimal rate limiting)
- **Normal**: 4-6 hours (average conditions)
- **Slow**: 6-12 hours (heavy rate limiting, network issues)

## 🚨 Troubleshooting

### Scraper Stopped/Slow?
1. Check monitor for rate limiting warnings
2. Wait for automatic retry (up to 10 minutes)
3. Restart individual scraper if needed

### No Products Found?
1. Website might be down - check manually
2. CSS selectors might have changed - site update
3. IP might be blocked - wait 30+ minutes

### Database Errors?
1. Ensure sufficient disk space (1-2 GB)
2. Close other database connections
3. Check file permissions

### Monitor Not Updating?
1. Check if scrapers are actually running
2. Verify database files exist and are growing
3. Restart monitor if needed

## 💡 Pro Tips

1. **Run overnight** - Scrapers can run for many hours
2. **Monitor disk space** - Databases can get large (100MB-1GB each)
3. **Don't close terminals** - Each scraper runs independently
4. **Check progress regularly** - Use monitor every few hours
5. **Consolidate periodically** - Run consolidator to check total progress
6. **Be patient** - Quality data takes time due to rate limiting

## 🎯 Success Metrics

### Target: 100,000+ Products
- ✅ **50,000+**: Good progress, continue scraping
- ✅ **75,000+**: Excellent, near target
- ✅ **100,000+**: Target achieved! 🎉

### Quality Indicators:
- ✅ Unique product URLs (no duplicates)
- ✅ Valid prices (> Rs. 50)
- ✅ Proper titles (> 5 characters)  
- ✅ Multiple brands represented
- ✅ Various categories covered

## 🔗 Integration with Backend API

Once scraping is complete:
1. Use `master_enhanced_products.db` as data source
2. Update FastAPI endpoints to read from new database
3. Products will appear in mobile app automatically
4. No code changes needed - just database swap

---

**Happy Scraping!** 🚀

*For issues or questions, check the terminal outputs and monitor dashboard first.*