#!/bin/bash
# Deploy WeighIt Flutter to tablet
# Run this from your laptop after building the Flutter app

set -e

TABLET_HOST="${1:-tablet.local}"  # Default to tablet.local, or pass as argument
TABLET_USER="${2:-justin}"

echo "================================================"
echo "WeighIt Flutter - Deploy to Tablet"
echo "================================================"
echo ""
echo "Tablet: $TABLET_USER@$TABLET_HOST"
echo ""

# Check if Flutter app is built
if [ ! -d "/home/justin/code/weighit_flutter/weighit_app/build/linux/x64/release/bundle" ]; then
    echo "Error: Flutter app not built yet!"
    echo "Please run: cd /home/justin/code/weighit_flutter/weighit_app && flutter build linux --release"
    exit 1
fi

echo "Step 1: Creating deployment package..."
cd /home/justin/code/weighit_flutter/weighit_app/build/linux/x64/release
tar -czf /tmp/weighit_app.tar.gz bundle/

echo "Step 2: Copying to tablet..."
scp /tmp/weighit_app.tar.gz $TABLET_USER@$TABLET_HOST:/tmp/

echo "Step 3: Copying Python API service..."
cd /home/justin/code/weighit_flutter
tar -czf /tmp/weighit_api.tar.gz weighit_api/
scp /tmp/weighit_api.tar.gz $TABLET_USER@$TABLET_HOST:/tmp/

echo "Step 4: Installing on tablet..."
ssh $TABLET_USER@$TABLET_HOST << 'ENDSSH'
    cd ~
    mkdir -p weighit_flutter
    cd weighit_flutter
    
    # Extract API service
    tar -xzf /tmp/weighit_api.tar.gz
    
    # Extract Flutter app
    mkdir -p weighit_app
    cd weighit_app
    tar -xzf /tmp/weighit_app.tar.gz
    
    # Install Python dependencies
    cd ../weighit_api
    pip install -r requirements.txt
    
    echo ""
    echo "✓ Installation complete!"
    echo ""
    echo "To run:"
    echo "  1. Start API: cd ~/weighit_flutter/weighit_api && python main.py &"
    echo "  2. Start app: cd ~/weighit_flutter/weighit_app/bundle && ./weighit_app"
ENDSSH

echo ""
echo "================================================"
echo "✓ Deployment Complete!"
echo "================================================"
echo ""
echo "On tablet, run:"
echo "  cd ~/weighit_flutter/weighit_api && python main.py &"
echo "  cd ~/weighit_flutter/weighit_app/bundle && ./weighit_app"
echo ""

# Cleanup
rm /tmp/weighit_app.tar.gz /tmp/weighit_api.tar.gz
