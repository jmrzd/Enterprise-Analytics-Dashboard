"""Safe, opt-in integration discovery for the public demo.

No database credentials are saved. Live connection testing requires an owner
secret and a server-configured hostname allowlist. No arbitrary SQL or table
data is exposed to visitors. Spreadsheet previews are kept in memory only.
"""
from __future__ import annotations

import csv
import hmac
import io
import ipaddress
import math
import os
import re
import socket
import ssl
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, Field, SecretStr

MAX_FILE_BYTES = 1_500_000
MAX_XLSX_EXPANDED = 9_000_000
MAX_ROWS = 12
MAX_COLUMNS = 24
HOST_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")
ENGINES = {"postgres": 5432, "mysql": 3306}


class ConnectionTest(BaseModel):
    engine: Literal["postgres", "mysql"]
    host: str = Field(min_length=3, max_length=253)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    password: SecretStr
    admin_token: SecretStr


def status():
    return {
        "engines": ["postgres", "mysql"],
        "formats": ["csv", "xlsx"],
        "live_test_enabled": bool(
            os.getenv("INTEGRATION_ADMIN_TOKEN") and os.getenv("INTEGRATION_ALLOWED_HOSTS")
        ),
        "data_policy": (
            "As senhas e os arquivos não são armazenados pela aplicação. "
            "O teste SQL exige autorização e só aceita destinos aprovados pelo operador. "
            "As conexões testadas não são salvas nem alimentam automaticamente o dashboard."
        ),
    }


def _approved_hosts():
    return {x.strip().lower().rstrip(".") for x in
            os.getenv("INTEGRATION_ALLOWED_HOSTS", "").split(",") if x.strip()}


def authorize_connection(req: ConnectionTest):
    expected = os.getenv("INTEGRATION_ADMIN_TOKEN", "")
    if not expected or not os.getenv("INTEGRATION_ALLOWED_HOSTS"):
        raise HTTPException(503, detail="Teste remoto desativado. Configure INTEGRATION_ADMIN_TOKEN e INTEGRATION_ALLOWED_HOSTS na Vercel.")
    if len(expected) < 24 or not hmac.compare_digest(expected, req.admin_token.get_secret_value()):
        raise HTTPException(403, detail="Acesso não autorizado para testar bancos remotos.")
    host = req.host.strip().lower().rstrip(".")
    if not HOST_RE.fullmatch(host) or host not in _approved_hosts():
        raise HTTPException(403, detail="Servidor não autorizado. Solicite ao administrador que aprove o endereço na Vercel.")
    if not req.password.get_secret_value() or len(req.password.get_secret_value()) > 1024:
        raise HTTPException(400, detail="Senha inválida.")
    # No internal network, metadata endpoints, special addresses, or localhost.
    try:
        infos = socket.getaddrinfo(host, req.port, type=socket.SOCK_STREAM)
    except OSError:
        raise HTTPException(400, detail="Não foi possível resolver o endereço do servidor.") from None
    if not infos:
        raise HTTPException(400, detail="Endereço de servidor inválido.")
    try:
        ips = {ipaddress.ip_address(info[4][0]) for info in infos}
    except (ValueError, IndexError):
        raise HTTPException(403, detail="Destino de rede bloqueado.") from None
    if not all(ip.is_global for ip in ips):
        raise HTTPException(403, detail="Endereços privados, locais ou reservados não são aceitos no site público.")
    return host


def _table_description(rows):
    tables = {}
    for schema, table, column, datatype in rows:
        if len(tables) >= 16 and (schema, table) not in tables:
            break
        key = (str(schema), str(table))
        entry = tables.setdefault(key, {"schema": str(schema), "table": str(table), "columns": []})
        if len(entry["columns"]) < MAX_COLUMNS:
            entry["columns"].append({"name": str(column), "type": str(datatype)})
    return list(tables.values())


