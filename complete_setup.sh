#!/bin/bash
# Complete setup and git push script for weighit_flutter
# Run this from /home/justin/weighit_flutter after cloning the repo

set -e

echo "================================================"
echo "WeighIt Flutter - Complete Setup & Git Push"
echo "================================================"
echo ""

# Step 1: Run the main setup script
echo "Step 1: Creating project structure..."
if [ -f "setup.sh" ]; then
    ./setup.sh
else
    echo "Error: setup.sh not found. Please copy it from /home/justin/code/weighit/setup_flutter_project.sh"
    exit 1
fi

echo ""
echo "Step 2: Initializing Flutter app..."
cd weighit_app
flutter create . --platforms=linux
cd ..

echo ""
echo "Step 3: Updating Flutter dependencies..."
cat > weighit_app/pubspec.yaml << 'EOF'
name: weighit_app
description: WeighIt Flutter desktop application for food pantry scale
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.0
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
EOF

cd weighit_app
flutter pub get
cd ..

echo ""
echo "Step 4: Adding to git..."
git add .
git status

echo ""
echo "================================================"
echo "Setup complete! Review the changes above."
echo "================================================"
echo ""
echo "To commit and push:"
echo "  git commit -m 'Initial project setup with Python API and Flutter app'"
echo "  git push origin main"
echo ""
echo "Or run: ./git_push.sh"
echo ""
