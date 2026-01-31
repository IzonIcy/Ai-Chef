#!/bin/bash

# AI Chef macOS App Setup Script
# This script sets up and builds the native macOS app for AI Chef

set -e

PROJECT_DIR="/Users/ryanbahadori/Documents/GitHub/Ai-Chef"
APP_NAME="AI Chef"
BUNDLE_ID="com.aichef.app"

echo "🍳 AI Chef macOS App Setup"
echo "=========================="
echo ""

# Check if Python is installed
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "  Found: $PYTHON_VERSION"

# Check if Xcode is installed
echo "✓ Checking Xcode..."
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode not found. Please install Xcode from App Store"
    exit 1
fi
echo "  Xcode is installed"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd "$PROJECT_DIR"
python3 -m pip install -r requirements.txt --upgrade

# Create Xcode project structure
echo ""
echo "🏗️  Creating Xcode project structure..."
XCODE_PROJ_DIR="$PROJECT_DIR/AiChef.xcodeproj"

# Create a simple Package.swift for SPM support (optional)
if [ ! -f "$PROJECT_DIR/Package.swift" ]; then
    echo "✓ Creating Swift Package manifest..."
    cat > "$PROJECT_DIR/Package.swift" << 'EOF'
// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "AiChef",
    platforms: [
        .macOS(.v12)
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "AiChef",
            dependencies: [],
            path: "macos_app"
        )
    ]
)
EOF
fi

# Create build directory
echo "✓ Creating build directory..."
mkdir -p "$PROJECT_DIR/build"

# Summary
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Open in Xcode: open $PROJECT_DIR"
echo "2. Or build from command line:"
echo "   cd $PROJECT_DIR"
echo "   xcodebuild build -scheme AiChef"
echo ""
echo "🚀 To run the app:"
echo "   xcodebuild run -scheme AiChef"
echo ""
echo "📱 Features:"
echo "   • Find recipes by ingredients"
echo "   • Generate recipes with AI"
echo "   • Plan meals for the week"
echo "   • Save your favorite recipes"
echo ""
echo "💡 The CLI still works: python3 ai_chef.py"
echo ""
