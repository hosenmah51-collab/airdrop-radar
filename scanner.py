#!/usr/bin/env python3
"""Validate the curated opportunity catalogue without inventing project facts.

The scanner intentionally does not scrape arbitrary Telegram bots or infer token/
claim status. Add projects only after checking their official sources.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "opportunities.json"
ALLOWED_STATUS = {"فعال", "در انتظار", "پایان‌یافته"}
ALLOWED_CLAIM = {"قابل Claim", "در انتظار", "غیرفعال", "نامشخص"}
REQUIRED = ("id", "name", "category", "description", "status", "source_url")

def valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"https", "http"} and bool(parsed.netloc)
    except Exception:
        return False

def main() -> int:
    if not DATA.exists():
        raise SystemExit("ERROR: data/opportunities.json not found")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(payload.get("opportunities"), list):
        raise SystemExit("ERROR: opportunities must be a JSON array")

    seen = set()
    warnings = []
    for index, item in enumerate(payload["opportunities"], start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"ERROR: item {index} is not an object")
        missing = [key for key in REQUIRED if not item.get(key)]
        if missing:
            raise SystemExit(f"ERROR: item {index} missing: {', '.join(missing)}")
        if item["id"] in seen:
            raise SystemExit(f"ERROR: duplicate id: {item['id']}")
        seen.add(item["id"])
        if item["status"] not in ALLOWED_STATUS:
            raise SystemExit(f"ERROR: invalid status for {item['id']}")
        if item.get("claim_status", "نامشخص") not in ALLOWED_CLAIM:
            raise SystemExit(f"ERROR: invalid claim_status for {item['id']}")
        for key in ("source_url", "entry_url", "website", "telegram"):
            if item.get(key) and not valid_http_url(item[key]):
                raise SystemExit(f"ERROR: invalid URL in {item['id']}: {key}")
        if not item.get("checked_at"):
            warnings.append(f"{item['id']}: checked_at is empty")
        if not item.get("source_url"):
            warnings.append(f"{item['id']}: no evidence source")

    payload["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: validated {len(seen)} opportunities")
    for warning in warnings:
        print("WARNING:", warning)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
