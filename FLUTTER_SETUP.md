# WeighIt Flutter Project Setup Guide

## Overview

This guide explains how to set up the Flutter version of WeighIt as a separate project that reuses the existing Python backend code.

## Architecture

```
weighit_flutter/
├── weighit_api/              # Python FastAPI service
│   ├── main.py              # REST API wrapper
│   ├── requirements.txt     # API dependencies
│   ├── .env.example         # Configuration template
│   └── README.md            # API documentation
│
├── weighit_app/             # Flutter desktop application
│   ├── lib/
│   │   ├── main.dart
│   │   ├── services/
│   │   │   └── api_service.dart
│   │   └── models/
│   └── pubspec.yaml
│
└── README.md                # Main project documentation
```

## Setup Instructions

### 1. Python API Service

The API service is a thin wrapper around the existing weighit Python code. It imports from the original weighit package without modifying it.

**Files to create in `weighit_flutter/weighit_api/`:**

#### `main.py`
```python
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
```

#### `requirements.txt`
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
```

#### `.env.example`
```
# Path to original weighit source code
WEIGHIT_PATH=/home/justin/code/weighit/src

# API server configuration
API_HOST=127.0.0.1
API_PORT=8000

# Database path (uses weighit default if not set)
# DB_PATH=/home/justin/weighit/weigh.db
```

#### `README.md` (for API service)
```markdown
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
```

### 2. Flutter Application

Initialize the Flutter app:

```bash
cd weighit_flutter
flutter create weighit_app
cd weighit_app
```

Add dependencies to `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.0
```

Create the API service client in `lib/services/api_service.dart`:

```dart
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
```

### 3. Running Both Applications

**Terminal 1 - Start Python API:**
```bash
cd weighit_flutter/weighit_api
python main.py
```

**Terminal 2 - Start Flutter App:**
```bash
cd weighit_flutter/weighit_app
flutter run -d linux
```

### 4. Deployment on Tablet

Create a launcher script `weighit_flutter/launch.sh`:
```bash
#!/bin/bash
# Start API service in background
cd "$(dirname "$0")/weighit_api"
python main.py &
API_PID=$!

# Wait for API to start
sleep 2

# Launch Flutter app
cd ../weighit_app
flutter run -d linux --release

# Cleanup on exit
kill $API_PID
```

## Key Benefits

1. **Zero modification** to existing weighit code
2. **Independent development** - can work on Flutter without affecting Streamlit
3. **Shared backend** - both apps use same database and scale driver
4. **Easy testing** - API can be tested independently with curl/Postman
5. **Clean separation** - UI and backend are properly decoupled

## Next Steps

1. Copy the files above into your `weighit_flutter` repository
2. Test the API service locally
3. Build the Flutter UI
4. Deploy to tablet
