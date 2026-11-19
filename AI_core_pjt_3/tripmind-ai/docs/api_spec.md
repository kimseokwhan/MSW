# 백엔드 API와 SQLite 설계

프로젝트 자체 계약이다. [FastAPI 라우터](../backend/routers/api.py)와 [SQLite 저장소](../backend/database/store.py)에 구현했다. `GET /health`는 기본 상태를 확인한다.

## SQLite 테이블

문자열 날짜는 ISO 날짜, 계획의 시간은 KST `HH:MM`, 생성·갱신·이벤트 시각은 UTC ISO 8601로 저장한다. 각 연결에서 `PRAGMA foreign_keys=ON`을 적용한다.

| 테이블 | 키와 필드 | 규칙 |
| --- | --- | --- |
| `sessions` | `id TEXT PK`, `memory_json TEXT`, `created_at TEXT`, `updated_at TEXT` | UUID, 구조화 조건·요약·초안 토큰. 비밀 및 원시 API 응답 제외 |
| `plans` | `id INTEGER PK`, `session_id TEXT FK NULL`, `title TEXT`, `region TEXT`, `visit_date TEXT`, `start_time TEXT`, `end_time TEXT`, `notes TEXT NULL`, `created_at TEXT`, `updated_at TEXT` | 세션 삭제 시 참조 SET NULL. 동일 날짜의 단일 시간대, 시작 < 종료. `(visit_date,start_time,end_time)` 인덱스 |
| `plan_items` | `id INTEGER PK`, `plan_id INTEGER FK`, `position INTEGER`, `content_id TEXT NULL`, `title TEXT`, `address TEXT NULL`, `latitude REAL NULL`, `longitude REAL NULL`, `start_time TEXT NULL`, `end_time TEXT NULL`, `evidence_json TEXT` | 계획 삭제 시 CASCADE. `UNIQUE(plan_id, position)`. 확인되지 않은 방문 슬롯은 null. 두 시각이 있으면 계획 시간대 내이고 시작 < 종료 |
| `execution_logs` | `event_id TEXT PK`, `session_id TEXT FK`, `run_id TEXT`, `seq INTEGER`, `event_type TEXT`, `node TEXT`, `occurred_at TEXT`, `payload_json TEXT` | 이벤트 append-only. `UNIQUE(run_id, seq)`, 세션별 조회 인덱스. 로그 삭제는 로그 행에 적용 |

계획 저장·수정은 계획 본문, 항목 목록, 충돌 검색을 하나의 쓰기 트랜잭션으로 처리한다. 같은 날짜이고 `existing.start_time < new.end_time && new.start_time < existing.end_time`인 계획을 반환한다. 경계에 맞닿은 경우는 충돌에서 제외하고, 수정 시 대상 자체도 제외한다. 충돌이 있어도 저장한다. Day 1 설계는 단일 사용자 로컬 실행을 대상으로 한다.

## 공통 구조

- `PlanInput`은 `{session_id?:uuid,title:string,region:string,visit_date:date,start_time:HH:MM,end_time:HH:MM,notes?:string|null,items:PlanItemInput[]}`이다. 제목·지역 필수, 항목 1~100개. 날짜와 시간 필수, UTC 오프셋 대신 KST 방문 시간 사용.
- `PlanItemInput`은 `{content_id?:string|null,title:string,address?:string|null,latitude?:number|null,longitude?:number|null,start_time?:HH:MM|null,end_time?:HH:MM|null,evidence?:Evidence[]}`다. 배열 순서가 방문 순서다. 슬롯 시작과 종료는 함께 지정하거나 둘 다 null로 보낸다.
- `Plan`은 입력 필드에 `id:int, created_at:datetime, updated_at:datetime`을 추가하고, 각 항목에 `id:int, position:int`를 추가한다. `PlanSummary`는 `id,title,region,visit_date,start_time,end_time,created_at,updated_at,item_count`다.
- `Evidence`는 `{tool:string,source:string,fact:string,reference_url?:url}`다. `Warning`은 `{code:string,message:string,tool?:string}`다. 실행 이벤트 스키마는 [Agent 설계](agent_design.md#실행-이벤트)를 따른다.
- 목록 기본 `limit=20`, 상한 100, `offset=0`. 입력 검증 422, 없는 리소스 404, 서버 저장소 장애 503은 `{"error":{"code":"...","message":"..."}}` 형식의 고정 안내를 사용한다. Tool 실패는 가능한 경우 200 대화 응답의 `warnings`에 넣는다.

## HTTP 경로

| 메서드와 경로 | 요청 | 성공 응답 |
| --- | --- | --- |
| POST `/api/chat` | JSON `{session_id?:uuid,message:string}`, 누락 세션은 새 세션 생성 | 200 `{session_id:uuid,run_id:uuid,status:"complete"\|"needs_input"\|"partial"\|"unavailable",reply:string,questions:string[],draft_plan:PlanInput|null,evidence:Evidence[],warnings:Warning[],events:ExecutionEvent[]}` |
| POST `/api/plans` | JSON `PlanInput` | 201 `{plan:Plan,conflicts:PlanSummary[]}` |
| GET `/api/plans` | 쿼리 `visit_date?:date,limit?:int,offset?:int`, 날짜·시작·ID 순 | 200 `{items:PlanSummary[],total:int}` |
| GET `/api/plans/{id}` | 정수 ID | 200 `Plan` |
| PATCH `/api/plans/{id}` | 정수 ID, 수정할 `title,region,visit_date,start_time,end_time,notes,items` 한 개 이상. `items` 지정 시 목록 전체 교체. 병합 후 검증 | 200 `{plan:Plan,conflicts:PlanSummary[]}` |
| DELETE `/api/plans/{id}` | 정수 ID | 204, 본문 없음 |
| GET `/api/logs` | 쿼리 `limit?,offset?`, 마지막 이벤트 시각 내림차순과 세션 ID 순 | 200 `{items:[{session_id:uuid,event_count:int,run_count:int,last_event_at:datetime}],total:int}` |
| GET `/api/logs/{session_id}` | UUID | 200 `{session_id:uuid,events:ExecutionEvent[]}`, 실행 시작 시각과 실행 내 seq 순. 동일 시작 시각에는 run_id로 정렬 |
| DELETE `/api/logs/{session_id}` | UUID | 204, 해당 세션 실행 로그 삭제 |

## 화면 연결

대화 화면은 POST 진행 중 로딩 상태를 보여준다. 응답을 받으면 결과와 실행 타임라인을 실행 순서대로 표시하고 재계획과 Tool 실패를 강조한다. 키 누락은 설정 안내로 표시한다. 사용자가 저장을 선택하면 초안을 POST하고 충돌 목록을 보여준다. 계획 화면은 목록·상세를 조회하고 수정·삭제 성공 뒤 목록을 갱신한다.
