#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카카오 로컬 API(주소 검색)로 31개 왜성 좌표를 재지오코딩.
   지번(산 XX) 주소 인식이 Nominatim보다 훨씬 정확해서 전체를 다시 맞춘다.
   주의: REST API 키는 이 스크립트에만 사용하고 git에는 커밋하지 않는다."""
import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

REST_KEY = os.environ.get("KAKAO_REST_KEY")
if not REST_KEY:
    raise SystemExit("KAKAO_REST_KEY 환경변수를 설정하세요 (카카오 개발자 콘솔의 REST API 키).")
SITE = Path(r"C:\Users\SSKIM-PLAY\Documents\waeseong-site")
DATA_PATH = SITE / "data" / "fortresses.json"

# 지금까지 조사로 확인된 가장 신뢰도 높은 주소 (지번 우선)
BEST_ADDRESS = {
    1: "울산광역시 중구 학성동",
    2: "울산광역시 울주군 서생면 서생리",
    3: "경상남도 양산시 물금읍 증산리 산15",
    4: "경상남도 양산시 동면 가산리",
    5: "부산광역시 기장군 장안읍 임랑리 산25",
    6: "부산광역시 기장군 기장읍 죽성리 601",
    7: "부산광역시 동구 좌천동",
    8: "부산광역시 동구 범일동 690-5",
    9: "부산광역시 중구 중앙동7가",
    10: "부산광역시 동래구 복산동",
    11: "부산광역시 강서구 눌차동",
    12: "부산광역시 강서구 성북동",
    13: "부산광역시 강서구 죽림동 787",
    14: "부산광역시 북구 덕천1동 산93",
    15: "부산광역시 영도구 동삼동 산137",
    16: "경상남도 김해시 주촌면 농소리 산1-1",
    17: "경상남도 김해시 생림면 마사리",
    18: "경상남도 창원시 진해구 안골동 산27",
    19: "경상남도 창원시 진해구 남문동 산211-1",
    20: "경상남도 창원시 진해구 웅천동",
    21: "경상남도 창원시 진해구 명동",
    22: "경상남도 창원시 마산합포구 산호동",
    23: "경상남도 진주시 망경동",
    24: "경상남도 고성군 고성읍 수남리 64-1",
    25: "경상남도 거제시 장목면 구영리 산6-17",
    26: "경상남도 거제시 장목면 장목리 산6-3",
    27: "경상남도 거제시 장목면 장목리 산130-43",
    28: "경상남도 거제시 사등면 덕호리 262",
    29: "경상남도 사천시 용현면 선진리 770",
    30: "경상남도 남해군 남해읍 선소리 192-14",
    31: "전라남도 순천시 해룡면 신성리 산1",
}


def kakao_geocode(query):
    url = "https://dapi.kakao.com/v2/local/search/address.json?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={"Authorization": f"KakaoAK {REST_KEY}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    docs = data.get("documents", [])
    if docs:
        d = docs[0]
        return float(d["y"]), float(d["x"]), d["address_name"]
    return None, None, None


def main():
    fortresses = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    by_id = {f["id"]: f for f in fortresses}

    for fid, addr in BEST_ADDRESS.items():
        f = by_id[fid]
        lat, lng, matched = kakao_geocode(addr)
        if lat is None:
            print(f"실패: id={fid} {f['name']}  주소='{addr}'")
        else:
            before = (f["lat"], f["lng"])
            f["lat"], f["lng"] = lat, lng
            f["address"] = addr
            print(f"id={fid:>2} {f['name']:8s} {before} -> ({lat:.6f}, {lng:.6f})  [{matched}]")
        time.sleep(0.15)

    DATA_PATH.write_text(json.dumps(fortresses, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n저장 완료")


if __name__ == "__main__":
    main()
