import json
import re
import sqlite3
from datetime import datetime
from threading import Lock
from time import perf_counter
from typing import TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from backend.agents.analyze import AnalysisError, Conditions, interpret
from backend.agents.logger import record_event
from backend.database import store
from backend.events.bus import EventBus
from backend.schemas.service import ChatResponse
from backend.tools.external_apis import KST
from backend.tools.regions import Destination, resolve_destination
from backend.tools.registry import TOOLS


MAX_REPLANS = 3
SESSION_LOCKS = [Lock() for _ in range(32)]
ASK = {"region": "어느 지역으로 가시나요?", "date": "여행 날짜는 언제인가요?",
       "start_time": "몇 시에 시작하시나요?", "end_time": "몇 시에 마치나요?",
       "count": "몇 곳을 방문하고 싶으세요?"}
AUTH_ERRORS = {"MISSING_API_KEY", "AUTH_FAILED", "RATE_LIMITED"}
SOURCES = {
    "search_attractions": ("TourAPI", "https://www.data.go.kr/data/15101578/openapi.do"),
    "get_attraction_detail": ("TourAPI", "https://www.data.go.kr/data/15101578/openapi.do"),
    "get_weather": ("Open-Meteo", "https://open-meteo.com/en/docs"),
    "get_air_quality": ("AirKorea", "https://www.airkorea.or.kr"),
}


class State(TypedDict, total=False):
    message: str
    memory: dict
    bus: EventBus
    conditions: dict
    destination: Destination
    intent: str
    questions: list
    warnings: list
    tasks: list
    cache: dict
    candidates: dict
    selected: list
    excluded: list
    evidence: list
    replan_count: int
    search_index: int
    needs_replan: bool
    fatal: bool
    tour_blocked: bool
    infeasible: bool
    weather: dict | None
    weather_point: str
    weather_attempted: bool
    air: dict | None
    indoor: bool
    constraints: list
    result: dict


def warning(code, message, tool=None):
    return {"code": code, "message": message, "tool": tool}


def evidence(tool, fact):
    source, url = SOURCES[tool]
    return {"tool": tool, "source": source, "fact": fact, "reference_url": url}


def analyze(state):
    today = datetime.now(KST).date()
    previous = state["memory"].get("conditions", {})
    try:
        request, used_llm = interpret(state["message"], previous, today)
    except AnalysisError as error:
        message = ("GMS 키와 모델 설정을 확인해 주세요." if str(error) == "MISSING_API_KEY"
                   else "요청 분석 서비스에 연결하지 못했습니다. 잠시 뒤 다시 요청해 주세요.")
        return {"fatal": True, "warnings": [*state["warnings"], warning(str(error), message)]}
    if used_llm:
        reason = request.reason.strip()
        if not reason or re.search(r"https?://|[A-Za-z0-9_-]{16,}|@", reason):
            reason = "현재 요청과 기존 대화 조건을 비교하여 의도를 분류했습니다."
        state["bus"].publish("llm_decision", "analyze", intent=request.intent,
                             reason=reason)
    if request.intent in {"help", "other"}:
        return {"intent": request.intent}
    changes = request.changes.model_dump(mode="json", exclude_unset=True, exclude_none=True)
    # A reply to a pending question can be only a date or a number.
    inherit = not request.reset and (request.intent == "revise_plan" or state["memory"].get("pending"))
    conditions = Conditions.model_validate({**(previous if inherit else {}), **changes}).model_dump(mode="json")
    intent = state["memory"].get("pending_intent", "create_plan") if (
        inherit and state["memory"].get("pending") and request.intent == "revise_plan"
    ) else request.intent
    required = ["region"]
    if intent != "lookup":
        required = list(ASK)
    elif conditions["rain_indoor"] or conditions["weather"]:
        required.append("date")
    questions = [ASK[key] for key in required if conditions.get(key) is None]
    destination = None
    if conditions["region"]:
        matches = resolve_destination(conditions["region"])
        if not matches:
            questions.append("국내 시도 또는 시·군·구를 알려 주세요. 예를 들어 부산 해운대구나 강원 강릉시입니다.")
        elif len(matches) > 1:
            options = ", ".join(item.label for item in matches[:5])
            questions.append(f"어느 지역인가요? 시도를 함께 알려 주세요. 후보 · {options}")
        else:
            destination = matches[0]
            conditions["region"] = destination.label
            if conditions["air"] and not destination.air_province:
                questions.append("대기질은 광주와 전남 중 어느 쪽의 관측값을 볼까요?")
    if conditions["start_time"] and conditions["end_time"] and conditions["start_time"] >= conditions["end_time"]:
        questions.append("종료 시간이 시작 시간보다 늦도록 당일 시간대를 알려 주세요.")
    safe_conditions = {key: value for key, value in conditions.items() if value is not None
                       and (key != "region" or destination is not None)}
    state["bus"].publish("conditions_extracted", "analyze", conditions=safe_conditions,
                         needs_input=bool(questions))
    return {"conditions": conditions, "intent": intent, "questions": questions, "destination": destination}


