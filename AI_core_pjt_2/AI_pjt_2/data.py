"""데이터 준비 — 공공데이터 학과정보로 대학 목록을 만들고, 위키백과에서 문서를 가져온다.

    python data.py        # data/universities.json 생성

출처와 이용 조건
- 한국대학교육협의회_대학별 학과정보 (공공데이터포털, 이용허락범위 제한 없음)
- 한국어 위키백과 (CC BY-SA 4.0)
"""
import json
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

import requests

import config

KCUE_URL = "https://apis.data.go.kr/B340014/SchoolMajorInfoService/getSchoolMajorInfo"
KCUE_PAGE = "https://www.data.go.kr/data/15158666/openapi.do"
WIKI_URL = "https://ko.wikipedia.org/w/api.php"
YEAR = 2025

DISCLAIMER = (
    "2025년 대학정보공시와 위키백과 문서를 근거로 안내합니다. 입학정원·전형은 해마다 바뀌므로 "
    "지원 전에는 반드시 각 대학 입학처의 최신 모집요강을 확인하세요. 진학 상담을 대신하지 않습니다."
)

# 화면에 보여줄 검색 조건 안내
SEARCHABLE = [
    "**지역(시·도)**: 서울, 부산, 경기, 충남 …",
    "**학과명**: 간호학과, 컴퓨터공학과, 해양 관련 학과 … (여러 개면 모두 있는 대학)",
    "**학교 이름에 들어간 말**: 여자대학교, 교육대학교, 가톨릭, 신학 …",
    "**특정 대학**: 연세대, 경상국립대 … (설립·캠퍼스·역사는 위키백과 근거)",
]
NOT_SEARCHABLE = [
    "**국립/공립/사립 구분**: 공시 데이터에 설립 유형이 없어, 이름에 '국립'이 들어간 학교만 찾습니다 (서울대·부산대 등은 빠짐)",
    "**순위·합격선·경쟁률·취업률·등록금**: 수집한 데이터에 없습니다",
    "**KAIST·GIST·UNIST·DGIST·한예종·경찰대·사관학교**: 공시 대상이 아니라 데이터에 없습니다",
    "**전문대학·대학원**: 4년제 학사과정만 담았습니다",
]
# 질문에 이 말이 있으면 답변에 경고를 붙인다
LIMIT_NOTES = {
    ("국립", "사립", "공립"): "국립/사립 구분 데이터가 없어 이름에 '국립'이 들어간 학교만 찾을 수 있습니다. 서울대·부산대처럼 이름에 '국립'이 없는 국립대는 빠집니다.",
    ("순위", "랭킹", "합격선", "커트라인", "경쟁률", "취업률", "등록금"): "순위·합격선·경쟁률·취업률·등록금은 수집한 데이터에 없어 답할 수 없습니다.",
    ("카이스트", "KAIST", "과학기술원", "사관학교", "경찰대", "예술종합"): "과학기술원·사관학교·경찰대·한국예술종합학교는 공시 데이터 대상이 아니라 정보가 없습니다.",
}


def limit_notes(question: str) -> list[str]:
    return [note for words, note in LIMIT_NOTES.items() if any(w.lower() in question.lower() for w in words)]


REGIONS = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시",
    "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "세종": "세종특별자치시",
    "경기": "경기도", "강원": "강원도", "충북": "충청북도", "충남": "충청남도", "전북": "전라북도",
    "전남": "전라남도", "경북": "경상북도", "경남": "경상남도", "제주": "제주특별자치도",
    "충청북": "충청북도", "충청남": "충청남도", "전라북": "전라북도", "전라남": "전라남도",
    "경상북": "경상북도", "경상남": "경상남도",
}


# ── 외부 API 호출 (재시도 + 호출 간격) ─────────────────────────
_last_call = 0.0


