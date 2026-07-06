#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/fortresses.json 기반으로 sitemap.xml 생성."""
import json
from pathlib import Path

SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
BASE_URL = "https://shinii0909-lab.github.io/waeseong-archive"

fortresses = json.loads((SITE / "data" / "fortresses.json").read_text(encoding="utf-8"))

urls = [
    (f"{BASE_URL}/", "1.0"),
    (f"{BASE_URL}/literature.html", "0.8"),
]
for f in sorted(fortresses, key=lambda x: x["id"]):
    urls.append((f"{BASE_URL}/fortress.html?id={f['id']}", "0.7"))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, priority in urls:
    lines.append(f"  <url><loc>{loc}</loc><priority>{priority}</priority></url>")
lines.append("</urlset>")

out = SITE / "sitemap.xml"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"저장 완료: {out} ({len(urls)}개 URL)")
