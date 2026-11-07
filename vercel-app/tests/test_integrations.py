"""Tests for the safe, transient business integration wizard."""
import asyncio
import io
import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrations import (
    ConnectionTest, authorize_connection, preview_file,
    status, _table_description
)
from app import integrations_status

TOKEN = "a-strong-example-admin-token-1234567890"
SAFE = "approved-database.example.com"


def conn(host=SAFE, engine="postgres", token=TOKEN):
    return ConnectionTest(
        engine=engine, host=host, port=5432 if engine == "postgres" else 3306,
        database="analytics", username="readonly", password="fake-readonly-password",
        admin_token=token,
    )


class IntegrationTests(unittest.TestCase):
    def test_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(status()["live_test_enabled"])
            with self.assertRaises(HTTPException) as error:
                authorize_connection(conn())
            self.assertEqual(error.exception.status_code, 503)
            self.assertNotIn(TOKEN, str(error.exception.detail))
            self.assertFalse(integrations_status().body.find(b"live_test_enabled") == -1)

    def test_admin_authorization_and_host_allowlist(self):
        env = {"INTEGRATION_ADMIN_TOKEN": TOKEN, "INTEGRATION_ALLOWED_HOSTS": SAFE}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(HTTPException) as error:
                authorize_connection(conn(token="incorrect-admin-token"))
            self.assertEqual(error.exception.status_code, 403)
            with self.assertRaises(HTTPException) as error:
                authorize_connection(conn(host="unapproved.example.com"))
            self.assertEqual(error.exception.status_code, 403)
            # DNS is not even queried for unapproved destinations.
            with patch("integrations.socket.getaddrinfo") as lookup:
                with self.assertRaises(HTTPException):
                    authorize_connection(conn(host="127.0.0.1"))
                lookup.assert_not_called()

    def test_private_addresses_are_blocked_after_dns_resolution(self):
        env = {"INTEGRATION_ADMIN_TOKEN": TOKEN, "INTEGRATION_ALLOWED_HOSTS": SAFE}
        with patch.dict(os.environ, env, clear=True), patch(
            "integrations.socket.getaddrinfo",
            return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.10.0.5", 5432))],
        ):
            with self.assertRaises(HTTPException) as error:
                authorize_connection(conn())
            self.assertEqual(error.exception.status_code, 403)
        with patch.dict(os.environ, env, clear=True), patch(
            "integrations.socket.getaddrinfo",
            return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 5432))],
        ):
            self.assertEqual(authorize_connection(conn()), SAFE)

    def test_bounded_catalog_metadata(self):
        records = [
            ("public", f"table_{i:02d}", "amount", "numeric") for i in range(30)
        ]
        tables = _table_description(records)
        self.assertEqual(len(tables), 16)
        self.assertEqual(tables[0]["columns"][0]["name"], "amount")

    def test_csv_preview_uses_memory_and_limits_rows(self):
        body = ("data;produto;valor\n" + "".join(
            f"2026-11-{i:02d};Item{i};{i}\n" for i in range(1, 20)
        )).encode("utf-8")
        sample = asyncio.run(preview_file(UploadFile(
            filename="vendas.csv", file=io.BytesIO(body)
        )))
        self.assertEqual(sample["columns"], ["data", "produto", "valor"])
        self.assertEqual(sample["format"], "csv")
        self.assertEqual(sample["preview_rows"], 12)
        self.assertFalse(sample["persisted"])
        self.assertTrue(sample["sample_only"])

    def test_xlsx_preview(self):
        book = Workbook()
        sheet = book.active
        sheet.append(["data", "categoria", "receita"])
        sheet.append(["2026-11-07", "Tecnologia", 250.5])
        buf = io.BytesIO()
        book.save(buf)
        buf.seek(0)
        sample = asyncio.run(preview_file(UploadFile(
            filename="vendas.xlsx", file=buf
        )))
        self.assertEqual(sample["format"], "xlsx")
        self.assertEqual(sample["columns"][:3], ["data", "categoria", "receita"])
        self.assertEqual(sample["rows"][0][2], "250.5")
        self.assertFalse(sample["persisted"])

    def test_invalid_extension_and_oversized_file(self):
        with self.assertRaises(HTTPException) as error:
            asyncio.run(preview_file(UploadFile(
                filename="report.exe", file=io.BytesIO(b"not a spreadsheet")
            )))
        self.assertEqual(error.exception.status_code, 415)
        with self.assertRaises(HTTPException) as error:
            asyncio.run(preview_file(UploadFile(
                filename="large.csv", file=io.BytesIO(b"a" * 1500002)
            )))
        self.assertEqual(error.exception.status_code, 413)


if __name__ == "__main__":
    unittest.main()
