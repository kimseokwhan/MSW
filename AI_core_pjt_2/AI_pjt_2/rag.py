"""RAG 파이프라인 — 프롬프트, 위키 문서 수집, LangGraph(retrieve → generate), 대학 비교.

질문 처리 순서
1. 질문에서 대학명·지역명·학과명·학교명 조건을 찾는다.
2. 대학명이 있으면 그 대학의 위키 문서를 수집·색인한다. (프롬프트1 검색어 추출 → 프롬프트2 후보 선별)
3. retrieve: 대학명 → 그 대학 정보 + 위키 청크 / 학과·학교명 조건 → 전체 대학을 직접 거른 결과
             / 지역명 → 그 지역 대학 전체 / 그 밖 → 의미 검색
4. generate: 근거만으로 답하고(프롬프트3) [근거 n]으로 출처를 표시한다. 목록형 질문은 목록을 코드로 만든다.
"""
import json
import re
from typing import Callable, TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

import config
import data
import index

ROLE = "너는 국내 대학과 학과 정보에 밝은 진학 상담 전문가야."
NOT_FOUND = "제공된 문서에서 확인되지 않습니다"
SOURCE_LABELS = {"meta": "대학 학과 공시", "wikipedia": "위키백과"}

# ── 프롬프트 ──────────────────────────────────────────────────
QUERY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROLE + """ 질문에 답하는 데 필요한 한국어 위키백과 검색어를 최대 3개 만든다.
대학 이름을 넣은 짧은 명사구로 쓰고, 대학 이름만 단독으로 쓰지 않는다.
JSON 문자열 배열 하나만 출력한다. 예) ["서울대학교 공과대학", "서울대학교 역사"]"""),
    ("human", "대학: {name}\n질문: {question}"),
])

SELECT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROLE + """ 위키백과 검색 후보의 제목과 요약만 보고, 질문의 근거가 될 문서를 최대 2개 고른다.
그 대학과 직접 관련된 문서만 고르고, 다른 대학·동음이의 문서·그 대학 출신이나 교수 같은 인물 문서는 버린다.
고른 번호의 JSON 정수 배열 하나만 출력한다. 없으면 []."""),
    ("human", "대학: {name}\n질문: {question}\n\n후보\n{candidates}"),
])

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROLE + """ 아래 [근거]의 내용만 사용해 한국어로 답한다.
- 근거에 없는 사실(순위, 합격선, 취업률 등)은 추측하지 않는다. 답할 근거가 없으면 "{not_found}"라고 답한다.
- 문장 끝에 사용한 근거 번호를 [근거 1], [근거 2, 3]처럼 붙인다. 확인되지 않는다는 문장에는 근거 번호를 붙이지 않는다.
- 조건에 맞는 대학을 묻는 질문이면, 근거에서 조건이 모두 확인되는 대학만 빠짐없이 목록으로 보여주고 대학마다 근거 번호를 붙인다.
  조건이 하나라도 확인되지 않는 대학은 목록에 넣지 않는다.
- 질문과 관계없는 정보는 덧붙이지 않는다. 입학정원을 언급할 때만 2025년 공시 기준임을 밝힌다.

[근거]
{context}"""),
    ("placeholder", "{history}"),
    ("human", "{question}"),
])

# 학과 조건 질문: 키워드가 다른 단어 속에 들어간 학과명(예: 바이오의약학과, 계약학과)이 같은 전공인지 판단한다
MAJOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROLE + """ 사용자는 '{keyword}'(이)라는 이름의 학과를 찾는다. 아래 학과명이 각각 그 학과(같은 전공 분야)인지 판단한다.
- 같은 전공이면 표기가 달라도 같은 학과다. (예: 정보컴퓨터공학부·전자전기컴퓨터공학부는 컴퓨터 분야)
- 키워드가 다른 단어의 일부로만 들어간 학과는 다른 학과다.
  (예: 계약학과의 '약학', 바이오의약학과·임상의약학과·신약학과·제약학과는 약학과와 다른 전공)
다른 학과인 것의 번호를 JSON 정수 배열 하나로만 출력한다. 모두 같은 학과면 []."""),
    ("human", "질문: {question}\n\n학과명\n{names}"),
])

COMPARE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROLE + """ 두 대학을 [근거]만으로 비교한다.
1. 비교표 (항목 | {a} | {b}): 소재지, 입학정원 합계, 학과 수, 계열 구성, 관심 분야 관련 학과
2. 차이점 3~5개
모든 사실에 [근거 n]을 붙인다. 순위·평판처럼 근거에 없는 내용은 "{not_found}"로 쓴다.

[근거]
{context}"""),
    ("human", "{a} vs {b}, 관심 분야: {focus}"),
])


