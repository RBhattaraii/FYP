# 📱 How to Test PricePilot Mobile App

## ✅ Current Status

✅ Expo server is running on `http://192.168.1.69:8081`
✅ QR code is displayed in the terminal
✅ react-native-web installed (web errors fixed)
✅ All screens created and ready

## 🎯 Option 1: Test on Your Phone (RECOMMENDED)

### Step 1: Make Sure Both Devices Are on the SAME WiFi

**CRITICAL**: Your phone and computer MUST be on the same WiFi network!

- Computer WiFi: Check your WiFi name
- Phone WiFi: Go to Settings → WiFi → Make sure it's the SAME network

### Step 2: Install Expo Go

- **Android**: [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- **iOS**: [App Store](https://apps.apple.com/app/expo-go/id982107779)

### Step 3: Scan the QR Code

- **Android**: Open Expo Go app → Tap "Scan QR code" → Scan the QR code in the terminal
- **iOS**: Open Camera app → Point at QR code → Tap the notification → Opens in Expo Go

### Step 4: Wait for Bundle to Load

- First time takes 30-60 seconds
- You'll see "Downloading JavaScript bundle"
- Then you should see: **"Login Screen"**

## 🎯 Option 2: Test on Android Emulator

### Requirements
- Android Studio installed
- Android emulator set up

### Steps
```bash
cd mobile
npx expo start --android
```

This will:
1. Start the Expo server
2. Launch Android emulator (if not running)
3. Install Expo Go on emulator
4. Open your app automatically

## 🎯 Option 3: Test on iOS Simulator (Mac Only)

```bash
cd mobile
npx expo start --ios
```

## ⚠️ Troubleshooting

### Error: "Failed to download remote update"

**Cause**: Your phone and computer are on different WiFi networks

**Solution**:
1. Check your computer's WiFi name
2. Check your phone's WiFi name
3. Make sure they're the SAME
4. Restart Expo server: Press `Ctrl+C` then `npx expo start`

### Error: "Network request failed"

**Cause**: Firewall blocking connection

**Solution**:
1. Open Windows Firewall
2. Allow Node.js through firewall
3. Or temporarily disable firewall for testing

### Error: "Unable to connect to Metro"

**Cause**: Port 8081 is blocked or in use

**Solution**:
```bash
# Kill the process on port 8081
netstat -ano | findstr :8081
taskkill /F /PID <PID_NUMBER>

# Restart Expo
cd mobile
npx expo start --clear
```

### Web Version Shows Error (IGNORE THIS)

The web version has errors - **this is normal**. We're building a mobile app, not a web app.

**Don't use the web version** - use your phone or emulator instead.

## 🔧 If Nothing Works: Use Tunnel Mode

If you can't get your phone and computer on the same WiFi, use tunnel mode:

```bash
cd mobile
npx expo start --tunnel
```

This creates a public URL that works on any network, but it's slower.

## 📊 What You Should See

When the app loads successfully on your phone:

1. **First screen**: "Login Screen" text in the center
2. **Navigation**: You can't navigate yet (we'll add that next)

## 🎉 Success Checklist

- [ ] Expo Go installed on phone
- [ ] Phone and computer on same WiFi
- [ ] QR code scanned
- [ ] App loaded (shows "Login Screen")

## 🚀 Next Steps (After Testing Works)

Once you confirm the app loads on your phone:

1. **Implement Login UI** - Add input fields, buttons, styling
2. **Connect to Backend** - Integrate with your FastAPI backend
3. **Add Authentication** - Store JWT tokens in SecureStore
4. **Build Home Screen** - Show product listings
5. **Add Product Search** - Search functionality

## 📝 Current Server Info

- **Metro Bundler**: `exp://192.168.1.69:8081`
- **Web (ignore)**: `http://localhost:8081`
- **Your Local IP**: `192.168.1.69`
- **Backend API**: `http://192.168.1.69:8000`

## 💡 Tips

1. **Keep terminal open** - Don't close the terminal running Expo
2. **Shake phone** - Opens developer menu (reload, debug, etc.)
3. **Hot reload** - Changes auto-reload (no need to restart)
4. **Check terminal** - Errors show in the terminal, not just on phone

## 🎓 For Viva

**Q: Why do we need to be on the same WiFi?**
- Expo Go connects to Metro Bundler running on your computer
- It downloads the JavaScript bundle over the local network
- Same WiFi = same local network = can communicate

**Q: What if we're on different networks?**
- Use tunnel mode (`--tunnel` flag)
- Creates a public URL via ngrok
- Slower but works anywhere

**Q: Why not just build an APK?**
- Expo Go is for development (fast iteration)
- For production, we'll build a standalone APK/IPA
- Command: `eas build --platform android`

---

## 🎯 Try It Now!

1. Make sure your phone and computer are on the **same WiFi**
2. Open **Expo Go** on your phone
3. **Scan the QR code** shown in the terminal
4. Wait for the app to load
5. You should see **"Login Screen"**

**Let me know when you see the Login Screen!** 🎉
