#!/usr/bin/env python3
"""Refresh the official UI plugin registry from oh-my-hita/ui-* releases."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ORG = "oh-my-hita"


def gh(*args: str):
    return subprocess.check_output(["gh", *args], text=True)


def get_json(*args: str):
    return json.loads(gh("api", *args))


def main() -> None:
    repos = get_json(f"orgs/{ORG}/repos?per_page=100")
    entries = []
    for repo in repos:
        name = repo.get("name", "")
        if not name.startswith("ui-") or repo.get("archived"):
            continue
        full = f"{ORG}/{name}"
        try:
            meta_b64 = get_json(
                f"repos/{full}/contents/ui-plugin/src/main/assets/plugin.json"
            )["content"]
            meta = json.loads(base64.b64decode(meta_b64).decode("utf-8"))
            release = get_json(f"repos/{full}/releases/latest")
        except subprocess.CalledProcessError as exc:
            print(f"skip {full}: {exc}")
            continue
        assets = [a for a in release.get("assets", []) if a.get("name", "").endswith(".apk")]
        if not assets:
            print(f"skip {full}: no APK asset")
            continue
        asset = assets[0]
        with tempfile.NamedTemporaryFile(suffix=".apk") as tmp:
            req = urllib.request.Request(asset["browser_download_url"], headers={"User-Agent": "oh-my-hita-registry"})
            with urllib.request.urlopen(req, timeout=120) as response:
                data = response.read()
            tmp.write(data)
            tmp.flush()
            sha = hashlib.sha256(data).hexdigest()
        entry = {
            "id": meta.get("id", name),
            "name": meta.get("name", name),
            "version": meta.get("version", release.get("tag_name", "").removeprefix("v")),
            "url": asset["browser_download_url"],
            "sha256": sha,
            "size": len(data),
            "minHostApi": 10,
            "description": meta.get("description", "OH-MY-HITA 官方界面插件"),
            "author": "OH-MY-HITA",
            "tags": ["HITA", "official"],
            "repo": f"https://github.com/{full}",
        }
        for key in ("capabilities", "mainTabs", "composeVersion"):
            if key in meta:
                entry[key] = meta[key]
        entries.append(entry)
        print(f"ok {full} {entry['version']}")

    entries.sort(key=lambda x: x["id"])
    path = Path("registry/index.json")
    old = json.loads(path.read_text()) if path.exists() else {}
    # 手工维护的 UI 条目（例如来自宿主 release 的 3.3.x 插件）不随 ui-* 刷新丢失。
    manual = [e for e in old.get("uiPlugins", []) if e.get("manual")]
    auto_ids = {e["id"] for e in entries}
    entries.extend(e for e in manual if e["id"] not in auto_ids)
    entries.sort(key=lambda x: x["id"])
    index = {
        "plugins": old.get("plugins", []),
        "uiPlugins": entries,
        "presets": old.get("presets", []),
    }
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {len(entries)} UI plugins ({len(manual)} manual)")


if __name__ == "__main__":
    if not os.environ.get("GH_TOKEN"):
        raise SystemExit("GH_TOKEN is required")
    main()
