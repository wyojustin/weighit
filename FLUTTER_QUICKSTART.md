# WeighIt Flutter - Quick Setup Instructions

## Step 1: Run the Setup Script

I've created a setup script that will generate all the necessary files for your weighit_flutter project.

```bash
cd /home/justin/weighit_flutter
cp /home/justin/code/weighit/setup_flutter_project.sh ./setup.sh
chmod +x setup.sh
./setup.sh
```

This will create:
```
weighit_flutter/
├── weighit_api/
│   ├── main.py              # FastAPI service
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Configuration template
│   └── README.md            # API documentation
├── weighit_app/
│   └── lib/
│       └── services/
│           └── api_service.dart  # Flutter API client
├── README.md                # Main project docs
└── .gitignore              # Git ignore rules
```

## Step 2: Initialize Flutter App

```bash
cd /home/justin/weighit_flutter/weighit_app
flutter create .
```

Then update `pubspec.yaml` to add these dependencies:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.0
```

Run:
```bash
flutter pub get
```

## Step 3: Test the API Service

```bash
cd /home/justin/weighit_flutter/weighit_api
pip install -r requirements.txt
python main.py
```

Visit http://127.0.0.1:8000/docs to see the API documentation.

## Step 4: Commit and Push to GitHub

```bash
cd /home/justin/weighit_flutter
git add .
git commit -m "Initial project setup with Python API and Flutter app structure"
git push origin main
```

## Step 5: Clone on Tablet

On your tablet:
```bash
git clone git@github.com:wyojustin/weighit_flutter.git
cd weighit_flutter
```

Then follow steps 2-3 above to set up Flutter and test the API.

## What's Included

### Python API Service (`weighit_api/`)
- **main.py**: Complete FastAPI wrapper around your existing weighit backend
- Imports from `/home/justin/code/weighit/src` (configurable via `WEIGHIT_PATH` env var)
- Exposes all necessary endpoints for the Flutter app
- Handles scale communication, logging, sources, types, totals, history

### Flutter App (`weighit_app/`)
- **api_service.dart**: Complete API client with all methods
- Models for ScaleReading and FoodType
- Ready to use in your Flutter UI

### Key Features
- ✅ Zero changes to existing weighit code
- ✅ Both Streamlit and Flutter can coexist
- ✅ Shared database and scale driver
- ✅ Clean REST API architecture
- ✅ Ready for tablet deployment

## Next Steps

After setup, you can start building the Flutter UI. The API service provides everything you need:
- Real-time scale readings
- Logging donations
- Getting sources and types
- Daily totals
- History
- Undo/redo functionality
