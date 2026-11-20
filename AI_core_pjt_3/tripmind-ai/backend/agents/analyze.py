import json
import re
from datetime import date as CalendarDate
from typing import Literal

from openai import APIError, OpenAI
from pydantic import BaseModel, Field, ValidationError

from backend.config import setting
from backend.llm import call_function
from backend.schemas.service import Clock


class Conditions(BaseModel):
    region: str | None = Field(default=None, max_length=80)
    date: CalendarDate | None = None
    end_date: CalendarDate | None = None
    days: int | None = Field(default=None, ge=1)
    start_time: Clock | None = None
    end_time: Clock | None = None
    count: int | None = Field(default=None, ge=1, le=20)
    total_count: int | None = Field(default=None, ge=1, le=280)
    category: Literal["indoor", "outdoor", "mixed", "any"] | None = None
    rain_indoor: bool | None = None
    max_rain_pct: int | None = Field(default=None, ge=0, le=100)
    budget: int | None = Field(default=None, ge=0)
    min_stay_minutes: int | None = Field(default=None, ge=1, le=1440)
    max_leg_minutes: int | None = Field(default=None, ge=0, le=1440)
    weather: bool | None = None
    air: bool | None = None
    attractions: bool | None = None


class Interpretation(BaseModel):
    intent: Literal["create_plan", "revise_plan", "lookup", "help", "other"]
    changes: Conditions
    reset: bool = False
    reason: str = Field(default="", max_length=140)


class AnalysisError(Exception):
    pass


def interpret(message, previous, today):
    # Common help requests bypass the model and external tools.
    if re.fullmatch(r"(안녕(?:하세요)?|반가워요|hi|hello)[!.?\s]*", message, re.IGNORECASE):
        return Interpretation(intent="other", changes=Conditions()), False
    if re.search(r"(삭제|저장|수정|로그).{0,15}(방법|어떻게|할 수 있)", message):
        return Interpretation(intent="help", changes=Conditions()), False
    key, model = setting("OPENAI_API_KEY"), setting("LLM_MODEL")
    if not key or not model:
        raise AnalysisError("MISSING_API_KEY")
    url = setting("LLM_BASE_URL") or "https://api.openai.com/v1"
    system = (
        f"너는 한국 여행 플래너의 요청 분류기다. 한국 기준 오늘은 {today}다. "
        "interpret_request 함수만 호출하라. 이번 메시지에 명시된 변경만 changes에 넣고 "
        "누락 조건을 추정하지 마라. 11월 21일처럼 연도가 생략되면 다음 해당 날짜를 쓰고 "
        "시간은 문맥의 오전/오후를 적용해 HH:MM으로 파싱한다. "
        "date는 시작일, end_date는 날짜 범위의 마지막 날이다. '21일부터 24일까지'처럼 날짜 범위의 끝을 빼먹지 마라. "
        "'4일 일정' 또는 '3박 4일'은 days=4다. 시작일이 없으면 date를 비워 둔다. "
        "count는 하루 방문 수, total_count는 사용자가 전체 여행의 합계라고 명시한 장소 수다. "
        "기존 대화 답변이나 교체 요청은 revise_plan, 독립 일정은 create_plan, "
        "시간창 없이 날씨·대기질이나 비가 올 경우의 대체 장소만 물으면 lookup을 사용한다. "
        "여행지나 가볼 만한 곳 추천만 구하면 날짜와 시간이 없어도 lookup, attractions=true를 사용한다. "
        "사용자가 명시적으로 일정 수립을 요청하면 create_plan으로 분류한다. "
        "이전 계획을 이어가는 추가 조건이면 revise_plan으로 분류하고, 새 계획은 reset=true를 준다. "
        "비가 오면 실내는 rain_indoor=true다. 실내만은 category=indoor, "
        "실내와 실외(야외)를 섞어 달라는 요청은 반드시 category=mixed다. "
        "목적지는 국내 시도나 시·군·구 이름을 그대로 넣고, 시도와 시군구를 함께 말하면 둘 다 보존한다. "
        "이전 목적지가 동명 지역이고 사용자가 시도만 골라 답했다면 이전 지역명 앞에 그 시도를 붙인다. "
        "날씨나 미세먼지를 언급하면 관련 플래그를 넣는다. "
        "단순 인사나 서비스 바깥 요청은 other, 사용법은 help다. "
        "reason에는 판단 기준을 한 문장으로 요약하고 원문, 개인 식별 정보, 키를 옮기지 마라."
    )
    try:
        with OpenAI(api_key=key, base_url=url, timeout=20 if model == "gpt-6-astra" else 12,
                    max_retries=0) as client:
            arguments = call_function(
                client, model, [{"role": "system", "content": system},
                                       {"role": "user", "content": json.dumps(
                                           {"request": message, "previous": previous}, ensure_ascii=False)}],
                {"name": "interpret_request", "description": "이번 사용자 요청의 의도와 변경 조건",
                 "parameters": Interpretation.model_json_schema()},
                required=True,
            )
        return Interpretation.model_validate_json(arguments), True
    except APIError:
        raise AnalysisError("LLM_UNAVAILABLE") from None
    except (IndexError, StopIteration, ValueError, TypeError, AttributeError):
        raise AnalysisError("LLM_INVALID_RESPONSE") from None