def llm(model: str = config.CHAT_MODEL) -> ChatOpenAI:
    return ChatOpenAI(model=model, api_key=config.GMS_KEY, base_url=config.GMS_BASE_URL, temperature=0)


def parse_json_list(text: str) -> list:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    try:
        return json.loads(match.group(0)) if match else []
    except json.JSONDecodeError:
        return []


# ── 위키 문서 수집 (F2003 ~ F2005) ────────────────────────────
def collect(item: dict, question: str | None, progress: Callable[[str], None] = print) -> dict:
    """이미 수집한 검색어는 건너뛴다. 대학 자체 문서는 선별과 상관없이 항상 넣는다.
    question이 None이면 대학 자체 문서만 수집한다."""
    log = json.loads(config.COLLECT_LOG.read_text(encoding="utf-8")) if config.COLLECT_LOG.exists() else {}
    done = log.setdefault(item["id"], {})
    info = {"queries": [], "cached": [], "indexed": [], "rejected": []}

    if "(대학 자체 문서)" not in done:
        progress(f"'{item['name']}' 위키백과 문서 찾는 중")
        doc_id = data.wiki_find(item["name"])
        done["(대학 자체 문서)"] = [doc_id] if doc_id else []
        if doc_id:
            doc = data.wiki_fetch(doc_id)
            index.index_doc(item["id"], doc, item["name"])
            info["indexed"].append(doc["title"])

    # 같은 대학에 같은 질문이 다시 오면 검색어 추출부터 건너뛴다
    asked = log.setdefault("_questions", {})
    key = f"{item['id']}|{question.strip()}" if question else None
    if question is None or key in asked:
        if key:
            info["queries"], info["cached"] = list(asked[key]), list(asked[key])
        config.COLLECT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
        return info

    progress("검색어 추출 중 (프롬프트 1)")
    queries = parse_json_list((QUERY_PROMPT | llm()).invoke({"name": item["name"], "question": question}).content)
    info["queries"] = [q for q in queries if isinstance(q, str)][:3]

    for query in info["queries"]:
        if query in done:
            info["cached"].append(query)
            continue
        progress(f"위키백과에서 '{query}' 검색 중")
        have = {d for ids in done.values() for d in ids}
        cands = [c for c in data.wiki_search(query) if c["doc_id"] not in have]
        listing = "\n".join(f"{n}. {c['title']} — {c['snippet'][:150]}" for n, c in enumerate(cands, 1))
        picked = parse_json_list((SELECT_PROMPT | llm()).invoke(
            {"name": item["name"], "question": question, "candidates": listing}).content) if cands else []
        done[query] = []
        for n, c in enumerate(cands, 1):
            doc = data.wiki_fetch(c["doc_id"]) if n in picked else None
            if doc and len(doc["text"]) >= 300:
                progress(f"'{doc['title']}' 청킹·색인 중")
                index.index_doc(item["id"], doc, query)
                done[query].append(doc["doc_id"])
                info["indexed"].append(doc["title"])
            elif c["title"] not in info["rejected"]:
                info["rejected"].append(c["title"])

    info["rejected"] = [t for t in info["rejected"] if t not in info["indexed"]]  # 다른 검색어에서 색인된 문서는 제외 목록에서 뺀다
    asked[key] = info["queries"]
    config.COLLECT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ── LangGraph: retrieve → generate (F2006 ~ F2008) ───────────
class State(TypedDict, total=False):
    question: str
    item_ids: list[str]   # 질문에 나온(또는 선택한) 대학
    regions: list[str]    # 질문에 나온 지역
    filtered: list | None  # 학과·학교명 조건으로 거른 대학 (조건 없으면 None)
    top_k: int
    history: list
    evidence: list[dict]
    answer: str
    citations: list[dict]


def make_evidence(docs) -> list[dict]:
    """검색 결과를 합치고 같은 청크는 한 번만 남긴 뒤 번호를 붙인다."""
    evidence, seen = [], set()
    for d in docs:
        if d.id in seen:
            continue
        seen.add(d.id)
        evidence.append({"no": len(evidence) + 1, "item_id": d.metadata["item_id"], "title": d.metadata["title"],
                         "url": d.metadata["url"], "source": SOURCE_LABELS[d.metadata["source_type"]],
                         "content": d.page_content})
    return evidence


def format_context(evidence: list[dict]) -> str:
    return "\n\n".join(f"[근거 {e['no']}] ({e['source']}) {e['title']}\n{e['content']}" for e in evidence)


def cited(answer: str, evidence: list[dict]) -> list[dict]:
    """답변에 실제로 쓰인 [근거 n]만 남긴다."""
    nums = {int(n) for group in re.findall(r"\[근거\s*([\d,\s]+)\]", answer) for n in re.findall(r"\d+", group)}
    return [e for e in evidence if e["no"] in nums]


