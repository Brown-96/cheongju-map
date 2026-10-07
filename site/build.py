"""candidates.csv + 동 경계 + template.html → 자체 완결형 HTML 두 개.
  index.html    : 정적 호스팅에 그대로 올리는 완전한 페이지
  artifact.html : 미리보기(Claude 아티팩트)용 조각 (doctype/head 없음)
사용: python3 site/build.py
"""
import csv, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "cheongju", "candidates.csv")

# 카카오 JavaScript 키(공개용 키, 등록된 도메인에서만 동작)
KAKAO_JS_KEY = "561045556c30f64d6151161914e68f87"

rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
cands = []
for r in rows:
    cands.append({
        "id": int(r["id"]), "g": r["구분"][0], "name": r["이름"], "gu": r["구"], "dong": r["읍면동"],
        "addr": r["리/상세주소"], "type": r["유형"], "scale": r["규모"], "period": r["시기"], "price": r["가격"],
        "feature": r["특징"], "confidence": r["확실도"],
        "sources": re.findall(r"https?://[^\s;]+", r["출처"]),
        "lon": float(r["경도"]), "lat": float(r["위도"]),
        "precision": r.get("좌표정확도") or "정확", "precisionNote": r.get("좌표근거", ""),
    })
assert all(c["g"] in "ABC" for c in cands)
assert all(36.3 < c["lat"] < 36.9 and 127.2 < c["lon"] < 127.8 for c in cands), "청주 밖 좌표"

dong = open(os.path.join(HERE, "data", "cheongju_dong.geojson"), encoding="utf-8").read()
json.loads(dong)
css = open(os.path.join(HERE, "vendor", "leaflet.css"), encoding="utf-8").read()
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

def j(x):  # </script> 깨짐 방지
    return json.dumps(x, ensure_ascii=False).replace("</", "<\\/")

body = (tpl.replace("/*LEAFLET_CSS*/", css)
           .replace("/*CANDIDATES_JSON*/", j(cands))
           .replace("/*DONG_GEOJSON*/", dong.replace("</", "<\\/"))
           .replace("/*KAKAO_JS_KEY*/", KAKAO_JS_KEY))
assert "/*" + "CANDIDATES_JSON" not in body
open(os.path.join(HERE, "artifact.html"), "w", encoding="utf-8").write(body)

head, rest = body.split("</style>\n\n", 1)  # <title>…스타일까지는 head로
page = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + head + "</style>\n</head>\n<body>\n" + rest + "</body>\n</html>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
print(f"후보 {len(cands)}곳 → index.html {len(page)//1024}KB, artifact.html")
