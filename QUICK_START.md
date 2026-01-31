# Quick Reference - AI Chef macOS App

## Installation (First Time)

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
chmod +x setup_macos_app.sh
./setup_macos_app.sh
```

## Opening the App

```bash
open /Users/ryanbahadori/Documents/GitHub/Ai-Chef
# Then press Cmd+R in Xcode to build & run
```

Or use Finder:
- Applications → AI Chef

## Files Created for the App

| File | Purpose |
|------|---------|
| `app_bridge.py` | Bridges SwiftUI app to Python backend |
| `macos_app/AiChef_Updated.swift` | Main app code (use this) |
| `macos_app/PythonBridge.swift` | Handles Python subprocess calls |
| `macos_app/README.md` | Detailed setup guide |
| `setup_macos_app.sh` | Automated setup script |
| `MACOS_APP_GUIDE.md` | Comprehensive guide |

## What Still Works

✅ **Terminal CLI**: `python3 ai_chef.py` - completely unchanged

✅ **Python modules**: All your code (recipes.py, etc.) - unchanged

✅ **API key**: `.env` file works with both app and CLI

## The App Has 4 Tabs

1. **Find Recipes** - Search by ingredients
2. **Generate** - AI-powered recipe creation
3. **Meal Plan** - Weekly meal planning
4. **Saved** - Your favorite recipes

## Key Files to Know

**Don't modify:**
- Original Python files (ai_chef.py, recipes.py, meal_planner.py) - they just work

**Can modify for features:**
- `app_bridge.py` - Add new Python functions here
- `macos_app/AiChef_Updated.swift` - Update UI here
- `macos_app/PythonBridge.swift` - Add new function calls here

## If Something Breaks

### App won't build
```bash
# Clean and rebuild
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
xcodebuild clean
xcodebuild build
```

### Can't find Python
Edit `PythonBridge.swift` line with:
```swift
task.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
```

Get your Python path:
```bash
which python3
```

### Changed recipes.py but app shows old recipes
- Close app (Cmd+Q)
- Reopen app
- (Subprocess caches don't persist across app restarts)

## Testing Changes

### Test Python code directly:
```bash
python3 app_bridge.py find_recipes '["chicken"]'
python3 app_bridge.py generate_recipe "pasta"
```

### Test in app:
1. Cmd+R in Xcode to rebuild
2. Try feature in app

## Build Distribution Version

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef

# Create .app bundle
xcodebuild build -scheme AiChef

# Find app in:
# build/Release/AI Chef.app
```

## Keyboard Shortcuts

- Cmd+R: Build & run in Xcode
- Cmd+Q: Quit app
- Cmd+, : Preferences (future)

## File Sizes

- `app_bridge.py` - ~2KB (small Python bridge)
- `AiChef_Updated.swift` - ~20KB (full app UI)
- `PythonBridge.swift` - ~3KB (communication layer)

## Important

- ✅ Your original CLI **always** works
- ✅ Both app and CLI read same recipes
- ✅ No data duplication
- ✅ One source of truth (your Python files)

## Next Steps

1. Run `./setup_macos_app.sh`
2. Open in Xcode
3. Press Cmd+R
4. Try the app!

For detailed info, see `MACOS_APP_GUIDE.md`

---

**Questions?** Check the comprehensive guide or test with:
```bash
python3 app_bridge.py get_all_recipes
```
