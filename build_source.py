#!/usr/bin/env python3
"""Builds source.json (AltStore / SideStore source) from apps.json.

For every app listed in apps.json, the GitHub releases of its repo are read and
each release that carries the app's .ipa becomes one entry in "versions".
Release tags are expected to look like v1.0.7.
"""
import json
import os
import sys
import urllib.request

MAX_VERSIONS = 5


def releases(repo):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases?per_page=20",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "houndapps"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def versions_for(app):
    found = []
    for release in releases(app["repo"]):
        if release.get("draft") or release.get("prerelease"):
            continue
        asset = next((a for a in release.get("assets", []) if a["name"] == app["asset"]), None)
        if asset is None:
            continue
        version = release["tag_name"].lstrip("v")
        if version in app.get("skipVersions", []):
            continue
        entry = {
            "version": version,
            "buildVersion": version.split(".")[-1],
            "date": release["published_at"],
            "localizedDescription": (release.get("body") or "").strip() or f"Version {version}",
            "downloadURL": asset["browser_download_url"],
            "size": asset["size"],
        }
        if app.get("minOSVersion"):
            entry["minOSVersion"] = app["minOSVersion"]
        found.append(entry)
    found.sort(key=lambda v: v["date"], reverse=True)   # newest first: the first entry is "latest"
    return found[:MAX_VERSIONS]


def main():
    with open("apps.json") as f:
        config = json.load(f)

    apps = []
    for app in config["apps"]:
        versions = versions_for(app)
        if not versions:
            print(f"skip {app['name']}: no release with {app['asset']}", file=sys.stderr)
            continue
        latest = versions[0]
        apps.append({
            "name": app["name"],
            "bundleIdentifier": app["bundleIdentifier"],
            "developerName": app["developerName"],
            "subtitle": app.get("subtitle", ""),
            "localizedDescription": app.get("localizedDescription", ""),
            "iconURL": app["iconURL"],
            "tintColor": app.get("tintColor", "000000"),
            "category": app.get("category", "other"),
            "screenshots": [],
            "versions": versions,
            "appPermissions": {"entitlements": [], "privacy": app.get("privacy", {})},
            # Older source format, kept so every AltStore / SideStore version can read it.
            "version": latest["version"],
            "versionDate": latest["date"],
            "versionDescription": latest["localizedDescription"],
            "downloadURL": latest["downloadURL"],
            "size": latest["size"],
        })

    source = dict(config["source"])
    source["apps"] = apps
    source["featuredApps"] = [a["bundleIdentifier"] for a in apps]
    source["news"] = []

    with open("source.json", "w") as f:
        json.dump(source, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote source.json with {len(apps)} app(s)")


if __name__ == "__main__":
    main()
