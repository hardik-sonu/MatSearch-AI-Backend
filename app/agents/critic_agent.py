
from app.schemas.agent_state import SearchState
import os


def run(state: SearchState) -> SearchState:
    """
    Deterministically validate the quality of the discovery result.

    The critic does not decide that a material is scientifically
    suitable merely because a candidate exists.

    It checks:
    - candidate availability
    - evaluation availability
    - failed candidates
    - incomplete/ambiguous evaluations
    - iteration limits
    """

    if state.get("status") == "failed":
        return state

    iterations = state.get("iterations", 0) + 1

    candidates = state.get("candidates", [])
    evaluations = state.get("evaluations", [])
    requirements = state.get("requirements", {})

    ambiguous_terms = requirements.get(
        "ambiguous_terms",
        [],
    )

    max_iterations = int(
        os.getenv("MAX_AGENT_ITERATIONS", "3")
    )

    # ---------------------------------------------------------
    # No candidates
    # ---------------------------------------------------------

    if len(candidates) == 0:
        if iterations < max_iterations:
            return {
                **state,
                "critic_result": "REVISE",
                "iterations": iterations,
                "current_step": "critic_validation",
            }

        return {
            **state,
            "critic_result": "FAIL",
            "iterations": iterations,
            "errors": state.get("errors", []) + [
                "Critic: No candidates were retrieved after "
                "the maximum allowed search iterations."
            ],
            "current_step": "critic_validation",
        }

    # ---------------------------------------------------------
    # Candidates exist but evaluations are missing
    # ---------------------------------------------------------

    if len(evaluations) == 0:
        return {
            **state,
            "critic_result": "FAIL",
            "iterations": iterations,
            "errors": state.get("errors", []) + [
                "Critic: Candidates were retrieved but no "
                "deterministic evaluations were produced."
            ],
            "current_step": "critic_validation",
        }

    # ---------------------------------------------------------
    # Validate evaluation completeness
    # ---------------------------------------------------------

    failed_count = 0
    incomplete_count = 0
    pass_count = 0

    for evaluation in evaluations:
        result = evaluation.get("result")

        if result == "FAIL":
            failed_count += 1

        elif result == "INCOMPLETE":
            incomplete_count += 1

        elif result == "PASS":
            pass_count += 1

    # ---------------------------------------------------------
    # Ambiguous requirements are not silently considered PASS
    # ---------------------------------------------------------

    if ambiguous_terms:
        return {
            **state,
            "critic_result": "PASS_WITH_AMBIGUITY",
            "iterations": iterations,
            "current_step": "critic_validation",
        }

    # ---------------------------------------------------------
    # All candidates failed
    # ---------------------------------------------------------

    if pass_count == 0:
        if iterations < max_iterations:
            return {
                **state,
                "critic_result": "REVISE",
                "iterations": iterations,
                "current_step": "critic_validation",
            }

        return {
            **state,
            "critic_result": "FAIL",
            "iterations": iterations,
            "current_step": "critic_validation",
        }

    # ---------------------------------------------------------
    # Some evaluations are incomplete
    # ---------------------------------------------------------

    if incomplete_count > 0:
        return {
            **state,
            "critic_result": "PASS_WITH_INCOMPLETE_DATA",
            "iterations": iterations,
            "current_step": "critic_validation",
        }

    # ---------------------------------------------------------
    # Valid deterministic result
    # ---------------------------------------------------------

    return {
        **state,
        "critic_result": "PASS",
        "iterations": iterations,
        "current_step": "critic_validation",
    }
