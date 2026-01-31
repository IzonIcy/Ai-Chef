# macOS App Guide

So I built you a native macOS app to go with the command-line version. You can still use the terminal if you want—nothing there broke. But now you've also got a proper GUI app with tabs, search, all that nice stuff.

## What You Actually Have

The project now has these pieces:

- Your original Python stuff (recipes.py, ai_chef.py, etc.) - completely untouched
- A bridge file (app_bridge.py) that lets the app talk to your Python code
- An actual macOS app written in SwiftUI (the modern Apple framework)
- Some helper scripts to set it all up

The cool part is that both the app and CLI use the same Python backend. Change recipes.py and both benefit. No duplicate code.

## Getting the App Running

This is straightforward:

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
chmod +x setup_macos_app.sh
./setup_macos_app.sh
```

This just checks that you have Python installed and installs the dependencies.

Then:

```bash
open /Users/ryanbahadori/Documents/GitHub/Ai-Chef
```

Xcode opens the project. Press **Cmd + R** and it builds and runs the app.

### 1. Find Recipes by Ingredients
- Type ingredients (comma-separated)
- Get matching recipes with cook times
- View full recipe details## How the App Talks to Python

The cool thing is that it's all pretty simple under the hood:

- The app (written in Swift) calls PythonBridge
- PythonBridge launches Python as a subprocess and passes it some commands
- Python does its thing and returns JSON with the results
- The app gets the JSON back and displays it

So you can edit your Python code (recipes.py, whatever) and both the CLI and app immediately benefit from it. No rebuilding, no duplicate logic. The Python backend is just Python.

## The App's Features

**Tab 1: Find Recipes**
Search by ingredients, get results, view details, save favorites.

**Tab 2: Generate Recipes**
Tell it what you want and it generates a recipe using your OpenAI key.

**Tab 3: Plan Your Week**
Add meals for each day. Breakfast, lunch, dinner, snacks.

**Tab 4: Saved Recipes**
Just shows everything you've saved.

## Using Both at the Same Time

The terminal version still works. The app works. They use the same data underneath. Pick whichever interface you like for each task.

```bash
python3 ai_chef.py  # Still works
```

Or just launch the app from Launchpad.

## Troubleshooting Stuff

### App says Python not found

Edit `macos_app/PythonBridge.swift` and change the Python path to wherever yours actually is:

```bash
which python3
```

Then update that path in the Swift file.

### App can't find your recipes

Make sure `recipes.py` is in the main folder where all your Python files are.

### Changed recipes.py but app still shows old results

Close the app completely (Cmd+Q) and reopen it. The subprocess doesn't cache anything across restarts.

### OpenAI not working

Add your key to `.env` file:
```
OPENAI_API_KEY=sk-whatever-your-key-is
```

Then restart the app. It reads the file fresh each time.

## Sharing Your App

For the .dmg distribution stuff (which is what you want), check out `DMG_QUICK_START.md` or `DMG_DISTRIBUTION.md`.

The `.app` bundle will be in `build/`.

### Creating an Export Options File

Create `exportOptions.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>mac-application</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>stripSwiftSymbols</key>
    <true/>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
</dict>
</plist>
```

---

## Customizing the App

### Adding New Tabs

In `AiChef_Updated.swift`, add to `ContentView`:

```swift
TabView(selection: $selectedTab) {
    // ... existing tabs ...
    
    MyNewView()
        .tabItem {
            Label("My Tab", systemImage: "icon.name")
        }
        .tag(4)
}
```

### Adding New Python Functions

1. Create function in `app_bridge.py`:
```python
def my_function(arg: str) -> dict:
    result = do_something(arg)
    return {"status": "success", "data": result}
```

2. Add command handler:
```python
elif command == "my_function":
    arg = sys.argv[2] if len(sys.argv) > 2 else ""
    result = my_function(arg)
```

3. Add to `PythonBridge.swift`:
```swift
func myFunction(arg: String, completion: @escaping (Result<[String: Any], Error>) -> Void) {
    executeCommand("my_function", arguments: [arg], completion: completion)
}
```

---

## Project Structure

```
AI-Chef/
├── Requirements (Python backend)
│   ├── ai_chef.py
│   ├── recipes.py
│   ├── meal_planner.py
│   ├── ai_generator.py
│   └── requirements.txt
│
├── Bridge Layer (CLI ↔ App)
│   └── app_bridge.py
│
├── macOS App
│   ├── macos_app/
│   │   ├── AiChef_Updated.swift    (Use this one)
│   │   ├── PythonBridge.swift
│   │   └── README.md
│   └── setup_macos_app.sh
│
└── Documentation
    └── MACOS_APP_GUIDE.md (this file)
```

---

## Development Tips

### Testing Python Code

Before building the app, test your Python code:

```bash
python3 app_bridge.py find_recipes '["chicken", "pasta"]'
python3 app_bridge.py generate_recipe "spicy curry"
```

### Debugging in Xcode

1. Set breakpoints in Swift code
2. Run with Xcode (Cmd+R)
3. Use Xcode's debugger (Cmd+Y)
4. Check console for Python errors

### Viewing App Logs

In Terminal:
```bash
log stream --predicate 'eventMessage contains "AiChef"' --level debug
```

---

## Keyboard Shortcuts

Once the app is running:
- **Cmd+T**: Search recipes
- **Cmd+G**: Generate recipe
- **Cmd+P**: Meal planner
- **Cmd+S**: Saved recipes
- **Cmd+Q**: Quit
- **Cmd+,**: Preferences (when implemented)

---

## Future Enhancements

These features are ready to add:

- [ ] Notifications for meal reminders
- [ ] Export meal plans to Calendar
- [ ] Share recipes via Mail
- [ ] Recipe ratings and reviews
- [ ] Grocery list with checkboxes
- [ ] Recipe browser with search filters
- [ ] Dark mode support
- [ ] Multiple recipe databases
- [ ] Cloud sync via iCloud
- [ ] Shortcuts integration

---

## Support

If you encounter issues:

1. **Check logs**: `python3 app_bridge.py find_recipes '[]'`
2. **Verify Python path**: `which python3`
3. **Test CLI**: `python3 ai_chef.py`
4. **Rebuild**: Clean build folder and rebuild

---

## Credits

Built with:
- **SwiftUI** - Native macOS interface
- **Python** - Backend logic
- **OpenAI** - Recipe generation

---

**Enjoy your native macOS AI Chef app! 🍳**
