#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_왜성별탐사자료 PDF들의 텍스트를 추출해서 JSON으로 저장.
   나중에 어떤 파일이 어떤 왜성(번호)에 해당하는지 사람이 눈으로 확인하기 위한 1차 덤프."""
import json
import pypdf
from pathlib import Path

SRC = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간\05_왜성별탐사자료")
OUT = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site\scripts\survey_text_dump.json")

result = {}
for pdf_path in sorted(SRC.glob("*.pdf")):
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        pages_text = []
        for i, page in enumerate(reader.pages):
            if i >= 6:
                break
            pages_text.append(page.extract_text() or "")
        full = "\n".join(pages_text)
        result[pdf_path.name] = {
            "num_pages": len(reader.pages),
            "text": full[:6000],
        }
        print(f"OK  {pdf_path.name}  pages={len(reader.pages)}  chars={len(full)}")
    except Exception as e:
        print(f"ERR {pdf_path.name}: {e}")
        result[pdf_path.name] = {"error": str(e)}

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved to", OUT)