def http_get(url: str, params: dict, headers: dict | None = None, interval: float = 0.5) -> requests.Response:
    global _last_call
    for attempt in range(3):
        time.sleep(max(0.0, interval - (time.time() - _last_call)))
        _last_call = time.time()
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code != 429 and resp.status_code < 500:
                resp.raise_for_status()
                return resp
        except requests.RequestException:
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError(f"외부 API 호출 실패: {url}")


# ── 대학 메타데이터 ────────────────────────────────────────────
def _query_majors(school_name: str) -> list[dict]:
    """학교명 부분 일치 조회. 페이지를 넘기는 동안 순서가 바뀌어 행이 중복·누락될 수 있어 크게 받는다."""
    rows, page = [], 1
    while True:
        resp = http_get(KCUE_URL, {
            "serviceKey": config.DATA_API_KEY, "svyYr": YEAR, "schlKrnNm": school_name,
            "pageNo": page, "numOfRows": 10000,
        }, interval=0.2)
        root = ET.fromstring(resp.text)
        items = [{c.tag: (c.text or "").strip() for c in item} for item in root.iter("item")]
        rows += items
        if not items or len(rows) >= int(root.findtext("./body/totalCount") or 0):
            return rows
        page += 1


def fetch_majors() -> list[dict]:
    """1) '대학교'로 전체를 받아 4년제 학교 이름을 모으고 2) 학교마다 다시 조회해 빠진 행을 채운다."""
    names = {r["schlNm"] for r in _query_majors("대학교") if r["schlKndNm"] in ("대학교", "교육대학", "산업대학")}
    unique = {}
    for n, name in enumerate(sorted(names), 1):
        print(f"\r학교별 조회 {n}/{len(names)}", end="")
        for r in _query_majors(name):
            unique[json.dumps(r, sort_keys=True, ensure_ascii=False)] = r  # 완전히 같은 행은 하나만
    print()
    return list(unique.values())


def build_items(rows: list[dict]) -> list[dict]:
    """4년제 대학 학사과정만 골라 대학 단위로 묶는다."""
    by_school = defaultdict(list)
    for r in rows:
        # '폐과' 표시여도 2025년 정원이 있으면 아직 모집 중인 학과로 본다
        if (r["schlKndNm"] in ("대학교", "교육대학", "산업대학") and r["pbnfDgriCrseDivNm"] == "학사"
                and (r["schlMjrStatNm"] != "폐과" or int(r.get("eschlPscpNum") or 0) > 0)):
            by_school[r["schlNm"]].append(r)

    items = []
    for name, school_rows in sorted(by_school.items()):
        # 정원도 졸업자도 없는 학교만 폐교·통합 전 교명으로 보고 뺀다 (부산교대처럼 정원이 0으로 공시된 곳도 있음)
        if not any(int(r.get("eschlPscpNum") or 0) or int(r.get("grdtNum") or 0) for r in school_rows):
            continue
        majors = defaultdict(lambda: {"quota": 0, "jobs": []})
        for r in school_rows:  # 주간/야간으로 나뉜 같은 학과는 합친다
            m = majors[r["korMjrNm"]]
            m["series"] = r.get("onsfSrsClftNm", "")
            m["quota"] += int(r.get("eschlPscpNum") or 0)
            m["jobs"] = list(dict.fromkeys(m["jobs"] + [j for j in r.get("pwayEmplLtrCtnt", "").split("|") if j]))
        total = sum(m["quota"] for m in majors.values())
        places = Counter(f"{r.get('mjrAreaNm', '')} {r.get('mjrAreaSignguNm', '')}".strip() for r in school_rows if r.get('mjrAreaNm'))
        items.append({
            "id": name,
            "name": name,
            "kind": school_rows[0]["schlKndNm"],
            "region": places.most_common(1)[0][0].split()[0],  # 학과가 가장 많은 캠퍼스의 시도
            "locations": [p for p, _ in places.most_common()],
            "total_quota": total,
            "series": dict(Counter(m["series"] for m in majors.values()).most_common()),
            "majors": [{"name": n, **m} for n, m in sorted(majors.items())],
            "jobs": [j for j, _ in Counter(j for m in majors.values() for j in m["jobs"]).most_common(10)],
        })
    return items


