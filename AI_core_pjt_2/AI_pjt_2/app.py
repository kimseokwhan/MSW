"""UniGuide — 국내 대학·학과 탐색 RAG 서비스

    streamlit run app.py
"""
import logging

import streamlit as st

import config
import data
import index
import rag

ALL = "전체 대학"
st.set_page_config(page_title="UniGuide", page_icon="🎓", layout="wide")
items = data.load_items()
by_id = {i["id"]: i for i in items}


def show_citations(citations: list[dict]) -> None:
    if not citations:
        st.info("이 답변에는 인용된 근거가 없습니다.")
        return
    with st.expander(f"📎 근거 {len(citations)}건"):
        for c in citations:
            st.markdown(f"**[근거 {c['no']}]** `{c['source']}` [{c['title']}]({c['url']})")


def show_collected(collected: list[dict]) -> None:
    """위키 문서 수집 내역. 이미 수집한 검색어는 다시 수집하지 않았음을 보여준다."""
    for c in collected:
        if c["cached"] and not c["indexed"]:
            st.caption(f"♻️ 이미 수집한 검색어라 다시 수집하지 않았습니다: {', '.join(c['cached'])}")
        with st.expander("🔍 문서 수집 내역"):
            st.markdown(f"- 검색어(프롬프트 1): {', '.join(c['queries']) or '없음'}")
            st.markdown(f"- 이미 수집한 검색어(재수집 안 함): {', '.join(c['cached']) or '없음'}")
            st.markdown(f"- 새로 색인한 문서: {', '.join(c['indexed']) or '없음'}")
            if c["rejected"]:
                st.markdown(f"- 선별에서 제외한 후보(프롬프트 2): {', '.join(c['rejected'])}")


def search_select(label: str, key: str, extra: list[str] | None = None) -> str:
    """검색창으로 198개 대학 목록을 대학명·지역으로 좁힌 뒤 고른다."""
    query = st.text_input(f"{label} 검색", key=f"{key}_query", placeholder="대학명 또는 지역 (예: 경상, 부산)").strip()
    ids = [i for i in by_id if not query or query in i or query in " ".join(by_id[i]["locations"])]
    if not ids:
        st.caption("검색 결과가 없습니다.")
    current = st.session_state.get(key)
    if current in by_id and current not in ids:  # 이미 고른 대학은 목록에서 사라지지 않게
        ids.insert(0, current)
    return st.selectbox(label, (extra or []) + ids, key=key,
                        format_func=lambda i: i if i not in by_id else f"{i} ({by_id[i]['region']})")


def clear_chat(all_chats: bool = False) -> None:
    if all_chats:
        st.session_state.chats = {}
    else:
        st.session_state.setdefault("chats", {}).pop(st.session_state.selected, None)


# 화면 오른쪽 아래에 고정되는 맨 위로 / 맨 아래로 버튼 (스트림릿에 스크롤 기능이 없어 JS로 붙인다)
SCROLL_BUTTONS = """
<script>
(() => {
  if (document.getElementById("scroll-buttons")) return;
  const box = document.createElement("div");
  box.id = "scroll-buttons";
  box.style.cssText = "position:fixed;right:24px;bottom:110px;z-index:1000;display:flex;flex-direction:column;gap:8px";
  const scroller = () => [...document.querySelectorAll(
      '[data-testid="stAppScrollToBottomContainer"],[data-testid="stMain"],[data-testid="stAppViewContainer"]')]
    .find(el => el.scrollHeight > el.clientHeight + 1) || document.scrollingElement;
  for (const [label, title, toTop] of [["⬆", "맨 위로", true], ["⬇", "맨 아래로", false]]) {
    const btn = document.createElement("button");
    btn.textContent = label;
    btn.title = title;
    btn.style.cssText = "width:42px;height:42px;border-radius:50%;border:1px solid #ccc;background:#fff;" +
                        "font-size:18px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.15)";
    btn.onclick = () => { const el = scroller(); el.scrollTo({top: toTop ? 0 : el.scrollHeight, behavior: "smooth"}); };
    box.appendChild(btn);
  }
  document.body.appendChild(box);
})();
</script>
"""


def pick(item_id: str) -> None:
    st.session_state.selected = item_id


def error_message(e: Exception) -> str:
    logging.exception("처리 중 오류")  # 상세 내용은 터미널에만 남기고 화면에는 안내만 보여준다
    if "Authentication" in type(e).__name__:
        return "LLM API 인증에 실패했습니다. .env의 GMS_KEY를 확인하세요."
    return "요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."


# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 UniGuide")
    st.caption("국내 대학·학과 탐색 RAG 서비스")
    c1, c2 = st.columns(2)
    c1.metric("대학 색인", f"{index.count(config.META_COLLECTION)}건")
    c2.metric("위키 청크", f"{index.count(config.DOCS_COLLECTION)}건")
    search_select("질문 대상", "selected", extra=[ALL])
    top_k = st.slider("근거 수 Top-k (위키 청크)", 1, 10, config.TOP_K)
    c1, c2 = st.columns(2)
    c1.button("🗑️ 이 대화 지우기", on_click=clear_chat, width="stretch",
              help="지금 질문 대상의 대화만 지웁니다")
    c2.button("모든 대화 지우기", on_click=clear_chat, args=(True,), width="stretch",
              help="모든 질문 대상의 대화를 지웁니다")
    st.warning(data.DISCLAIMER, icon="⚠️")

# ── 실행 전 점검 ─────────────────────────────────────────────
if not config.GMS_KEY:
    st.error("GMS_KEY가 없습니다. .env 파일에 키를 넣고 다시 실행하세요.")
    st.stop()
if not items or index.count(config.META_COLLECTION) == 0:
    st.warning("색인이 없습니다. 터미널에서 `python data.py` → `python index.py`를 실행하세요.")
    st.stop()

selected = by_id.get(st.session_state.selected)
st.html(SCROLL_BUTTONS, unsafe_allow_javascript=True)
chats = st.session_state.setdefault("chats", {})          # 질문 대상별로 대화를 따로 저장
messages = chats.setdefault(st.session_state.selected, [])

tab_chat, tab_compare = st.tabs(["💬 질문하기", "⚖️ 대학 비교"])

with tab_chat:
    if selected:
        st.subheader(f"{selected['name']}에 대해 질문하기")
        st.caption(f"{', '.join(selected['locations'])} · 학과 {len(selected['majors'])}개 · 입학정원 {selected['total_quota']}명")
    else:
        st.subheader(f"{len(items)}개 대학 중에서 찾아보기")
        st.caption("예) 서울에 있는 여자대학교 알려줘 / 간호학과와 약학과가 모두 있는 대학은? / 연세대는 언제 설립됐어?")
    with st.expander("📋 질문할 수 있는 조건 / 구분할 수 없는 조건"):
        c1, c2 = st.columns(2)
        c1.markdown("**✅ 찾을 수 있어요**\n\n" + "\n".join(f"- {s}" for s in data.SEARCHABLE))
        c2.markdown("**❌ 구분할 수 없어요**\n\n" + "\n".join(f"- {s}" for s in data.NOT_SEARCHABLE))

    for n, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            for note in msg.get("notes", []):
                st.warning(note, icon="⚠️")
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                show_citations(msg["citations"])
                show_collected(msg.get("collected", []))
                # 답변에 나온 대학을 누르면 그 대학에 대한 질문으로 이어진다
                ids = list(dict.fromkeys(c["item_id"] for c in msg["citations"] if c["source"] == "대학 학과 공시"))
                if not selected and len(ids) > 1:
                    cols = st.columns(4)
                    for k, item_id in enumerate(ids[:12]):
                        cols[k % 4].button(item_id, key=f"pick_{n}_{item_id}", on_click=pick, args=(item_id,))

    if question := st.chat_input("대학에 대해 물어보세요"):
        history = [("human" if m["role"] == "user" else "ai", m["content"]) for m in messages]
        messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            try:
                with st.status("처리 중...", expanded=True) as status:
                    result = rag.ask(question, items, selected, top_k, history, progress=status.write)
                    status.update(label="완료", state="complete", expanded=False)
            except Exception as e:
                messages.pop()
                st.error(error_message(e))
                st.stop()
        messages.append({"role": "assistant", "content": result["answer"], "citations": result["citations"],
                         "collected": result["collected"], "notes": data.limit_notes(question)})
        st.rerun()

with tab_compare:
    st.subheader("두 대학 비교")
    st.session_state.setdefault("cmp_a", "서울대학교")
    st.session_state.setdefault("cmp_b", "연세대학교")
    c1, c2 = st.columns(2)
    with c1:
        a = search_select("대학 A", "cmp_a")
    with c2:
        b = search_select("대학 B", "cmp_b")
    focus = st.text_input("관심 분야 (선택)", placeholder="예: 컴퓨터·AI")
    submitted = st.button("비교하기", type="primary")
    if submitted and a != b:
        try:
            with st.status("비교 중...", expanded=True) as status:
                result = rag.compare(by_id[a], by_id[b], focus, progress=status.write)
                status.update(label="완료", state="complete", expanded=False)
            st.markdown(result["answer"])
            show_citations(result["citations"])
        except Exception as e:
            st.error(error_message(e))
    elif submitted:
        st.warning("서로 다른 두 대학을 고르세요.")
