# houndapps

A source for [SideStore](https://sidestore.io) and AltStore Classic with apps by horsehound.

Add this URL as a source in the app:

    https://raw.githubusercontent.com/horsehound/houndapps/main/source.json

## How it works

- `apps.json` lists the apps and the GitHub repo each one is released from.
- `build_source.py` reads the latest releases of those repos and writes `source.json`.
- The "Update source" workflow runs that script every hour, on changes to this repo, and on demand.

To add an app, add an entry to `apps.json` and put its icon in `icons/`.
