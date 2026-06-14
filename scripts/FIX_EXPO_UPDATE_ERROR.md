# Fix Expo "Failed to Download Remote Update" Error

## What I Fixed

Added this to `mobile/app.json`:

```json
"updates": {
  "enabled": false,
  "fallbackToCacheTimeout": 0
}
```

This disables Expo's automatic update system which was causing the error.

## Steps to Apply Fix

### 1. Stop Expo if Running
Press `Ctrl+C` in the Expo terminal

### 2. Clear Cache
```bash
cd mobile
npx expo start -c
```

Wait for it to start, then press `Ctrl+C`

### 3. Delete .expo Folder
```bash
rmdir /s /q .expo
```

### 4. Start Fresh
```bash
npx expo start
```

## What This Does

- **Disables remote updates**: App won't try to download updates from Expo servers
- **Falls back to cache immediately**: Uses local code instead of waiting for updates
- **Fixes "failed to download remote update" error**: No more update errors

## Why This Error Happened

Expo Go tries to download updates from Expo's servers when:
1. You're on a different network
2. Firewall blocks Expo's update servers
3. Network connectivity issues
4. Expo servers are slow/unreachable

By disabling updates, the app runs entirely locally without trying to connect to Expo's servers.

## For Production

When you build a standalone app (APK/IPA), you can re-enable updates by removing this configuration or using EAS Update for over-the-air updates.

---

**Date**: Current session  
**Issue**: Failed to download remote update  
**Solution**: Disabled Expo updates in app.json
