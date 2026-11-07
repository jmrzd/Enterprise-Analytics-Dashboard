"""Security and synchronization tests; never connect to a real business DB."""
import json
import os
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from sync_service import SyncRequest, _catalog_types, _result, sync_aggregates

TOKEN = "example-administrator-secret-with-32-characters-not-real"


def request(**kwargs):
    payload = dict(
        engine="postgres", host="approved.example.com", port=5432,
        database="analytics", username="read_only", password="fake-password-not-real",
        admin_token=TOKEN, schema_name="public", table_name="vendas",
        date_column="data", value_column="receita",
        category_column="categoria", window_days=90,
    )
    payload.update(kwargs)
    return SyncRequest(**payload)


class SyncTests(unittest.TestCase):
    def test_no_public_unprotected_sync(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("sync_service._postgres") as query:
                with self.assertRaises(HTTPException) as raised:
                    sync_aggregates(request())
                self.assertEqual(raised.exception.status_code, 503)
                query.assert_not_called()

    def test_sql_columns_checked_against_catalog(self):
        expected = [("data", "date"), ("receita", "numeric"), ("categoria", "character varying")]
        _catalog_types(expected, request())
        with self.assertRaises(HTTPException) as error:
            _catalog_types(expected, request(value_column="DROP TABLE vendas; --"))
        self.assertEqual(error.exception.status_code, 422)
        with self.assertRaises(HTTPException):
            _catalog_types(expected, request(date_column="receita"))
        with self.assertRaises(HTTPException):
            _catalog_types(expected, request(value_column="categoria"))
        with self.assertRaises(HTTPException):
            _catalog_types(expected, request(category_column="email_clientes"))

    def test_sync_is_aggregate_only_and_returns_no_secrets(self):
        sample = [(date(2026, 10, 1), 1500, 10), (date(2026, 11, 1), 2500, 18)]
        groups = [("Hardware", 3000), ("Suporte", 1000)]
        with patch("sync_service.authorize_connection", return_value="approved.example.com"), \
             patch("sync_service._postgres", return_value=(sample, groups)):
            result = sync_aggregates(request())
        self.assertTrue(result["connected"])
        self.assertFalse(result["persisted"])
        self.assertEqual(result["total_amount"], 4000)
        self.assertEqual(result["row_count"], 28)
        self.assertEqual(len(result["months"]), 2)
        self.assertEqual(len(result["categories"]), 2)
        output = json.dumps(result)
        self.assertNotIn(TOKEN, output)
        self.assertNotIn("fake-password-not-real", output)
        self.assertNotIn("read_only", output)

    def test_sensible_validation_and_no_raw_sql_or_periods(self):
        with self.assertRaises(ValidationError):
            request(window_days=1000)
        with self.assertRaises(ValidationError):
            request(engine="sqlite")
        with self.assertRaises(HTTPException):
            _result(request(), [("2026-11", float("nan"), 1)], [])

    def test_browser_csp_nonce_and_defensive_headers(self):
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        csp = response.headers.get("content-security-policy", "")
        self.assertIn("script-src 'nonce-", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("connect-src 'self'", csp)
        self.assertNotIn("'unsafe-eval'", csp)
        self.assertNotIn("script-src 'unsafe-inline'", csp)
        self.assertIn('nonce="', response.text)
        self.assertEqual(response.headers.get("x-frame-options"), "DENY")
        self.assertEqual(response.headers.get("referrer-policy"), "no-referrer")
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")

    def test_cross_origin_and_oversize_blocked(self):
        client = TestClient(app)
        r = client.post("/api/integrations/sync", headers={
            "sec-fetch-site": "cross-site", "content-type": "application/json",
        }, json={})
        self.assertEqual(r.status_code, 403)
        r = client.post("/api/integrations/sync",
            content=b"a"*21000,
            headers={"content-type": "application/json"})
        self.assertEqual(r.status_code, 413)


if __name__ == "__main__":
    unittest.main()
