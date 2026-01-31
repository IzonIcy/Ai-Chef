# AI Chef macOS App Setup Guide

This directory contains the native macOS app for AI Chef. The app provides a beautiful GUI while keeping the original Python CLI fully functional.

## Architecture

- **Frontend**: SwiftUI (native macOS interface)
- **Backend**: Python (all original functionality)
- **Communication**: Process execution & file-based data exchange

## Prerequisites

- macOS 12.0 or later
- Xcode 14.0 or later
- Python 3.8+
- Your existing AI Chef Python environment

## Setup Instructions

### 1. Using Xcode

1. Open Xcode
2. Click `File` → `Open`
3. Navigate to this directory and select the folder
4. Xcode will auto-detect and create a SwiftUI project

### 2. Manual Project Creation

If Xcode doesn't auto-detect:

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef/macos_app
xcodebuild -createBootstrapProject
```

### 3. Configure Python Path

In the `PythonHelper.swift` file, update the Python executable path:

```swift
let pythonPath = "/path/to/your/python" // e.g., /usr/local/bin/python3
```

### 4. Build & Run

```bash
xcodebuild build
xcodebuild run
```

Or simply press `Cmd + R` in Xcode.

## Features

### 1. Find Recipes
Search through available recipes by entering ingredients you have on hand. The app will suggest matching recipes with cook times and difficulty levels.

### 2. Generate Recipes with AI
Describe the type of recipe you want, and the AI will generate a custom recipe for you (requires OpenAI API key in `.env` file).

### 3. Meal Planner
Plan your meals for the entire week. Simply select a day and add a meal.

### 4. Saved Recipes
Keep track of your favorite recipes for quick access.

## How It Works

The macOS app communicates with your Python backend by:

1. **Passing user input** to Python scripts
2. **Executing Python functions** from SwiftUI
3. **Displaying results** in the native UI

The CLI still works independently - run `python ai_chef.py` anytime.

## Troubleshooting

### App won't run
- Ensure Python path is correctly configured in `PythonHelper.swift`
- Check that all Python dependencies are installed: `pip install -r requirements.txt`

### Python execution fails
- Verify your `.env` file exists with your OpenAI API key
- Run the Python CLI directly to test: `python ai_chef.py`

### App can't find recipes
- Make sure `recipes.py` and other modules are in the parent directory
- Check that the Python path is absolute, not relative

## Building for Distribution

To create a standalone `.app` bundle:

```bash
xcodebuild archive -scheme AiChef -archivePath build/AiChef.xcarchive
xcodebuild -exportArchive -archivePath build/AiChef.xcarchive -exportOptionsPlist export.plist -exportPath build
```

## File Structure

```
macos_app/
├── AiChef.swift              # Main app and all views
├── README.md                 # This file
└── python_bridge/
    ├── python_helper.swift   # Python execution logic
    └── models.swift          # Data models
```

## Future Improvements

- [ ] Native data persistence (CoreData)
- [ ] Notifications for meal reminders
- [ ] Drag-and-drop recipe import
- [ ] Export meal plans to Calendar
- [ ] Recipe sharing via iCloud
- [ ] Offline recipe database

## Contact & Support

For issues or improvements, check your project repository.

---

**Note**: The CLI remains fully functional. You can use both the GUI and terminal interchangeably.
