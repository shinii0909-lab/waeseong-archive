#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/fortresses.json의 address를 Nominatim(OSM)으로 지오코딩하여 lat/lng 채움.
   Nominatim 사용정책: 1req/sec, 커스텀 User-Agent 필수."""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
DATA_PATH = SITE / "data" / "fortresses.json"

HEADERS = {"User-Agent": "waeseong-site-geocoder/0.1 (personal research project)"}


def geocode(query: str):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": query, "format": "json", "limit": 1, "countrycodes": "kr",
    })
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


def main():
    fortresses = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for f in fortresses:
        if f.get("lat"):
            continue
        addr = f["address"]
        lat, lng = geocode(addr)
        if lat is None:
            # 주소를 좀 더 단순화(마지막 지번 등 제거)해서 재시도
            simplified = " ".join(addr.split()[:-1]) if len(addr.split()) > 1 else addr
            time.sleep(1.1)
            lat, lng = geocode(simplified)
        f["lat"], f["lng"] = lat, lng
        print(f"{f['id']:>2} {f['name']:8s} {addr}  -> {lat}, {lng}")
        time.sleep(1.1)

    DATA_PATH.write_text(json.dumps(fortresses, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [f["name"] for f in fortresses if not f.get("lat")]
    print("\n미확인:", missing if missing else "없음")


if __name__ == "__main__":
    main()
