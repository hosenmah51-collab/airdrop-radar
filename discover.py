#!/usr/bin/env python3
"""Discover Telegram game candidates from a maintained public catalogue.

Discovery is NOT proof of an airdrop, token, payout, or safety. This script
only imports Telegram game listings whose upstream status is 'ok' and preserves
the upstream source and last-checked date for human verification.
"""
from __future__ import annotations
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://raw.githubusercontent.com/coolpac/telegram-mini-apps-catalog/main/data/apps.json"
OUTPUT = ROOT / "data" / "discovery-candidates.json"

def main() -> int:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "AirdropRadar/1.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        upstream = json.load(response)

    candidates = []
    for app in upstream.get("apps", []):
        url = str(app.get("url", "")).strip()
        if app.get("category") != "Games" or app.get("status") != "ok":
            continue
        if not url.startswith("https://t.me/"):
            continue
        candidates.append({
            "id": "tma-" + str(abs(hash(url))),
            "name": app.get("name", "نامشخص"),
            "description": app.get("description", ""),
            "entry_url": url,
            "discovery_status": "نیازمند بررسی انسانی",
            "airdrop_status": "تأیید نشده",
            "token": "نامشخص",
            "claim_status": "نامشخص",
            "upstream_checked_at": app.get("lastChecked"),
            "upstream_status": app.get("status"),
            "source_url": SOURCE_URL,
            "source_pr": app.get("sourcePR", ""),
        })

    # Stable IDs across runs (unlike Python's randomized hash).
    import hashlib
    for item in candidates:
        item["id"] = "tma-" + hashlib.sha256(item["entry_url"].encode()).hexdigest()[:12]
    candidates.sort(key=lambda item: item["name"].casefold())

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": SOURCE_URL,
        "source_updated": upstream.get("updated"),
        "source_count": upstream.get("count"),
        "candidate_count": len(candidates),
        "important_notice": "این‌ها فقط بازی‌های تلگرامی کشف‌شده‌اند؛ وجود ایردراپ، توکن، امکان برداشت و امنیت آن‌ها تأیید نشده است.",
        "candidates": candidates,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Discovered {len(candidates)} Telegram game candidates; no airdrop claims were inferred.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
