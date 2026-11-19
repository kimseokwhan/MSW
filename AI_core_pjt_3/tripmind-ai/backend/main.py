import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from backend.database.store import NotFound, initialize
from backend.routers.api import router


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title="TripMind AI", lifespan=lifespan)
app.include_router(router)
FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def error(status, code, message):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def invalid_input(request, exc):
    return error(422, "INVALID_INPUT", "입력 형식, 필수 항목과 시간 범위를 확인해 주세요.")


@app.exception_handler(NotFound)
async def not_found(request, exc):
    return error(404, "NOT_FOUND", "요청한 계획 또는 로그를 찾을 수 없습니다.")


@app.exception_handler(sqlite3.Error)
async def storage_unavailable(request, exc):
    return error(503, "STORAGE_UNAVAILABLE", "저장소에 연결할 수 없습니다. 잠시 뒤 다시 시도해 주세요.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/app.js", include_in_schema=False)
def frontend_script():
    # Windows MIME mappings can serve .js as text/plain, which module scripts reject.
    return FileResponse(FRONTEND / "app.js", media_type="application/javascript")


app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
