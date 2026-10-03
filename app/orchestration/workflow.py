
from enum import Enum

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents import (
    critic_agent,
    evaluator_agent,
    materials_agent,
    planner_agent,
    report_agent,
    requirement_agent,
)
from app.models.search import SearchJob
from app.schemas.agent_state import SearchState


# ---------------------------------------------------------
# JSON SERIALIZATION SAFETY
# ---------------------------------------------------------

def _json_safe(value):
    """
    Convert enums and nested values into JSON-serializable
    Python primitives before persisting workflow state
    to SQLite JSON columns.

    Materials Project may return enum values such as
    CrystalSystem.CUBIC. SQLite JSON cannot serialize
    those enum objects directly.
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {
            key: _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _json_safe(item)
            for item in value
        ]

    return value


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def should_continue_after_critic(state: SearchState):
    """
    Decide what happens after critic validation.

    REVISE:
        Return to planner and perform another search iteration.

    PASS:
        Generate final report.

    FAIL:
        Stop workflow.
    """

    if state.get("status") == "failed":
        return END

    critic_result = state.get(
        "critic_result",
        "",
    )

    if critic_result == "REVISE":
        return "planner"

    if critic_result == "FAIL":
        return END

    if critic_result in {
        "PASS",
        "PASS_WITH_AMBIGUITY",
        "PASS_WITH_INCOMPLETE_DATA",
    }:
        return "report"

    # Unknown critic state should never silently produce
    # a potentially misleading report.
    return END


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

workflow = StateGraph(SearchState)


workflow.add_node(
    "requirement",
    requirement_agent.run,
)

workflow.add_node(
    "planner",
    planner_agent.run,
)

workflow.add_node(
    "materials",
    materials_agent.run,
)

workflow.add_node(
    "evaluator",
    evaluator_agent.run,
)

workflow.add_node(
    "critic",
    critic_agent.run,
)

workflow.add_node(
    "report",
    report_agent.run,
)


workflow.set_entry_point("requirement")


workflow.add_edge(
    "requirement",
    "planner",
)

workflow.add_edge(
    "planner",
    "materials",
)

workflow.add_edge(
    "materials",
    "evaluator",
)

workflow.add_edge(
    "evaluator",
    "critic",
)


workflow.add_conditional_edges(
    "critic",
    should_continue_after_critic,
    {
        "planner": "planner",
        "report": "report",
        END: END,
    },
)


workflow.add_edge(
    "report",
    END,
)


app_graph = workflow.compile()


# ---------------------------------------------------------
# WORKFLOW EXECUTION
# ---------------------------------------------------------

def run_workflow(
    job_id: str,
    query: str,
    db_session: Session,
):
    """
    Execute the complete MatSearch AI workflow.

    Each completed graph node is persisted to SQLite.

    This allows the API/SSE layer to observe the real agent
    progression without inventing frontend events.
    """

    job = (
        db_session.query(SearchJob)
        .filter(SearchJob.id == job_id)
        .first()
    )

    if not job:
        return

    initial_state: SearchState = {
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

    # Preserve an already-created initial state if present.
    if job.state:
        existing_state = dict(job.state)

        for key, value in initial_state.items():
            existing_state.setdefault(
                key,
                value,
            )

        initial_state = existing_state

    try:

        for output in app_graph.stream(initial_state):

            if not output:
                continue

            for node_name, state in output.items():

                if state is None:
                    continue

                state = dict(state)

                # Ensure workflow metadata is always present.
                state["job_id"] = job_id
                state["query"] = query

                # -------------------------------------------------
                # IMPORTANT:
                # Convert Materials Project enums and any nested
                # enum values before writing to SQLite JSON.
                # -------------------------------------------------

                safe_state = _json_safe(state)

                # Persist the latest state.
                job.state = safe_state

                workflow_status = safe_state.get(
                    "status",
                    "running",
                )

                job.status = workflow_status

                db_session.commit()

    except Exception as exc:

        current_state = dict(
            job.state or initial_state
        )

        # Make the existing state JSON-safe before manipulating it.
        current_state = _json_safe(current_state)

        errors = current_state.get(
            "errors",
            [],
        )

        if not isinstance(errors, list):
            errors = [str(errors)]

        errors.append(
            f"Workflow Orchestration Error: {str(exc)}"
        )

        current_state["errors"] = errors
        current_state["status"] = "failed"
        current_state["current_step"] = "workflow_error"

        job.state = _json_safe(current_state)
        job.status = "failed"

        db_session.commit()