def load_items() -> list[dict]:
    if not config.ITEMS_PATH.exists():
        return []
    return json.loads(config.ITEMS_PATH.read_text(encoding="utf-8"))


def item_text(item: dict) -> str:
    """대학 1곳을 하나의 검색 텍스트로 만든다. 사용자가 찾는 기준(지역·학과·계열·정원)을 모두 넣는다."""
    majors = ", ".join(f"{m['name']} {m['quota']}" if m["quota"] else m["name"] for m in item["majors"])
    return "\n".join([
        f"대학명: {item['name']} ({item['kind']})",
        f"소재지: {', '.join(item['locations'])}",
        f"학사과정 학과 {len(item['majors'])}개, 입학정원 합계 {item['total_quota']}명 ({YEAR}년 공시)",
        f"계열: {', '.join(f'{k} {v}개' for k, v in item['series'].items())}",
        f"학과(입학정원): {majors}",
        f"관련 직업: {', '.join(item['jobs'])}",
    ])


def major_keywords(text: str) -> list[str]:
    """'간호학과', '약학과', '해양 관련' 같은 표현에서 학과 키워드를 뽑는다."""
    words = re.findall(r"([가-힣]{2,}?)(?:학과|학부|전공|과)", text) + re.findall(r"([가-힣]{2,})\s*관련", text)
    # '컴퓨터공학과' → '컴퓨터': 학교마다 컴퓨터학과·컴퓨터공학부처럼 이름이 달라서 '공'은 떼고 찾는다
    words = [w[:-1] if w.endswith("공") and len(w) > 2 else w for w in words]
    return list(dict.fromkeys(w for w in words if w not in {"관련", "어떤", "무슨", "해당", "있는", "인기"}))


def name_keywords(text: str, items: list[dict]) -> list[str]:
    """'여자대학교', '교육대학교', '가톨릭'처럼 여러 대학 이름에 들어가는 단어."""
    words = [re.sub(r"(은|는|이|가|을|를|와|과|에|의|도|만|으로|로)$", "", w) for w in re.findall(r"[가-힣]{2,}", text)]
    return [w for w in dict.fromkeys(words)
            if len(w) >= 2 and w not in ("대학교", "대학") and not any(r in w for r in REGIONS)  # 지역명은 regions_in이 처리
            and sum(w in i["name"] for i in items) >= 2]


def match_name(name: str) -> str:
    """키워드 비교용 학과명. '계약학과·협약학과'는 전공이 아닌 운영 형태 표기라 지운다 ('약학'이 걸리지 않게)."""
    return re.sub(r"(계약|협약)학(과|부)", "", name)


def major_candidates(question: str, items: list[dict]) -> dict[str, list[str]]:
    """학과 키워드별로, 이름에 그 키워드가 들어간 학과명을 중복 없이 모은다. (LLM이 다른 분야 이름을 걸러낸다)"""
    return {k: sorted({m["name"] for i in items for m in i["majors"] if k in match_name(m["name"])}) for k in major_keywords(question)}


