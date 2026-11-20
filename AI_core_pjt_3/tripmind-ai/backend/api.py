from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query, Response

from backend.agents.graph import chat
from backend import store
from backend.schemas.service import (
    ChatInput, ChatResponse, LogDetail, LogList, PlanInput, PlanList, PlanPatch, PlanWrite, SavedPlan,
)


router = APIRouter(prefix="/api")


@router.post("/chat", response_model=ChatResponse, tags=["대화"])
def chat_route(request: ChatInput):
    return chat(request.message, request.session_id)


@router.post("/plans", response_model=PlanWrite, status_code=201, tags=["계획"])
def create_plan(request: PlanInput):
    return store.save_plan(request)


@router.get("/plans", response_model=PlanList, tags=["계획"])
def list_plans(visit_date: date | None = None, limit: int = Query(20, ge=1, le=100),
               offset: int = Query(0, ge=0)):
    return store.list_plans(visit_date.isoformat() if visit_date else None, limit, offset)


@router.get("/plans/{plan_id}", response_model=SavedPlan, tags=["계획"])
def get_plan(plan_id: int):
    return store.get_plan(plan_id)


@router.patch("/plans/{plan_id}", response_model=PlanWrite, tags=["계획"])
def update_plan(plan_id: int, request: PlanPatch):
    return store.save_plan(request, plan_id)


@router.delete("/plans/{plan_id}", status_code=204, tags=["계획"])
def delete_plan(plan_id: int):
    store.delete_plan(plan_id)
    return Response(status_code=204)


@router.get("/logs", response_model=LogList, tags=["실행 로그"])
def list_logs(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return store.list_logs(limit, offset)


@router.get("/logs/{session_id}", response_model=LogDetail, tags=["실행 로그"])
def get_logs(session_id: UUID):
    return store.get_logs(str(session_id))


@router.delete("/logs/{session_id}", status_code=204, tags=["실행 로그"])
def delete_logs(session_id: UUID):
    store.delete_logs(str(session_id))
    return Response(status_code=204)
