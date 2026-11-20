# 외부 API와 LLM 검증 기록

## 전국 목적지 확장 검증 (2026-11-19 KST)

- TourAPI `ldongCode2` 공식 응답의 최상위 지역 16개와 시군구 행 269개를 [지역 코드 목록](../backend/tools/regions.json)에 저장했다. TourAPI가 반환하는 전남광주통합특별시 코드는 광주와 전남 검색 범위를 구별해서 사용한다. 에어코리아는 제공자 입력명인 `광주`, `전남`을 각각 사용한다. [TourAPI 공식 문서](https://www.data.go.kr/data/15101578/openapi.do)
- 서울, 부산 해운대구, 제주시, 수원, 여수, 광주광역시, 세종, 경주에서 실제 `areaBasedList2` 검색을 확인했다. 하위 구가 있는 수원은 시 코드 단독 호출에서 결과가 없었고, 하위 구 코드로 조회했을 때 수원시 주소가 반환됐다.
- 부산 해운대구와 제주시의 실제 Agent 실행에서 일정 초안과 날씨·대기질 결과를 받았다. 날씨에는 각 지역에서 실제 확인한 장소 좌표를 사용했고 대기질에는 각각 `부산`, `제주`를 전달했다. 동명 지역을 먼저 확인하는 경로는 `고성` 서비스 테스트에서 검증했다.
- 기존 경주 로그와 화면은 최초 필수 기능 검증의 기록이다.

검증일은 2026-11-18 KST다. 15:36 KST까지 기록한 결과는 **실제 호출 성공 1종, 미검증 2종**이다. 1일차 16시 기준은 서로 다른 외부 API 3종의 정상 JSON을 코드로 수신하고 Tool에 필요한 필드를 확인하는 것이다. TourAPI의 검색과 상세는 같은 제공 서비스 한 종으로 계산한다.

## 인증키 설정 후 재검증 (16:38 KST)

- `backend/.env`에서 공공 API 키 2개와 GMS 설정 3개를 읽었다. 키는 출력하지 않았다.
- TourAPI는 경주 키워드 검색, 후보 ID 전달, 상세의 이름·주소·좌표 확인에 성공했다.
- 에어코리아는 경북 측정소 관측 53건을 받았다. PM10 누락 1건, PM2.5 누락 3건을 확인했다.
- SSAFY GMS는 텍스트 응답과 모델의 `get_weather` 자동 선택 및 날짜·좌표 인자 검증에 모두 성공했다.
- Open-Meteo는 앞서 실제 예보 파싱에 성공했으며, 이번 통합 실행과 단독 재시도에서는 모두 `TIMEOUT`이었다. 통합 실행은 9건 중 8건 통과, 1건 실패였다.
- 누적 실제 호출 성공은 외부 API 3종이다. TourAPI와 에어코리아의 성공은 16시 이후에 확인했다.

### Open-Meteo 연결 진단

같은 예보 URL을 Python 바깥에서 Windows curl로 확인했다. IPv4는 8초 내 TCP 연결을 맺지 못했고, IPv6는 호스트 주소를 조회하지 못했다. 양쪽 모두 HTTP 응답을 받기 전에 종료됐다. 현재 네트워크에서는 `api.open-meteo.com:443`에 대한 HTTPS 접속과 프록시 정책 확인이 필요하다. 최근 실시간 호출 결과는 타임아웃으로 유지한다.

## 2026-11-19 필수 기능 통합 검증

- TourAPI, Open-Meteo, 에어코리아 3종과 GMS 텍스트 응답·Tool 자동 선택을 같은 테스트 명령에서 모두 확인했다.
- 실제 한국어 일정 요청에서 GMS가 날짜·시간·장소 수를 추출했고, TourAPI 검색·상세와 Open-Meteo 예보가 한 번의 Agent 실행에서 정상 종료했다. 11월 21일 경주 예보에서 일별 최대 강수 확률 0%, 최저 −3°C, 최고 5°C를 받았다.
- TourAPI에 존재하지 않는 검증용 검색어를 사용했을 때 실제 `NO_RESULT`를 확인했다. 에어코리아는 실제 관측 53건에서 PM10 누락 1건, PM2.5 누락 3건이 있었다.
- 사용자 확인에 따라 여행 도메인으로 구현을 진행했다. 1일차 16시 마감 기록은 그대로다.

## 15:36 KST까지의 실제 호출

| API | 상태 | 확인 내용과 남은 작업 |
| --- | --- | --- |
| 한국관광공사 TourAPI | 미검증 | `TOUR_API_SERVICE_KEY`가 없어 HTTP 요청을 생략했다. `경주` 검색 응답에서 주소·좌표가 있는 후보의 콘텐츠 ID를 뽑아 그 ID로 상세를 호출하는 검사를 준비했다. |
| Open-Meteo | 성공 | 경주 대표점 35.8562, 129.2248의 응답 JSON에서 2026-11-21 일별 최대 강수 확률 4%, 최저 −2.5°C, 최고 5.9°C를 파싱했다. 응답 예보 범위는 2026-11-18~12-03 KST였다. |
| 한국환경공단 에어코리아 | 미검증 | `AIRKOREA_SERVICE_KEY`가 없어 HTTP 요청을 생략했다. 경북 측정소 응답의 시각, PM10·PM2.5, 결측을 확인하는 검사를 준비했다. |
| LLM 텍스트 | 미검증 | `OPENAI_API_KEY`, `LLM_MODEL` 설정이 없어 건너뛰었다. |
| LLM Tool 선택 | 미검증 | 동일한 설정 누락으로 건너뛰었다. 명세를 전달하고 자동 선택된 함수명과 날짜·좌표 인자를 확인하는 별도 검사다. 후속 Tool 실행과 모델 응답 통합은 Agent 구현에서 검증한다. |

## 출처, 필수 인자와 이용 조건

### TourAPI

- **엔드포인트와 인자** — `https://apis.data.go.kr/B551011/KorService2/searchKeyword2`, `.../detailCommon2`. 공통 필수 `serviceKey, MobileOS, MobileApp`; 검색은 `keyword`, 상세는 `contentId`. 코드에서 `_type=json`을 지정. 검색 응답에서 기대하는 필드는 `contentid,title,addr1,addr2,mapx,mapy`다.
- **인증·이용 조건** — 공공데이터포털 활용 신청과 서비스키 필요. 무료. 개발계정 1,000건/일, 운영은 활용사례 등록 후 증량 신청. 일반 이용허락은 포털 표기를 따르며 이미지에는 개별 공공누리 유형과 별도 제한이 있다. [공식 서비스와 명세](https://www.data.go.kr/data/15101578/openapi.do?recommendDataYn=Y)

### Open-Meteo

- **엔드포인트와 인자** — `https://api.open-meteo.com/v1/forecast`. WGS84 `latitude,longitude` 필수, `daily` 요청 시 `timezone` 필수. `daily=precipitation_probability_max,temperature_2m_min,temperature_2m_max`, `timezone=Asia/Seoul`, `forecast_days=16`. 일별 시계열을 `daily.time`에 맞춰 읽는다.
- **인증·이용 조건** — 무료 비상업 엔드포인트는 키 없이 이용. 일 10,000, 시간 5,000, 분 600 호출 미만. CC BY 4.0에 따라 출처 표시. 공식 기본 예보 7일, 최대 16일이며 실제 반환 날짜를 확인해야 한다. [공식 API 문서](https://open-meteo.com/en/docs) · [이용약관](https://open-meteo.com/en/terms)

### 에어코리아

- **엔드포인트와 인자** — `https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty`. `serviceKey,sidoName` 필수, `returnType=json,pageNo=1,numOfRows=100,ver=1.0` 지정. `stationName,dataTime,pm10Value,pm25Value`를 확인한다.
- **인증·이용 조건** — 공공데이터포털 활용 신청과 서비스키 필요. 무료. 개발계정 안내 기준 일 500건이며 상세기능별 승인 한도를 마이페이지에서 확인한다. 운영계정은 심의 신청. 포털의 공공누리 3유형·제3자 권리 표시에 따라 출처 표시 및 원자료 변경 금지 조건을 따른다. 지역 대푯값으로 변환하지 않고 해당 측정소의 원 단위 관측값을 표시한다. [공식 서비스와 명세](https://www.data.go.kr/data/15073861/openapi.do) · [공공누리 제3유형](https://www.kogl.or.kr/info/licenseType3.do)

### 키 발급과 설정

1. 위 TourAPI와 에어코리아 공식 서비스에 공공데이터포털 계정으로 로그인해 **활용신청**을 각각 완료한다. 마이페이지의 **오픈API → 활용신청 현황 → 상세보기**에서 승인 상태와 각 서비스의 일반 인증키(Decoding)를 확인한다.
2. `backend/.env.example`을 `backend/.env`로 복사하고 `TOUR_API_SERVICE_KEY`, `AIRKOREA_SERVICE_KEY`를 입력한다. 코드는 `requests`의 쿼리 인코딩을 사용한다. 파일을 커밋하거나 키를 로그에 남기지 않는다.
3. SSAFY GMS 또는 사용할 제공자에서 발급한 키를 `OPENAI_API_KEY`에 입력한다. Chat Completions와 함수 호출을 지원하는 제공자의 모델을 `LLM_MODEL`로 설정한다. OpenAI 호환 제공자는 해당 포털에서 확인한 접속 주소를 `LLM_BASE_URL`로 설정한다. [SSAFY GMS](https://gms.ssafy.io/web/)
4. 아래 명령을 같은 환경에서 다시 실행해 테스트 3종의 성공 여부와 텍스트/Tool 선택을 각각 기록한다.

## 실행 명령과 근거

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.test_external_apis backend.tests.test_llm -v
.\.venv\Scripts\python.exe -m unittest backend.tests.test_external_apis.LocalToolTests -v
.\.venv\Scripts\python.exe -m pip check
```

- 통합 명령 결과는 9건 중 5건 통과, 4건 건너뜀, 종료 코드 0이다. 통과는 Open-Meteo 실제 호출 1건과 로컬 처리 4건이다. 로컬 검사는 예보 범위 밖 차단, 강수 확률 결측 보존, 관측시각과 PM 결측 처리, 키 누락 시 HTTP 호출 생략을 확인한다. 이 검사에 사용한 합성 데이터는 외부 API 수신 증거에서 제외한다.
- 초기 Open-Meteo 호출은 기본 환경에서 프록시 연결 오류(`NETWORK_ERROR`), 외부 네트워크 재시도에서 `TIMEOUT`이었다. Windows curl도 연결 타임아웃(코드 28)이었다. 공식 버전 가상환경과 외부 네트워크 권한으로 다시 실행했을 때 실제 응답을 받았다. 타임아웃의 원인은 확인되지 않았다.
- `pip check`는 깨진 의존성을 발견하지 않았다. FastAPI 테스트 클라이언트에서 `GET /health` 200과 `{"status":"ok"}`를 확인했다.
- Python 3.11 가상환경에 1일차 실행용 공식 버전 7개를 설치했다. 명세서의 전체 17개 버전은 `pip install --dry-run --ignore-installed`에서 의존성 해석을 완료했고 충돌이 보고되지 않았다. 전체 17개의 실제 설치 및 실행 확인은 후속 단계다.
- 대표 사례 A의 입력 경로를 검토했다. 요청에서 `경주, 2026-11-21, 10:00, 18:00, 3곳`을 추출해 검색 조건을 채우고, 반환 ID로 상세, 지역 설정의 좌표로 날씨를 조회하도록 설계했다. 시간 창은 480분이며 체류·이동 합계가 없으면 허용 시간 창만 제시한다. 사례 B에서는 강수 조건 충족 시 후보 유형 14와 새 ID로 탐색하고 기존 날씨·상세는 재사용한다. 사례 D는 서로 다른 신규 탐색 범위가 남아 있다는 시험 조건에서 세 번째 재계획 결과까지 평가하고 종료한다. 검토는 설계 추적이며 Agent 실행 증거는 후속 작업으로 남아 있다.
- 검증 과정에서 경주 전체나 여행일에 대한 대기질 예보로 시도 단위 관측값을 표시할 수 없다는 점을 반영해 `kind=observation`과 측정소·시각을 스키마에 명시했다. TourAPI 현재 카탈로그의 조회 기준과 여행 요청일도 별도 필드로 남긴다. 실제 제공자의 빈 결과·결측 응답 대조는 연결 확인 뒤 진행한다.

## 대체 API 조사와 도메인 결정

- **관광지**는 OpenTripMap을 조사했다. 좌표 기반 목록과 개별 상세를 제공하지만 경주 데이터의 주소·시설 분류·한국어 품질과 계정 한도를 별도 검증해야 한다. TourAPI 키 미설정만 확인된 상태이므로 공급자는 유지한다. [OpenTripMap 제품 문서](https://dev.opentripmap.org/product)
- **날씨**는 MET Norway Locationforecast를 조사했다. 기온과 강수 관련 예보의 독립 공급원 후보다. User-Agent 식별과 제공 조건이 필요하며 한국 좌표에서 확률의 제공 범위 및 시간대별 값을 확인해야 한다. Open-Meteo 재시도가 성공해 기존 공급자를 유지한다. [MET Norway 응답 형식](https://api.met.no/doc/ForecastJSON) · [이용 안내](https://docs.api.met.no/doc/FAQ.html)
- **대기질**은 Open-Meteo Air Quality를 조사했다. PM10·PM2.5 모델 예보를 제공한다. 이 값은 에어코리아 측정소 관측과 의미가 다르므로 변경 시 계약과 UI를 수정하고, 3종 충족 근거는 프로젝트에서 별도 확인해야 한다. [Open-Meteo Air Quality 문서](https://open-meteo.com/en/docs/air-quality-api)

여행 기획의 API 관문은 미통과 상태다. 명세서 §1.2·§2.7은 1일차 16시까지 성공 3종을 확보하지 못하면 제공 영화 도메인 팩으로 전환하도록 정한다. 검증 시점에는 여행 도메인 설계를 완료하고 호출 결과를 기록했으며, 저장소에는 제공 영화 팩이 없다.
