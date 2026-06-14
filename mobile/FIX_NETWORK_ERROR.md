# Fix Network Error - Home Screen Testing

## Problem
Expo is showing "Network request failed" error trying to connect to login endpoint, even though we redirected to home screen.

## Root Cause
The app might be:
1. Cached with old navigation state
2. Still trying to load login screen first
3. Has some auto-login logic running

## Solution

### Option 1: Clear Cache and Restart (Recommended)
```bash
cd mobile

# Stop the current Expo server (Ctrl+C)

# Clear cache and restart
expo start -c
```

Then scan the QR code again on your phone.

### Option 2: Force Reload on Phone
1. Shake your phone to open Expo menu
2. Tap "Reload"
3. If that doesn't work, tap "Go to Home"

### Option 3: Restart Expo Go App
1. Close Expo Go app completely
2. Reopen Expo Go
3. Scan QR code again

### Option 4: Check App Layout
The app should load directly to home screen without touching backend. If it's still trying to login, we need to check the navigation logic.

## Verification

After clearing cache, you should see:
- ✅ App loads directly to home screen
- ✅ No network requests to backend
- ✅ Dummy data displays correctly
- ✅ No login screen appears

## If Still Not Working

### Check 1: Verify Index Route
The `mobile/app/index.tsx` should redirect to `/(tabs)/home`:

```typescript
import { Redirect } from 'expo-router';

export default function Index() {
  return <Redirect href="/(tabs)/home" />;
}
```

### Check 2: Verify No Auto-Login Logic
Check if there's any useEffect or navigation logic in:
- `mobile/app/_layout.tsx`
- `mobile/app/(tabs)/_layout.tsx`
- `mobile/app/(tabs)/home.tsx`

### Check 3: Backend Not Needed
The home screen uses dummy data only. Backend doesn't need to be running for testing the home screen.

## Quick Test Commands

```bash
# Terminal 1: Start Expo (no backend needed)
cd mobile
expo start -c

# Scan QR code on phone
# App should load directly to home screen
```

## Expected Behavior

1. **App starts** → Shows splash screen
2. **Loads** → Goes directly to home screen (no login)
3. **Home screen** → Shows dummy data
4. **No network calls** → Everything works offline

## Troubleshooting

### Error: "Network request failed"
- **Cause**: App is trying to reach backend
- **Fix**: Clear cache with `expo start -c`

### Error: "Unable to connect to server"
- **Cause**: Old navigation state cached
- **Fix**: Reload app on phone (shake → reload)

### App shows login screen
- **Cause**: Index redirect not working
- **Fix**: Check `app/index.tsx` file

### Blank screen
- **Cause**: Navigation error
- **Fix**: Check console for errors, restart Expo

## Success Checklist

- [ ] Expo server started with `-c` flag
- [ ] Scanned QR code on phone
- [ ] App loaded to home screen (not login)
- [ ] Dummy products visible
- [ ] Can scroll and interact
- [ ] No network errors in console

## Notes

- **Backend not required** for home screen testing
- **Dummy data** is hardcoded in `home.tsx`
- **No API calls** are made from home screen
- **Offline mode** works perfectly

---

**Quick Fix**: Run `expo start -c` and scan QR code again!