def search_tasks(state, index):
    conditions = state["conditions"]
    destination = state["destination"]
    indoor = state.get("indoor") or conditions["category"] == "indoor"
    type_id = "14" if indoor else "12"
    page = index + 1
    if not indoor and index % 2:
        type_id, page = "14", index // 2 + 1
    elif not indoor:
        page = index // 2 + 1
    return [("search_attractions", {"region_code": destination.region_code,
                                    "district_codes": list(destination.districts),
                                    "excluded_districts": list(destination.excluded_districts),
                                    "visit_date": conditions["date"], "page": page,
                                    "content_type_id": type_id})]


def wants_attractions(state):
    c = state["conditions"]
    return bool(state["intent"] != "lookup" or c["rain_indoor"] or c["category"] or c["attractions"])


def wants_weather(state):
    c = state["conditions"]
    return bool(c["date"] and (wants_attractions(state) or c["weather"]))


def plan(state):
    c = state["conditions"]
    tasks = search_tasks(state, 0) if wants_attractions(state) or wants_weather(state) else []
    if wants_weather(state):
        tasks.append(("get_weather", {"date": c["date"]}))
    province = state["destination"].air_province
    if province and (c["air"] or wants_attractions(state)):
        tasks.append(("get_air_quality", {"province": province}))
    state["bus"].publish("plan_created", "plan", tools=[tool for tool, _ in tasks],
                         detail_dependency="search_attractions.content_id")
    return {"tasks": tasks}


def call_tool(state, cache, warnings, name, arguments):
    key = (name, json.dumps(arguments, sort_keys=True, ensure_ascii=False))
    if key in cache:
        state["bus"].publish("tool_reused", "execute", tool=name, arguments=arguments)
        return cache[key]
    bus = state["bus"]
    bus.publish("tool_requested", "execute", tool=name, arguments=arguments)
    started = perf_counter()
    result = TOOLS[name][2](**arguments)
    data = result.data.model_dump(mode="json") if result.ok else None
    code = None if result.ok else result.error.code
    count = len(data.get("attractions", data.get("observations", []))) if data else 0
    summary = None
    if data:
        if name == "search_attractions":
            summary = {"content_ids": [row["content_id"] for row in data["attractions"]],
                       "basis": data.get("basis")}
        elif name == "get_attraction_detail":
            summary = {key: data.get(key) for key in ("content_id", "title", "address")}
        elif name == "get_weather":
            summary = {key: data.get(key) for key in ("date", "precipitation_probability_max",
                       "temperature_min_c", "temperature_max_c")}
        else:
            summary = {"province": data.get("province"), "kind": data.get("kind"), "observations": count}
    bus.publish("tool_completed", "execute", tool=name, ok=result.ok, error_code=code,
                fields=list(data) if data else [], result_count=count, result=summary,
                duration_ms=round((perf_counter() - started) * 1000))
    if code:
        text = ("API 키와 이용 권한을 확인해 주세요." if code in {"AUTH_FAILED", "MISSING_API_KEY"}
                else "조회 가능한 데이터가 없습니다." if code in {"NO_RESULT", "OUT_OF_FORECAST_RANGE", "MISSING_DATA"}
                else "외부 데이터를 가져오지 못했습니다.")
        warnings.append(warning(code, text, name))
    cache[key] = (data, code)
    return data, code


