import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import compare, materials, reports, search
from app.db.database import Base, engine

# Create database tables at startup/import time.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MatSearch AI Backend",
    description=(
        "Autonomous AI-powered materials discovery and engineering "
        "agent using Materials Project data and deterministic evaluation."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)

origins = [
    origin.strip()
    for origin in raw_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

app.include_router(
    search.router,
    prefix="/api/search",
    tags=["Search"],
)

app.include_router(
    materials.router,
    prefix="/api/material",
    tags=["Materials"],
)

app.include_router(
    compare.router,
    prefix="/api/compare",
    tags=["Comparison"],
)

app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Reports"],
)

# ---------------------------------------------------------
# SYSTEM ENDPOINTS
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "MatSearch AI",
        "status": "online",
        "version": "1.0.0",
        "description": "Autonomous Materials Discovery & Engineering Agent",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "matsearch-ai-backend",
    }


@app.get("/api/status")
def api_status():
    return {
        "status": "ok",
        "api": "operational",
        "materials_project": bool(os.getenv("MP_API_KEY")),
        "llm_provider": os.getenv(
            "LLM_PROVIDER",
            "gemini",
        ),
        "llm_model": os.getenv(
            "LLM_MODEL",
            "gemini-3.8-flash",
        ),
    }

