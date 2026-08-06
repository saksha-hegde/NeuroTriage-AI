"""
NeuroTriage AI - Prototype backend entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000

This app deliberately stays thin: it wires up CORS and routers only. Business
logic lives in app/services and app/core so it can be unit tested without
spinning up HTTP.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_studies import router as studies_router
from app.core.config import APP_NAME, APP_VERSION, CORS_ORIGINS

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(studies_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    """Liveness check used by the dev script and manual QA."""
    return {"status": "ok", "service": APP_NAME}
