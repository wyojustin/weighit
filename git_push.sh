#!/bin/bash
# Git commit and push script
# Run after complete_setup.sh

set -e

echo "Committing changes..."
git add .
git commit -m "Initial project setup with Python API and Flutter app

- Added Python FastAPI service (weighit_api/)
- Added Flutter app structure (weighit_app/)
- Includes API client and models
- Complete documentation and setup instructions"

echo ""
echo "Pushing to GitHub..."
git push origin main

echo ""
echo "✓ Successfully pushed to git@github.com:wyojustin/weighit_flutter.git"
echo ""
echo "You can now clone this on your tablet:"
echo "  git clone git@github.com:wyojustin/weighit_flutter.git"
