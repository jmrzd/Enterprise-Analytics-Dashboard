"""FastAPI entrypoint for Vercel. Public demo: synthetic data only."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse

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
    return FileResponse(ROOT / "public" / "index.html", media_type="text/html")


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
