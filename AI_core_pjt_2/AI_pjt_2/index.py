"""Vector DB(Chroma) 색인 — 대학 메타데이터(RAG 1)와 위키 문서 청크(RAG 2).

    python index.py          # 대학 198곳 색인 (다시 실행해도 덮어쓰기만 일어난다)
    python index.py --show 서울대학교   # 색인 텍스트 1건 확인
    python index.py --docs              # 위키 문서를 현재 청크 설정으로 다시 색인
"""
import json
import sys
from functools import lru_cache

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
import data

client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))


@lru_cache(maxsize=2)
def get_store(name: str) -> Chroma:
    embeddings = OpenAIEmbeddings(model=config.EMBED_MODEL, api_key=config.GMS_KEY,
                                  base_url=config.GMS_BASE_URL, check_embedding_ctx_length=False)
    return Chroma(client=client, collection_name=name, embedding_function=embeddings,
                  collection_metadata={"hnsw:space": "cosine"})


def count(name: str) -> int:
    try:
        return client.get_collection(name).count()
    except Exception:
        return 0


# ── RAG 1: 대학 메타데이터 ─────────────────────────────────────
def index_items(items: list[dict]) -> None:
    docs = [Document(page_content=data.item_text(i), metadata={
        "item_id": i["id"], "title": f"{i['name']} 학과 공시 정보 ({data.YEAR})", "url": data.KCUE_PAGE,
        "source_type": "meta", "region": i["region"],
    }) for i in items]
    for s in range(0, len(docs), 50):  # 청크 ID = 대학명 → 다시 색인하면 덮어쓴다
        get_store(config.META_COLLECTION).add_documents(docs[s:s + 50], ids=[i["id"] for i in items[s:s + 50]])


def get_items(ids: list[str]) -> list[Document]:
    got = client.get_collection(config.META_COLLECTION).get(ids=ids)
    return [Document(id=i, page_content=t, metadata=m)
            for i, t, m in zip(got["ids"], got["documents"], got["metadatas"])]


def items_in_regions(regions: list[str]) -> list[Document]:
    got = client.get_collection(config.META_COLLECTION).get(where={"region": {"$in": regions}})
    return [Document(id=i, page_content=t, metadata=m)
            for i, t, m in zip(got["ids"], got["documents"], got["metadatas"])]


def search_items(query: str, k: int) -> list[Document]:
    return get_store(config.META_COLLECTION).similarity_search(query, k=k)


# ── RAG 2: 위키 문서 ──────────────────────────────────────────
def index_doc(item_id: str, doc: dict, query: str) -> int:
    """청크 ID = 대학ID:문서ID:순번 → 여러 대학이 같은 문서를 넣어도 서로 덮어쓰지 않는다."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    chunks = splitter.split_text(f"{doc['title']}\n\n{doc['text']}")
    docs = [Document(page_content=c, metadata={
        "item_id": item_id, "doc_id": doc["doc_id"], "title": doc["title"], "url": doc["url"],
        "source_type": "wikipedia", "query": query,
    }) for c in chunks]
    store = get_store(config.DOCS_COLLECTION)
    store.delete(where={"$and": [{"item_id": item_id}, {"doc_id": doc["doc_id"]}]})  # 옛 청크 정리
    if docs:
        store.add_documents(
            docs, ids=[f"{item_id}:{doc['doc_id']}:{n}" for n in range(len(docs))])
    return len(docs)


def search_docs(query: str, item_ids: list[str], k: int) -> list[Document]:
    if not item_ids or count(config.DOCS_COLLECTION) == 0:
        return []
    return get_store(config.DOCS_COLLECTION).similarity_search(query, k=k, filter={"item_id": {"$in": item_ids}})


def rebuild_docs() -> None:
    """이미 받아 둔 위키 문서를 현재 CHUNK_SIZE/CHUNK_OVERLAP으로 다시 청킹한다 (외부 호출 없음)."""
    log = json.loads(config.COLLECT_LOG.read_text(encoding="utf-8")) if config.COLLECT_LOG.exists() else {}
    for item_id, queries in log.items():
        if item_id.startswith("_"):  # '_questions'는 질문 기록이라 건너뛴다
            continue
        for query, doc_ids in queries.items():
            for doc_id in doc_ids:
                index_doc(item_id, data.wiki_fetch(doc_id), query)


if __name__ == "__main__":
    items = data.load_items()
    if len(sys.argv) == 3 and sys.argv[1] == "--show":
        print(next((data.item_text(i) for i in items if i["name"] == sys.argv[2]), "없는 대학입니다."))
    elif len(sys.argv) == 2 and sys.argv[1] == "--docs":
        before = count(config.DOCS_COLLECTION)
        rebuild_docs()
        print(f"청크 {config.CHUNK_SIZE}자/중복 {config.CHUNK_OVERLAP}자: 위키 청크 {before}건 → {count(config.DOCS_COLLECTION)}건")
    else:
        before = count(config.META_COLLECTION)
        index_items(items)
        print(f"로드한 대학 {len(items)}곳 / 색인 전 {before}건 → 색인 후 {count(config.META_COLLECTION)}건")