def filter_items(question: str, items: list[dict], allowed: set[str] | None = None) -> list[tuple[str, str]] | None:
    """학과·학교명 조건으로 전체 대학을 직접 거른다. 조건이 없으면 None.

    학과 키워드가 여러 개면 모두 있어야 하고, 질문에 '또는'이 있으면 하나만 있어도 된다.
    allowed를 주면 그 학과명만 조건에 맞는 것으로 본다.
    돌려주는 값은 (대학 ID, '대학명 (소재지) 일치한 학과 정원') 목록.
    """
    majors_kw, regions = major_keywords(question), regions_in(question)
    name_kw = [w for w in name_keywords(question, items) if not any(k in w for k in majors_kw)]
    if not majors_kw and not name_kw:
        return None
    need = any if re.search(r"또는|이나|거나|혹은", question) else all
    lines = []
    for i in items:
        if (regions and i["region"] not in regions) or (name_kw and not any(w in i["name"] for w in name_kw)):
            continue
        found = {k: [m for m in i["majors"] if k in match_name(m["name"]) and (allowed is None or m["name"] in allowed)]
                 for k in majors_kw}
        if majors_kw and not need(found.values()):
            continue
        # 정원이 있는 학과가 있으면 그것만 보여준다 ('간호학과 0명' 같은 하위 항목 때문에 LLM이 없는 학과로 오해하지 않게)
        found = {k: [f"{m['name']} {m['quota']}명" for m in (([m for m in ms if m["quota"]] or ms))]
                 for k, ms in found.items()}
        detail = ", ".join(x for v in found.values() for x in v) or f"학과 {len(i['majors'])}개, 입학정원 {i['total_quota']}명"
        lines.append((i["id"], f"{i['name']} ({', '.join(i['locations'])}) {detail}"))
    return lines


def regions_in(text: str) -> list[str]:
    return sorted({full for short, full in REGIONS.items() if short in text})


def names_in(text: str, items: list[dict]) -> list[dict]:
    """질문에 나온 대학을 찾는다. '서울대학교'와 줄임말 '서울대' 둘 다 본다."""
    found = []
    for item in items:
        short = item["name"].replace("대학교", "대")
        if item["name"] in text or (short != item["name"] and re.search(re.escape(short) + r"(?!학)", text)):
            found.append(item)
    # '고려대'가 '고려대학교(세종)'까지 잡지 않게, 괄호 캠퍼스는 질문에 괄호 표기가 있을 때만 남긴다
    return [i for i in found if "(" not in i["name"] or i["name"] in text][:3]


# ── 위키백과 (User-Agent에 연락처 포함) ─────────────────────────
def _wiki(params: dict) -> dict:
    headers = {"User-Agent": f"UniGuide/1.0 (SSAFY project; {config.WIKI_CONTACT})"}
    return http_get(WIKI_URL, {"action": "query", "format": "json", "formatversion": 2, **params}, headers).json()


def wiki_find(title: str) -> str | None:
    """제목이 일치하는 문서 ID. '건국대학교(글로컬)'은 '건국대학교 글로컬캠퍼스'로도 찾아본다."""
    m = re.match(r"^(.+?)\((.+)\)$", title)
    for t in ([f"{m[1]} {m[2]}캠퍼스", m[1]] if m else [title]):
        pages = _wiki({"titles": t, "redirects": 1, "prop": "pageprops"})["query"]["pages"]
        if pages and not pages[0].get("missing") and "disambiguation" not in pages[0].get("pageprops", {}):
            return str(pages[0]["pageid"])
    return None


def wiki_search(query: str, limit: int = 5) -> list[dict]:
    hits = _wiki({"list": "search", "srsearch": query, "srlimit": limit})["query"]["search"]
    return [{"doc_id": str(h["pageid"]), "title": h["title"], "snippet": re.sub(r"<[^>]+>", "", h["snippet"])}
            for h in hits]


def wiki_fetch(doc_id: str) -> dict:
    """본문은 한 번만 받아 data/docs에 저장해 두고 다시 쓴다."""
    path = config.DOCS_DIR / f"{doc_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    page = _wiki({"pageids": doc_id, "prop": "extracts|info", "explaintext": 1, "inprop": "url"})["query"]["pages"][0]
    doc = {"doc_id": doc_id, "title": page["title"], "url": page["fullurl"], "text": page.get("extract", "")}
    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return doc


if __name__ == "__main__":
    raw_path = config.DATA_DIR / "raw" / f"kcue_majors_{YEAR}.json"
    if raw_path.exists():
        rows = json.loads(raw_path.read_text(encoding="utf-8"))
    else:
        print("공공데이터 API에서 학과정보를 받는 중... (약 3분)")
        rows = fetch_majors()
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    items = build_items(rows)
    config.ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print(f"대학 {len(items)}곳 저장 → {config.ITEMS_PATH}")
