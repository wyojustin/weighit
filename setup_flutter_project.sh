#!/bin/bash
# Script to set up weighit_flutter project structure
# Run this from /home/justin/weighit_flutter

set -e

echo "Setting up WeighIt Flutter project structure..."

# Create directory structure
mkdir -p weighit_api
mkdir -p weighit_app/lib/services
mkdir -p weighit_app/lib/models

# Create Python API main.py
cat > weighit_api/main.py << 'EOF'
#!/usr/bin/env python3
"""
WeighIt FastAPI Service

Thin REST API wrapper around the existing weighit Python backend.
Imports from the original weighit package without modification.
"""
import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add the original weighit package to path
WEIGHIT_PATH = os.getenv('WEIGHIT_PATH', '/home/justin/code/weighit/src')
sys.path.insert(0, WEIGHIT_PATH)

# Import from existing weighit package
from weigh.scale_backend import DymoHIDScale, ScaleReading
from weigh import logger_core, db

# Initialize FastAPI
app = FastAPI(title="WeighIt API", version="1.0.0")

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scale (singleton)
scale: Optional[DymoHIDScale] = None

@app.on_event("startup")
async def startup_event():
    """Initialize scale connection on startup"""
    global scale
    try:
        scale = DymoHIDScale()
        print("✓ Scale initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize scale: {e}")
        scale = None

@app.on_event("shutdown")
async def shutdown_event():
    """Close scale connection on shutdown"""
    global scale
    if scale:
        scale.close()

# Pydantic models for request/response
class LogEntryRequest(BaseModel):
    source: str
    type: str
    weight_lb: float
    temp_pickup_f: Optional[float] = None
    temp_dropoff_f: Optional[float] = None

class ScaleReadingResponse(BaseModel):
    value: float
    unit: str
    is_stable: bool
    available: bool

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "WeighIt API",
        "status": "running",
        "scale_connected": scale is not None
    }

@app.get("/scale/reading", response_model=ScaleReadingResponse)
async def get_scale_reading():
    """Get current scale reading"""
    if not scale:
        return ScaleReadingResponse(
            value=0.0,
            unit="lb",
            is_stable=False,
            available=False
        )
    
    reading = scale.get_latest()
    if not reading:
        return ScaleReadingResponse(
            value=0.0,
            unit="lb",
            is_stable=False,
            available=False
        )
    
    return ScaleReadingResponse(
        value=reading.value,
        unit=reading.unit,
        is_stable=reading.is_stable,
        available=True
    )

@app.get("/scale/stable")
async def get_stable_reading(timeout: float = 2.0):
    """Wait for stable reading (for LOG button)"""
    if not scale:
        raise HTTPException(status_code=503, detail="Scale not available")
    
    reading = scale.read_stable_weight(timeout_s=timeout)
    if not reading:
        raise HTTPException(status_code=408, detail="Timeout waiting for stable reading")
    
    return {
        "value": reading.value,
        "unit": reading.unit,
        "is_stable": reading.is_stable
    }

@app.get("/sources")
async def get_sources():
    """Get list of donation sources"""
    sources = logger_core.get_sources_dict()
    return {"sources": list(sources.keys())}

@app.get("/types")
async def get_types():
    """Get list of food types with metadata"""
    types = logger_core.get_types_dict()
    return {
        "types": [
            {
                "name": name,
                "requires_temp": info["requires_temp"],
                "sort_order": info["sort_order"]
            }
            for name, info in types.items()
        ]
    }

