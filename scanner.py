#!/usr/bin/env python3
"""Validate catalog data and expire opportunities whose deadline has passed."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data/opportunities.json"
DISCOVERY=ROOT/"data/discovery-candidates.json"
ALLOWED={"فعال","در انتظار","پایان‌یافته"}
CLAIM={"قابل Claim","در انتظار","غیرفعال","نامشخص"}
def valid_url(s):
 try:
  p=urlparse(s); return p.scheme in {"https","http"} and bool(p.netloc)
 except Exception: return False
def main():
 now=datetime.now(timezone.utc); today=now.date().isoformat()
 payload=json.loads(DATA.read_text(encoding="utf-8"))
 if not isinstance(payload.get("opportunities"),list): raise SystemExit("opportunities must be an array")
 ids=set()
 for i,x in enumerate(payload["opportunities"],1):
  if not isinstance(x,dict): raise SystemExit(f"opportunity {i} is not an object")
  for k in ("id","name","category","description","status","source_url","entry_url"):
   if not x.get(k): raise SystemExit(f"opportunity {i} missing {k}")
  if x["id"] in ids: raise SystemExit("duplicate opportunity id: "+x["id"])
  ids.add(x["id"])
  if x["status"] not in ALLOWED or x.get("claim_status","نامشخص") not in CLAIM: raise SystemExit("invalid status: "+x["id"])
  for k in ("source_url","entry_url","website","telegram"):
   if x.get(k) and not valid_url(x[k]): raise SystemExit("invalid URL: "+x["id"]+"/"+k)
  if x.get("deadline") and x["deadline"]<today:
   x["status"]="پایان‌یافته"; x["claim_status"]="غیرفعال"
  x["checked_at"]=today
 payload["last_updated"]=now.strftime("%Y-%m-%d %H:%M UTC")
 DATA.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 if DISCOVERY.exists():
  d=json.loads(DISCOVERY.read_text(encoding="utf-8")); seen=set()
  for i,x in enumerate(d.get("candidates",[]),1):
   for k in ("id","name","entry_url","source_url","airdrop_status"):
    if not x.get(k): raise SystemExit(f"candidate {i} missing {k}")
   if x["id"] in seen: raise SystemExit("duplicate candidate id")
   seen.add(x["id"])
   if x["airdrop_status"]!="تأیید نشده": raise SystemExit("candidate incorrectly marked verified")
   for k in ("entry_url","source_url"):
    if not valid_url(x[k]): raise SystemExit("invalid candidate URL")
  print(f"Validated {len(seen)} discovery candidates")
 print(f"Validated {len(ids)} opportunities; refreshed {today}")
if __name__=="__main__": main()
