#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_현지조사자료의 사진들을 리사이즈/압축해 assets/img/<id>/ 에 넣고
   data/fortresses.json에 photos 배열을 채운다.
   - 조선총독부(박물관) 관련 옛 문서/사진: 공공저작물(저작권 없음)로 판단, 포함
   - 전문위원 제공 현장 사진, 울산 답사 사진: 팀 조사자료로 포함
   * 사용자 지시에 따라 자료 활용 범위를 확대함(2026-07-06)."""
import json
from pathlib import Path
from PIL import Image

ONEDRIVE = Path(r"C:\Users\SSKIM-PLAY\OneDrive\6. 업무\2026년\왜성 보고서 발간")
FIELD_DIR = ONEDRIVE / "06_현지조사자료"
SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
IMG_OUT = SITE / "assets" / "img"
DATA_PATH = SITE / "data" / "fortresses.json"

MAX_PER_FOLDER = 8
MAX_SIDE = 1600
JPEG_QUALITY = 78

FOLDER_TO_ID = {
    "고성왜성": 24, "구포왜성": 14, "기장왜성": 6, "남해왜성": 30, "농소왜성": 16,
    "동래왜성": 10, "마사왜성": 17, "망진왜성": 23, "사천왜성": 29, "순천왜성": 31,
    "양산왜성": 3, "임랑포": 5, "호포왜성": 4,
}

ROOT_FILE_TO_ID = {
    "서생포왜성.jpg": (2, "archival", "서생포왜성(용성산) 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "임랑왜성.jpg": (5, "archival", "임랑포성 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "증산왜성.jpg": (3, "archival", "양산 증산성 국유림 경계도(국립중앙박물관 소장 조선총독부박물관 문서)"),
    "울산 서생포 왜성 사진엽서(구입998, 부산박물관).jpg": (2, "archival", "서생포왜성 옛 사진엽서(부산박물관 소장)"),
}


def save_resized(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, MAX_SIDE / max(w, h))
        if scale < 1.0:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)


def caption_from_filename(name: str, folder_label: str) -> str:
    stem = Path(name).stem
    if stem.startswith(folder_label):
        stem = stem[len(folder_label):].strip()
    # 파일명 끝의 미완성 괄호·구두점 제거, 짝 안 맞는 괄호 정리
    stem = stem.strip(" -_,·")
    if stem.count("(") > stem.count(")"):
        stem = stem.rstrip("(").strip()
    return stem or folder_label


def main():
    fortresses = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    by_id = {f["id"]: f for f in fortresses}
    for f in fortresses:
        f["photos"] = []

    # 1) 전문위원 제공 왜성별 현장사진
    expert_dir = FIELD_DIR / "(260512_전문위원님 제공)"
    for folder_name, fid in FOLDER_TO_ID.items():
        folder = expert_dir / folder_name
        if not folder.exists():
            continue
        files = sorted([p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
        for i, src in enumerate(files[:MAX_PER_FOLDER]):
            out_name = f"{i+1:02d}.jpg"
            dst = IMG_OUT / str(fid) / out_name
            save_resized(src, dst)
            by_id[fid]["photos"].append({
                "file": f"assets/img/{fid}/{out_name}",
                "caption": caption_from_filename(src.name, folder_name),
                "type": "field",
                "credit": "현장 조사(전문위원 제공)",
            })
        print(f"{folder_name}(id={fid}): {min(len(files), MAX_PER_FOLDER)}/{len(files)}장 처리")

    # 2) 울산 답사 사진 (KakaoTalk) -> 울산왜성(id1)
    ulsan_dir = FIELD_DIR / "(260519) 울산 조사 사진"
    if ulsan_dir.exists():
        files = sorted([p for p in ulsan_dir.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
        for i, src in enumerate(files):
            out_name = f"{i+1:02d}.jpg"
            dst = IMG_OUT / "1" / out_name
            save_resized(src, dst)
            by_id[1]["photos"].append({
                "file": f"assets/img/1/{out_name}",
                "caption": "울산왜성 현장 조사(2026-05-19)",
                "type": "field",
                "credit": "현장 조사팀",
            })
        print(f"울산왜성(id=1): {len(files)}장 처리")

    # 3) 루트 개별 파일 (총독부박물관 문서 스캔 / 옛 사진엽서 등, 공공저작물)
    idx_by_id = {}
    for fname, (fid, ptype, caption) in ROOT_FILE_TO_ID.items():
        src = FIELD_DIR / fname
        if not src.exists():
            print("누락:", fname)
            continue
        idx_by_id[fid] = idx_by_id.get(fid, 0) + 1
        out_name = f"archival_{idx_by_id[fid]:02d}.jpg"
        dst = IMG_OUT / str(fid) / out_name
        save_resized(src, dst)
        by_id[fid]["photos"].append({
            "file": f"assets/img/{fid}/{out_name}",
            "caption": caption,
            "type": ptype,
            "credit": "조선총독부박물관 문서(국립중앙박물관 소장, 공공저작물)" if ptype == "archival" else "현장 조사팀",
        })
        print(f"{fname} -> id={fid} 처리")

    DATA_PATH.write_text(json.dumps(fortresses, ensure_ascii=False, indent=2), encoding="utf-8")
    total_photos = sum(len(f["photos"]) for f in fortresses)
    print(f"\n총 {total_photos}장, fortresses.json 갱신 완료")


if __name__ == "__main__":
    main()
