# TripMind AI

전국 국내 여행 일정에 관광지, 날씨와 대기질 정보를 연결하는 Agent 서비스다. 목적지의 시도 또는 시·군·구, 날짜, 시간과 방문 장소 수를 입력하면 후보와 판단 근거를 제시한다. 한 요청은 한 목적지를 기준으로 하며, 같은 이름의 지역이 여러 곳이면 시도를 확인한다. 확인한 계획은 저장하고 별도 실행 로그 화면에서 처리 과정을 확인할 수 있다.

## 실행

Python 3.10 이상을 사용한다. Windows의 Git Bash에서 저장소 루트 기준으로 실행한다.

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r backend/requirements.txt
test -f backend/.env || cp backend/.env.example backend/.env
python -m uvicorn backend.main:app
```

브라우저에서 [여행 플래너](http://127.0.0.1:8000/)를 연다. [FastAPI 문서](http://127.0.0.1:8000/docs)와 [상태 확인](http://127.0.0.1:8000/health)도 제공한다. 첫 실행 시 `backend/tripmind.sqlite3`에 계획, 세션과 로그를 저장한다. VS Code PowerShell에서는 활성화 없이 `.\.venv\Scripts\python.exe -m uvicorn backend.main:app`으로 실행할 수 있다.

`backend/.env`가 이미 있으면 기존 설정을 사용한다. TourAPI와 에어코리아는 공공데이터포털에서 각각 활용 신청한 뒤 일반 인증키의 Decoding 값을 `TOUR_API_SERVICE_KEY`, `AIRKOREA_SERVICE_KEY`에 넣는다. SSAFY GMS 키와 제공자가 안내하는 OpenAI 호환 기본 주소, 모델 ID는 각각 `OPENAI_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`에 넣는다. Open-Meteo 비상업 공개 예보는 키 없이 호출한다. [API별 이용 조건 및 발급 안내](docs/api_verification.md)

## 기능

- LangGraph 일정 대화, 세션 후속 조건 반영, 비가 올 때 실내 후보 탐색, 최대 3회 재계획
- 관광지 추천과 함께 해당 시도의 현재 대기질을 조회하고, 방문일이 있으면 확인된 관광지 좌표의 날짜별 날씨도 표시
- 계획 저장·조회·수정·삭제와 같은 날짜 일정 중복 알림
- 실행 이벤트와 Tool 호출 결과·소요 시간 표시, 세션별 실행 로그 조회·삭제
- 검증 가능한 시간 예산과 후보 근거 표시. 운영시간, 입장료 및 이동시간이 확인되지 않으면 사용자에게 표시한다.

필수 기능 범위는 F3001~F3019다. F3020~F3023 심화 기능은 구현 범위에서 제외했다.

## 테스트

```bash
python -m unittest backend.tests.test_service backend.tests.test_external_apis backend.tests.test_llm -v
```

키 누락 시 해당 실연동 테스트에 `skipped`가 표시된다. 외부 네트워크 없이 서비스 구조와 실패 처리를 확인하려면 `python -m unittest backend.tests.test_service backend.tests.test_external_apis.LocalToolTests -v`를 실행한다.

## 설계와 검증

- [요구사항 및 대표 시나리오](docs/requirements.md)
- [API 출처·이용 조건과 실제 검증 결과](docs/api_verification.md)
- [Tool 입출력 및 오류 계약](docs/tool_spec.md)
- [LangGraph 및 로깅 설계](docs/agent_design.md)
- [FastAPI 및 SQLite 설계](docs/api_spec.md)
- [필수 기능 검증 결과와 제출 증거](docs/verification.md)
