#!/bin/bash

# Create a fancy .dmg with custom layout and background (optional)
# Run this after build_dmg.sh if you want a professional-looking DMG

set -e

PROJECT_DIR="/Users/ryanbahadori/Documents/GitHub/Ai-Chef"
BUILD_DIR="$PROJECT_DIR/build"
DMG_FILE="$BUILD_DIR/AI-Chef.dmg"
DMG_TEMP="$BUILD_DIR/dmg_temp_fancy"
FINAL_DMG="$BUILD_DIR/AI-Chef-Fancy.dmg"

echo "🎨 Creating Fancy DMG with Custom Layout"
echo "========================================"
echo ""

# Check if DMG exists
if [ ! -f "$DMG_FILE" ]; then
    echo "❌ Error: $DMG_FILE not found"
    echo "   Run build_dmg.sh first"
    exit 1
fi

# Mount the DMG
echo "📦 Mounting DMG..."
hdiutil attach "$DMG_FILE" -mountpoint "/Volumes/AI Chef"

# Get the device name
DEVICE=$(hdiutil attach "$DMG_FILE" | grep GUID_partition_scheme | awk '{print $1}')

# Set custom properties
echo "🎨 Setting custom layout..."

# Set view options
osascript << EOF
tell application "Finder"
    set theFolder to POSIX file "/Volumes/AI Chef"
    tell container window of (open theFolder)
        set current view to icon view
        set the bounds to {100, 100, 500, 400}
        set icon size of the icon view options to 96
        set arrangement of the icon view options to not arranged
        
        -- Position app icon
        set position of item "AI Chef" of container window to {150, 150}
        
        -- Position Applications symlink
        set position of item "Applications" of container window to {350, 150}
        
        -- Set background (optional)
        set background picture of the icon view options to file (POSIX file "/Users/ryanbahadori/Documents/GitHub/Ai-Chef/dmg-background.png")
    end tell
end tell
EOF

# Unmount and convert
echo "📦 Unmounting and finalizing..."
hdiutil detach "/Volumes/AI Chef"

# Convert to compressed DMG
hdiutil convert "$DMG_FILE" -format UDZO -o "$FINAL_DMG"

echo ""
echo "✅ Fancy DMG created: $FINAL_DMG"
echo ""
echo "💡 To customize further:"
echo "   1. Create a 600x400px background image: dmg-background.png"
echo "   2. Place it in: $PROJECT_DIR/"
echo "   3. Run this script again"
echo ""
