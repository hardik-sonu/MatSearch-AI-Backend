
from app.schemas.agent_state import SearchState


def _get_value(candidate: dict, property_name: str):
    """
    Safely retrieve a SOURCE_VALUE from a candidate.
    """
    property_data = candidate.get(property_name)

    if not isinstance(property_data, dict):
        return None

    return property_data.get("value")


def _evaluate_range(
    value,
    minimum=None,
    maximum=None,
):
    """
    Deterministically evaluate a numerical range.
    """
    if value is None:
        return "UNAVAILABLE"

    if minimum is not None and value < minimum:
        return "FAIL"

    if maximum is not None and value > maximum:
        return "FAIL"

    return "PASS"


def run(state: SearchState) -> SearchState:
    """
    Deterministically evaluate Materials Project candidates.

    No LLM is used here.

    Numerical requirements are evaluated directly against retrieved
    Materials Project values.

    Ambiguous requirements such as:
        "good thermodynamic stability"

    are NOT converted into an invented threshold.

    They are explicitly reported as AMBIGUOUS unless the user has
    supplied a numerical stability criterion.
    """

    if state.get("status") == "failed":
        return state

    candidates = state.get("candidates", [])
    requirements = state.get("requirements", {})
    constraints = requirements.get("constraints", [])

    evaluations = []

    for candidate in candidates:
        material_id = candidate.get("material_id")

        checks = []
        overall_status = "PASS"

        for constraint in constraints:
            property_name = constraint.get("property")
            minimum = constraint.get("min")
            maximum = constraint.get("max")

            # --------------------------------------------
            # Band gap
            # --------------------------------------------
            if property_name == "band_gap":
                value = _get_value(candidate, "band_gap")

                result = _evaluate_range(
                    value,
                    minimum,
                    maximum,
                )

                check = {
                    "property": "band_gap",
                    "result": result,
                    "value": value,
                    "unit": "eV",
                    "min": minimum,
                    "max": maximum,
                    "source_type": "SOURCE_VALUE",
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif result == "UNAVAILABLE" and overall_status == "PASS":
                    overall_status = "INCOMPLETE"

            # --------------------------------------------
            # Density
            # --------------------------------------------
            elif property_name == "density":
                value = _get_value(candidate, "density")

                result = _evaluate_range(
                    value,
                    minimum,
                    maximum,
                )

                check = {
                    "property": "density",
                    "result": result,
                    "value": value,
                    "unit": "g/cm3",
                    "min": minimum,
                    "max": maximum,
                    "source_type": "SOURCE_VALUE",
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif result == "UNAVAILABLE" and overall_status == "PASS":
                    overall_status = "INCOMPLETE"

            # --------------------------------------------
            # Volume
            # --------------------------------------------
            elif property_name == "volume":
                value = _get_value(candidate, "volume")

                result = _evaluate_range(
                    value,
                    minimum,
                    maximum,
                )

                check = {
                    "property": "volume",
                    "result": result,
                    "value": value,
                    "unit": "A^3",
                    "min": minimum,
                    "max": maximum,
                    "source_type": "SOURCE_VALUE",
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif result == "UNAVAILABLE" and overall_status == "PASS":
                    overall_status = "INCOMPLETE"

            # --------------------------------------------
            # Thermodynamic stability
            # --------------------------------------------
            elif property_name in {
                "thermodynamic_stability",
                "stability",
                "energy_above_hull",
            }:
                energy_above_hull = _get_value(
                    candidate,
                    "energy_above_hull",
                )

                # If the user actually supplied a numerical
                # threshold, evaluate it.
                if minimum is not None or maximum is not None:
                    result = _evaluate_range(
                        energy_above_hull,
                        minimum,
                        maximum,
                    )

                    check = {
                        "property": "energy_above_hull",
                        "result": result,
                        "value": energy_above_hull,
                        "unit": "eV/atom",
                        "min": minimum,
                        "max": maximum,
                        "source_type": "SOURCE_VALUE",
                    }

                    checks.append(check)

                    if result == "FAIL":
                        overall_status = "FAIL"

                    elif (
                        result == "UNAVAILABLE"
                        and overall_status == "PASS"
                    ):
                        overall_status = "INCOMPLETE"

                else:
                    # "Good stability" has no universal numerical
                    # threshold supplied by the user.
                    checks.append({
                        "property": "thermodynamic_stability",
                        "result": "AMBIGUOUS",
                        "value": energy_above_hull,
                        "unit": "eV/atom",
                        "min": None,
                        "max": None,
                        "source_type": (
                            "SOURCE_VALUE"
                            if energy_above_hull is not None
                            else "UNAVAILABLE"
                        ),
                        "reason": (
                            "The requirement uses qualitative wording "
                            "'good thermodynamic stability' without "
                            "specifying a numerical criterion. "
                            "No arbitrary threshold was assumed."
                        ),
                    })

                    if overall_status == "PASS":
                        overall_status = "INCOMPLETE"

            # --------------------------------------------
            # Unknown property
            # --------------------------------------------
            else:
                checks.append({
                    "property": property_name,
                    "result": "UNAVAILABLE",
                    "value": None,
                    "unit": constraint.get("unit"),
                    "min": minimum,
                    "max": maximum,
                    "source_type": "UNAVAILABLE",
                    "reason": (
                        "No deterministic evaluator is currently "
                        "implemented for this property."
                    ),
                })

                if overall_status == "PASS":
                    overall_status = "INCOMPLETE"

        # If there were no deterministic constraints at all,
        # the candidate cannot honestly be labelled PASS.
        if not constraints:
            overall_status = "INCOMPLETE"

        evaluations.append({
            "material_id": material_id,
            "result": overall_status,
            "checks": checks,
            "reason": (
                "All supplied numerical constraints passed."
                if overall_status == "PASS"
                else (
                    "One or more deterministic constraints failed."
                    if overall_status == "FAIL"
                    else (
                        "Candidate requires clarification or "
                        "contains unavailable/ambiguous requirements."
                    )
                )
            ),
        })

    return {
        **state,
        "evaluations": evaluations,
        "current_step": "evaluating_candidates",
    }