@app.post("/log")
async def log_entry(entry: LogEntryRequest):
    """Log a donation entry"""
    try:
        logger_core.log_entry(
            weight_lb=entry.weight_lb,
            source=entry.source,
            type_=entry.type,
            temp_pickup_f=entry.temp_pickup_f,
            temp_dropoff_f=entry.temp_dropoff_f
        )
        return {"status": "success", "message": "Entry logged"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/totals/today")
async def get_today_totals(source: Optional[str] = None):
    """Get today's totals by type"""
    totals = logger_core.totals_today_weight_per_type(source=source)
    total_weight = sum(totals.values())
    return {
        "totals_by_type": totals,
        "total_weight": total_weight,
        "date": datetime.now().date().isoformat()
    }

@app.get("/history/recent")
async def get_recent_history(limit: int = 15, source: Optional[str] = None):
    """Get recent donation entries"""
    entries = logger_core.get_recent_entries(limit=limit, source=source)
    return {"entries": entries}

@app.post("/undo")
async def undo_last():
    """Undo last entry"""
    entry_id = logger_core.undo_last_entry()
    if entry_id:
        return {"status": "success", "undone_id": entry_id}
    else:
        raise HTTPException(status_code=404, detail="No entry to undo")

@app.post("/redo")
async def redo_last():
    """Redo last undone entry"""
    entry_id = logger_core.redo_last_entry()
    if entry_id:
        return {"status": "success", "redone_id": entry_id}
    else:
        raise HTTPException(status_code=404, detail="No entry to redo")

if __name__ == "__main__":
    # Run with: python main.py
    uvicorn.run(app, host="127.0.0.1", port=8000)
EOF

# Create Python API requirements.txt
cat > weighit_api/requirements.txt << 'EOF'
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
EOF

# Create .env.example
cat > weighit_api/.env.example << 'EOF'
# Path to original weighit source code
WEIGHIT_PATH=/home/justin/code/weighit/src

# API server configuration
API_HOST=127.0.0.1
API_PORT=8000

# Database path (uses weighit default if not set)
# DB_PATH=/home/justin/weighit/weigh.db
EOF

# Create API README
cat > weighit_api/README.md << 'EOF'
# WeighIt API Service

REST API wrapper for the WeighIt Python backend.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment (optional):
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. Run the service:
   ```bash
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

## API Documentation

Once running, visit:
- Interactive docs: http://127.0.0.1:8000/docs
- Alternative docs: http://127.0.0.1:8000/redoc

## Endpoints

- `GET /` - Health check
- `GET /scale/reading` - Current scale reading
- `GET /scale/stable` - Wait for stable reading
- `GET /sources` - List donation sources
- `GET /types` - List food types
- `POST /log` - Log donation entry
- `GET /totals/today` - Today's totals
- `GET /history/recent` - Recent entries
- `POST /undo` - Undo last entry
- `POST /redo` - Redo last undo
EOF

# Create Flutter API service
cat > weighit_app/lib/services/api_service.dart << 'EOF'
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;

  ApiService({this.baseUrl = 'http://127.0.0.1:8000'});

  Future<ScaleReading> getScaleReading() async {
    final response = await http.get(Uri.parse('$baseUrl/scale/reading'));
    if (response.statusCode == 200) {
      return ScaleReading.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to get scale reading');
  }

  Future<void> logEntry({
    required String source,
    required String type,
    required double weight,
    double? tempPickup,
    double? tempDropoff,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/log'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'source': source,
        'type': type,
        'weight_lb': weight,
        'temp_pickup_f': tempPickup,
        'temp_dropoff_f': tempDropoff,
      }),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to log entry');
    }
  }

  Future<List<String>> getSources() async {
    final response = await http.get(Uri.parse('$baseUrl/sources'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['sources']);
    }
    throw Exception('Failed to get sources');
  }

  Future<List<FoodType>> getTypes() async {
    final response = await http.get(Uri.parse('$baseUrl/types'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['types'] as List)
          .map((t) => FoodType.fromJson(t))
          .toList();
    }
    throw Exception('Failed to get types');
  }

  Future<Map<String, dynamic>> getTodayTotals({String? source}) async {
    final uri = source != null
        ? Uri.parse('$baseUrl/totals/today?source=$source')
        : Uri.parse('$baseUrl/totals/today');
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to get totals');
  }

  Future<void> undo() async {
    final response = await http.post(Uri.parse('$baseUrl/undo'));
    if (response.statusCode != 200) {
      throw Exception('Failed to undo');
    }
  }

  Future<void> redo() async {
    final response = await http.post(Uri.parse('$baseUrl/redo'));
    if (response.statusCode != 200) {
      throw Exception('Failed to redo');
    }
  }
}

class ScaleReading {
  final double value;
  final String unit;
  final bool isStable;
  final bool available;

  ScaleReading({
    required this.value,
    required this.unit,
    required this.isStable,
    required this.available,
  });

  factory ScaleReading.fromJson(Map<String, dynamic> json) {
    return ScaleReading(
      value: json['value'].toDouble(),
      unit: json['unit'],
      isStable: json['is_stable'],
      available: json['available'],
    );
  }
}

class FoodType {
  final String name;
  final bool requiresTemp;
  final int sortOrder;

  FoodType({
    required this.name,
    required this.requiresTemp,
    required this.sortOrder,
  });

  factory FoodType.fromJson(Map<String, dynamic> json) {
    return FoodType(
      name: json['name'],
      requiresTemp: json['requires_temp'],
      sortOrder: json['sort_order'],
    );
  }
}
EOF

# Create main README
cat > README.md << 'EOF'
# WeighIt Flutter

Flutter-based UI for the WeighIt food pantry scale application.

## Architecture

This project consists of two components:

1. **weighit_api/** - Python FastAPI service that wraps the existing weighit backend
2. **weighit_app/** - Flutter desktop application (UI)

The Flutter app communicates with the Python API service via REST API calls over localhost.

## Benefits

- ✅ **Zero modification** to existing weighit Python code
- ✅ **Independent development** - work on Flutter without affecting Streamlit version
- ✅ **Shared backend** - both apps use same database and scale driver
- ✅ **Native performance** - Flutter provides better touch support and performance
- ✅ **Clean separation** - UI and backend are properly decoupled

## Setup

### 1. Python API Service

```bash
cd weighit_api
pip install -r requirements.txt
python main.py
```

The API will be available at http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

### 2. Flutter Application

First, initialize the Flutter app (one-time setup):

```bash
cd weighit_app
flutter create .
```

Add dependencies to `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.0
```

Then run:
```bash
flutter pub get
flutter run -d linux
```

## Running Both Together

**Terminal 1 - Start API:**
```bash
cd weighit_api
python main.py
```

**Terminal 2 - Start Flutter:**
```bash
cd weighit_app
flutter run -d linux
```

## Deployment

For production deployment on the tablet, you can create a launcher script that starts both services.

## Development

The API service imports from the original weighit package at `/home/justin/code/weighit/src`. This path can be configured via the `WEIGHIT_PATH` environment variable.

## Next Steps

1. Test the API service locally
2. Build the Flutter UI components
3. Implement the main app screens
4. Package for deployment on tablet
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
*.egg-info/
dist/
build/

# Flutter
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
build/
*.iml
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db
EOF

echo "✓ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. cd weighit_app && flutter create ."
echo "2. Update weighit_app/pubspec.yaml with dependencies"
echo "3. Test the API: cd weighit_api && python main.py"
echo "4. Run Flutter app: cd weighit_app && flutter run -d linux"
EOF

chmod +x setup.sh

echo "✓ Setup script created!"
echo ""
echo "To set up your weighit_flutter project:"
echo "1. cd /home/justin/weighit_flutter"
echo "2. Copy this script there and run: ./setup.sh"
