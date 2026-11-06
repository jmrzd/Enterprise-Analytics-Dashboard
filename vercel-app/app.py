"""FastAPI entrypoint for Vercel. Public demo: synthetic data only."""
import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from analytics import dashboard

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

    Vercel may serve static assets outside the FastAPI routes, which left CSS
    and JS missing in the initial deployment. Inline the trusted local assets
    and bootstrap all demo periods, so navigation never depends on /assets/*
    or an additional /api/dashboard request.
    """
    page = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
    stylesheet = (ROOT / "public" / "app.css").read_text(encoding="utf-8")
    javascript = (ROOT / "public" / "app.js").read_text(encoding="utf-8")
    data = json.dumps(
        {period: dashboard(period) for period in ("30d", "90d", "180d", "365d")},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
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
        + '</script></body>',
    )
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})


@app.get("/assets/app.css", include_in_schema=False)
def styles():
    return FileResponse(ROOT / "public" / "app.css", media_type="text/css")


@app.get("/assets/app.js", include_in_schema=False)
def scripts():
    return FileResponse(ROOT / "public" / "app.js", media_type="application/javascript")


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(ROOT / "public" / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "enterprise-analytics", "mode": "synthetic-demo"}


@app.get("/api/dashboard")
def get_dashboard(
    period: Literal["30d", "90d", "180d", "365d", "all"] = Query("90d")
):
    return JSONResponse(dashboard(period))
