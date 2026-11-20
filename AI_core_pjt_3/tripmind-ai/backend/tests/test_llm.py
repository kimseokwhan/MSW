import unittest
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

from openai import APIError, OpenAI
from pydantic import ValidationError

from backend.agents.analyze import interpret
from backend.config import setting
from backend.llm import call_function
from backend.schemas.tools import WeatherInput
from backend.tools.external_apis import KST


class LlmRoutingTests(unittest.TestCase):
    function = {"name": "get_weather", "description": "Get a forecast", "parameters": {"type": "object"}}
    messages = [{"role": "user", "content": "부산 날씨"}]

    def test_astra_uses_responses_with_required_function(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output=[
            SimpleNamespace(type="reasoning"),
            SimpleNamespace(type="function_call", name="get_weather", arguments='{"city":"부산"}'),
        ])
        result = call_function(client, "gpt-6-astra", self.messages, self.function, required=True)
        self.assertEqual(result, '{"city":"부산"}')
        client.responses.create.assert_called_once_with(
            model="gpt-6-astra", input=self.messages,
            tools=[{"type": "function", **self.function, "strict": False}],
            tool_choice={"type": "function", "name": "get_weather"}, reasoning={"effort": "low"}, store=False,
        )
        client.chat.completions.create.assert_not_called()

    def test_sol_and_luna_use_chat_completions_with_tools(self):
        for model in ("gpt-6-sol", "gpt-6-luna"):
            with self.subTest(model=model):
                client = Mock()
                client.chat.completions.create.return_value = SimpleNamespace(choices=[
                    SimpleNamespace(message=SimpleNamespace(tool_calls=[])),
                ])
                self.assertIsNone(call_function(client, model, self.messages, self.function))
                client.chat.completions.create.assert_called_once_with(
                    model=model, messages=self.messages,
                    tools=[{"type": "function", "function": self.function}], tool_choice="auto",
                    reasoning_effort="none",
                )
                client.responses.create.assert_not_called()


class LlmTests(unittest.TestCase):
    def setUp(self):
        if not setting("OPENAI_API_KEY") or not setting("LLM_MODEL"):
            self.skipTest("OPENAI_API_KEY and LLM_MODEL are required")
        self.model = setting("LLM_MODEL")
        try:
            self.client = OpenAI(api_key=setting("OPENAI_API_KEY"),
                                 base_url=setting("LLM_BASE_URL") or "https://api.openai.com/v1",
                                 timeout=15, max_retries=0)
        except (APIError, ValueError, TypeError) as error:
            self.fail(f"LLM client configuration: {type(error).__name__}")
        self.addCleanup(self.client.close)

    def complete(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}],
            )
        except APIError as error:
            self.fail(f"LLM request: {type(error).__name__}")
        self.assertTrue(bool(response and response.choices), "Missing completion choices")
        return response.choices[0].message

    def test_simple_message(self):
        message = self.complete("Reply with a short greeting.")
        self.assertTrue(bool(message.content and message.content.strip()), "Missing text reply")

    def test_model_selects_weather_tool(self):
        schema = WeatherInput.model_json_schema()
        target = datetime.now(KST).date() + timedelta(days=1)
        prompt = (f"Fetch the forecast for {target} at latitude 35.8562, longitude 129.2248. "
                  "Use the weather tool to obtain it.")
        try:
            raw = call_function(self.client, self.model, [{"role": "user", "content": prompt}],
                                {"name": "get_weather", "description": "Fetch a daily forecast for a trip.",
                                 "parameters": schema})
        except APIError as error:
            self.fail(f"LLM request: {type(error).__name__}")
        self.assertIsNotNone(raw, "Model did not select get_weather")
        try:
            arguments = WeatherInput.model_validate_json(raw)
        except (ValueError, ValidationError, TypeError):
            self.fail("Model returned invalid weather tool arguments")
        self.assertEqual(arguments.date, target)
        self.assertAlmostEqual(arguments.latitude, 35.8562, places=4)
        self.assertAlmostEqual(arguments.longitude, 129.2248, places=4)

    def test_itinerary_analyzer_preserves_range_and_mixed_preference(self):
        result, used_llm = interpret(
            "2030년 11월 21일부터 24일까지 부산 여행 일정을 짜 줘. "
            "매일 오전 10시부터 오후 5시까지 하루 두 곳씩 실내와 야외를 섞어 줘.",
            {}, date(2030, 11, 20),
        )
        self.assertTrue(used_llm)
        self.assertEqual(result.intent, "create_plan")
        self.assertEqual(result.changes.date, date(2030, 11, 21))
        self.assertEqual(result.changes.end_date, date(2030, 11, 24))
        self.assertEqual((result.changes.start_time, result.changes.end_time), ("10:00", "17:00"))
        self.assertEqual(result.changes.count, 2)
        self.assertEqual(result.changes.category, "mixed")
