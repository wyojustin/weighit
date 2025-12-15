#!/bin/bash

# Parse command line arguments for browser selection
BROWSER="firefox"  # Default to firefox to avoid chromium library issues

while [[ $# -gt 0 ]]; do
    case $1 in
        --browser|-b)
            BROWSER="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--browser BROWSER]"
            echo ""
            echo "Options:"
            echo "  --browser, -b    Browser to use (firefox, epiphany, chromium)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --browser firefox"
            echo "  $0 --browser epiphany"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate browser choice
case $BROWSER in
    firefox|epiphany|chromium)
        # Valid browser
        ;;
    *)
        echo "Error: Unsupported browser '$BROWSER'"
        echo "Supported browsers: firefox, epiphany, chromium"
        exit 1
        ;;
esac

# Show a notification that we're starting
notify-send "WeighIt" "Starting Food Pantry Scale...(10 seconds) with $BROWSER" -t 10000 -i /home/alarm/weighit/src/weigh/assets/scale_icon.png

set -e

# Activate conda environment
source /home/alarm/miniconda3/bin/activate foodlog

# Set Python path
export PYTHONPATH=/home/alarm/weighit/src:$PYTHONPATH

# Performance tuning environment variables for PineTab2
# WEIGHIT_WEIGHT_UPDATE_INTERVAL: How often weight display updates (in seconds)
#   - Set to 3 for moderate performance (default)
#   - Set to 5 for better performance
#   - Set to 0 to disable auto-update entirely (best performance)
export WEIGHIT_WEIGHT_UPDATE_INTERVAL="${WEIGHIT_WEIGHT_UPDATE_INTERVAL:-3}"

# WEIGHIT_CACHE_TTL: How long to cache database queries (in seconds)
#   - Higher = better performance, slightly less fresh data
export WEIGHIT_CACHE_TTL="${WEIGHIT_CACHE_TTL:-5.0}"

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

# Launch browser based on selection
case $BROWSER in
    firefox)
        firefox --kiosk http://localhost:8501 &
        ;;
    epiphany)
        epiphany --application-mode http://localhost:8501 &
        ;;
    chromium)
        /usr/bin/chromium --kiosk --app=http://localhost:8501 \
          --disable-gpu \
          --disable-software-rasterizer \
          --disable-dev-shm-usage \
          --disable-extensions \
          --disable-sync \
          --no-first-run \
          --fast \
          --fast-start &
        ;;
esac

