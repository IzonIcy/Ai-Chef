# Sharing Your App as a DMG File

You've got a native macOS app. Now you probably want other people to be able to use it. The easiest way is to package it as a `.dmg` file and let people download it.

## What You Need to Do

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
./build_dmg.sh
```

That's it. You'll get `build/AI-Chef.dmg` when it's done.

## Sharing It

Put it literally anywhere people can download files from. GitHub releases is easiest if you're already on GitHub, but your website, Dropbox, wherever works.

## What Users Do

They download the file, double-click it, drag the app to their Applications folder, and they're done. Super simple install process.

## No Complicated Setup Needed

You don't need code signing, app store accounts, any of that. Just build the DMG and share it.

For more details, check `DMG_QUICK_START.md` or `DMG_DISTRIBUTION.md`.
