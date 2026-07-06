#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_연구문헌 폴더를 스캔해서 서지정보만 담은 data/literature.json 생성.
   저작권 문제 회피를 위해 원문 PDF는 링크/복사하지 않고 서지사항(저자/연도/제목/학술지/학회)만 기록한다."""
import json
import re
from pathlib import Path

ONEDRIVE = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간")
LIT_DIR = ONEDRIVE / "01_연구문헌"
SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")

YEAR_RE = re.compile(r"(18|19|20)\d{2}")


def parse_filename(stem: str, category: str):
    """'저자, 연도, 제목, 학술지, 학회' 형태를 최대한 파싱. 실패하면 title만 채움."""
    parts = [p.strip() for p in stem.split(",")]
    year_idx = None
    for i, p in enumerate(parts):
        if YEAR_RE.fullmatch(p.strip()):
            year_idx = i
            break
    if year_idx is not None and year_idx >= 1:
        author = ", ".join(parts[:year_idx])
        year = parts[year_idx]
        rest = parts[year_idx + 1:]
        title = rest[0] if rest else stem
        journal = rest[1] if len(rest) > 1 else None
        publisher = rest[2] if len(rest) > 2 else None
        return {
            "author": author, "year": year, "title": title,
            "journal": journal, "publisher": publisher, "category": category,
        }
    # 파싱 실패: 파일명 전체를 제목으로
    return {
        "author": None, "year": None, "title": stem,
        "journal": None, "publisher": None, "category": category,
    }


def main():
    entries = []
    seen = set()

    def add_from(dir_path: Path, category: str):
        if not dir_path.exists():
            return
        for f in sorted(dir_path.glob("*.pdf")):
            if f.name in seen:
                continue
            seen.add(f.name)
            entries.append(parse_filename(f.stem, category))

    add_from(LIT_DIR, "학술논문")
    add_from(LIT_DIR / "단행본", "단행본")
    add_from(LIT_DIR / "기타학술자료", "기타학술자료")
    add_from(LIT_DIR / "倭城の研究시리즈", "倭城の研究 시리즈(일본)")

    entries.sort(key=lambda e: (e["year"] is None, e["year"] or "", e["author"] or e["title"]))

    out_path = SITE / "data" / "literature.json"
    out_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장 완료: {out_path} (총 {len(entries)}건)")


if __name__ == "__main__":
    main()
