from backend.schemas.tools import AirInput, DetailInput, SearchInput, WeatherInput
from backend.tools.external_apis import (
    get_air_quality, get_attraction_detail, get_weather, search_attractions,
)


TOOLS = {
    "search_attractions": ("목적지의 관광 후보나 대체 후보가 필요할 때 사용", SearchInput, search_attractions),
    "get_attraction_detail": ("후보 ID의 세부 정보가 판단에 필요할 때 사용", DetailInput, get_attraction_detail),
    "get_weather": ("방문일 강수 확률이나 기온이 필요할 때 사용", WeatherInput, get_weather),
    "get_air_quality": ("현재 지역 대기질 관측값을 요청했을 때 사용", AirInput, get_air_quality),
}


def tool_specs():
    return [
        {"name": name, "description": description, "parameters": schema.model_json_schema(),
         "kind": "external"}
        for name, (description, schema, _) in TOOLS.items()
    ]


if __name__ == "__main__":
    import json

    print(json.dumps(tool_specs(), ensure_ascii=False, indent=2))
