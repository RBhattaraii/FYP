# 📚 PricePilot Documentation Index

## 🚀 Getting Started (Pick One)

### Fastest Way (Recommended)
1. Open `RUN_THIS_NOW.txt` - Visual guide with exact commands
2. Run `.\quick-start.ps1` - One command does everything

### Step-by-Step Way
1. Read `START_HERE.md` - 3-minute quick start guide
2. Follow the instructions exactly

### Test-First Way
1. Run `.\test-everything.ps1` - See what's working
2. Fix issues based on test results
3. Then start the app

---

## 📖 Documentation Files

### Quick Reference
| File | Purpose | When to Use |
|------|---------|-------------|
| `RUN_THIS_NOW.txt` | Visual quick start | First time setup, need simple instructions |
| `START_HERE.md` | Quick start guide | Want step-by-step instructions |
| `SOLUTION_SUMMARY.md` | Complete solution | Need to understand everything |
| `WHAT_I_FIXED.md` | Explanation of fixes | Want to know what changed |
| `COMPLETE_FIX_GUIDE.md` | Detailed troubleshooting | Having specific issues |

### Scripts
| Script | Purpose | Command |
|--------|---------|---------|
| `quick-start.ps1` | One-click start everything | `.\quick-start.ps1` |
| `test-everything.ps1` | System diagnostics | `.\test-everything.ps1` |
| `mobile/fix-and-start.ps1` | Fix mobile app | `cd mobile; .\fix-and-start.ps1` |
| `backend/trigger_scraper.ps1` | Populate database | `cd backend; .\trigger_scraper.ps1` |

---

## 🎯 Common Scenarios

### Scenario 1: First Time Setup
```
1. Read: RUN_THIS_NOW.txt
2. Run: .\quick-start.ps1
3. Done!
```

### Scenario 2: App Not Working
```
1. Run: .\test-everything.ps1
2. Read: START_HERE.md (troubleshooting section)
3. Run: cd mobile; .\fix-and-start.ps1
```

### Scenario 3: "No Products" Error
```
1. Check: curl http://localhost:8000/products/home
2. If empty: cd backend; .\trigger_scraper.ps1
3. Wait 60 seconds, refresh app
```

### Scenario 4: Metro Bundler Error
```
1. Run: cd mobile
2. Run: npx expo start --clear --reset-cache
```

### Scenario 5: Understanding the System
```
1. Read: SOLUTION_SUMMARY.md
2. Read: WHAT_I_FIXED.md
3. Check: Backend/Mobile READMEs for details
```

### Scenario 6: Preparing for Viva
```
1. Read: START_HERE.md (Q&A section at bottom)
2. Read: SOLUTION_SUMMARY.md (Technical Explanation section)
3. Review: Backend/Mobile code comments
```

---

## 🗂️ Project Documentation Structure

```
FYP/
│
├── 📄 INDEX.md (this file)             ← You are here
├── 📄 RUN_THIS_NOW.txt                 ← Quick visual guide
├── 📄 START_HERE.md                    ← Main getting started guide
├── 📄 SOLUTION_SUMMARY.md              ← Complete overview
├── 📄 WHAT_I_FIXED.md                  ← Explanation of changes
├── 📄 COMPLETE_FIX_GUIDE.md            ← Detailed troubleshooting
│
├── 🔧 quick-start.ps1                  ← One-click launcher
├── 🔧 test-everything.ps1              ← Diagnostic tool
│
├── 📁 backend/
│   ├── 📄 README.md                    ← Backend documentation
│   ├── 🔧 trigger_scraper.ps1          ← Populate database
│   └── 🔧 start_backend.bat            ← Start backend
│
└── 📁 mobile/
    ├── 📄 HOW_TO_TEST.md               ← Mobile testing guide
    ├── 📄 MOBILE_SETUP_COMPLETE.md     ← Setup documentation
    ├── 🔧 fix-and-start.ps1            ← Mobile fix script
    └── 🔧 clear-cache-and-start.bat    ← Simple cache clear
```

---

## 🔍 Quick Search

**Looking for...**

### Commands?
- Start everything: `.\quick-start.ps1`
- Test system: `.\test-everything.ps1`
- Fix mobile: `cd mobile; .\fix-and-start.ps1`
- Start backend: `cd backend; uvicorn main:app --host 0.0.0.0 --reload`
- Populate database: `cd backend; .\trigger_scraper.ps1`

### Error Solutions?
- "Unable to resolve": `START_HERE.md` → Problem 1
- "No Products": `START_HERE.md` → Problem 2
- "Unable to connect": `START_HERE.md` → Problem 3
- Backend won't start: `COMPLETE_FIX_GUIDE.md` → Step 3

