#!/bin/bash
# ONE-COMMAND SETUP FOR WEIGHIT_FLUTTER
# This script does everything: setup, git add, commit, and push

cd /home/justin/code/weighit_flutter || exit 1

echo "================================================"
echo "WeighIt Flutter - Complete Setup"
echo "================================================"
echo ""

# Copy and run setup script
echo "Copying setup script..."
cp /home/justin/code/weighit/setup_flutter_project.sh ./setup.sh
chmod +x setup.sh

echo "Running setup..."
./setup.sh

echo ""
echo "================================================"
echo "Git Operations"
echo "================================================"
echo ""

# Git operations
echo "Adding files to git..."
git add .

echo ""
echo "Files to be committed:"
git status --short

echo ""
read -p "Proceed with commit and push? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Committing..."
    git commit -m "Initial project setup with Python API and Flutter app

- Added Python FastAPI service (weighit_api/)
  - Complete REST API wrapper around existing weighit backend
  - Imports from /home/justin/code/weighit/src
  - All endpoints: scale, logging, sources, types, totals, history
  
- Added Flutter app structure (weighit_app/)
  - Complete API client (api_service.dart)
  - Models for ScaleReading and FoodType
  - Ready for UI development
  
- Documentation
  - Main README with architecture overview
  - API service README with setup instructions
  - Complete code examples"

    echo ""
    echo "Pushing to GitHub..."
    git push origin main
    
    echo ""
    echo "================================================"
    echo "✓ SUCCESS!"
    echo "================================================"
    echo ""
    echo "Your weighit_flutter project is now on GitHub!"
    echo ""
    echo "Next steps on your tablet:"
    echo "  1. git clone git@github.com:wyojustin/weighit_flutter.git"
    echo "  2. cd weighit_flutter/weighit_app"
    echo "  3. flutter create . --platforms=linux"
    echo "  4. Update pubspec.yaml with dependencies (http, provider)"
    echo "  5. flutter pub get"
    echo "  6. Start building your UI!"
    echo ""
else
    echo "Aborted. You can commit manually with:"
    echo "  git commit -m 'Initial setup'"
    echo "  git push origin main"
fi
