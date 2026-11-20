# TripMind AI 제출 체크리스트 수행 가이드

보내주신 27개 항목의 번호와 요구사항 ID를 기준으로, 확인 순서와 제출 칸 작성 방법을 정리한다. [기존 검증 기록](verification.md)과 [API 실연동 기록](api_verification.md)은 이미 확보한 근거를 찾을 때 사용한다.

## 준비와 결과 기록

프로젝트 루트의 Git Bash에서 가상환경을 활성화한 뒤 아래 명령을 실행한다. 마지막 명령은 서버를 계속 실행하므로 그 상태에서 브라우저를 연다.

```bash
source .venv/Scripts/activate
python -m backend.tools.registry
python -m unittest backend.tests.test_llm backend.tests.test_service backend.tests.test_external_apis -v
python -c "from backend.agents.graph import graph; print(graph.get_graph().draw_mermaid())"
python -m uvicorn backend.main:app
```

- [앱 화면](http://127.0.0.1:8000/)과 [FastAPI Swagger](http://127.0.0.1:8000/docs)를 사용한다. Swagger에서는 경로를 펼친 뒤 **Try it out → Execute**로 응답을 확인한다.
- 브라우저에서 **F12 → Network → Fetch/XHR**를 열고 요청을 다시 보낸다. `chat` 항목의 **Response**에서 `reply`, `evidence`, `events`를 볼 수 있다. 실행 로그 상세 API는 `GET /api/logs/{session_id}`다. 세션 ID는 대화 응답의 `session_id`에서 가져온다.
- 결과는 **통과 / 부분 확인 / 실패 / 미확인 / 해당 없음**으로 적는다. 여러 조건 중 일부만 확인했다면 **부분 확인**으로 표시하고 확인 범위를 비고에 쓴다. 테스트가 `skipped`이면 해당 호출은 **미확인**이다.
- 새 캡처는 `docs/evidence/번호_확인내용.png`로 정리한다. 아래에서 제안하는 번호 붙은 파일명은 새로 찍을 캡처 이름이다. 기존 경주 캡처는 역사적 증빙으로 사용하고, 화면 동작을 확인하는 항목은 현재 버전에서 다시 찍는다. 검증용 응답으로 만든 캡처는 비고에 **재현 테스트**라고 표시한다.

## Tool 1~4

### 1 · F3001 Tool 등록과 정상·실패 응답

1. `python -m backend.tools.registry` 출력의 이름·설명·입력 스키마를 [Tool 정의서](tool_spec.md)와 대조한다. 현재 네 Tool의 `kind`는 `external`이다.
2. `ExternalApiTests`로 관광지 검색·상세, 날씨, 대기질 정상 응답을 확인한다. 아래 명령은 각 Tool의 잘못된 입력과 키 누락 응답을 출력한다. 키 누락은 현재 Python 프로세스 안에서만 재현한다.

```bash
python - <<'PY'
from unittest.mock import patch
from backend.tools import external_apis as api
from backend.tools.registry import TOOLS

for name, (_, _, tool) in TOOLS.items():
    result = tool()
    print(name, result.model_dump(mode="json"))
    assert not result.ok and result.error.code == "INVALID_INPUT"

with patch.object(api, "setting", return_value=""):
    for tool, args in [
        (api.search_attractions, {"keyword": "경주"}),
        (api.get_attraction_detail, {"content_id": "1"}),
        (api.get_air_quality, {"province": "경북"}),
    ]:
        result = tool(**args)
        print(tool.__name__, result.model_dump(mode="json"))
        assert not result.ok and result.error.code == "MISSING_API_KEY"
PY
```

**증빙** `01_tool_registry.png`, `01_tool_errors.png`, 실연동 테스트 출력. **비고 예시** “등록 Tool 4개는 외부 Tool. Open-Meteo의 키 누락 검사는 해당 없음.”

### 2 · F3002 기준 날짜와 실제 조회 기준

아래 결과에서 첫 호출의 `requested_date`가 KST 오늘인지, 두 번째가 요청한 날짜인지 확인한다. 두 호출 모두 `basis=current_catalog`이면 관광지 정보는 현재 카탈로그 기준이다. 앱 답변에서도 방문일 운영 여부를 별도로 확인하라는 문구를 찾는다.

```bash
python - <<'PY'
from datetime import datetime, timedelta
from backend.tools.external_apis import KST, search_attractions

today = datetime.now(KST).date()
for args in ({}, {"visit_date": today + timedelta(days=7)}):
    result = search_attractions(keyword="경주", **args)
    if result.ok:
        data = result.data
        print(data.requested_date, data.checked_at, data.basis)
    else:
        print(result.error.code)
PY
```

**증빙** `02_date_basis.png`와 미래 날짜 대화 화면. **비고 예시** “미래 방문일을 요청일로 보존하고, 관광지는 현재 카탈로그에서 검색.”

### 3 · F3002·F3003 후보 ID와 결측 속성

`test_tourapi_search_and_detail`을 확인하고 `tool_completed.payload.result.content_ids`에 있는 후보가 상세 호출의 `tool_requested.payload.arguments.content_id`로 전달됐는지 대조한다. 주소나 좌표 등이 빠진 실제 후보를 발견하면 상세 응답의 `null`과 판단 보류를 함께 확인한다.

**증빙** [실제 일정 전체 로그](evidence/normal-live.json), `03_content_id.png`. **비고 예시** “실제 후보 ID 전달 확인. TourAPI 실응답의 결측 후보는 확보하지 못해 미확인.”

### 4 · F3004 보조 정보와 빈 결과

대화에서 `부산의 현재 대기질과 미세먼지를 알려 줘`라고 입력한다. 측정소, 관측 시각, PM10·PM2.5, 출처 링크를 확인한다. 보조 Tool의 빈 결과 형식을 재현하려면 아래처럼 데이터 공급 단계에서 `NO_RESULT`를 만들고 반환 객체를 확인한다.

```bash
python - <<'PY'
from unittest.mock import patch
from backend.tools.external_apis import ApiError, get_air_quality
with patch("backend.tools.external_apis.public_rows", side_effect=ApiError("NO_RESULT")):
    result = get_air_quality(province="부산")
print(result.model_dump(mode="json"))
assert not result.ok and result.error.code == "NO_RESULT"
PY
```

**증빙** `04_air_source.png`, `04_no_result.png`. **비고 예시** “정상 관측과 출처는 실연동. 빈 결과는 재현 테스트. 대기질 표시에는 측정소명과 측정 시각을 사용.”

## 메인 Agent 5~13

정상 일정 예시로 `11월 21일부터 24일까지 부산 여행 일정을 짜 줘. 매일 오전 10시부터 오후 5시까지 하루 2곳씩 실내와 야외를 섞어 줘.`를 사용한다. 해당 날짜가 지났다면 미래 날짜로 바꿔 실행한다.

### 5 · F3005 요청 조건 추출

정상 예시와 `부산 여행 일정을 짜 줘`를 각각 새 대화에서 실행한다. `conditions_extracted.payload.conditions`에서 지역·날짜·시간·장소 수·유형을 확인하고, 두 번째 요청에서 비어 있는 값과 추가 질문을 대조한다.

**증빙** `05_conditions_full.png`, `05_conditions_missing.png`. **비고 예시** “누락된 날짜와 시간은 조건 목록에 채워지지 않았고 화면에서 추가 질문을 받음.”

### 6 · F3006 Tool 계획과 그래프

정상 일정의 `plan_created`와 `tool_requested` 순서를 비교한다. `안녕하세요`를 새 대화에서 보내 Tool 요청이 없는지 확인한다. 터미널의 Mermaid 그래프 출력을 [Agent 설계](agent_design.md)와 대조한다.

**증빙** `06_graph.png`, `06_tool_order.png`, [대표 시나리오 로그](evidence/scenario-runs.json)의 `no-tool`.

### 7 · F3007·NF3003 ID 전달과 단일 Tool 장애

3번의 ID 전달 증빙을 사용한다. `test_weather_failure_returns_tourism_and_warning`에서 날씨 `TIMEOUT` 후 부분 일정이 반환되는지 확인한다. 이어서 앱에서 별도 정상 요청을 보낸다.

**증빙** [날씨 실패 화면](evidence/weather-failure.png), `07_next_request.png`, 테스트 결과. **비고 예시** “타임아웃은 재현했고, 별도 요청은 정상 실행.”

### 8 · F3008 계산과 불확실한 값

`11월 21일 부산 오전 10시부터 오후 1시까지 관광지 2곳을 추천해 줘. 각 장소에서 최소 30분 머물고 싶어.`를 보낸다. 시간 창 180분에서 최소 체류 60분을 빼면 최대 120분이 남는다. 확인되지 않은 운영시간이나 실제 이동시간을 확정하지 않는지도 본다.

**증빙** `08_constraint_math.png`. **비고 예시** “남은 최대 시간은 계산했고, 실제 이동시간은 확인이 필요한 값으로 안내.”

### 9 · F3009 재계획과 결과 재사용

`test_rain_replans_and_reuses_forecast` 또는 대표 로그의 `rain-replan`을 본다. `replanned`가 1회이고 새로운 관광지 검색은 추가되지만 날씨 Tool 요청은 1회인지 확인한다.

**증빙** [실내 재계획 화면](evidence/rain-replan.png), [대표 로그](evidence/scenario-runs.json). **비고 예시** “재현용 강수 확률 80%에서 재계획 1회, 날씨 1회.”

### 10 · F3009·NF3004 재계획 상한

`test_replan_cap_and_unique_search` 또는 대표 로그의 `cap`을 본다. `replanned.count`가 1, 2, 3이고 마지막에 `run_finished`로 종료되며 답변에 상한과 조건 변경 안내가 있는지 확인한다.

**증빙** `10_replan_cap.png`, [대표 로그](evidence/scenario-runs.json). **비고 예시** “후보가 계속 부족한 상황을 재현해 상한 3회에서 종료 확인.”

### 11 · F3010 후속 요청

같은 대화에서 일정을 만든 뒤 `종료 시간만 오후 6시로 바꿔 줘`를 보낸다. 같은 세션의 `conditions_extracted` 두 건을 비교한다. 종료 시간만 바뀌고 날짜·지역·시작 시간·장소 수가 유지되는지 확인한다.

**증빙** `11_before_after.png`, `test_followup_only_changes_given_condition` 결과.

### 12 · F3011 추천 근거와 제외 사유

`부산에서 실내 관광지만 3곳 추천해 줘`처럼 분류 조건을 보낸다. 응답에서 추천 목록과 제외 후보의 사유를 확인한다. 하단 **출처**에서 관광지와 대기질의 근거를 확인한다. 날짜가 있는 일정이면 날씨가 조회됐을 때 그 출처도 확인한다.

**증빙** `12_recommendation_evidence.png`.

### 13 · F3011 위험 도메인 안내

**결과** 해당 없음. **증빙** [도메인 정의](requirements.md). **비고** “국내 여행 일정 추천이며 건강·금융 조언을 제공하는 도메인이 아님.”

## 로깅 Agent와 실행 로그 14~18

### 14 · F3012·F3013 이벤트와 세션 분리

두 번 **새 대화**를 만들어 각각 요청한다. **실행 로그** 탭과 상세 API에서 서로 다른 `session_id`를 확인한다. `node_enter`·`node_exit`, `tool_requested`·`tool_completed`와 `duration_ms`, `llm_decision`의 `intent`·`reason`을 확인한다.

**증빙** `14_log_sessions.png`, `14_llm_decision.png`, [실제 전체 로그](evidence/normal-live.json).

### 15 · F3012 로깅 구독 없이 실행

`test_no_tool_log_isolation_and_subscriber_failure`에서 `subscribers=()`로 호출한 대화가 정상 응답했는지 확인한다.

**증빙** `15_logging_disabled.png`, [서비스 테스트 코드](../backend/tests/test_service.py).

### 16 · F3013 로깅 Agent의 LLM 미호출

[로깅 코드](../backend/agents/logger.py)에서 이벤트를 저장 함수에 전달하는 부분을 확인한다. 실행 로그의 `llm_decision`은 메인 Agent의 요청 분석 단계에서 발생한다.

**증빙** `16_logger_code.png`, 세션 로그.

### 17 · F3013 원본 이벤트와 저장 장애

한 요청의 `POST /api/chat → events`와 `GET /api/logs/{session_id} → events`를 같은 `run_id`로 맞춘다. `event_id`, `seq`, `payload`가 일치하는지 대조한다. 저장 구독자가 예외를 내는 경로는 15번과 같은 서비스 테스트로 확인한다.

**증빙** `17_event_comparison.png`, 테스트 결과. **비고 예시** “실제 응답과 저장 로그를 대조했고 구독자 실패는 로컬에서 재현.”

### 18 · F3014 실행 로그 조회·삭제

Swagger에서 `GET /api/logs`, `GET /api/logs/{session_id}`로 목록과 순서대로 정렬된 상세를 확인한다. 전용 테스트 세션으로 `DELETE /api/logs/{session_id}`를 실행해 `204`, 이어 같은 ID 조회에서 `404`를 확인한다. Swagger에서 로그 수정 메서드도 확인한다.

**증빙** `18_logs_api.png`, `18_logs_delete.png`.

## 계획 관리와 서비스 화면 19~22

### 19 · F3015 저장과 시간 중복

계획 초안을 저장한 뒤 목록과 상세 API에서 날짜·시간·`created_at`을 확인한다. 같은 날 시간이 겹치는 두 번째 테스트 계획을 저장해 응답 상태 `201`과 `conflicts`를 확인한다.

**증빙** `19_plan_conflict.png`, `test_normal_plan_and_crud_overlap` 결과.

### 20 · F3016 계획 수정·삭제

**저장한 계획** 탭에서 테스트 계획 제목을 바꾼 뒤 목록이 갱신되는지 확인한다. 같은 테스트 계획을 삭제하고 목록에서 사라지는 장면을 남긴다.

**증빙** `20_plan_edit.png`, `20_plan_deleted.png`. **비고 예시** “삭제 API와 화면 목록 갱신을 확인.” 화면 확인 전이라면 부분 확인으로 기록한다.

### 21 · F3017·F3018 FastAPI와 화면 연결

Swagger에서 대화·계획·로그 경로를 [API 명세](api_spec.md)와 비교한다. Network 탭에서 메시지를 보낼 때 `POST /api/chat`, 계획 탭을 열 때 `GET /api/plans`가 호출되고 응답이 화면에 표시되는지 확인한다.

**증빙** `21_swagger.png`, `21_chat_network.png`, `21_plans_network.png`. Swagger의 응답 예시와 실제 JSON이 다르면 차이를 비고에 남긴다.

### 22 · F3019 처리 중·실패·재계획 화면

정상 요청을 보내는 순간 처리 중 표시를 캡처한다. 실행 과정에서 단계와 Tool이 발생 순서대로 나오는지 확인한다. 실패, 키 누락, 재계획은 실제 발생 시 기록하거나 재현 결과를 첨부한다.

**증빙** `22_loading.png`, 기존 [재계획](evidence/rain-replan.png), [Tool 실패](evidence/weather-failure.png), [키 누락](evidence/missing-key.png). **비고 예시** “기존 재계획·실패·키 누락 캡처는 재현 테스트 화면.”

## 대표 시나리오와 제출 점검 23~27

### 23 · 필수·NF3005 대표 요청과 응답 시간

[대표 시나리오 로그](evidence/scenario-runs.json)의 `normal`, `rain-replan`, `cap`, `weather-failure`, `no-tool` 다섯 사례를 확인한다. 각 사례의 요청, 최종 `reply`, Tool 순서, 재계획 여부, 기대와 실제의 차이, `run_finished.payload.duration_ms`를 적는다. 실사용 응답 시간은 현재 앱에서 정상 요청을 보내고 같은 필드에서 측정한다.

**증빙** [대표 시나리오 로그](evidence/scenario-runs.json), [실제 전체 로그](evidence/normal-live.json), `23_current_duration.png`. **비고 예시** “재현 테스트와 실제 호출의 처리 시간은 별도 기록.”

### 24 · 필수 전체 실행과 재계획 로그 첨부

실제 정상 요청 한 건의 **전체 이벤트**와 실제로 재계획이 발생한 사례의 로그를 첨부한다. 기존 경주 로그는 초기 검증 기록으로 사용할 수 있고, 현재 전국·여러 날 기능의 증빙은 새 요청의 응답 JSON을 함께 저장한다.

**증빙** [실제 정상 요청](evidence/normal-live.json), [재계획 사례](evidence/scenario-runs.json)의 `rain-replan`, 새로 저장한 `24_current_run.json`.

### 25 · NF3001·NF3002 키와 오류 노출

소스와 제출 파일에서 키가 포함됐는지 확인한다. `.env`와 로컬 SQLite는 제출 대상에서 제외됐는지 확인하고, 오류 화면에는 안전한 안내와 오류 코드만 나오는지 본다. 키 값 자체와 `.env`는 캡처하지 않는다.

**증빙** `25_secret_check.png`, [오류 화면](evidence/weather-failure.png), [.gitignore](../.gitignore). **비고 예시** “이전 점검에서 실제 키 3개를 소스·Markdown·JSON 등 30개 파일과 대조했고 일치 0건. 최종 제출 파일은 제출 직전 다시 확인.”

### 26 · NF3006·NF3007 모듈과 외부 API 이용 조건

`frontend/`, `backend/agents/`, `backend/tools/`를 탐색기에서 확인한다. 외부 API별 출처, 호출 한도와 이용 조건이 문서에 있는지 대조한다.

**증빙** `26_project_structure.png`, [README](../README.md), [외부 API 이용 조건](api_verification.md#출처-필수-인자와-이용-조건).

### 27 · 필수 최종 제출 대조

제출 폴더에서 [요구사항 정의서](requirements.md), [기획 검증 기록](api_verification.md), [Agent 설계](agent_design.md), [Tool 정의](tool_spec.md), [API 명세](api_spec.md), 소스, 캡처, 실행 로그, [README](../README.md), [검증 결과](verification.md), 작성한 셀프 체크리스트를 대조한다. 대표 화면은 현재 전국 여행 버전에서 다시 확인한다.

**증빙** `27_submission_files.png`와 최종 체크리스트. **비고 예시** “심화 기능 미선택. 1일차 16시 기준은 당시 미충족이며, 이후 API 3종 실제 호출 성공 기록을 별도 첨부.”

## 제출 칸에 옮겨 적는 예시

| 번호 | 결과 | 증빙 | 비고 |
| --- | --- | --- | --- |
| 9 | 통과 | `rain-replan.png`, `scenario-runs.json`의 `rain-replan` | 강수 80% 재현. 재계획 1회, 날씨 조회 1회 확인. |
| 13 | 해당 없음 | `requirements.md` | 국내 여행 일정 추천 도메인. |
| 20 | 부분 확인 | `plans.png`, 서비스 테스트 결과 | 수정 화면과 삭제 API 확인. 삭제 후 목록 캡처는 추가 필요. |
