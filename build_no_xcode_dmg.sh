#!/bin/bash

# Build a no-Xcode DMG distribution for AI Chef.
# This package uses a .command launcher and Python source files,
# so users can run the app without Xcode.

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$PROJECT_DIR/build_no_xcode"
PAYLOAD_DIR="$BUILD_DIR/payload"
APP_DIR="$PAYLOAD_DIR/AI Chef"
PYTHON_SRC_DIR="$APP_DIR/python_src"
FINAL_DMG="$BUILD_DIR/AI-Chef-No-Xcode.dmg"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "AI Chef No-Xcode DMG Builder"
echo "============================="
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required to build this package."
    exit 1
fi

echo -e "${BLUE}Step 1: Preparing build directories...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$PYTHON_SRC_DIR"
echo "OK"

echo ""
echo -e "${BLUE}Step 2: Copying Python project files...${NC}"
PYTHON_FILES=(
    "ai_chef.py"
    "app_bridge.py"
    "recipes.py"
    "ai_generator.py"
    "meal_planner.py"
    "gamification.py"
    "requirements.txt"
    "meal_plans.json"
)

for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        cp "$PROJECT_DIR/$file" "$PYTHON_SRC_DIR/$file"
    else
        echo "Warning: missing $file"
    fi
done

if [ -f "$PROJECT_DIR/realopenaikey.example" ]; then
    cp "$PROJECT_DIR/realopenaikey.example" "$PYTHON_SRC_DIR/.env.example"
fi

echo "OK"

echo ""
echo -e "${BLUE}Step 3: Creating user launcher...${NC}"
cat > "$APP_DIR/AI Chef.command" << 'EOF'
#!/bin/bash

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
BUNDLED_SRC="$APP_DIR/python_src"
RUNTIME_ROOT="$HOME/Library/Application Support/AIChef"
RUNTIME_SRC="$RUNTIME_ROOT/src"
VENV_DIR="$RUNTIME_ROOT/.venv"
REQ_HASH_FILE="$RUNTIME_ROOT/requirements.sha256"

mkdir -p "$RUNTIME_ROOT" "$RUNTIME_SRC"

# Sync source from bundled package into user-writable runtime directory.
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$BUNDLED_SRC/" "$RUNTIME_SRC/"
else
    rm -rf "$RUNTIME_SRC"
    mkdir -p "$RUNTIME_SRC"
    cp -R "$BUNDLED_SRC/." "$RUNTIME_SRC/"
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to run AI Chef."
    echo "Install Python 3, then run this launcher again."
    read -r -p "Press Enter to close..." _
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
    python3 -m venv "$VENV_DIR"
fi

CURRENT_HASH="$(shasum -a 256 "$RUNTIME_SRC/requirements.txt" | awk '{print $1}')"
SAVED_HASH=""
if [ -f "$REQ_HASH_FILE" ]; then
    SAVED_HASH="$(cat "$REQ_HASH_FILE")"
fi

if [ "$CURRENT_HASH" != "$SAVED_HASH" ]; then
    "$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
    "$VENV_DIR/bin/pip" install -r "$RUNTIME_SRC/requirements.txt"
    printf "%s" "$CURRENT_HASH" > "$REQ_HASH_FILE"
fi

cd "$RUNTIME_SRC"
exec "$VENV_DIR/bin/python" "$RUNTIME_SRC/ai_chef.py"
EOF

chmod +x "$APP_DIR/AI Chef.command"
echo "OK"

echo ""
echo -e "${BLUE}Step 4: Writing usage notes...${NC}"
cat > "$APP_DIR/README.txt" << 'EOF'
AI Chef (No Xcode Package)

This package runs AI Chef without Xcode.

How to use:
1. Drag the "AI Chef" folder to your desired location (Applications or Desktop).
2. Open the folder.
3. Double-click "AI Chef.command".

Notes:
- Python 3 is required.
- On first launch, dependencies are installed automatically.
- Runtime files are stored in:
  ~/Library/Application Support/AIChef
- To enable AI generation features, create:
  ~/Library/Application Support/AIChef/src/.env
  and add: OPENAI_API_KEY=your_key_here
EOF

echo "OK"

echo ""
echo -e "${BLUE}Step 5: Building DMG...${NC}"
ln -s /Applications "$PAYLOAD_DIR/Applications"

hdiutil create \
    -volname "AI Chef No Xcode" \
    -srcfolder "$PAYLOAD_DIR" \
    -ov \
    -format UDZO \
    "$FINAL_DMG"

echo ""
echo -e "${GREEN}Build complete.${NC}"
echo "DMG: $FINAL_DMG"
echo ""
echo "Users can now run AI Chef without Xcode by launching AI Chef.command."
