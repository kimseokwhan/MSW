import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from backend.config import setting
from backend.tools.external_apis import (
    KST, get_air_quality, get_attraction_detail, get_weather, search_attractions,
)


class ExternalApiTests(unittest.TestCase):
    def require_success(self, result, operation):
        if not result.ok:
            self.fail(f"{operation}: {result.error.code}")
        return result.data

    def test_tourapi_search_and_detail(self):
        if not setting("TOUR_API_SERVICE_KEY"):
            self.skipTest("TOUR_API_SERVICE_KEY is missing")
        candidates = self.require_success(search_attractions(keyword="경주"), "TourAPI search")
        candidate = next((row for row in candidates.attractions
                          if row.address and row.latitude is not None and row.longitude is not None), None)
        self.assertIsNotNone(candidate, "TourAPI search did not return a candidate with address and coordinates")
        self.assertEqual(candidates.requested_date, candidates.checked_at.date())
        self.assertEqual(candidates.basis, "current_catalog")
        detail = self.require_success(get_attraction_detail(content_id=candidate.content_id), "TourAPI detail")
        self.assertTrue(detail.content_id == candidate.content_id, "TourAPI detail ID mismatch")
        self.assertTrue(bool(detail.title and detail.address), "TourAPI detail missing name or address")
        self.assertTrue(detail.latitude is not None and detail.longitude is not None,
                        "TourAPI detail missing coordinates")

    def test_open_meteo_forecast(self):
        today = datetime.now(KST).date()
        target = date(2026, 11, 21)
        if not today <= target < today + timedelta(days=16):
            target = today + timedelta(days=1)
        coordinates = {"latitude": 35.8562, "longitude": 129.2248}
        weather = self.require_success(get_weather(**coordinates, date=target), "Open-Meteo forecast")
        self.assertEqual(weather.date, target)
        self.assertLessEqual(weather.available_from, target)
        self.assertGreaterEqual(weather.available_to, target)
        self.assertIsNotNone(weather.precipitation_probability_max, "Missing precipitation probability")
        self.assertIsNotNone(weather.temperature_min_c, "Missing daily minimum temperature")
        self.assertIsNotNone(weather.temperature_max_c, "Missing daily maximum temperature")
        self.assertLessEqual(weather.temperature_min_c, weather.temperature_max_c)
        print(f"Open-Meteo: {weather.date}, window {weather.available_from} to {weather.available_to}, "
              f"precipitation {weather.precipitation_probability_max:g}%, "
              f"min/max {weather.temperature_min_c:g}/{weather.temperature_max_c:g} C", flush=True)

    def test_airkorea_observations(self):
        if not setting("AIRKOREA_SERVICE_KEY"):
            self.skipTest("AIRKOREA_SERVICE_KEY is missing")
        data = self.require_success(get_air_quality(province="경북"), "AirKorea observations")
        self.assertEqual(data.kind, "observation")
        self.assertTrue(all(row.station_name and row.measured_at.utcoffset() == timedelta(hours=9)
                            for row in data.observations), "Invalid station or measurement timestamp")
        self.assertTrue(any(row.pm10_ug_m3 is not None for row in data.observations), "Missing PM10")
        self.assertTrue(any(row.pm25_ug_m3 is not None for row in data.observations), "Missing PM2.5")
        missing_pm10 = sum(row.pm10_ug_m3 is None for row in data.observations)
        missing_pm25 = sum(row.pm25_ug_m3 is None for row in data.observations)
        print(f"AirKorea: {len(data.observations)} observations, "
              f"{missing_pm10} missing PM10, {missing_pm25} missing PM2.5", flush=True)


class LocalToolTests(unittest.TestCase):
    # Local checks use synthetic data and do not establish provider availability.
    def test_out_of_range_is_reported_locally(self):
        target = datetime.now(KST).date() + timedelta(days=16)
        result = get_weather(latitude=35.8562, longitude=129.2248, date=target)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, "OUT_OF_FORECAST_RANGE")

    def test_weather_missing_probability_stays_null(self):
        target = datetime.now(KST).date()
        payload = {"daily": {"time": [target.isoformat()], "temperature_2m_min": [3]}}
        with patch("backend.tools.external_apis.get_json", return_value=payload):
            result = get_weather(latitude=35.8562, longitude=129.2248, date=target)
        self.assertTrue(result.ok)
        self.assertIsNone(result.data.precipitation_probability_max)
        self.assertEqual(result.data.temperature_min_c, 3)

    def test_air_quality_retains_missing_value_and_measurement_date(self):
        rows = [{"stationName": "시험측정소", "dataTime": "2026-11-18 24:00",
                 "pm10Value": "-", "pm25Value": "12"},
                {"stationName": "시각누락", "pm10Value": "9"}]
        with patch("backend.tools.external_apis.public_rows", return_value=rows):
            result = get_air_quality(province="경북")
        self.assertTrue(result.ok)
        self.assertEqual(result.data.kind, "observation")
        self.assertEqual(len(result.data.observations), 1)
        observation = result.data.observations[0]
        self.assertEqual(observation.measured_at, datetime(2026, 11, 19, tzinfo=KST))
        self.assertIsNone(observation.pm10_ug_m3)
        self.assertEqual(observation.pm25_ug_m3, 12)

    def test_missing_public_api_keys_prevent_http_calls(self):
        with patch("backend.tools.external_apis.setting", return_value=""), \
                patch("backend.tools.external_apis.get_json") as get_json:
            results = [search_attractions(keyword="경주"), get_attraction_detail(content_id="1"),
                       get_air_quality(province="경북")]
        self.assertTrue(all(result.error.code == "MISSING_API_KEY" for result in results))
        get_json.assert_not_called()