def retrieve(state: State) -> dict:
    if state["item_ids"]:      # 특정 대학: 대학 정보는 항상 + 그 대학의 위키 청크 검색
        docs = index.get_items(state["item_ids"]) + index.search_docs(state["question"], state["item_ids"], state["top_k"])
    elif state["filtered"] is not None:  # 학과·학교명 조건: 전체 대학을 직접 거른 결과를 근거로
        docs = [Document(id=item_id, page_content=text, metadata={
            "item_id": item_id, "title": f"{item_id} 학과 공시 정보 ({data.YEAR})",
            "url": data.KCUE_PAGE, "source_type": "meta"}) for item_id, text in state["filtered"]]
    elif state["regions"]:     # 지역 질문: 그 지역 대학 전체
        docs = index.items_in_regions(state["regions"])
    else:                      # 그 밖의 조건: 의미가 가까운 대학
        docs = index.search_items(state["question"], config.META_K)
    return {"evidence": make_evidence(docs)}


def generate(state: State) -> dict:
    if state["filtered"]:  # 목록형 질문: LLM이 긴 목록을 쓰면 일부를 빼먹어서 목록은 코드로 만든다
        evidence = state["evidence"]
        lines = [f"- **{e['content'].split(' (')[0]}** ({e['content'].split(' (', 1)[1]} [근거 {e['no']}]" for e in evidence]
        answer = f"조건에 맞는 대학은 **{len(evidence)}곳**입니다. (입학정원은 {data.YEAR}년 공시 기준)\n\n" + "\n".join(lines)
        return {"answer": answer, "citations": evidence}

    history = [(role, re.sub(r"\[근거[^\]]*\]", "", text)) for role, text in state["history"][-4:]]
    answer = (ANSWER_PROMPT | llm(config.ANSWER_MODEL)).invoke({
        "context": format_context(state["evidence"]) or "(근거 없음)", "not_found": NOT_FOUND,
        "history": history, "question": state["question"],
    }).content
    return {"answer": answer, "citations": cited(answer, state["evidence"])}


builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
graph = builder.compile()


def allowed_majors(question: str, items: list[dict], progress: Callable[[str], None] = print) -> set[str] | None:
    """질문의 학과 키워드가 들어간 학과명 중 같은 전공인 이름만 남긴다.

    이름(또는 그 안의 단어)이 키워드로 시작하면 바로 인정하고(약학과, 컴퓨터공학부),
    키워드가 단어 중간에 들어간 이름(바이오의약학과, 계약학과)만 LLM이 판단한다.
    """
    candidates = data.major_candidates(question, items)
    if not candidates:
        return None
    allowed = set()
    for keyword, names in candidates.items():
        starts = re.compile(r"(^|[\s(·ㆍ,\[/])" + re.escape(keyword))
        allowed |= {n for n in names if starts.search(n)}
        unclear = [n for n in names if not starts.search(n)]
        if unclear:
            progress(f"'{keyword}' 학과명 확인 중")
            listing = "\n".join(f"{k}. {n}" for k, n in enumerate(unclear, 1))
            drop = set(parse_json_list((MAJOR_PROMPT | llm(config.ANSWER_MODEL)).invoke(
                {"keyword": keyword, "question": question, "names": listing}).content))
            allowed |= {n for k, n in enumerate(unclear, 1) if k not in drop}
    return allowed


def ask(question: str, items: list[dict], selected: dict | None = None, top_k: int = config.TOP_K,
        history: list | None = None, progress: Callable[[str], None] = print) -> dict:
    targets = [selected] if selected else data.names_in(question, items)
    collected = [collect(item, question, progress) for item in targets]
    progress("근거 검색 후 답변 생성 중")
    result = graph.invoke({
        "question": question, "item_ids": [t["id"] for t in targets],
        "regions": [] if targets else data.regions_in(question),
        "filtered": None if targets else data.filter_items(question, items, allowed_majors(question, items, progress)),
        "top_k": top_k, "history": history or [],
    })
    return {**result, "collected": collected}


# ── 특화 기능: 대학 비교 (F2010) ──────────────────────────────
def compare(a: dict, b: dict, focus: str, progress: Callable[[str], None] = print) -> dict:
    for item in (a, b):
        collect(item, None, progress)
    docs = index.get_items([a["id"], b["id"]]) + index.search_docs(focus or "대학 소개", [a["id"], b["id"]], 4)
    evidence = make_evidence(docs)
    progress("비교표 작성 중")
    answer = (COMPARE_PROMPT | llm(config.ANSWER_MODEL)).invoke({
        "a": a["name"], "b": b["name"], "focus": focus or "전반",
        "context": format_context(evidence), "not_found": NOT_FOUND,
    }).content
    return {"answer": answer, "citations": cited(answer, evidence)}


if __name__ == "__main__":
    print(graph.get_graph().draw_mermaid())
