#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B-2 매트릭스(31개 왜성) + 05_왜성별탐사자료 텍스트를 결합해 data/fortresses.json 생성.
   좌표는 아직 없음(geocode_fortresses.py에서 별도로 채움)."""
import json
import re
import openpyxl
import pypdf
from pathlib import Path

ONEDRIVE = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간")
SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")

XLSX = ONEDRIVE / "_Claude작업_자료정리_20260705.xlsx"
SURVEY_DIR = ONEDRIVE / "05_왜성별탐사자료"

# 파일명(hanja) -> 번호 매핑 (PDF 본문 텍스트 대조로 확인 완료)
FILE_TO_ID = {
    "中央洞倭城.pdf": 9,
    "南海倭城 踏査用.pdf": 30,
    "固城倭城.pdf": 24,
    "子城台倭城.pdf": 8,
    "孤浦倭城.pdf": 4,
    "安骨浦倭城.pdf": 18,
    "影島倭城.pdf": 15,
    "望津倭城 踏査用.pdf": 23,
    "東莱倭城.pdf": 10,
    "林浦倭城.pdf": 5,
    "機張竹城里倭城　踏査用.pdf": 6,
    "竹島倭城.pdf": 13,
    "見乃梁城.pdf": 28,
    "農所倭城.pdf": 16,
    "釜山浦倭城.pdf": 7,
    "長門浦倭城.pdf": 27,
    "順天倭城 踏査用.pdf": 31,
    "馬沙倭城 踏査用.pdf": 17,
    "龜浦倭城.pdf": 14,
}


def extract_overview(pdf_path: Path, max_pages=8) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    parts = []
    for i, page in enumerate(reader.pages):
        if i >= max_pages:
            break
        t = page.extract_text() or ""
        if t.strip():
            parts.append(t)
    text = "\n".join(parts)
    # 가독성을 위해 불릿 항목마다 줄바꿈
    text = text.replace("•", "\n• ")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def main():
    id_to_file = {v: k for k, v in FILE_TO_ID.items()}

    wb = openpyxl.load_workbook(str(XLSX), data_only=True)
    ws = wb["B-2. 31왜성 매트릭스"]

    fortresses = []
    for row in ws.iter_rows(min_row=4, max_row=34, values_only=True):
        (번호, 왜성명, 별명, 소재지, 축조시기, 발굴이력, 문화재지정,
         *_rest, 상태) = row
        entry = {
            "id": 번호,
            "name": 왜성명,
            "alias": 별명,
            "address": 소재지,
            "era": 축조시기,
            "excavation": 발굴이력,
            "heritage": 문화재지정,
            "status": 상태,
            "lat": None,
            "lng": None,
            "overview": None,
            "overview_source": None,
        }

        pdf_name = id_to_file.get(번호)
        if pdf_name:
            pdf_path = SURVEY_DIR / pdf_name
            entry["overview"] = extract_overview(pdf_path)
            entry["overview_source"] = f"05_왜성별탐사자료/{pdf_name}"

        fortresses.append(entry)

    out_path = SITE / "data" / "fortresses.json"
    out_path.write_text(json.dumps(fortresses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장 완료: {out_path}  (총 {len(fortresses)}개, 본문 확보 {sum(1 for f in fortresses if f['overview'])}개)")


if __name__ == "__main__":
    main()
