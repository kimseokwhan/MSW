import os
import tempfile
import unittest
from contextlib import ExitStack
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import RootModel

from backend.agents.analyze import Conditions, Interpretation
from backend.agents.graph import chat
from backend.main import app
from backend.schemas.tools import ToolError, ToolFailure, ToolSuccess
from backend.tools.external_apis import KST
from backend.tools.registry import TOOLS, tool_specs


class RequiredServiceTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.enter_context = stack.enter_context
        temporary = self.enter_context(tempfile.TemporaryDirectory())
        self.enter_context(patch.dict(os.environ, {"TRIPMIND_DB_PATH": temporary + "/test.sqlite3"}))
        self.client = self.enter_context(TestClient(app))
        self.date = (datetime.now(KST).date() + timedelta(days=2)).isoformat()

    def message(self, message, session=None):
        response = self.client.post("/api/chat", json={"message": message, "session_id": session})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def fake_conditions(self, **changes):
        return Conditions(**{"region": "경주", "date": self.date, "start_time": "10:00",
                             "end_time": "18:00", "count": 1, **changes})

    def fake_sources(self, rain=10, indoor_available=True, weather_failure=False, empty=False):
        def success(data):
            # Fixtures exercise the service path without depending on providers or their data.
            return ToolSuccess(data=RootModel(data))

        def search(**args):
            if empty:
                return ToolFailure(error=ToolError(code="NO_RESULT", message="empty"))
            indoor = args["content_type_id"] == "14" and indoor_available
            key = ("14" if indoor else "12") + str(args["page"])
            return success({"attractions": [{"content_id": key, "title": "시험 장소",
                             "address": "경상북도 경주시 양정로", "latitude": 35.8, "longitude": 129.2}]})

        def detail(content_id):
            return success({"overview": "실내 전시" if content_id.startswith("14") else "야외 정원"})

        def weather(**args):
            if weather_failure:
                return ToolFailure(error=ToolError(code="TIMEOUT", message="timeout"))
            return success({"date": args["date"], "precipitation_probability_max": rain,
                            "temperature_min_c": 1, "temperature_max_c": 12})

        def air(**args):
            return success({"province": args["province"], "kind": "observation", "observations": [{
                "station_name": "시험 측정소", "measured_at": "2026-11-19T10:00:00+09:00",
                "pm10_ug_m3": 20, "pm25_ug_m3": 10,
            }]})

        for name, handler in {"search_attractions": search, "get_attraction_detail": detail,
                              "get_weather": weather, "get_air_quality": air}.items():
            self.enter_context(patch.dict(TOOLS, {name: (*TOOLS[name][:2], handler)}))

    def fake_request(self, conditions, intent="create_plan"):
        return self.enter_context(patch("backend.agents.graph.interpret", return_value=(
            Interpretation(intent=intent, changes=conditions, reason="사용자가 요청한 여행 조건을 추출했습니다."), True)))

    @staticmethod
    def calls(result):
        return [(e["payload"]["tool"], e["payload"]["arguments"])
                for e in result["events"] if e["type"] == "tool_requested"]

    def test_normal_plan_and_crud_overlap(self):
        self.fake_sources()
        self.fake_request(self.fake_conditions())
        response = self.message("정상 일정")
        self.assertEqual(response["status"], "complete")
        self.assertEqual([name for name, _ in self.calls(response)],
                         ["search_attractions", "get_attraction_detail", "get_weather", "get_air_quality"])
        self.assertIn("480분", response["reply"])
        plan = response["draft_plan"]
        self.assertIsNone(plan["items"][0]["start_time"])
        first = self.client.post("/api/plans", json=plan)
        second = self.client.post("/api/plans", json=plan)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        plan_id = first.json()["plan"]["id"]
        self.assertEqual(second.json()["conflicts"][0]["id"], plan_id)
        touch = self.client.post("/api/plans", json={**plan, "start_time": "18:00", "end_time": "19:00"})
        self.assertEqual(touch.json()["conflicts"], [])
        self.assertEqual(self.client.get("/api/plans").json()["total"], 3)
        self.assertEqual(self.client.get(f"/api/plans/{plan_id}").json()["id"], plan_id)
        invalid = self.client.patch(f"/api/plans/{plan_id}", json={"end_time": "09:00"})
        self.assertEqual(invalid.status_code, 422)
        changed = self.client.patch(f"/api/plans/{plan_id}", json={"title": "변경된 일정"})
        self.assertEqual(changed.json()["plan"]["title"], "변경된 일정")
        self.assertEqual(self.client.delete(f"/api/plans/{plan_id}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/plans/{plan_id}").status_code, 404)

    def test_rain_replans_and_reuses_forecast(self):
        self.fake_sources(rain=80)
        self.fake_request(self.fake_conditions(rain_indoor=True))
        result = self.message("비가 오면 실내")
        calls = self.calls(result)
        self.assertEqual(sum(name == "get_weather" for name, _ in calls), 1)
        self.assertEqual([args["content_type_id"] for name, args in calls if name == "search_attractions"],
                         ["12", "14"])
        self.assertEqual(result["draft_plan"]["items"][0]["content_id"], "141")
        self.assertTrue(any(e["type"] == "replanned" for e in result["events"]))

    def test_replan_cap_and_unique_search(self):
        self.fake_sources(empty=True)
        self.fake_request(self.fake_conditions(count=5, category="indoor"))
        result = self.message("후보가 부족한 일정")
        replay = [e["payload"]["count"] for e in result["events"] if e["type"] == "replanned"]
        self.assertEqual(replay, [1, 2, 3])
        self.assertEqual([args["page"] for name, args in self.calls(result) if name == "search_attractions"],
                         [1, 2, 3, 4])
        self.assertIn("재계획을 3회", result["reply"])

    def test_weather_failure_returns_tourism_and_warning(self):
        self.fake_sources(weather_failure=True)
        self.fake_request(self.fake_conditions(rain_indoor=True))
        result = self.message("날씨 장애")
        self.assertEqual(result["status"], "partial")
        self.assertIsNotNone(result["draft_plan"])
        self.assertIn("강수 확률 확인 불가", result["reply"])
        self.assertEqual(result["warnings"][0]["code"], "TIMEOUT")

    def test_no_tool_log_isolation_and_subscriber_failure(self):
        first = self.message("안녕하세요")
        second = self.message("안녕하세요")
        self.assertEqual(self.calls(first), [])
        self.assertNotEqual(first["session_id"], second["session_id"])
        response = self.client.get("/api/logs/" + first["session_id"]).json()
        self.assertEqual(len(response["events"]), len(first["events"]))
        self.assertTrue(all(e["session_id"] == first["session_id"] for e in response["events"]))
        self.assertEqual(self.client.get("/api/logs").json()["total"], 2)
        path = "/api/logs/" + first["session_id"]
        self.assertEqual(self.client.patch(path, json={}).status_code, 405)
        self.assertEqual(self.client.delete(path).status_code, 204)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(chat("안녕하세요", subscribers=()).status, "complete")
        with self.assertLogs("backend.events.bus", level="WARNING"):
            def broken(event):
                raise RuntimeError("logging failed")

            self.assertEqual(chat("안녕하세요", subscribers=(broken,)).status, "complete")

    def test_followup_only_changes_given_condition(self):
        self.fake_sources()
        extractor = self.fake_request(Conditions(region="경주"))
        first = self.message("경주 여행 일정 짜 줘")
        self.assertEqual(first["status"], "needs_input")
        self.assertEqual(self.calls(first), [])
        extractor.return_value = (Interpretation(intent="revise_plan", changes=Conditions(
            date=self.date, start_time="09:00", end_time="17:00", count=1)), True)
        second = self.message("오전 9시부터 오후 5시까지 1곳", first["session_id"])
        self.assertEqual(second["draft_plan"]["region"], "경북 경주시")
        extractor.return_value = (Interpretation(intent="revise_plan", changes=Conditions(end_time="18:00")), True)
        third = self.message("종료만 6시로", first["session_id"])
        self.assertEqual(third["draft_plan"]["start_time"], "09:00")
        self.assertEqual(third["draft_plan"]["end_time"], "18:00")

    def test_registry_frontend_and_missing_llm_key(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        script = self.client.get("/app.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn("javascript", script.headers["content-type"])
        self.assertEqual(sum(len(methods) for path, methods in self.client.get("/openapi.json").json()[
            "paths"].items() if path.startswith("/api/")), 9)
        self.assertEqual({spec["name"] for spec in tool_specs()}, set(TOOLS))
        with patch("backend.agents.analyze.setting", return_value=""):
            result = self.message("경주 여행을 짜 줘")
        self.assertEqual(result["warnings"][0]["code"], "MISSING_API_KEY")
        self.assertEqual(self.calls(result), [])

    def test_nationwide_scope_locates_forecast_and_air(self):
        self.fake_sources()
        self.fake_request(self.fake_conditions(region="부산 해운대구", air=True))
        air = {"province": "부산", "observations": []}
        def air_response(**args):
            return ToolSuccess(data=RootModel(air))

        self.enter_context(patch.dict(TOOLS, {"get_air_quality": (
            *TOOLS["get_air_quality"][:2], air_response)}))
        response = self.message("부산 해운대구 여행")
        calls = dict(self.calls(response))
        self.assertEqual(calls["search_attractions"]["region_code"], "26")
        self.assertEqual(calls["search_attractions"]["district_codes"], ["350"])
        self.assertEqual(calls["get_weather"]["latitude"], 35.8)
        self.assertEqual(calls["get_air_quality"]["province"], "부산")
        self.assertEqual(response["draft_plan"]["title"], "부산 해운대구 여행")

    def test_ambiguous_destination_prompts_for_province(self):
        self.fake_request(self.fake_conditions(region="고성"))
        response = self.message("고성 여행")
        self.assertEqual(response["status"], "needs_input")
        self.assertEqual(self.calls(response), [])
        self.assertIn("강원 고성군", response["reply"])
        self.assertIn("경남 고성군", response["reply"])

    def test_attraction_lookup_includes_air_observation_and_source(self):
        self.fake_sources()
        self.fake_request(Conditions(region="부산", attractions=True, count=1), intent="lookup")
        result = self.message("부산 관광지 한 곳 추천해 줘")
        self.assertEqual(result["status"], "complete")
        self.assertIsNone(result["draft_plan"])
        self.assertIn("현재 대기질", result["reply"])
        self.assertIn("PM10 20", result["reply"])
        self.assertEqual([item["source"] for item in result["evidence"]], ["TourAPI", "AirKorea"])
