import json
import unittest
from datetime import datetime, timedelta

from openai import APIError, OpenAI
from pydantic import ValidationError

from backend.config import chat_tool_options, setting
from backend.schemas.tools import WeatherInput
from backend.tools.external_apis import KST


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

    def complete(self, prompt, **options):
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}], **options,
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
        message = self.complete(
            f"Fetch the forecast for {target} at latitude 35.8562, longitude 129.2248. "
            "Use the weather tool to obtain it.",
            tools=[{"type": "function", "function": {
                "name": "get_weather", "description": "Fetch a daily forecast for a trip.",
                "parameters": schema,
            }}],
            tool_choice="auto",
            **chat_tool_options(self.model),
        )
        calls = [call.function for call in message.tool_calls or []
                 if call.type == "function" and call.function.name == "get_weather"]
        self.assertTrue(bool(calls), "Model did not select get_weather")
        try:
            arguments = WeatherInput.model_validate(json.loads(calls[0].arguments))
        except (ValueError, ValidationError, TypeError):
            self.fail("Model returned invalid weather tool arguments")
        self.assertEqual(arguments.date, target)
        self.assertAlmostEqual(arguments.latitude, 35.8562, places=4)
        self.assertAlmostEqual(arguments.longitude, 129.2248, places=4)