def execute(state):
    cache, warnings = state["cache"].copy(), list(state["warnings"])
    candidates = state["candidates"].copy()
    weather, air = state.get("weather"), state.get("air")
    point, attempted = state.get("weather_point"), state.get("weather_attempted", False)
    blocked = state.get("tour_blocked", False)
    for name, args in state["tasks"]:
        if name == "get_weather":
            located = next((row for row in candidates.values() if row.get("latitude") is not None
                            and row.get("longitude") is not None
                            and (row["latitude"], row["longitude"]) != (0, 0)), None)
            if not located:
                continue
            point = located["title"]
            attempted = True
            args = {**args, "latitude": located["latitude"], "longitude": located["longitude"]}
        data, code = call_tool(state, cache, warnings, name, args)
        if name == "get_weather":
            weather = data
        elif name == "get_air_quality":
            air = data
        elif name == "search_attractions":
            blocked = code in AUTH_ERRORS or code in {"TIMEOUT", "NETWORK_ERROR"}
            if data:
                size = min(12, max(3, state["conditions"]["count"] or 3) + 2)
                for row in [row for row in data["attractions"] if row["content_id"] not in candidates][:size]:
                    detail, detail_code = (call_tool(state, cache, warnings, "get_attraction_detail",
                                           {"content_id": row["content_id"]})
                                           if wants_attractions(state) else (None, None))
                    merged = {**row, **{key: value for key, value in (detail or {}).items() if value is not None}}
                    candidates[row["content_id"]] = {**merged, "detail_ok": bool(detail)}
                    if detail_code in AUTH_ERRORS:
                        blocked = True
                        break
    return {"cache": cache, "warnings": warnings, "candidates": candidates,
            "weather": weather, "air": air, "tour_blocked": blocked, "weather_point": point,
            "weather_attempted": attempted}


def integrate(state):
    return {"candidates": {key: value for key, value in state["candidates"].items()
                           if value["title"]}}


def minutes(value):
    hour, minute = map(int, value.split(":"))
    return 60 * hour + minute


def decide(state):
    c = state["conditions"]
    target = c["count"] or 3
    rain = (state.get("weather") or {}).get("precipitation_probability_max")
    threshold = c["max_rain_pct"] if c["max_rain_pct"] is not None else 50
    rain_switch = bool(c["rain_indoor"] and rain is not None and rain >= threshold)
    indoor = rain_switch or c["category"] == "indoor"
    selected, excluded = [], []
    for row in state["candidates"].values():
        description = row.get("overview") or ""
        title = row["title"]
        indoor_evidence = "실내" in description or re.search(r"(박물관|전시관|미술관|과학관)$", title)
        outdoor_evidence = "야외" in description or re.search(r"(공원|해수욕장|산책로)$", title)
        if indoor and not (indoor_evidence and not outdoor_evidence):
            excluded.append(f"{title} · 실내 방문 근거 부족")
        elif c["category"] == "outdoor" and not indoor and not (outdoor_evidence and not indoor_evidence):
            excluded.append(f"{title} · 야외 방문 근거 부족")
        else:
            selected.append(row)
    constraints = []
    impossible = False
    if c["start_time"] and c["end_time"]:
        window = minutes(c["end_time"]) - minutes(c["start_time"])
        lower_bound = target * (c["min_stay_minutes"] or 0)
        impossible = lower_bound > window
        if impossible:
            constraints.append(f"최소 체류 {lower_bound}분이 여행 시간 {window}분을 초과합니다.")
        elif lower_bound:
            constraints.append(f"여행 시간 {window}분에서 최소 체류 {lower_bound}분을 빼면 이동 등 여유는 최대 {window-lower_bound}분입니다.")
        else:
            constraints.append(f"체류와 이동의 합이 여행 시간 {window}분 이하여야 합니다.")
        constraints.append("실제 운영시간과 이동·체류 소요를 확인해야 합니다.")
    if c["max_leg_minutes"] is not None:
        constraints.append(f"구간당 이동 {c['max_leg_minutes']}분 이내인지 확인할 자료가 없습니다.")
    if c["budget"] is not None:
        constraints.append(f"예산 {c['budget']:,}원 충족 여부는 입장료·이동비 확인이 필요합니다.")
    if c["rain_indoor"]:
        constraints.append(f"일별 최대 강수 확률 {threshold}% 이상이면 실내 후보를 탐색합니다."
                           if rain is not None else "강수 확률 확인 불가로 날씨에 따른 교체 여부를 판단할 수 없습니다.")
    search_requested = wants_attractions(state)
    if not search_requested:
        selected = []
    missing_point = wants_weather(state) and not state.get("weather_attempted")
    replan = ((search_requested and len(selected) < target or missing_point) and not impossible
              and not state.get("tour_blocked") and state["replan_count"] < MAX_REPLANS)
    state["bus"].publish("constraints_checked", "decide", matched=len(selected), target=target,
                         indoor=bool(indoor), replan=bool(replan), infeasible=impossible)
    return {"indoor": indoor, "selected": selected[:target], "excluded": excluded,
            "constraints": constraints, "needs_replan": bool(replan), "infeasible": impossible}


