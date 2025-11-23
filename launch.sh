#!/bin/bash

# Show a notification that we're starting
notify-send "WeighIt" "Starting Food Pantry Scale...(10 seconds)" -t 10000 -i /home/alarm/weighit/src/weigh/assets/scale_icon.png

set -e

# Activate conda environment
source /home/alarm/miniconda3/bin/activate foodlog

# Set Python path
export PYTHONPATH=/home/alarm/weighit/src:$PYTHONPATH

# Change to weighit directory
cd /home/alarm/weighit

# Start Streamlit with performance flags
streamlit run src/weigh/app.py \
  --server.port=8501 \
  --server.headless=true \
  --server.runOnSave=false \
  --server.fileWatcherType=none \
  --browser.gatherUsageStats=false &

# Wait for Streamlit to be ready (you can adjust this timing)
sleep 3

# Launch Chromium with performance flags
/usr/bin/chromium --kiosk --app=http://localhost:8501 \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-dev-shm-usage \
  --disable-extensions \
  --disable-sync \
  --no-first-run \
  --fast \
  --fast-start
