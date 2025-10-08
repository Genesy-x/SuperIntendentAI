# 📱 SuperIntendent - Android Build Instructions

## 🎯 Prerequisites

Before building the APK, make sure you have:

1. **Node.js** installed (v18 or higher)
2. **npm** or **yarn** package manager
3. **Expo account** (free - create at https://expo.dev/signup)

---

## ⚠️ CRITICAL: Project Structure

Your project has this structure:
```
/superintendent/
├── backend/        (Python FastAPI server)
└── frontend/       (Expo React Native app) ← BUILD FROM HERE!
    ├── package.json
    ├── app.json
    ├── eas.json
    └── ... (all app code)
```

**IMPORTANT:** Always run build commands from the `/frontend` directory, NOT the root!

---

## 🚀 Quick Start - Build APK with EAS

### Step 1: Install EAS CLI

Open your terminal/command prompt on your PC and run:

```bash
npm install -g eas-cli
```

### Step 2: Navigate to the Frontend Folder

**This is crucial!** Navigate to the **frontend** folder:

```bash
cd /path/to/superintendent/frontend
```

Or if you're in the root:
```bash
cd frontend
```

### Step 3: Login to Expo

```bash
eas login
```

Enter your Expo credentials (username and password).

### Step 4: Build Android APK

Run this command to build the APK:

```bash
eas build -p android --profile preview
```

**What happens:**
- EAS will upload your code to their build servers
- They'll compile a native Android APK
- Build takes approximately 10-15 minutes
- You'll get a download link when complete

### Step 5: Download & Install

1. Once the build completes, EAS will provide a download link
2. Download the APK to your Android phone (Xperia)
3. Open the APK file to install
4. If prompted, enable "Install from unknown sources" in settings
5. Grant permissions when the app asks (Camera, Contacts, SMS, etc.)

---

## 📦 What's Included

Your SuperIntendent APK will have:

✅ **AI Core:**
- Multi-LLM routing (OpenAI, Gemini, DeepSeek)
- Tharos & SuperIntendent personalities
- Conversation memory & history

✅ **Device Control:**
- SMS/Text messaging
- Phone calls
- Contact access
- Camera integration
- Music/YouTube control

✅ **Required Permissions:**
- Camera
- Contacts (Read/Write)
- SMS (Send/Read)
- Phone calls
- Storage (for photos/media)

---

## 🔧 Alternative: Local Build

If you want to build locally instead of using EAS:

### Prerequisites:
- Android Studio installed
- Android SDK configured
- USB debugging enabled on your phone

### Build Command:
```bash
npx expo run:android
```

This will build and install directly to your connected Android device.

---

## ⚙️ Configuration Files

Your project includes these important files:

- **package.json** - Project dependencies and Expo configuration
- **app.json** - App metadata and permissions
- **eas.json** - Build configuration for EAS
- **.env** - Environment variables (backend URL)

---

## 🐛 Troubleshooting

### Build fails on EAS:
- Check your internet connection
- Ensure you're logged into Expo (`eas whoami`)
- Try `eas build --clear-cache`

### App crashes on device:
- Ensure backend is running and accessible
- Check backend URL in .env file
- Grant all required permissions when prompted

### Permissions not working:
- Go to Android Settings → Apps → SuperIntendent → Permissions
- Manually enable required permissions

---

## 📞 Backend Connection

**Important:** The app connects to your backend API. Make sure:

1. Backend is deployed and accessible from your phone
2. Update `EXPO_PUBLIC_BACKEND_URL` in `.env` file to your backend URL
3. Backend must be HTTPS for production (not localhost)

Current backend URL: `https://personal-ai-os.preview.emergentagent.com`

---

## 🎨 App Details

- **Name:** SuperIntendent
- **Package:** com.superintendent.app
- **Version:** 1.0.0
- **Min Android Version:** Android 6.0+ (API 23)
- **Target:** Latest Android

---

## 📝 Notes

- First build may take 15-20 minutes
- Subsequent builds are faster (5-10 minutes)
- You can track build progress at https://expo.dev/builds
- APK works on any Android device (no Google Play needed)
- You can share the APK link with others

---

## 🚀 Ready to Build?

Run this command to start:

```bash
eas build -p android --profile preview
```

That's it! You'll have your SuperIntendent APK ready to install in 15 minutes! 🎉