def replan(state):
    count = state["replan_count"] + 1
    # Indoor search begins on page 1 if the initial search was for outdoor candidates.
    index = count
    if state["indoor"] and state["conditions"]["category"] != "indoor":
        index -= 1
    tasks = search_tasks(state, index)
    if wants_weather(state) and not state.get("weather_attempted"):
        tasks.append(("get_weather", {"date": state["conditions"]["date"]}))
    state["bus"].publish("replanned", "replan", count=count, reason="제약에 맞는 후보 수 부족",
                         tools=[name for name, _ in tasks], cached_results=len(state["cache"]))
    return {"tasks": tasks, "replan_count": count}


def respond(state):
    c = state.get("conditions", {})
    warnings = state["warnings"]
    questions = state["questions"]
    evidence_list = []
    draft = None
    status = "complete"
    if state.get("fatal"):
        status, reply = "unavailable", warnings[-1]["message"]
    elif questions:
        status, reply = "needs_input", "일정을 구성하려면 아래 조건을 알려 주세요.\n" + "\n".join(questions)
    elif state.get("intent") == "help":
        reply = "대화에서 여행 날짜와 시간, 장소 수를 입력하세요. 제안한 일정은 저장 버튼으로 저장할 수 있습니다. 계획 관리에서 조회·수정·삭제하고, 실행 로그에서 처리 과정을 확인하세요."
    elif state.get("intent") == "other":
        reply = "안녕하세요. 국내 여행 목적지와 날짜, 시간, 방문하고 싶은 장소 수를 알려 주세요."
    else:
        lines = []
        selected = state.get("selected", [])
        items = []
        for index, row in enumerate(selected, 1):
            tool = "get_attraction_detail" if row["detail_ok"] else "search_attractions"
            fact = f"{row['title']} · {row.get('address') or '주소 확인 불가'}"
            item_evidence = evidence(tool, fact)
            evidence_list.append(item_evidence)
            lines.append(f"{index}. {fact}")
            items.append({key: row.get(key) for key in ("content_id", "title", "address", "latitude", "longitude")}
                         | {"evidence": [item_evidence]})
        if items:
            lines.append("관광지는 현재 카탈로그 기준입니다. 방문일 운영 여부와 개별 방문 시간은 확인이 필요합니다.")
        if items and c["date"] and c["start_time"] and c["end_time"] and not state.get("infeasible"):
            draft = {"session_id": state["bus"].session_id, "title": f"{c['region']} 여행", "region": c["region"],
                     "visit_date": c["date"], "start_time": c["start_time"], "end_time": c["end_time"],
                     "items": items, "notes": " ".join(state.get("constraints", []))}
        if state.get("weather"):
            weather = state["weather"]
            rain = weather["precipitation_probability_max"]
            forecast = (f"{weather['date']} {state['weather_point']} 인근 일별 최대 강수 확률 "
                        f"{f'{rain:g}%' if rain is not None else '확인 불가'}")
            low, high = weather["temperature_min_c"], weather["temperature_max_c"]
            if low is not None and high is not None:
                forecast += f", 최저 {low:g}°C·최고 {high:g}°C"
            lines.append(forecast)
            evidence_list.append(evidence("get_weather", forecast))
        if wants_weather(state) and not state.get("weather_attempted"):
            warnings = [*warnings, warning("MISSING_DATA", "목적지에서 예보를 조회할 좌표를 확인하지 못했습니다.",
                                           "get_weather")]
        if state.get("air"):
            row = next((row for row in state["air"]["observations"]
                        if row["pm10_ug_m3"] is not None or row["pm25_ug_m3"] is not None), None)
            if row:
                pm10, pm25 = row["pm10_ug_m3"], row["pm25_ug_m3"]
                observation = (f"현재 대기질 · {state['destination'].air_province} {row['station_name']} 측정소 "
                               f"{row['measured_at']} 관측 · "
                               f"PM10 {pm10 if pm10 is not None else '결측'} / "
                               f"PM2.5 {pm25 if pm25 is not None else '결측'} µg/m³")
                lines.append(observation)
                evidence_list.append(evidence("get_air_quality", observation))
        lines.extend(state.get("constraints", []))
        if state.get("excluded"):
            lines.append("제외 후보 · " + ", ".join(state["excluded"][:8]))
        if state["replan_count"] >= MAX_REPLANS and len(selected) < (c["count"] or 3):
            lines.append("재계획을 3회 수행했습니다. 장소 수나 분류 조건을 조정하면 다시 탐색할 수 있습니다.")
        if not lines:
            lines.append("확인된 결과가 없습니다.")
        needs_candidates = wants_attractions(state)
        if warnings or state.get("infeasible") or (needs_candidates and len(items) < (c["count"] or 3)):
            status = "partial"
        reply = "\n".join(lines)
    return {"result": {"reply": reply, "status": status, "questions": questions,
                        "draft_plan": draft, "evidence": evidence_list, "warnings": warnings}}


