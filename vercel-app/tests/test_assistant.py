"""Tests for the BYOK assistant without calling OpenAI or Gemini."""
import asyncio
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import dashboard
from assistant_api import ChatRequest, answer_question, _extract_openai, _extract_gemini

FAKE_KEY = "test_key_fake_no_real_secret_123456789"


class MockResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.called = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, headers, json):
        self.called = (url, headers, json)
        return self.response


class AssistantTests(unittest.TestCase):
    def test_weekly_data_reconciles_with_monthly_kpis(self):
        data = dashboard("90d", date(2026, 11, 6))
        self.assertGreater(len(data["weekly"]), 10)
        self.assertEqual(sum(row["revenue"] for row in data["weekly"]), data["kpis"]["revenue"])
        self.assertEqual(sum(row["orders"] for row in data["weekly"]), data["kpis"]["orders"])
        self.assertAlmostEqual(sum(row["income"] for row in data["weekly"]), data["kpis"]["income"], places=2)

    def test_provider_parsers(self):
        self.assertEqual(
            _extract_openai({"output": [{"type": "message", "content": [{"type": "output_text", "text": "R$ 10"}]}]}),
            "R$ 10",
        )
        self.assertEqual(
            _extract_gemini({"candidates": [{"content": {"parts": [{"text": "Resposta OK"}]}}]}),
            "Resposta OK",
        )

    def test_openai_request_is_bounded_and_not_stored(self):
        client = FakeClient(MockResponse({"output": [{"type": "message", "content": [{"type": "output_text", "text": "Margem: 30%"}]}]}))
        with patch("assistant_api.httpx.AsyncClient", return_value=client):
            result = asyncio.run(answer_question(ChatRequest(
                provider="openai", api_key=FAKE_KEY, question="Qual é a margem?", period="90d"
            )))
        self.assertEqual(result["answer"], "Margem: 30%")
        self.assertEqual(result["provider"], "openai")
        url, headers, payload = client.called
        self.assertEqual(url, "https://api.openai.com/v1/responses")
        self.assertEqual(payload["store"], False)
        self.assertNotIn(FAKE_KEY, json.dumps(result))
        self.assertNotIn(FAKE_KEY, json.dumps(payload))

    def test_gemini_sends_key_in_header_not_url(self):
        client = FakeClient(MockResponse({"candidates": [{"content": {"parts": [{"text": "Calculado."}]}}]}))
        with patch("assistant_api.httpx.AsyncClient", return_value=client):
            result = asyncio.run(answer_question(ChatRequest(
                provider="gemini", api_key=FAKE_KEY, question="Compare dois meses", period="30d"
            )))
        self.assertEqual(result["answer"], "Calculado.")
        url, headers, payload = client.called
        self.assertNotIn(FAKE_KEY, url)
        self.assertIn("generativelanguage.googleapis.com", url)
        self.assertEqual(headers["x-goog-api-key"], FAKE_KEY)
        self.assertNotIn(FAKE_KEY, json.dumps(payload))

    def test_invalid_key_does_not_reach_external_provider(self):
        with patch("assistant_api.httpx.AsyncClient") as client:
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(answer_question(ChatRequest(
                    provider="openai", api_key="tiny", question="Teste"
                )))
            self.assertEqual(raised.exception.status_code, 400)
            client.assert_not_called()

    def test_upstream_error_never_echoes_key(self):
        client = FakeClient(MockResponse({"error": {"message": FAKE_KEY}}, status=401))
        with patch("assistant_api.httpx.AsyncClient", return_value=client):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(answer_question(ChatRequest(
                    provider="openai", api_key=FAKE_KEY, question="Teste"
                )))
        self.assertEqual(raised.exception.status_code, 401)
        self.assertNotIn(FAKE_KEY, str(raised.exception.detail))


if __name__ == "__main__":
    unittest.main()
