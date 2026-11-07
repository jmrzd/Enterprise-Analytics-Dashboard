"""Owner-authorized read-only aggregates; nothing persisted to disk/database.

Connections are explicit, TLS-verified and read-only. Columns are looked up
in the metadata catalog and identifiers safely quoted. Only aggregated numeric
totals are returned. This is NOT a multi-tenant recurring synchronization.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from ipaddress import ip_address
from math import isfinite
import socket
import ssl
from typing import Literal

from fastapi import HTTPException
from pydantic import Field

from integrations import ConnectionTest, authorize_connection

PG_DATES = {"date", "timestamp without time zone", "timestamp with time zone"}
PG_NUMBERS = {"smallint", "integer", "bigint", "numeric", "real", "double precision", "decimal"}
MY_DATES = {"date", "datetime", "timestamp"}
MY_NUMBERS = {"tinyint", "smallint", "mediumint", "int", "bigint", "decimal", "numeric", "float", "double"}
CATEGORIES = {"text", "character", "character varying", "varchar", "char", "enum",
              "smallint", "integer", "bigint", "int", "tinyint", "mediumint"}


class SyncRequest(ConnectionTest):
    schema_name: str = Field(min_length=1, max_length=128)
    table_name: str = Field(min_length=1, max_length=128)
    date_column: str = Field(min_length=1, max_length=128)
    value_column: str = Field(min_length=1, max_length=128)
    category_column: str | None = Field(default=None, max_length=128)
    window_days: Literal[30, 90, 180, 365] = 90


def _public_address(host, port):
    try:
        addresses = {ip_address(item[4][0]) for item in
                     socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    except (OSError, IndexError, ValueError):
        raise HTTPException(403, detail="Endereço de rede inválido.") from None
    if not addresses or any(not address.is_global for address in addresses):
        raise HTTPException(403, detail="Destinos privados ou reservados são bloqueados.") from None
    return str(sorted(addresses, key=lambda x: (x.version, int(x)))[0])


def _catalog_types(rows, request):
    columns = {str(name): str(kind).lower() for name, kind in rows}
    expected_date = PG_DATES if request.engine == "postgres" else MY_DATES
    expected_number = PG_NUMBERS if request.engine == "postgres" else MY_NUMBERS
    if columns.get(request.date_column) not in expected_date:
        raise HTTPException(422, detail="Selecione uma coluna de data/timestamp reconhecida.")
    if columns.get(request.value_column) not in expected_number:
        raise HTTPException(422, detail="Selecione uma coluna numérica para somar os valores.")
    if request.category_column and columns.get(request.category_column) not in CATEGORIES:
        raise HTTPException(422, detail="A categoria deve conter texto ou números.")
    if request.category_column and any(term in request.category_column.lower()
        for term in ("email", "cpf", "cnpj", "telefone", "phone", "senha", "password",
                     "token", "secret", "documento", "endereco", "address",
                     "nome", "name", "cliente", "customer", "pessoa", "employee", "funcionario")):
        raise HTTPException(422, detail="Este campo não pode ser usado como categoria.")
    if request.date_column == request.value_column:
        raise HTTPException(422, detail="Data e valor devem ser colunas diferentes.")


def _result(request, months, categories):
    values = []
    for month, total, count in months[:13]:
        month = month.strftime("%Y-%m") if isinstance(month, (date, datetime)) else str(month)[:7]
        if len(month) != 7 or month[4] != "-" or not month[:4].isdigit() or not month[-2:].isdigit():
            raise HTTPException(422, detail="A coluna de data não pôde ser agrupada por mês.")
        total = float(total or 0)
        if not isfinite(total):
            raise HTTPException(422, detail="A soma retornou um valor inválido.")
        values.append({"month": month, "amount": round(total, 2), "records": int(count or 0)})
    groups = []
    for label, amount in categories[:8]:
        amount = float(amount or 0)
        if not isfinite(amount):
            continue
        groups.append({"category": str(label)[:60] if label is not None else "Sem categoria",
                       "amount": round(amount, 2)})
    return {
        "mode": "ephemeral-readonly", "connected": True, "persisted": False,
        "engine": request.engine, "table": f"{request.schema_name}.{request.table_name}",
        "window_days": request.window_days, "synced_at": datetime.now(timezone.utc).isoformat(),
        "months": values, "categories": groups,
        "total_amount": round(sum(m["amount"] for m in values), 2),
        "row_count": sum(m["records"] for m in values),
        "disclaimer": "Agregados de uma tabela autorizada; não foram salvos. A sincronização permanente e multiempresa requer login e armazenamento privado.",
    }


def _postgres(request, host, first_day, exclusive_end):
    import psycopg
    from psycopg import sql
    # Pin the resolved public IP to stop DNS rebinding on the PostgreSQL path.
    peer = _public_address(host, request.port)
    with psycopg.connect(
        host=host, hostaddr=peer, port=request.port, dbname=request.database,
        user=request.username, password=request.password.get_secret_value(),
        sslmode="verify-full", connect_timeout=4,
        options="-c default_transaction_read_only=on -c statement_timeout=3500",
    ) as connection:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position LIMIT 64",
                (request.schema_name, request.table_name))
            columns = cur.fetchall()
            if not columns:
                raise HTTPException(422, detail="Tabela não encontrada ou não autorizada.")
            _catalog_types(columns, request)
            table = sql.Identifier(request.schema_name, request.table_name)
            dt, amount = sql.Identifier(request.date_column), sql.Identifier(request.value_column)
            query = sql.SQL(
                "SELECT date_trunc('month', {}::timestamp)::date AS month, "
                "SUM({})::float8 AS total, COUNT(*)::bigint AS count "
                "FROM {} WHERE {} >= %s AND {} < %s "
                "GROUP BY 1 ORDER BY 1 LIMIT 13"
            ).format(dt, amount, table, dt, dt)
            cur.execute(query, (first_day, exclusive_end))
            months = cur.fetchall()
            categories = []
            if request.category_column:
                group = sql.Identifier(request.category_column)
                query = sql.SQL(
                    "SELECT {}::text AS label, SUM({})::float8 AS total "
                    "FROM {} WHERE {} >= %s AND {} < %s "
                    "GROUP BY 1 ORDER BY 2 DESC LIMIT 8"
                ).format(group, amount, table, dt, dt)
                cur.execute(query, (first_day, exclusive_end))
                categories = cur.fetchall()
    return months, categories


def _mysql(request, host, first_day, exclusive_end):
    import pymysql
    tls = ssl.create_default_context()
    tls.verify_mode = ssl.CERT_REQUIRED
    tls.check_hostname = True
    connection = pymysql.connect(
        host=host, port=request.port, user=request.username,
        password=request.password.get_secret_value(), database=request.database,
        ssl=tls, connect_timeout=4, read_timeout=5, write_timeout=5,
        charset="utf8mb4", autocommit=True, local_infile=False,
        init_command="SET SESSION TRANSACTION READ ONLY")
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.columns "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION LIMIT 64",
                (request.schema_name, request.table_name))
            columns = cur.fetchall()
            if not columns:
                raise HTTPException(422, detail="Tabela não encontrada ou não autorizada.")
            _catalog_types(columns, request)
            def ident(name):
                quote = chr(96)
                return quote + name.replace(quote, quote + quote) + quote
            table = ident(request.schema_name) + "." + ident(request.table_name)
            dt, amount = ident(request.date_column), ident(request.value_column)
            cur.execute(
                f"SELECT DATE_FORMAT({dt}, '%%Y-%%m-01'), SUM({amount}), COUNT(*) "
                f"FROM {table} WHERE {dt} >= %s AND {dt} < %s GROUP BY 1 ORDER BY 1 LIMIT 13",
                (first_day, exclusive_end))
            months = cur.fetchall()
            categories = []
            if request.category_column:
                group = ident(request.category_column)
                cur.execute(
                    f"SELECT CAST({group} AS CHAR), SUM({amount}) FROM {table} "
                    f"WHERE {dt} >= %s AND {dt} < %s GROUP BY 1 ORDER BY 2 DESC LIMIT 8",
                    (first_day, exclusive_end))
                categories = cur.fetchall()
    finally:
        connection.close()
    return months, categories


def sync_aggregates(request: SyncRequest):
    host = authorize_connection(request)
    today = date.today()
    first_day = today - timedelta(days=request.window_days - 1)
    end = today + timedelta(days=1)
    try:
        if request.engine == "postgres":
            months, categories = _postgres(request, host, first_day, end)
        else:
            months, categories = _mysql(request, host, first_day, end)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, detail="Falha na leitura segura. Confira tabela, tipos de colunas, rede, TLS e permissão SELECT.") from None
    return _result(request, months, categories)
