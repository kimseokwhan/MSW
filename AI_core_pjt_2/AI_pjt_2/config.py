"""실행 설정 — 키는 .env에서 읽고, 청킹·검색 값은 여기서 바꾼다."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# API 키 (소스코드에 넣지 않는다)
GMS_KEY = os.getenv("GMS_KEY", "").strip()
DATA_API_KEY = os.getenv("DATA_API_KEY", "").strip()
WIKI_CONTACT = os.getenv("WIKI_CONTACT", "").strip()
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

# 모델
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1-mini")        # 검색어 추출·후보 선별
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "gpt-5.4-mini")    # 답변 생성·대학 비교
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# 경로
DATA_DIR = BASE_DIR / "data"
ITEMS_PATH = DATA_DIR / "universities.json"   # 대학 메타데이터
DOCS_DIR = DATA_DIR / "docs"                  # 수집한 위키 문서 원문
COLLECT_LOG = DATA_DIR / "collect_log.json"   # 이미 수집한 검색어 기록
CHROMA_DIR = BASE_DIR / "chroma_db"

# Vector DB 컬렉션
META_COLLECTION = "univ_meta"   # 대학 1곳 = 1청크
DOCS_COLLECTION = "univ_docs"   # 위키 문서 청크

# 청킹·검색 설정
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
TOP_K = int(os.getenv("TOP_K", 5))        # 위키 문서 청크 근거 수
META_K = 15                               # 지역·대학명이 없을 때 의미 검색할 대학 수
