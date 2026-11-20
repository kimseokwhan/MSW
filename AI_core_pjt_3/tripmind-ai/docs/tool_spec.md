# 외부 Tool 정의서

아래 계약은 프로젝트 자체 설계다. [Pydantic 모델](../backend/schemas/tools.py), [HTTP 래퍼](../backend/tools/external_apis.py), [Tool 등록부](../backend/tools/registry.py)에 구현했다. 실제 API 응답 및 사용 조건은 [검증 기록](api_verification.md)을 따른다.

## 공통 계약

성공 구조는 `{"ok":true,"data":{},"error":null}`이다. 성공의 `data`는 아래 Tool별 스키마로 채운다. 실패의 예는 `{"ok":false,"data":null,"error":{"code":"MISSING_API_KEY","message":"Configure the service key."}}`다. 날짜는 ISO 8601, 시각은 시간대 포함 ISO 8601, 좌표는 WGS84다. 표의 `T?`는 값이 없으면 JSON `null`을 뜻한다.

| 오류 코드 | 조건 및 Agent 처리 |
| --- | --- |
| `INVALID_INPUT` | 형식 또는 제공자 입력 오류. 사용자 조건이 불명확하면 되묻고, 내부 생성 인자라면 한도를 적용해 교정 |
| `MISSING_API_KEY`, `AUTH_FAILED` | 키 누락 또는 인증·권한 오류. 설정 안내, 동일 출처 재계획 중지 |
| `RATE_LIMITED` | 사용량 제한. 해당 출처 호출 중지 후 결과에 표시 |
| `TIMEOUT`, `NETWORK_ERROR`, `HTTP_ERROR` | 통신 또는 HTTP 오류. 독립 작업 계속, 장애 출처 때문에 후보를 변경할 필요 없음 |
| `INVALID_RESPONSE` | 지원하지 않는 응답 구조나 데이터 형식 |
| `NO_RESULT` | 조회 결과 없음. 바꿀 수 있는 검색 조건이 있으면 새 후보 조회 |
| `MISSING_DATA` | 유효한 데이터가 부족함. 관련 제약을 미확인 상태로 남김 |
| `OUT_OF_FORECAST_RANGE` | 지원 범위 밖 또는 응답의 실제 예보 범위 밖. 가능한 날짜에 다시 확인하도록 안내 |

HTTP 호출은 연결 5초, 읽기 15초이며 HTTP 상태와 공공데이터포털 JSON·XML 오류 코드만 매핑한다. 화면과 로그에는 고정 코드와 메시지를 사용한다. 일부 데이터만 있는 성공 응답은 해당 필드를 `null`로 유지한다.

## 외부 Tool

### `search_attractions`

- **호출 시점** — 목적지에 갈 후보가 아직 없거나 대안을 더 찾아야 할 때 호출한다.
- **입력** — `keyword:string?`, `region_code:string?` 중 하나 필요. `district_codes:string[]`, `excluded_districts:string[]`는 지역 코드와 함께 사용. `visit_date:date?`, `page:integer>=1` 기본 1, `content_type_id:"12"|"14"` 기본 "12"
- **성공 응답의 데이터**

  ```text
  source:"TourAPI",
  requested_date:date,
  checked_at:datetime,
  basis:"current_catalog",
  page:integer,
  attractions:Attraction[]
  ```

### `get_attraction_detail`

- **호출 시점** — 확보한 관광지 ID의 상세 속성이 제약 판단이나 표시 근거에 필요할 때 호출한다.
- **입력** — `content_id:string` 필수, 숫자 문자열
- **성공 응답의 데이터** — `Attraction`의 필드와 `source:"TourAPI", overview:string?, homepage:string?`

### `get_weather`

- **호출 시점** — 방문일 강수 확률이나 기온을 알려 주거나 강수 조건을 판단할 때 호출한다.
- **입력** — `latitude:number, longitude:number, date:date` 모두 필수
- **성공 응답의 데이터**

  ```text
  source:"Open-Meteo",
  kind:"forecast",
  date:date,
  timezone:"Asia/Seoul",
  precipitation_probability_max:number?,
  temperature_min_c:number?,
  temperature_max_c:number?,
  available_from:date,
  available_to:date
  ```

### `get_air_quality`

- **호출 시점** — 해당 시도 측정소의 현재 대기질을 참고 정보로 제시할 때 호출한다.
- **입력** — `province:string` 필수, 예시 `경북`
- **성공 응답의 데이터**

  ```text
  source:"AirKorea",
  kind:"observation",
  province:string,
  observations:Observation[]
  ```

`Attraction` 객체는 `content_id:string, title:string, address:string?, latitude:number?, longitude:number?, content_type_id:string?, category_code:string?`를 포함한다. `Observation`은 `station_name:string, measured_at:datetime, pm10_ug_m3:number?, pm25_ug_m3:number?`를 포함한다.

- **후보 검색**은 여행 요청에 TourAPI `areaBasedList2`를 사용하고, 키워드를 제공한 직접 호출은 `searchKeyword2`를 사용한다. `visit_date` 기본값은 KST 오늘이다. 항상 현재 카탈로그를 조회하며 사용자가 미래 날짜를 지정했다면 그 차이를 응답에 표시한다. 이름과 `content_id`를 반환하고 ID를 상세 Tool에 전달한다. 유형 12는 관광지, 14는 문화시설이며 실내 여부는 별도 근거가 필요하다. [TourAPI 공식 문서](https://www.data.go.kr/data/15101578/openapi.do)
- **상세 조회**는 TourAPI `detailCommon2`를 사용한다. 주소·좌표·분류·설명을 제공 범위 내에서 반환한다. `homepage`는 제공자 원본 문자열로 HTML을 포함할 수 있다. 후속 UI에서는 문자열을 그대로 HTML로 삽입하지 않고 링크를 검증해 표시한다. 주소·좌표·실내 분류·운영 정보가 없으면 해당 조건을 미확인으로 둔다. 방문 지역 좌표가 없고 개별 장소의 날씨를 확인하려면 상세 위치의 위도·경도를 Weather Tool로 전달할 수 있다.
- **날씨 조회**는 Open-Meteo `/v1/forecast`를 사용한다. 일별 최대 강수 확률은 시간별 강수 확률의 최댓값이며 여행 시간대의 확률을 의미하지 않는다. 방문일과 미리 확인한 지역 대표 좌표 또는 상세 좌표를 사용한다. 예보 범위 및 강수·기온 결측을 조건 판단으로 넘긴다.
- **대기질 조회**는 에어코리아 `getCtprvnRltmMesureDnsty`를 사용한다. 시도 기준 관측값과 측정소·측정 시각을 표시한다. 특정 도시를 대표하려면 도시와 측정소 매핑을 확인하고, 확인 전에는 관측값을 도시 전체에 일반화하지 않는다. 두 농도가 모두 결측인 행은 표시용으로만 취급한다. 본 Tool의 출력은 다른 Tool의 필수 입력이 아니다.

## Tool 등록

등록부는 위 네 함수의 이름, 호출 조건 설명, Pydantic 입력 스키마와 실행 함수를 연결한다. GMS가 구조화한 의도와 사용자 조건으로 LangGraph가 Tool과 실행 순서를 선택한다. 서버는 등록된 함수에서 입력을 검증한 다음 호출한다. 목록은 `python -m backend.tools.registry`로 출력한다. 지역 매핑, 제약 계산, 계획 저장과 로그 CRUD는 애플리케이션 흐름에서 실행한다.