def test_connection(req: ConnectionTest):
    host = authorize_connection(req)
    # Do not print exceptions or return error messages from database drivers;
    # those messages sometimes contain usernames or connection strings.
    try:
        if req.engine == "postgres":
            import psycopg
            with psycopg.connect(
                host=host, port=req.port, dbname=req.database, user=req.username,
                password=req.password.get_secret_value(), sslmode="verify-full",
                connect_timeout=4, options="-c default_transaction_read_only=on -c statement_timeout=3500",
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                    cur.execute(
                        "SELECT table_schema,table_name,column_name,data_type "
                        "FROM information_schema.columns "
                        "WHERE table_schema NOT IN ('pg_catalog','information_schema') "
                        "ORDER BY table_schema,table_name,ordinal_position LIMIT 350"
                    )
                    tables = _table_description(cur.fetchall())
        else:
            import pymysql
            tls = ssl.create_default_context()
            tls.verify_mode = ssl.CERT_REQUIRED
            tls.check_hostname = True
            conn = pymysql.connect(
                host=host, port=req.port, user=req.username,
                password=req.password.get_secret_value(), database=req.database,
                ssl=tls, connect_timeout=4, read_timeout=5, write_timeout=5,
                charset="utf8mb4", autocommit=True, local_infile=False,
                init_command="SET SESSION TRANSACTION READ ONLY",
            )
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                    cur.execute(
                        "SELECT table_schema,table_name,column_name,data_type "
                        "FROM information_schema.columns "
                        "WHERE table_schema = DATABASE() "
                        "ORDER BY table_name,ordinal_position LIMIT 350"
                    )
                    tables = _table_description(cur.fetchall())
            finally:
                conn.close()
    except Exception:
        raise HTTPException(
            422, detail=(
                "Não foi possível estabelecer uma conexão TLS verificada e consultar "
                "as tabelas. Confira host, porta, credenciais, certificado e acesso "
                "de rede do servidor. Nenhuma credencial foi salva."
            )
        ) from None
    return {"connected": True, "engine": req.engine, "server": host,
            "tables": tables, "table_count": len(tables),
            "message": "Conexão segura validada com SELECT 1. Foram retornados somente nomes e tipos de colunas. Senhas não foram salvas.",
            "saved": False}


def _render_cell(value):
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return ""
    return str(value)[:180]


def _clean_rows(records):
    source = iter(records)
    try:
        original_headers = next(source)
    except StopIteration:
        raise HTTPException(400, detail="Arquivo sem linhas de dados.") from None
    headers = [
        str(v).strip()[:90] if v is not None and str(v).strip() else f"Coluna {i+1}"
        for i, v in enumerate(original_headers[:MAX_COLUMNS])
    ]
    if not headers:
        raise HTTPException(400, detail="Arquivo sem colunas.")
    rows = []
    for record in source:
        rows.append([_render_cell(x) for x in record[:len(headers)]] +
                    [""] * max(0, len(headers) - len(record)))
        if len(rows) >= MAX_ROWS:
            break
    return {"columns": headers, "rows": rows, "preview_rows": len(rows),
            "sample_only": True, "persisted": False}


async def preview_file(file: UploadFile):
    filename = Path(file.filename or "").name[:120]
    suffix = Path(filename).suffix.lower()
    if suffix not in (".csv", ".xlsx"):
        raise HTTPException(415, detail="Use arquivos CSV ou Excel .xlsx.")
    # Read one extra byte to reject oversize uploads without parsing them.
    raw = await file.read(MAX_FILE_BYTES + 1)
    await file.close()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(413, detail="Arquivo muito grande. Limite: 1,5 MB.")
    if not raw:
        raise HTTPException(400, detail="O arquivo está vazio.")

    if suffix == ".csv":
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(400, detail="Salve o CSV com codificação UTF-8.") from None
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t|")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ";" if sample.count(";") > sample.count(",") else ","
        parsed = _clean_rows(csv.reader(io.StringIO(text), delimiter=delimiter))
    else:
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if len(z.infolist()) > 180 or sum(x.file_size for x in z.infolist()) > MAX_XLSX_EXPANDED:
                    raise HTTPException(413, detail="Planilha excede o limite de tamanho descompactado.")
            from openpyxl import load_workbook
            workbook = load_workbook(io.BytesIO(raw), read_only=True, data_only=True, keep_links=False)
            try:
                sheet = workbook.active
                if sheet is None:
                    raise HTTPException(400, detail="Planilha sem páginas.")
                parsed = _clean_rows(
                    sheet.iter_rows(min_row=1, max_row=MAX_ROWS + 1,
                                    max_col=MAX_COLUMNS, values_only=True)
                )
            finally:
                workbook.close()
        except HTTPException:
            raise
        except (ValueError, KeyError, OSError, zipfile.BadZipFile, RuntimeError):
            raise HTTPException(400, detail="Excel inválido ou não suportado.") from None
    return {"filename": filename, "format": suffix[1:], **parsed,
            "message": "Amostra lida em memória e descartada. Nenhum arquivo foi salvo ou conectado permanentemente."}
