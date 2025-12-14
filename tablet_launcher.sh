#!/bin/bash
# Launcher script for tablet
# Copy this to ~/weighit_flutter/ on the tablet

cd "$(dirname "$0")"

echo "Starting WeighIt Flutter..."

# Start Python API in background
cd weighit_api
python main.py &
API_PID=$!

# Wait for API to start
sleep 2

# Launch Flutter app
cd ../weighit_app/bundle
./weighit_app

# Cleanup on exit
kill $API_PID 2>/dev/null
