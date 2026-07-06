#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사진자료를 모아 assets/img/<id>/ 에 리사이즈/압축해 넣고 fortresses.json의 photos를 채운다.

출처:
  1) 06_현지조사자료/(260512_전문위원님 제공)/<왜성명>/         현장 조사사진 (전문위원 제공)
  2) 06_현지조사자료/(260519) 울산 조사 사진/                  현장 조사사진 (KakaoTalk, 울산왜성)
  3) 06_현지조사자료/<파일>.jpg (개별)                        옛 문서/사진엽서 (총독부박물관 등, 공공저작물)
  4) 03_항공사진_지도/<왜성명>/(20260519) ...드론사진/          드론 촬영(현장조사팀)
  5) 03_항공사진_지도/<왜성명>/(B040)항공사진_*.tif             항공사진(국토정보플랫폼, 공공데이터)
  6) 03_항공사진_지도/<왜성명>/(B120)종이지도_*.tif/jpg          옛 지도(국토정보플랫폼, 공공데이터)
  7) 03_항공사진_지도/부산 영도 왜성/<동삼동 지적도|청학동>/     지적도(국토정보플랫폼, 공공데이터)

* 사용자 지시에 따라 자료 활용 범위를 확대함(2026-07-06).
* 왜성 1곳당 최대 MAX_PER_FORTRESS 장, 우선순위: 현장/드론사진 > 항공사진 > 옛지도 > 지적도.
"""
import json
import re
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # 초대형 항공사진 TIFF 허용

ONEDRIVE = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간")
FIELD_DIR = ONEDRIVE / "06_현지조사자료"
AERIAL_DIR = ONEDRIVE / "03_항공사진_지도"
SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
IMG_OUT = SITE / "assets" / "img"
DATA_PATH = SITE / "data" / "fortresses.json"

MAX_PER_FORTRESS = 100
MAX_SIDE = 1600
JPEG_QUALITY = 78
IMG_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff")

PRIORITY = {"field": 0, "aerial": 1, "map": 2, "cadastral": 3, "archival": 1}

EXPERT_FOLDER_TO_IDS = {
    "고성왜성": [24], "구포왜성": [14], "기장왜성": [6], "남해왜성": [30], "농소왜성": [16],
    "동래왜성": [10], "마사왜성": [17], "망진왜성": [23], "사천왜성": [29], "순천왜성": [31],
    "양산왜성": [3], "임랑포": [5], "호포왜성": [4],
}

AERIAL_FOLDER_TO_IDS = {
    "가덕 왜성, 가덕지성": [11, 12],
    "거제 견내량왜성": [28],
    "거제 송진포, 장문포왜성": [26, 27],
    "거제 영등포왜성": [25],
    "고성왜성": [24],
    "기장 임랑 왜성": [5, 6],
    "남해왜성(선소왜성)": [30],
    "마사왜성": [17],
    "마산왜성": [22],
    "부산 영도 왜성": [15],
    "사천왜성(선진리왜성)": [29],
    "순천 왜성": [31],
    "울산 서생포 왜성": [2],
    "울산 왜성": [1],
    "죽도 농소왜성": [13, 16],
    "진주 망진왜성": [23],
    "창원 웅천, 안골포, 자마, 명동 왜성": [18, 19, 20, 21],
    "호포, 양산왜성": [3, 4],
}

ROOT_FILE_TO_ID = {
    "서생포왜성.jpg": (2, "archival", "서생포왜성(용성산) 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "임랑왜성.jpg": (5, "archival", "임랑포성 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "증산왜성.jpg": (3, "archival", "양산 증산성 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "울산 서생포 왜성 사진엽서(구입998, 부산박물관).jpg": (2, "archival", "서생포왜성 옛 사진엽서(부산박물관 소장)"),
}

CREDIT = {
    "field": "현장 조사(전문위원 제공)",
    "aerial": "국토정보플랫폼 항공사진(공공데이터)",
    "map": "국토정보플랫폼 옛 지도(공공데이터)",
    "cadastral": "국토정보플랫폼 지적도(공공데이터)",
    "archival": "조선총독부박물관 문서(국립중앙박물관 소장, 공공저작물)",
}

YEAR_RE = re.compile(r"^\((?:B040|B120)\)(?:항공사진|종이지도)_(\d{4})")


def caption_from_filename(name: str, folder_label: str, ptype: str) -> str:
    stem = Path(name).stem
    m = YEAR_RE.match(stem)
    if m:
        year = m.group(1)
        return f"{folder_label} 항공사진({year}년)" if ptype == "aerial" else f"{folder_label} 옛지도({year}년)"
    if ptype == "cadastral":
        return folder_label if "지적도" in folder_label else f"{folder_label} 지적도"
    if stem.startswith(folder_label):
        stem = stem[len(folder_label):].strip()
    stem = stem.strip(" -_,·")
    if stem.count("(") > stem.count(")"):
        stem = stem.rstrip("(").strip()
    return stem or folder_label


def save_resized(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, MAX_SIDE / max(w, h))
        if scale < 1.0:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)


def classify_aerial_file(path: Path) -> str:
    name = path.name
    if name.startswith("(B040)"):
        return "aerial"
    if name.startswith("(B120)"):
        return "map"
    if name.upper().startswith("DJI_"):
        return "field"
    return "cadastral"  # BJCA... 지적도 타일 등


def main():
    fortresses = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    by_id = {f["id"]: f for f in fortresses}

    # id별 후보 (path, ptype, caption, credit) 수집
    candidates = {f["id"]: [] for f in fortresses}

    # 1) 전문위원 제공
    expert_dir = FIELD_DIR / "(260512_전문위원님 제공)"
    for folder_name, ids in EXPERT_FOLDER_TO_IDS.items():
        folder = expert_dir / folder_name
        if not folder.exists():
            continue
        for src in sorted(folder.iterdir()):
            if src.suffix.lower() not in IMG_EXTS:
                continue
            cap = caption_from_filename(src.name, folder_name, "field")
            for fid in ids:
                candidates[fid].append((src, "field", cap))

    # 2) 울산 조사 사진 (KakaoTalk) -> 울산왜성(1)
    ulsan_dir = FIELD_DIR / "(260519) 울산 조사 사진"
    if ulsan_dir.exists():
        for src in sorted(ulsan_dir.iterdir()):
            if src.suffix.lower() in IMG_EXTS:
                candidates[1].append((src, "field", "울산왜성 현장 조사(2026-05-19)"))

    # 3) 항공사진_지도 (재귀적으로 하위 폴더 포함)
    for folder_name, ids in AERIAL_FOLDER_TO_IDS.items():
        folder = AERIAL_DIR / folder_name
        if not folder.exists():
            print("누락(항공):", folder_name)
            continue
        for src in sorted(folder.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in IMG_EXTS:
                continue
            ptype = classify_aerial_file(src)
            sub_label = src.parent.name if src.parent != folder else folder_name
            cap = caption_from_filename(src.name, sub_label, ptype)
            for fid in ids:
                candidates[fid].append((src, ptype, cap))

    # 4) 루트 개별 파일 (총독부박물관 문서 등)
    for fname, (fid, ptype, caption) in ROOT_FILE_TO_ID.items():
        src = FIELD_DIR / fname
        if src.exists():
            candidates[fid].append((src, ptype, caption))
        else:
            print("누락(루트):", fname)

    # 우선순위 정렬 후 상한 적용, 리사이즈 저장
    total_saved = 0
    for f in fortresses:
        fid = f["id"]
        items = candidates[fid]
        items.sort(key=lambda x: PRIORITY.get(x[1], 9))
        items = items[:MAX_PER_FORTRESS]

        photos = []
        for i, (src, ptype, caption) in enumerate(items):
            out_name = f"{i+1:03d}.jpg"
            dst = IMG_OUT / str(fid) / out_name
            try:
                save_resized(src, dst)
            except Exception as e:
                print(f"오류(id={fid}, {src.name}): {e}")
                continue
            photos.append({
                "file": f"assets/img/{fid}/{out_name}",
                "caption": caption,
                "type": ptype,
                "credit": CREDIT.get(ptype, ""),
            })
        f["photos"] = photos
        total_saved += len(photos)
        print(f"id={fid:>2} {f['name']:8s}: {len(photos):>3}/{len(items)}장")

    DATA_PATH.write_text(json.dumps(fortresses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n총 {total_saved}장, fortresses.json 갱신 완료")


if __name__ == "__main__":
    main()
