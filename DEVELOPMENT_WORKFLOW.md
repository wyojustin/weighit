# WeighIt Flutter - Development Workflow

## Summary

**Develop on laptop, deploy compiled binary to tablet.** No Flutter installation needed on tablet!

## On Your Laptop

### 1. Initial Setup (One Time)

```bash
# Run the setup script
/home/justin/code/weighit/one_command_setup.sh

# Initialize Flutter app
cd /home/justin/code/weighit_flutter/weighit_app
flutter create . --platforms=linux

# Update pubspec.yaml with dependencies:
# dependencies:
#   http: ^1.1.0
#   provider: ^6.1.0

flutter pub get
```

### 2. Development Cycle

```bash
# Develop and test locally
cd /home/justin/code/weighit_flutter/weighit_app
flutter run -d linux

# Make changes, test, repeat...

# When ready, build release binary
flutter build linux --release

# Commit and push code
git add .
git commit -m "Your changes"
git push
```

### 3. Deploy to Tablet

```bash
# Deploy everything to tablet
/home/justin/code/weighit/deploy_to_tablet.sh [tablet-hostname] [username]

# Example:
/home/justin/code/weighit/deploy_to_tablet.sh tablet.local justin
```

## On Your Tablet

### First Time Setup

The deploy script handles everything, but manually:

```bash
# The deployment creates:
~/weighit_flutter/
├── weighit_api/          # Python API service
└── weighit_app/bundle/   # Compiled Flutter app (no Flutter SDK needed!)

# Install Python dependencies (one time)
cd ~/weighit_flutter/weighit_api
pip install -r requirements.txt
```

### Running the App

**Option 1: Use launcher script**
```bash
cd ~/weighit_flutter
./launch.sh
```

**Option 2: Manual**
```bash
# Terminal 1: Start API
cd ~/weighit_flutter/weighit_api
python main.py

# Terminal 2: Start app
cd ~/weighit_flutter/weighit_app/bundle
./weighit_app
```

## What Gets Deployed

**From laptop to tablet:**
- ✅ Compiled Flutter binary (no source code, no Flutter SDK needed)
- ✅ Python API service
- ✅ Launcher script

**NOT deployed:**
- ❌ Flutter SDK
- ❌ Dart source code
- ❌ Build tools

## File Sizes

- Flutter binary bundle: ~50-100 MB (includes all dependencies)
- Python API: <1 MB
- Total deployment: ~100 MB

## Benefits

✅ **No Flutter on tablet** - Just run the binary  
✅ **Faster development** - Use laptop's better tools  
✅ **Easy updates** - Just re-run deploy script  
✅ **Smaller footprint** - Tablet only needs Python  
✅ **Better IDE** - Develop with VS Code/Android Studio on laptop  

## Scripts Created

- `one_command_setup.sh` - Initial project setup and git push
- `deploy_to_tablet.sh` - Deploy compiled app to tablet
- `tablet_launcher.sh` - Simple launcher for tablet (auto-deployed)

## Typical Workflow

1. **Laptop**: Develop Flutter UI
2. **Laptop**: Test locally with `flutter run`
3. **Laptop**: Build release with `flutter build linux --release`
4. **Laptop**: Deploy with `./deploy_to_tablet.sh`
5. **Tablet**: Run with `./launch.sh`
6. **Repeat**: Make changes on laptop, redeploy

## Architecture

```
Laptop (Development):
├── weighit_flutter/
│   ├── weighit_api/              # Python API (develop here)
│   └── weighit_app/              # Flutter app (develop here)
│       ├── lib/                  # Source code
│       └── build/linux/x64/release/bundle/  # Compiled binary
│
└── Deploy to tablet ──────────────────────────┐
                                               │
Tablet (Production):                           │
├── weighit/                                   │
│   └── src/weigh/  ← API imports from here   │
│                                              │
└── weighit_flutter/  ← Deployed here ─────────┘
    ├── weighit_api/              # Python API service
    ├── weighit_app/bundle/       # Compiled binary only
    └── launch.sh                 # Launcher script
```

## Next Steps

1. Run `one_command_setup.sh` to create and push the project
2. Develop the Flutter UI on your laptop
3. Test locally
4. Deploy to tablet when ready
5. No Flutter installation needed on tablet!
