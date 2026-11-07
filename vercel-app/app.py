"""FastAPI entrypoint for Vercel. Public demo: synthetic data only."""
import json
import secrets
from urllib.parse import urlsplit
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from analytics import dashboard
from assistant_api import ChatRequest, answer_question
from integrations import ConnectionTest, status as integration_status, test_connection, preview_file
from sync_service import SyncRequest, sync_aggregates
from features import ScenarioInput, calculate_scenario, create_powerbi_kit, export_data, get_insights, insights_for, DAX_EXAMPLES

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title="Enterprise Analytics API",
    description="API pública com dados sintéticos. Não contém dados empresariais reais.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)


@app.get("/", include_in_schema=False)
def home():
    """Deliver the entire dashboard in one HTML response.

    A public/index.html shadows this route on Vercel and leaves the CSS and JS
    missing. The private templates/ folder keeps FastAPI in charge of /. Inline the trusted local assets
    and bootstrap all demo periods, so navigation never depends on /assets/*
    or an additional /api/dashboard request.
    """
    page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    stylesheet = (ROOT / "templates" / "app.css").read_text(encoding="utf-8")
    javascript = (ROOT / "templates" / "app.js").read_text(encoding="utf-8")
    upgrade_css = (ROOT / "templates" / "upgrade.css").read_text(encoding="utf-8")
    upgrade_js = (ROOT / "templates" / "upgrade.js").read_text(encoding="utf-8")
    studio_css = (ROOT / "templates" / "studio.css").read_text(encoding="utf-8")
    studio_js = (ROOT / "templates" / "studio.js").read_text(encoding="utf-8")
    integrations_css = (ROOT / "templates" / "integrations.css").read_text(encoding="utf-8")
    integrations_js = (ROOT / "templates" / "integrations.js").read_text(encoding="utf-8")
    responsive_css = (ROOT / "templates" / "responsive.css").read_text(encoding="utf-8")
    responsive_js = (ROOT / "templates" / "responsive.js").read_text(encoding="utf-8")
    bundled = {}
    for period in ("30d", "90d", "180d", "365d"):
        record = dashboard(period)
        record["smart"] = insights_for(record)
        bundled[period] = record
    data = json.dumps(bundled, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    page = page.replace(
        '<link rel="stylesheet" href="/assets/app.css">',
        '<style id="dashboard-style">' + stylesheet + '</style>',
    ).replace('<script src="/assets/app.js" defer></script>', "")
    page = page.replace(
        "</body>",
        '<script id="dashboard-bootstrap" type="application/json">'
        + data
        + '</script><script id="dashboard-script">'
        + javascript
        + '</script><style id="dashboard-upgrade-style">'
        + upgrade_css
        + '</style><script id="dashboard-upgrade-script">'
        + upgrade_js
        + '</script><style id="dashboard-studio-style">'
        + studio_css
        + '</style><script id="dashboard-studio-script">'
        + studio_js
        + '</script><style id="dashboard-integrations-style">'
        + integrations_css
        + '</style><script id="dashboard-integrations-script">'
        + integrations_js
        + '</script><style id="dashboard-responsive-style">'
        + responsive_css
        + '</style><script id="dashboard-responsive-script">'
        + responsive_js
        + '</script></body>',
    )
    nonce = secrets.token_urlsafe(24)
    page = page.replace('<script id="', '<script nonce="' + nonce + '" id="')
    csp = (
        "default-src 'none'; base-uri 'none'; object-src 'none'; "
        "script-src 'nonce-" + nonce + "'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; img-src 'self' data:; "
        "connect-src 'self'; form-action 'self'; frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    )
    return HTMLResponse(page, headers={
        "Cache-Control": "no-store", "X-Dashboard-Render": "fastapi-inline-v8",
        "Content-Security-Policy": csp
    })


@app.get("/assets/app.css", include_in_schema=False)
def styles():
    return FileResponse(ROOT / "templates" / "app.css", media_type="text/css")


@app.get("/assets/app.js", include_in_schema=False)
def scripts():
    return FileResponse(ROOT / "templates" / "app.js", media_type="application/javascript")


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(ROOT / "templates" / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "enterprise-analytics", "mode": "synthetic-demo"}


@app.get("/api/dashboard")
def get_dashboard(
    period: Literal["30d", "90d", "180d", "365d", "all"] = Query("90d")
):
    return JSONResponse(dashboard(period))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Bring-your-own-key assistant; the key never persists on this server."""
    return JSONResponse(
        await answer_question(request),
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/insights")
def insights(period: Literal["30d", "90d", "180d", "365d"] = "90d"):
    return JSONResponse(get_insights(period), headers={"Cache-Control": "no-store"})


@app.post("/api/scenario")
def scenario(payload: ScenarioInput):
    return JSONResponse(calculate_scenario(payload), headers={"Cache-Control": "no-store"})


@app.get("/api/powerbi/kit")
def powerbi_kit(period: Literal["30d", "90d", "180d", "365d"] = "90d"):
    content = create_powerbi_kit(dashboard(period))
    return Response(
        content, media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="enterprise-analytics-powerbi-kit.zip"',
                 "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.get("/api/powerbi/dax")
def powerbi_dax():
    return Response(
        DAX_EXAMPLES, media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="medidas.dax"',
                 "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.get("/api/powerbi/{dataset}")
def powerbi_export(
    dataset: Literal["vendas", "financeiro", "rh", "produtos", "clientes", "categorias"],
    period: Literal["30d", "90d", "180d", "365d"] = "90d",
):
    body = export_data(dataset, dashboard(period))
    return Response(
        body, media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{dataset}.csv"',
                 "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.get("/api/integrations/status")
def integrations_status():
    """Public configuration only; never expose the server allowlist or tokens."""
    return JSONResponse(integration_status(), headers={"Cache-Control": "no-store"})


@app.post("/api/integrations/test")
def integrations_test(request: ConnectionTest):
    """Authorized, one-shot TLS connection test; no credentials persisted."""
    return JSONResponse(test_connection(request), headers={"Cache-Control": "no-store"})


@app.post("/api/integrations/file-preview")
async def integrations_preview(file: UploadFile = File(...)):
    """Read a small spreadsheet into RAM for a bounded, nonpersistent preview."""
    result = await preview_file(file)
    return JSONResponse(result, headers={"Cache-Control": "no-store"})


@app.post("/api/integrations/sync")
def integrations_sync(payload: SyncRequest):
    """Owner-only, read-only aggregation into transient response, no persistence."""
    return JSONResponse(sync_aggregates(payload), headers={"Cache-Control": "no-store"})


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Defensive headers, restrictive cross-site browser policy and size guards."""
    path = request.url.path
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin", "")
        if origin:
            parsed = urlsplit(origin)
            if parsed.netloc.lower() != request.headers.get("host", "").lower() or parsed.scheme not in {"http", "https"}:
                return JSONResponse({"detail": "Origem da requisição não autorizada."}, status_code=403)
        fetch_site = request.headers.get("sec-fetch-site", "")
        if fetch_site in {"cross-site", "same-site"}:
            return JSONResponse({"detail": "Requisição entre origens não autorizada."}, status_code=403)
        if path.startswith("/api/integrations/") or path == "/api/chat":
            content_length = request.headers.get("content-length")
            limit = 2_000_000 if path.endswith("/file-preview") else 20_000
            if content_length:
                try:
                    size = int(content_length)
                except ValueError:
                    return JSONResponse({"detail": "Tamanho da requisição inválido."}, status_code=400)
                if size < 0 or size > limit:
                    return JSONResponse({"detail": "Requisição excede o tamanho permitido."}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if path.startswith("/api/") or path == "/":
        response.headers["Cache-Control"] = "no-store"
    return response
