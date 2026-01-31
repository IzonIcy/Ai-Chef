#!/bin/bash

# Build AI Chef macOS App and Create .dmg Distribution File
# This creates a .dmg file you can share with others

set -e

PROJECT_DIR="/Users/ryanbahadori/Documents/GitHub/Ai-Chef"
APP_NAME="AI Chef"
BUILD_DIR="$PROJECT_DIR/build"
DMG_DIR="$BUILD_DIR/dmg_temp"
FINAL_DMG="$BUILD_DIR/AI-Chef.dmg"

echo "🍳 Building AI Chef for Distribution"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Clean previous builds
echo -e "${BLUE}Step 1: Cleaning previous builds...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
echo "✓ Build directory ready"

# Step 2: Build the app
echo ""
echo -e "${BLUE}Step 2: Building the app...${NC}"
cd "$PROJECT_DIR"

# Build for Release (optimized)
xcodebuild build \
    -scheme AiChef \
    -configuration Release \
    -derivedDataPath "$BUILD_DIR/DerivedData"

# Find the built app
APP_PATH="$BUILD_DIR/DerivedData/Build/Products/Release/$APP_NAME.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Build failed - app not found at $APP_PATH"
    exit 1
fi

echo "✓ App built successfully"

# Step 3: Create DMG structure
echo ""
echo -e "${BLUE}Step 3: Creating .dmg file...${NC}"
mkdir -p "$DMG_DIR"

# Copy app to dmg directory
cp -r "$APP_PATH" "$DMG_DIR/"

# Create symlink to Applications folder
ln -s /Applications "$DMG_DIR/Applications"

# Create .dmg file
rm -f "$FINAL_DMG"
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$DMG_DIR" \
    -ov \
    -format UDZO \
    "$FINAL_DMG"

echo "✓ DMG created successfully"

# Step 4: Cleanup
echo ""
echo -e "${BLUE}Step 4: Cleaning up temporary files...${NC}"
rm -rf "$DMG_DIR"
rm -rf "$BUILD_DIR/DerivedData"
echo "✓ Cleaned up"

# Step 5: Show results
echo ""
echo -e "${GREEN}✅ Build Complete!${NC}"
echo ""
echo "📦 Distribution file created:"
echo "   $FINAL_DMG"
echo ""
echo "📊 File size: $(du -h "$FINAL_DMG" | cut -f1)"
echo ""
echo "🎯 How to distribute:"
echo "   1. Upload $FINAL_DMG to your website/GitHub"
echo "   2. Users download it"
echo "   3. Users open the .dmg file"
echo "   4. Drag 'AI Chef' to Applications folder"
echo "   5. Done! They can now run the app"
echo ""
echo "💡 Tip: You can also add a background image and custom icon"
echo "   to the DMG for a professional look. See create_fancy_dmg.sh"
echo ""