def tracked(name, node):
    def run(state):
        bus = state["bus"]
        started = perf_counter()
        bus.publish("node_enter", name)
        try:
            result = node(state)
        except Exception:
            bus.publish("node_exit", name, ok=False, duration_ms=round((perf_counter() - started) * 1000))
            raise
        bus.publish("node_exit", name, ok=True, duration_ms=round((perf_counter() - started) * 1000))
        return result
    return run


def after_analysis(state):
    return "respond" if state.get("fatal") or state["questions"] or state["intent"] in {"help", "other"} else "plan"


builder = StateGraph(State)
for name, node in (("analyze", analyze), ("plan", plan), ("execute", execute),
                   ("integrate", integrate), ("decide", decide), ("replan", replan), ("respond", respond)):
    builder.add_node(name, tracked(name, node))
builder.add_edge(START, "analyze")
builder.add_conditional_edges("analyze", after_analysis, ["plan", "respond"])
builder.add_edge("plan", "execute")
builder.add_edge("execute", "integrate")
builder.add_edge("integrate", "decide")
builder.add_conditional_edges("decide", lambda state: "replan" if state["needs_replan"] else "respond",
                              ["replan", "respond"])
builder.add_edge("replan", "execute")
builder.add_edge("respond", END)
graph = builder.compile()


def chat(message, session_id=None, *, subscribers=(record_event,)):
    session_id = str(session_id or uuid4())
    run_id = str(uuid4())
    bus = EventBus(session_id, run_id, subscribers)
    started = perf_counter()
    with SESSION_LOCKS[hash(session_id) % len(SESSION_LOCKS)]:
        warnings = []
        try:
            memory = store.read_memory(session_id)
        except sqlite3.Error:
            memory = {}
            warnings.append(warning("MEMORY_UNAVAILABLE", "이전 대화 조건을 읽을 수 없습니다."))
        state = graph.invoke({"bus": bus, "message": message, "memory": memory, "warnings": warnings,
                              "questions": [], "cache": {}, "candidates": {}, "replan_count": 0},
                             config={"recursion_limit": 32})
        result = state["result"]
        if "conditions" in state:
            try:
                store.write_memory(session_id, {"conditions": state["conditions"],
                    "pending": bool(state["questions"]), "pending_intent": state["intent"],
                    "last_reply": result["reply"][:500]})
            except sqlite3.Error:
                result["warnings"].append(warning("MEMORY_UNAVAILABLE", "대화 조건을 저장하지 못했습니다."))
        bus.publish("run_finished", "respond", status=result["status"], replan_count=state["replan_count"],
                    duration_ms=round((perf_counter() - started) * 1000))
    return ChatResponse(session_id=session_id, run_id=run_id, events=bus.events, **result)
