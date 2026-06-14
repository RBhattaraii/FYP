# Scripts & Documentation

This folder contains all helper scripts and documentation files for the PricePilot project.

## 🚀 Quick Start

**Start here:** `START_HERE.md` - Complete 5-step guide to get the app running

## 📜 Scripts

### Firewall & Network
- **fix-firewall.ps1** - Adds Windows Firewall rules for port 8000 (run as Admin)
- **test-network.ps1** - Tests network connectivity and diagnoses issues
- **FIX_FIREWALL.bat** - Batch file to run fix-firewall.ps1

### App Startup
- **START_APP.bat** - Quick start script for backend and mobile
- **FIX_NETWORK_AND_START.bat** - Clears cache and starts app
- **test_all.bat** - Runs all tests

## 📚 Documentation

### Setup & Configuration
- **START_HERE.md** - Main quick start guide (read this first!)
- **CURRENT_STATUS.md** - Complete project status and overview
- **HOW_TO_TEST_NOW.md** - Testing instructions

### Network & Firewall
- **NETWORK_FIX_GUIDE.md** - Detailed network troubleshooting
- **FIREWALL_FIX_GUIDE.md** - Firewall configuration details
- **DYNAMIC_IP_SOLUTION.md** - How auto IP detection works

### Testing & Troubleshooting
- **TESTING_GUIDE.md** - Complete testing guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **COMPLETE_SYSTEM_TEST.md** - System testing checklist
- **TEST_RESULTS_TEMPLATE.md** - Template for test results

### Feature Documentation
- **HOME_SCREEN_READY.md** - Home screen implementation details
- **START_FULL_APP.md** - Full app startup guide

### Issue Fixes
- **FIX_500_ERROR.md** - How to fix 500 errors
- **FIX_TEST_FAILURES.md** - How to fix test failures

### Quick Reference
- **QUICK_START.txt** - Simple text version of quick start

## 🎯 Most Important Files

1. **START_HERE.md** - Start with this
2. **fix-firewall.ps1** - Run this if you have network issues
3. **test-network.ps1** - Run this to diagnose problems
4. **CURRENT_STATUS.md** - See what's complete and what's next

## 💡 Usage

### Fix Network Issues
```powershell
# Run as Administrator
.\fix-firewall.ps1
```

### Test Network
```powershell
.\test-network.ps1
```

### Start App
```bash
# Backend
cd ..\backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --reload

# Mobile (in another terminal)
cd ..\mobile
npx expo start
```

## 📁 Project Structure

```
FYP/
├── scripts/          # This folder - all scripts and docs
├── backend/          # FastAPI backend
├── mobile/           # React Native mobile app
├── docs/             # Architecture documentation
├── .kiro/            # Kiro specs
└── README.md         # Main project README
```

---

**Need help?** Read START_HERE.md or TROUBLESHOOTING.md
