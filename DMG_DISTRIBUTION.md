# AI Chef - DMG Distribution Guide

This guide explains how to build and distribute your AI Chef macOS app as a `.dmg` file.

## What is a .dmg File?

A `.dmg` (Disk Image) file is a common way to distribute macOS applications. Users simply:
1. Download the `.dmg` file
2. Open it (double-click)
3. Drag the app into Applications
4. Run the app

No App Store needed, no code signing certificates required (though optional).

## Building Your DMG

### Quick Build

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
chmod +x build_dmg.sh
./build_dmg.sh
```

This creates: `build/AI-Chef.dmg`

### What the Script Does

1. ✅ Cleans previous builds
2. ✅ Builds the app in Release mode (optimized)
3. ✅ Creates a `.dmg` file
4. ✅ Includes a shortcut to Applications folder
5. ✅ Shows file size and distribution instructions

### Result

After running `build_dmg.sh`:
- Location: `/Users/ryanbahadori/Documents/GitHub/Ai-Chef/build/AI-Chef.dmg`
- Size: ~50-150 MB (depending on Python)
- Ready to: Share, upload, or email

## Distributing Your App

### Option 1: GitHub Releases

```bash
# Tag your release
git tag -a v1.0 -m "AI Chef v1.0"
git push origin v1.0

# Go to GitHub and create a release
# Upload build/AI-Chef.dmg to the release
```

### Option 2: Your Website

1. Upload `build/AI-Chef.dmg` to your website
2. Create a download link
3. Users click → downloads → double-click → install

### Option 3: Direct Share

```bash
# Via email, Google Drive, Dropbox, etc.
# Just share the AI-Chef.dmg file
```

## User Installation

Your users will:

1. **Download** the `.dmg` file
2. **Double-click** to open it (or it auto-opens)
3. **Drag** "AI Chef" to Applications folder
4. **Close** the window
5. **Launch** AI Chef from Applications or Spotlight (Cmd+Space)

That's it! No Terminal, no installation wizard.

## Advanced: Fancy DMG

To create a professional-looking DMG with custom layout:

```bash
chmod +x create_fancy_dmg.sh
./create_fancy_dmg.sh
```

This:
- Positions icons nicely
- Shows Applications folder shortcut
- Optional: Uses a background image
- Creates `build/AI-Chef-Fancy.dmg`

### Customize the DMG Background

1. Create a 600x400px PNG image (logo, artwork, etc.)
2. Save as: `dmg-background.png` in project root
3. Run: `./create_fancy_dmg.sh`

## File Sizes

```
Build types:
  Release build: ~100-150 MB
  With Python bundle: depends on dependencies
  After DMG compression: ~50-80 MB

Breakdown:
  SwiftUI app: ~2 MB
  Python runtime: ~30-50 MB
  Dependencies: ~20-50 MB
  DMG overhead: minimal
```

## Code Signing (Optional)

For maximum compatibility, you can code sign:

```bash
# Before building, set up signing
export DEVELOPMENT_TEAM="your-team-id"  # From Apple Developer
export CODE_SIGN_IDENTITY="Mac Developer"

./build_dmg.sh
```

For most users, unsigned is fine. Users will just see:
> "AI Chef is from an unidentified developer"

They click "Open" and it works. If you want to remove this, you need:
- Apple Developer account (~$99/year)
- Development certificate
- Team ID

## Troubleshooting

### DMG build fails
```bash
# Make sure Xcode is installed
xcodebuild -version

# Clean and try again
rm -rf build/
./build_dmg.sh
```

### App won't run after installation
- Verify `app_bridge.py` path is correct in `PythonBridge.swift`
- Check Python is installed: `which python3`
- Test Python bridge: `python3 app_bridge.py get_all_recipes`

### DMG too large
- Remove unused Python packages from `requirements.txt`
- Use lightweight alternatives
- Consider splitting into separate downloads

### Users can't open app (security warning)
- On first run, macOS may block unsigned apps
- Users right-click → Open → Open (one-time)
- Or provide signing certificate (paid)

## Distribution Checklist

Before sharing:

- [ ] Ran `./build_dmg.sh` successfully
- [ ] `build/AI-Chef.dmg` exists
- [ ] Tested app runs from DMG (double-click, drag, launch)
- [ ] CLI still works: `python3 ai_chef.py`
- [ ] OpenAI key works (if using AI features)
- [ ] Documentation updated
- [ ] Version number bumped

## Version Updates

For new releases:

```bash
# 1. Update version number somewhere
#    (can add to app code or release notes)

# 2. Rebuild
./build_dmg.sh

# 3. New DMG created at:
#    build/AI-Chef.dmg

# 4. Upload to GitHub/website
```

## Post-Installation

After users install and run the app:

1. They might see: "AI Chef is from an unidentified developer"
2. They click: Open (one time)
3. App runs normally thereafter

This is normal for unsigned apps. If annoying, you can:
- Get signing certificate (paid)
- Have Apple notarize the app (free but requires certificate)

## GitHub Release Example

```
Release: AI Chef v1.0

Create a native macOS app for your AI Chef project.

Features:
- Find recipes by ingredients
- Generate recipes with AI
- Plan weekly meals
- Save favorite recipes

Installation:
1. Download AI-Chef.dmg
2. Open the file
3. Drag AI Chef to Applications
4. Done!

[Download AI-Chef.dmg]
```

## Sharing Tips

**On GitHub:**
```markdown
## Download

[Download AI-Chef v1.0](https://github.com/username/AI-Chef/releases/download/v1.0/AI-Chef.dmg)

Installation: Open the .dmg file and drag to Applications.
```

**On Website:**
```html
<a href="/downloads/AI-Chef.dmg" class="btn">
  Download AI Chef (v1.0)
</a>
<p>Requires macOS 12.0+</p>
```

**In Email/Social:**
```
Download AI Chef for Mac - beautiful native app for meal planning and recipe discovery. Just open the .dmg and drag to Applications!
```

## What's Included in the DMG

```
AI-Chef.dmg
├── AI Chef.app          (the actual application)
└── Applications/        (shortcut to system folder)
    └── Users drag app here
```

Users just drag `AI Chef.app` to the `Applications` shortcut, and it's installed.

## Keeping It Updated

For future versions:

1. Make changes to code
2. Update version number (if desired)
3. Run: `./build_dmg.sh`
4. Get new: `build/AI-Chef.dmg`
5. Upload to releases/website
6. Done!

Each build is independent, so users get the latest when they download the newest DMG.

## Security Notes

### Code Signing
- Currently: Unsigned (safe, users just approve first run)
- With signing: Requires Apple Developer Account
- Recommended: Get signing cert for professional distribution

### Notarization (Optional)
- Free with Apple Developer account
- Removes security warnings
- Takes a few minutes per build
- See: `notarize.sh` (can create if needed)

### Privacy
- App only runs locally
- Uses Python subprocess (no internet unless using OpenAI)
- Data stored locally only

## Summary

**Building:** `./build_dmg.sh` → Creates `AI-Chef.dmg`

**Distributing:** Upload to GitHub releases, website, or share directly

**Users Install:** Download → Open → Drag to Applications → Run

**No App Store needed!** 🎉

For questions, check `MACOS_APP_GUIDE.md` for full documentation.
