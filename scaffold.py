import os

BASE_DIR = r"C:\Users\Ahmadcomputer\.gemini\antigravity\scratch\MatSearch-AI\backend"

files = {
    "app/main.py": """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import search, materials, compare, reports
from app.db.database import engine, Base
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MatSearch AI Backend")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(materials.router, prefix="/api/material", tags=["materials"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
""",
    "app/db/database.py": """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./matsearch.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "app/models/search.py": """
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.db.database import Base
from datetime import datetime

class SearchJob(Base):
    __tablename__ = "search_jobs"
    id = Column(String, primary_key=True, index=True)
    query = Column(String)
    status = Column(String, default="pending")
    state = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
""",
    "app/schemas/search.py": """
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    search_id: str
    status: str

class MaterialDetail(BaseModel):
    material_id: str
    formula: str
    density: Optional[float] = None
    band_gap: Optional[float] = None
    source: str = "Materials Project"
""",
    "app/api/search.py": """
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from app.db.database import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.models.search import SearchJob
from app.orchestration.workflow import run_workflow
import uuid
import asyncio
import json

router = APIRouter()

@router.post("/", response_model=SearchResponse)
def create_search(req: SearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = SearchJob(id=job_id, query=req.query, status="running")
    db.add(job)
    db.commit()
    background_tasks.add_task(run_workflow, job_id, req.query, db)
    return SearchResponse(search_id=job_id, status="running")

@router.get("/{search_id}")
def get_search(search_id: str, db: Session = Depends(get_db)):
    job = db.query(SearchJob).filter(SearchJob.id == search_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": job.id, "query": job.query, "status": job.status, "state": job.state}

@router.get("/{search_id}/events")
async def search_events(search_id: str, db: Session = Depends(get_db)):
    async def event_generator():
        while True:
            job = db.query(SearchJob).filter(SearchJob.id == search_id).first()
            if not job:
                break
            yield json.dumps({"status": job.status, "state": job.state})
            if job.status in ["completed", "failed"]:
                break
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())
""",
    "app/api/materials.py": """
from fastapi import APIRouter
router = APIRouter()
@router.get("/{material_id}")
def get_material(material_id: str):
    return {"material_id": material_id, "status": "mocked"}
""",
    "app/api/compare.py": """
from fastapi import APIRouter
router = APIRouter()
@router.post("/")
def compare_materials():
    return {}
""",
    "app/api/reports.py": """
from fastapi import APIRouter
router = APIRouter()
@router.post("/")
def generate_report():
    return {}
""",
    "app/orchestration/workflow.py": """
from app.models.search import SearchJob
from sqlalchemy.orm import Session
from app.agents.materials_agent import query_materials_project
import json
import time

def run_workflow(job_id: str, query: str, db_session: Session):
    job = db_session.query(SearchJob).filter(SearchJob.id == job_id).first()
    if not job:
        return
    
    try:
        job.state = {"step": "understanding_requirement", "message": "Parsing query"}
        db_session.commit()
        time.sleep(1)
        
        job.state = {"step": "querying_materials_project", "message": "Fetching from MP"}
        db_session.commit()
        time.sleep(1)
        
        # In a full LangGraph setup, we'd invoke the graph here.
        # For simplicity, we directly call MP
        results = query_materials_project(query)
        
        job.state = {"step": "completed", "results": results}
        job.status = "completed"
        db_session.commit()
    except Exception as e:
        job.status = "failed"
        job.state = {"error": str(e)}
        db_session.commit()
""",
    "app/agents/materials_agent.py": """
import os
import requests

def query_materials_project(query: str):
    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        return {"error": "Missing MP_API_KEY"}
    
    # Mocking real call for now since we'd need mp-api
    return [{"material_id": "mp-149", "formula": "Si", "band_gap": 1.1}]
""",
    ".env.example": """
MP_API_KEY=
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
ENVIRONMENT=development
MAX_AGENT_ITERATIONS=3
DATABASE_URL=sqlite:///./matsearch.db
CORS_ORIGINS=http://localhost:3000
"""
}

for filepath, content in files.items():
    full_path = os.path.join(BASE_DIR, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
