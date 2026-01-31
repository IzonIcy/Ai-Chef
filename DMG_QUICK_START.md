# Building & Sharing Your App

So you want to get this app out to people without dealing with the App Store. Smart move. Here's what you do.

## The Quick Version

Run this:

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
./build_dmg.sh
```

Grab a coffee. When it's done (couple minutes), you've got `build/AI-Chef.dmg`.

## Sharing It

Put it wherever you want:
- GitHub releases (easiest)
- Your website
- Dropbox, Google Drive
- Email
- Forum post

Your users will download it, double-click to open, drag the app to Applications, and they're done. That's the whole install process.

No Terminal, no weird permission issues (usually), just straightforward.

## File Size

Expect around 60-100 MB, depends on what Python packages you have. It's compressed, so not too bad for downloading.

## GitHub is Your Best Bet

If you're using GitHub (which I assume you are), tag your code and create a release:

```bash
git tag -a v1.0 -m "AI Chef v1.0"
git push origin v1.0
```

Then go to your repo's Releases tab, create a new release for that tag, upload the `.dmg`, write something like "Native macOS app version 1.0 - just download and drag to Applications", and hit publish.

People see it right there and can grab it.

## About Code Signing

You don't need it. Yeah, users might see "this is from an unidentified developer" the first time they launch it. They click Open, it runs, and that's it. Never shows up again.

If you want to remove that (looks more professional), you need an Apple Developer account ($99/year). But for just getting your app out? Not worth it at this stage.

## Your Own Website

Upload the `.dmg` to your server, make a download link, done. People download, install, move on.

## That's the whole thing

Build it, upload it, share the link. Pretty straightforward. Check `DMG_DISTRIBUTION.md` if you want more details on anything.
