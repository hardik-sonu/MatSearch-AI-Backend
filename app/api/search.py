
import asyncio
import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from app.db.database import SessionLocal, get_db
from app.models.search import SearchJob
from app.orchestration.workflow import run_workflow
from app.schemas.search import SearchRequest, SearchResponse


router = APIRouter()


# =========================================================
# BACKGROUND WORKFLOW
# =========================================================

def run_search_background(
    job_id: str,
    query: str,
):
    """
    Execute a search using an independent database session.

    The HTTP request session must never be reused by the
    background workflow.
    """

    db = SessionLocal()

    try:
        run_workflow(
            job_id=job_id,
            query=query,
            db_session=db,
        )

    except Exception as exc:

        job = (
            db.query(SearchJob)
            .filter(SearchJob.id == job_id)
            .first()
        )

        if job:

            state = dict(
                job.state or {}
            )

            errors = state.get(
                "errors",
                [],
            )

            if not isinstance(errors, list):
                errors = [str(errors)]

            errors.append(
                f"Background workflow error: {str(exc)}"
            )

            state["errors"] = errors
            state["status"] = "failed"
            state["current_step"] = "workflow_error"

            job.state = state
            job.status = "failed"

            db.commit()

    finally:
        db.close()


# =========================================================
# CREATE SEARCH
# =========================================================

@router.post(
    "/",
    response_model=SearchResponse,
)
def create_search(
    req: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a new autonomous materials discovery search.
    """

    query = req.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    job_id = str(uuid.uuid4())

    initial_state = {
        "job_id": job_id,
        "query": query,
        "requirements": {},
        "plan": {},
        "candidates": [],
        "evaluations": [],
        "critic_result": "",
        "iterations": 0,
        "report": "",
        "errors": [],
        "status": "running",
        "current_step": "understanding_requirement",
    }

    job = SearchJob(
        id=job_id,
        query=query,
        status="running",
        state=initial_state,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        run_search_background,
        job_id,
        query,
    )

    return SearchResponse(
        search_id=job_id,
        status="running",
    )


# =========================================================
# GET SEARCH STATE
# =========================================================

@router.get(
    "/{search_id}",
)
def get_search(
    search_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve the latest persisted workflow state.
    """

    job = (
        db.query(SearchJob)
        .filter(SearchJob.id == search_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Search job not found.",
        )

    return {
        "id": job.id,
        "query": job.query,
        "status": job.status,
        "state": job.state or {},
    }


# =========================================================
# SERVER-SENT EVENTS
# =========================================================

@router.get(
    "/{search_id}/events",
)
async def search_events(
    search_id: str,
):
    """
    Stream real persisted workflow state through SSE.

    The endpoint polls SQLite using a fresh SQLAlchemy session
    on every cycle. This prevents stale ORM state and avoids
    holding a request-scoped database connection open.
    """

    # Verify search exists before opening the stream.
    verification_db = SessionLocal()

    try:

        job = (
            verification_db.query(SearchJob)
            .filter(SearchJob.id == search_id)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Search job not found.",
            )

    finally:
        verification_db.close()

    async def event_generator():

        last_payload = None

        while True:

            db = SessionLocal()

            try:

                job = (
                    db.query(SearchJob)
                    .filter(SearchJob.id == search_id)
                    .first()
                )

                if not job:

                    yield {
                        "event": "error",
                        "data": json.dumps(
                            {
                                "search_id": search_id,
                                "error": "Search job not found.",
                            }
                        ),
                    }

                    break

                state = job.state or {}

                payload = {
                    "search_id": job.id,
                    "status": job.status,
                    "query": job.query,
                    "state": state,
                }

                serialized = json.dumps(
                    payload,
                    default=str,
                    sort_keys=True,
                )

                # Only emit a new update when the persisted
                # workflow state actually changed.
                if serialized != last_payload:

                    yield {
                        "event": "agent_update",
                        "data": serialized,
                    }

                    last_payload = serialized

                if job.status in {
                    "completed",
                    "failed",
                }:

                    yield {
                        "event": "complete",
                        "data": serialized,
                    }

                    break

            finally:
                db.close()

            await asyncio.sleep(1)

    return EventSourceResponse(
        event_generator(),
        ping=15,
    )
