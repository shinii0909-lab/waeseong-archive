#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""00_기준자료/0304왜성문헌(연대별).docx 를 마스터 서지목록으로 파싱해
   data/literature.json 을 재생성한다.

   원문 구조:
   - `○ YYYY년` : 연도 구분 헤더
   - `저자,연도,「제목」,『수록지』권호,발행처.` : 논문
   - `저자,연도,『서명』,출판사.` : 저서·보고서
   - 연도 없는 `저자「제목」` : 직전 논집(단행본)에 수록된 개별 논문
   - 연도·괄호 없는 짧은 줄 : 논집 내 부(部) 제목 → 다음 수록논문들의 접두어
   - 연도 있는 줄이 콤마로 끝나면 다음 줄이 이어지는 내용(발행처 등)
"""
import json
import re
import unicodedata
from pathlib import Path

SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
RAW = SITE / "scripts" / "raw_0304.txt"
ONEDRIVE = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간")
LIT_DIR = ONEDRIVE / "01_연구문헌"

HANGUL_RE = re.compile(r"[가-힣]")
YEAR_HDR_RE = re.compile(r"^○\s*(\d{4})년")
YEAR_IN_LINE_RE = re.compile(r"(\d{4})(?:\s*[•·\-~〜]\s*\d{2,4})?")
CHAPTER_RE = re.compile(r"^([^「」『』]*?)[「『](.+?)[」』]?$")


def normalize_for_match(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\(\（][^\)\）]*[\)\）]", "", s)
    s = re.sub(r"[\s,\.\-―–‐~〜:;·•․「」『』《》\"'‘’“”_]", "", s)
    return s.lower()


def categorize(line: str, has_article_brackets: bool) -> str:
    if "학위논문" in line:
        return "학위논문"
    return "논문" if has_article_brackets else "저서·보고서"


def parse_dated_line(line: str, year_hint: str):
    entry = {
        "author": None, "year": year_hint, "title": None,
        "journal": None, "publisher": None,
        "category": None, "lang": None, "held": False,
    }
    m = YEAR_IN_LINE_RE.search(line)
    if m:
        entry["year"] = m.group(1)

    art = re.search(r"「(.+?)」", line)
    book_titles = re.findall(r"『(.+?)』", line)
    if art:
        entry["title"] = art.group(1).strip()
        entry["category"] = categorize(line, True)
        after = line[art.end():]
        j = re.search(r"『(.+?)』", after)
        if j:
            vol = re.match(r"\s*([0-9\-‐–―・•·]+)", after[j.end():])
            entry["journal"] = j.group(1).strip() + ((" " + vol.group(1).strip()) if vol else "")
        elif "학위논문" in line:
            # 「제목」, XX대학교 석/박사학위논문
            tail = after.strip().lstrip(",，").rstrip(".").strip()
            entry["journal"] = tail
    elif book_titles:
        entry["title"] = book_titles[0].strip()
        entry["category"] = categorize(line, False)
    else:
        parts = [p.strip() for p in line.split(",")]
        entry["title"] = (parts[2] if len(parts) >= 3 else line).rstrip(".")
        entry["category"] = categorize(line, False)

    if m and m.start() > 0:
        author = line[:m.start()].strip().rstrip(",，").strip()
        entry["author"] = author or None

    tail_start = max(line.rfind("」"), line.rfind("』"))
    tail = line[tail_start + 1:] if tail_start >= 0 else ""
    tail = tail.strip().lstrip(",，").rstrip(".").strip()
    tail = re.sub(r"^[0-9\-‐–―・•·]+\s*[,，]?\s*", "", tail)
    if tail and "학위논문" not in tail:
        entry["publisher"] = tail
    elif tail and entry["category"] == "학위논문" and not entry["journal"]:
        entry["journal"] = tail

    entry["lang"] = "국문" if HANGUL_RE.search(entry["title"] or "") else "일문"
    return entry


def main():
    lines = [l.strip() for l in RAW.read_text(encoding="utf-8").splitlines() if l.strip()]

    # 1) 콤마로 끝나는 줄 병합 (다음 줄에 연도가 없을 때)
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        while (line.endswith((",", "，")) and i + 1 < len(lines)
               and not YEAR_IN_LINE_RE.search(lines[i + 1][:20])
               and not lines[i + 1].startswith("○")):
            i += 1
            line = line + " " + lines[i]
        merged.append(line)
        i += 1

    entries = []
    year_hint = None
    parent = None      # 직전 논집(단행본) 엔트리
    section = None     # 논집 내 부(部) 제목

    for line in merged:
        if line.startswith("왜성 연구 목록"):
            continue
        hm = YEAR_HDR_RE.match(line)
        if hm:
            year_hint = hm.group(1)
            continue

        has_year = bool(YEAR_IN_LINE_RE.search(line))
        if has_year:
            e = parse_dated_line(line, year_hint)
            entries.append(e)
            if e["category"] == "저서·보고서":
                parent = e
                section = None
            continue

        # 연도 없는 줄: 논집 수록논문 or 부제목
        cm = CHAPTER_RE.match(line)
        if cm and ("「" in line or "『" in line):
            author = cm.group(1).strip().rstrip(",，·•･") or None
            title = cm.group(2).strip()
            if section:
                title = f"{section}－{title}"
            entries.append({
                "author": author,
                "year": parent["year"] if parent else year_hint,
                "title": title,
                "journal": parent["title"] if parent else None,
                "publisher": parent["publisher"] if parent else None,
                "category": "논문",
                "lang": "국문" if HANGUL_RE.search(title) else "일문",
                "held": False,
            })
        else:
            # 괄호 없는 짧은 줄 = 부(部) 제목
            section = line.rstrip(".")

    # 로컬 소장 PDF 대조
    local_keys = set()
    for sub in ["", "단행본", "기타학술자료", "倭城の研究시리즈"]:
        d = LIT_DIR / sub if sub else LIT_DIR
        if d.exists():
            for f in d.glob("*.pdf"):
                local_keys.add(normalize_for_match(f.stem))

    matched = 0
    for e in entries:
        tkey = normalize_for_match(e["title"] or "")
        if len(tkey) < 4:
            continue
        if any(tkey in lk for lk in local_keys):
            e["held"] = True
            matched += 1

    entries.sort(key=lambda e: (e["year"] or "9999", e["author"] or ""))

    out = SITE / "data" / "literature.json"
    out.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    cats = {}
    for e in entries:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"총 {len(entries)}건 저장 → {out}")
    print("분류:", cats)
    print("언어:", {l: sum(1 for e in entries if e['lang'] == l) for l in ('국문', '일문')})
    print("로컬 소장 매칭:", matched)


if __name__ == "__main__":
    main()