### Understanding?
- System architecture: `SOLUTION_SUMMARY.md` → Architecture Overview
- Technical details: `SOLUTION_SUMMARY.md` → Technical Explanation
- What changed: `WHAT_I_FIXED.md`
- Viva prep: `START_HERE.md` → For Viva section

### Testing?
- Run tests: `.\test-everything.ps1`
- Backend API: `http://localhost:8000/docs`
- Mobile guide: `mobile/HOW_TO_TEST.md`

---

## 📝 Reading Order (Recommended)

### For Quick Fix:
1. `RUN_THIS_NOW.txt` (1 minute)
2. Run `.\quick-start.ps1`
3. Done!

### For Understanding:
1. `START_HERE.md` (5 minutes)
2. `WHAT_I_FIXED.md` (3 minutes)
3. `SOLUTION_SUMMARY.md` (10 minutes)
4. Backend/Mobile READMEs (as needed)

### For Troubleshooting:
1. `START_HERE.md` → Troubleshooting section
2. `COMPLETE_FIX_GUIDE.md` → Detailed fixes
3. Run `.\test-everything.ps1`
4. Check specific guides based on error

### For Viva Preparation:
1. `START_HERE.md` → "For Viva" section
2. `SOLUTION_SUMMARY.md` → Technical explanations
3. Backend code → Read inline comments
4. Mobile code → Read inline comments

---

## ✅ Checklist

### Initial Setup
- [ ] Read `RUN_THIS_NOW.txt` or `START_HERE.md`
- [ ] Run `.\quick-start.ps1` or follow manual steps
- [ ] Verify backend is running
- [ ] Verify mobile app loads
- [ ] Verify products display

### Before Demo/Viva
- [ ] Read "For Viva" sections in guides
- [ ] Understand tiered search architecture
- [ ] Know why dual database (PostgreSQL + MongoDB)
- [ ] Can explain Metro cache issue and fix
- [ ] Can explain 10.0.2.2 vs LAN IP
- [ ] Test app end-to-end once

### Regular Development
- [ ] Backend running in Terminal 1
- [ ] Mobile Metro running in Terminal 2
- [ ] Know how to trigger scraper
- [ ] Know how to clear cache
- [ ] Can run diagnostic tests

---

## 🆘 Emergency Quick Reference

### App won't start?
```powershell
cd mobile
npx expo start --clear --reset-cache
```

### Backend won't start?
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --reload
```

### No data showing?
```powershell
# Check backend has data
curl http://localhost:8000/products/home

# If empty, populate
cd backend
.\trigger_scraper.ps1
```

### Network issues?
```powershell
# Check firewall
cd mobile
.\fix-firewall.ps1

# Check IP
ipconfig
# Use that IP in mobile device browser: http://YOUR_IP:8000/docs
```

### Complete reset?
```powershell
# Stop everything
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# Clear all caches
cd mobile
rmdir /s /q .expo
rmdir /s /q node_modules\.cache

# Restart fresh
cd ..
.\quick-start.ps1
```

---

## 📞 Support Matrix

| Problem | Solution File | Script to Run |
|---------|---------------|---------------|
| First time setup | `RUN_THIS_NOW.txt` | `.\quick-start.ps1` |
| Metro error | `START_HERE.md` | `cd mobile; .\fix-and-start.ps1` |
| No products | `START_HERE.md` | `cd backend; .\trigger_scraper.ps1` |
| Network issue | `COMPLETE_FIX_GUIDE.md` | `cd mobile; .\fix-firewall.ps1` |
| Need diagnostics | `test-everything.ps1` output | `.\test-everything.ps1` |
| Understanding system | `SOLUTION_SUMMARY.md` | N/A (just read) |

---

## 🎓 Learning Path

### Beginner (Just want it working)
1. `RUN_THIS_NOW.txt`
2. Run `.\quick-start.ps1`
3. Done

### Intermediate (Want to understand)
1. `START_HERE.md`
2. `WHAT_I_FIXED.md`
3. Explore backend/mobile code

### Advanced (Deep technical understanding)
1. `SOLUTION_SUMMARY.md`
2. `COMPLETE_FIX_GUIDE.md`
3. Read all inline code comments
4. Study architecture diagrams

---

## 📊 Success Metrics

After setup, you should have:

✅ Backend running on `http://localhost:8000`  
✅ `/products/home` returns 20+ products  
✅ Mobile app loads without errors  
✅ Home screen shows real products  
✅ Images loading correctly  
✅ Product detail page works  
✅ Search functionality operational  

If ANY metric is ❌, check:
1. `START_HERE.md` troubleshooting section
2. Run `.\test-everything.ps1`
3. Read error-specific guide

---

**You're all set! Start with `RUN_THIS_NOW.txt` and your app will be working in 30 seconds! 🚀**
