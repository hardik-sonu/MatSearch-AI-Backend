
from app.schemas.agent_state import SearchState


def run(state: SearchState) -> SearchState:
    """
    Build a deterministic research plan from the parsed
    requirements.

    The planner does not invent scientific thresholds.
    """

    if state.get("status") == "failed":
        return state

    requirements = state.get("requirements", {})

    constraints = requirements.get("constraints", [])
    ambiguous_terms = requirements.get("ambiguous_terms", [])

    steps = [
        "Parse user requirements",
        "Identify explicit numerical constraints",
    ]

    if constraints:
        steps.append(
            "Query Materials Project using supported deterministic constraints"
        )
    else:
        steps.append(
            "Determine whether the requirement contains searchable constraints"
        )

    steps.append(
        "Retrieve source material properties from Materials Project"
    )

    steps.append(
        "Evaluate candidates using deterministic engineering checks"
    )

    if ambiguous_terms:
        steps.append(
            "Flag ambiguous qualitative requirements without inventing thresholds"
        )

    steps.append(
        "Critically validate candidate results and evidence"
    )

    steps.append(
        "Generate evidence-based engineering report"
    )

    plan = {
        "steps": steps,
        "explicit_constraints": constraints,
        "ambiguous_requirements": ambiguous_terms,
        "planning_status": (
            "REQUIRES_CLARIFICATION"
            if ambiguous_terms
            else "READY_FOR_SEARCH"
        ),
    }

    return {
        **state,
        "plan": plan,
        "current_step": "planning_research",
    }
