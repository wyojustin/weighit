# WeighIt Flutter - Setup Instructions for GitHub Push

## Quick Start (3 Commands)

```bash
cd /home/justin/weighit_flutter
cp /home/justin/code/weighit/setup_flutter_project.sh ./setup.sh && chmod +x setup.sh && ./setup.sh
git add . && git commit -m "Initial project setup" && git push origin main
```

## Detailed Instructions

### Step 1: Copy Setup Script

```bash
cd /home/justin/weighit_flutter
cp /home/justin/code/weighit/setup_flutter_project.sh ./setup.sh
chmod +x setup.sh
```

### Step 2: Run Setup

```bash
./setup.sh
```

This creates:
- `weighit_api/` - Python FastAPI service
  - `main.py` - Complete REST API wrapper
  - `requirements.txt` - Dependencies
  - `.env.example` - Configuration template
  - `README.md` - API documentation
  
- `weighit_app/lib/services/` - Flutter API client
  - `api_service.dart` - Complete API client with models

- `README.md` - Main project documentation
- `.gitignore` - Git ignore rules

### Step 3: Commit and Push

```bash
git add .
git commit -m "Initial project setup with Python API and Flutter app

- Added Python FastAPI service (weighit_api/)
- Added Flutter app structure (weighit_app/)
- Includes API client and models
- Complete documentation and setup instructions"

git push origin main
```

### Step 4: Clone on Tablet

On your tablet:

```bash
git clone git@github.com:wyojustin/weighit_flutter.git
cd weighit_flutter
```

### Step 5: Initialize Flutter (on Tablet)

```bash
cd weighit_app
flutter create . --platforms=linux
```

Update `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.0
```

Then:
```bash
flutter pub get
```

### Step 6: Test API Service (on Tablet)

```bash
cd ../weighit_api
pip install -r requirements.txt
python main.py
```

Visit http://127.0.0.1:8000/docs to see API documentation.

## What You Get

### Complete Python API Service
- ✅ FastAPI wrapper around existing weighit backend
- ✅ Imports from `/home/justin/code/weighit/src` (no modifications needed)
- ✅ All endpoints: scale reading, logging, sources, types, totals, history, undo/redo
- ✅ Auto-generated API docs at `/docs`

### Flutter API Client
- ✅ Complete `ApiService` class
- ✅ Models for `ScaleReading` and `FoodType`
- ✅ All methods implemented: getScaleReading, logEntry, getSources, getTypes, getTodayTotals, undo, redo

### Documentation
- ✅ Main README with architecture overview
- ✅ API service README with setup instructions
- ✅ Complete code examples

## Architecture

```
┌─────────────────────────────────────┐
│      Flutter App (weighit_app)      │
│   - Native Linux UI                 │
│   - Touch-optimized                 │
│   - Better performance              │
└──────────────┬──────────────────────┘
               │ HTTP REST API
               │ (localhost:8000)
┌──────────────▼──────────────────────┐
│   Python API Service (weighit_api)  │
│   - FastAPI wrapper                 │
│   - Imports from weighit package    │
└──────────────┬──────────────────────┘
               │ Direct imports
┌──────────────▼──────────────────────┐
│   Existing WeighIt Backend          │
│   /home/justin/code/weighit/src     │
│   - scale_backend.py (USB HID)      │
│   - logger_core.py (business logic) │
│   - db.py (SQLite database)         │
└─────────────────────────────────────┘
```

## Key Benefits

1. **Zero Modification**: Original weighit code stays completely untouched
2. **Coexistence**: Both Streamlit and Flutter versions can run
3. **Shared Backend**: Same database, same scale driver, same business logic
4. **Clean Separation**: UI and backend properly decoupled via REST API
5. **Easy Testing**: API can be tested independently
6. **Native Performance**: Flutter provides better touch support and performance

## Files Created

```
weighit_flutter/
├── .gitignore
├── README.md
├── setup.sh
├── weighit_api/
│   ├── .env.example
│   ├── README.md
│   ├── main.py              (200+ lines, complete API)
│   └── requirements.txt
└── weighit_app/
    └── lib/
        └── services/
            └── api_service.dart  (100+ lines, complete client)
```

## Next Steps After Push

1. Clone on tablet
2. Initialize Flutter app
3. Start building the UI
4. The API client is ready to use - just import and call methods

All the backend work is done! You can focus entirely on building a beautiful Flutter UI.
