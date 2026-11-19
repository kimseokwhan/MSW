import math
from datetime import date, datetime, timedelta, timezone
from itertools import zip_longest
from xml.etree import ElementTree

import requests
from pydantic import ValidationError

from backend.config import setting
from backend.schemas.tools import (
    AirData, AirInput, AirObservation, Attraction, DetailData, DetailInput,
    SearchData, SearchInput, ToolError, ToolFailure, ToolSuccess, WeatherData,
    WeatherInput,
)


KST = timezone(timedelta(hours=9))
TOUR_BASE = "https://apis.data.go.kr/B551011/KorService2"
AIR_URL = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_FIELDS = ("precipitation_probability_max", "temperature_2m_min", "temperature_2m_max")


class ApiError(Exception):
    """Only carries a fixed, user-safe error code."""


MESSAGES = {
    "INVALID_INPUT": "Check the tool arguments.",
    "MISSING_API_KEY": "Configure the service key.",
    "AUTH_FAILED": "Check service key and API approval.",
    "RATE_LIMITED": "The provider call limit was reached.",
    "TIMEOUT": "The provider request timed out.",
    "NETWORK_ERROR": "The provider connection failed.",
    "HTTP_ERROR": "The provider rejected or could not complete the request.",
    "INVALID_RESPONSE": "The provider returned an unexpected response.",
    "NO_RESULT": "No matching data was returned.",
    "MISSING_DATA": "The response lacked usable measurements.",
    "OUT_OF_FORECAST_RANGE": "The requested date is outside the available forecast.",
}


def failure(code: str) -> ToolFailure:
    return ToolFailure(error=ToolError(code=code, message=MESSAGES[code]))


def check_provider_code(code: str) -> None:
    if code in {"0", "00", "0000"}:
        return
    if code in {"20", "30", "31", "32", "SERVICE_KEY_IS_NOT_REGISTERED_ERROR",
                "SERVICE_ACCESS_DENIED_ERROR", "UNREGISTERED_IP_ERROR",
                "DEADLINE_HAS_EXPIRED_ERROR"}:
        raise ApiError("AUTH_FAILED")
    if code in {"22", "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR"}:
        raise ApiError("RATE_LIMITED")
    if code == "03":
        raise ApiError("NO_RESULT")
    if code in {"10", "11"}:
        raise ApiError("INVALID_INPUT")
    raise ApiError("HTTP_ERROR" if code else "INVALID_RESPONSE")


def get_json(url: str, params: dict) -> dict:
    try:
        response = requests.get(url, params=params, timeout=(5, 15), allow_redirects=False)
    except requests.Timeout:
        raise ApiError("TIMEOUT") from None
    except requests.RequestException:
        raise ApiError("NETWORK_ERROR") from None
    if response.status_code in {401, 403}:
        raise ApiError("AUTH_FAILED")
    if response.status_code == 429:
        raise ApiError("RATE_LIMITED")
    if not 200 <= response.status_code < 300:
        raise ApiError("HTTP_ERROR")
    if not response.content.strip():
        raise ApiError("NO_RESULT")
    try:
        body = response.json()
    except ValueError:
        # The public data gateway may send an XML error even when JSON was requested.
        try:
            root = ElementTree.fromstring(response.content)
        except ElementTree.ParseError:
            raise ApiError("INVALID_RESPONSE") from None
        code = root.findtext(".//returnReasonCode") or root.findtext(".//resultCode")
        if code:
            check_provider_code(code.strip())
        raise ApiError("INVALID_RESPONSE") from None
    if not isinstance(body, dict):
        raise ApiError("INVALID_RESPONSE")
    return body


def public_rows(url: str, key_name: str, params: dict, *, tour: bool) -> list[dict]:
    key = setting(key_name)
    if not key:
        raise ApiError("MISSING_API_KEY")
    payload = get_json(url, {**params, "serviceKey": key})
    if "OpenAPI_ServiceResponse" in payload:
        header = payload["OpenAPI_ServiceResponse"]["cmmMsgHeader"]
        check_provider_code(str(header.get("returnReasonCode", "")))
    envelope = payload["response"]
    check_provider_code(str(envelope["header"].get("resultCode", "")))
    items = envelope["body"].get("items")
    if tour and isinstance(items, dict):
        items = items.get("item")
        if isinstance(items, dict):
            items = [items]
    if not items:
        raise ApiError("NO_RESULT")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ApiError("INVALID_RESPONSE")
    return items


def optional_text(value: object) -> str | None:
    if isinstance(value, (str, int)) and not isinstance(value, bool):
        clean = str(value).strip()
        if clean and clean != "-":
            return clean
    return None


def number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def attraction(row: dict) -> Attraction:
    return Attraction(
        content_id=optional_text(row.get("contentid")),
        title=row.get("title"),
        address=" ".join(filter(None, (optional_text(row.get("addr1")),
                                       optional_text(row.get("addr2"))))) or None,
        latitude=number(row.get("mapy")),
        longitude=number(row.get("mapx")),
        content_type_id=optional_text(row.get("contenttypeid")),
        category_code=optional_text(row.get("lclsSystm3")),
    )


def tour_rows(operation: str, **params: str | int) -> list[dict]:
    return public_rows(f"{TOUR_BASE}/{operation}", "TOUR_API_SERVICE_KEY",
                       {"MobileOS": "ETC", "MobileApp": "TripMindAI", "_type": "json", **params},
                       tour=True)


def search_rows(query: SearchInput) -> list[dict]:
    params = {"pageNo": query.page, "numOfRows": 12, "contentTypeId": query.content_type_id}
    if query.region_code:
        params["lDongRegnCd"] = query.region_code
    if query.keyword:
        params["keyword"] = query.keyword
    groups = []
    operation = "searchKeyword2" if query.keyword else "areaBasedList2"
    for district in dict.fromkeys(query.district_codes or [None]):
        scope = {"lDongSignguCd": district} if district else {}
        try:
            rows = tour_rows(operation, **params, **scope)
        except ApiError as error:
            if str(error) != "NO_RESULT":
                raise
            continue
        groups.append([
            row for row in rows
            if (not query.region_code or str(row.get("lDongRegnCd")) == query.region_code)
            and (not district or str(row.get("lDongSignguCd")) == district)
            and (not query.excluded_districts or (
                row.get("lDongSignguCd") and str(row["lDongSignguCd"]) not in query.excluded_districts
            ))
        ])
    # Interleave subdistricts so the first district cannot fill the entire page.
    items = [row for batch in zip_longest(*groups) for row in batch if row is not None][:12]
    if not items:
        raise ApiError("NO_RESULT")
    return items


def search_attractions(**arguments) -> ToolSuccess[SearchData] | ToolFailure:
    try:
        query = SearchInput(**arguments)
    except ValidationError:
        return failure("INVALID_INPUT")
    try:
        rows = search_rows(query)
        checked_at = datetime.now(KST)
        results = [attraction(row) for row in rows
                   if optional_text(row.get("contentid")) and optional_text(row.get("title"))]
        if not results:
            return failure("MISSING_DATA")
        return ToolSuccess(data=SearchData(requested_date=query.visit_date or checked_at.date(),
                                           checked_at=checked_at, page=query.page,
                                           attractions=results))
    except ApiError as error:
        return failure(str(error))
    except (KeyError, TypeError, ValueError, AttributeError):
        return failure("INVALID_RESPONSE")


def get_attraction_detail(**arguments) -> ToolSuccess[DetailData] | ToolFailure:
    try:
        query = DetailInput(**arguments)
    except ValidationError:
        return failure("INVALID_INPUT")
    try:
        rows = tour_rows("detailCommon2", contentId=query.content_id)
        row = next((item for item in rows
                    if optional_text(item.get("contentid")) == query.content_id), None)
        if row is None:
            return failure("NO_RESULT")
        return ToolSuccess(data=DetailData(**attraction(row).model_dump(),
                                           overview=optional_text(row.get("overview")),
                                           homepage=optional_text(row.get("homepage"))))
    except ApiError as error:
        return failure(str(error))
    except (KeyError, TypeError, ValueError, AttributeError):
        return failure("INVALID_RESPONSE")


def get_weather(**arguments) -> ToolSuccess[WeatherData] | ToolFailure:
    try:
        query = WeatherInput(**arguments)
    except ValidationError:
        return failure("INVALID_INPUT")
    today = datetime.now(KST).date()
    if not 0 <= (query.date - today).days < 16:
        return failure("OUT_OF_FORECAST_RANGE")
    try:
        body = get_json(WEATHER_URL, {
            "latitude": query.latitude, "longitude": query.longitude,
            "daily": ",".join(WEATHER_FIELDS), "timezone": "Asia/Seoul",
            "forecast_days": 16,
        })
        daily = body["daily"]
        dates = [date.fromisoformat(item) for item in daily["time"]]
        if not dates:
            return failure("NO_RESULT")
        if query.date not in dates:
            code = "OUT_OF_FORECAST_RANGE" if not min(dates) <= query.date <= max(dates) else "MISSING_DATA"
            return failure(code)
        index = dates.index(query.date)
        values = []
        for field in WEATHER_FIELDS:
            series = daily.get(field)
            values.append(number(series[index]) if isinstance(series, list) and index < len(series) else None)
        if all(value is None for value in values):
            return failure("MISSING_DATA")
        rain, low, high = values
        return ToolSuccess(data=WeatherData(date=query.date, precipitation_probability_max=rain,
                                           temperature_min_c=low, temperature_max_c=high,
                                           available_from=min(dates), available_to=max(dates)))
    except ApiError as error:
        return failure(str(error))
    except (KeyError, TypeError, ValueError, AttributeError):
        return failure("INVALID_RESPONSE")


def get_air_quality(**arguments) -> ToolSuccess[AirData] | ToolFailure:
    try:
        query = AirInput(**arguments)
    except ValidationError:
        return failure("INVALID_INPUT")
    try:
        rows = public_rows(AIR_URL, "AIRKOREA_SERVICE_KEY", {
            "sidoName": query.province, "returnType": "json", "pageNo": 1,
            "numOfRows": 100, "ver": "1.0",
        }, tour=False)
        observations = []
        for row in rows:
            station = optional_text(row.get("stationName"))
            measured_at = optional_text(row.get("dataTime"))
            if not station or not measured_at:
                continue
            # AirKorea sometimes denotes the end of the day as YYYY-MM-DD 24:00.
            try:
                if measured_at.endswith(" 24:00"):
                    timestamp = datetime.strptime(measured_at[:10], "%Y-%m-%d") + timedelta(days=1)
                else:
                    timestamp = datetime.strptime(measured_at, "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            pm10 = number(row.get("pm10Value"))
            pm25 = number(row.get("pm25Value"))
            observations.append(AirObservation(
                station_name=station, measured_at=timestamp.replace(tzinfo=KST),
                pm10_ug_m3=pm10 if pm10 is not None and pm10 >= 0 else None,
                pm25_ug_m3=pm25 if pm25 is not None and pm25 >= 0 else None,
            ))
        if not any(row.pm10_ug_m3 is not None or row.pm25_ug_m3 is not None for row in observations):
            return failure("MISSING_DATA")
        return ToolSuccess(data=AirData(province=query.province, observations=observations))
    except ApiError as error:
        return failure(str(error))
    except (KeyError, TypeError, ValueError, AttributeError):
        return failure("INVALID_RESPONSE")
