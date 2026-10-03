from app.schemas.agent_state import SearchState


def _normalize_property_name(property_name):
    """
    Normalize natural-language property names into canonical names.
    """
    if not isinstance(property_name, str):
        return property_name

    normalized = property_name.strip().lower()

    aliases = {
        "band gap": "band_gap",
        "bandgap": "band_gap",
        "band_gap": "band_gap",
        "density": "density",
        "volume": "volume",
        "stability": "stability",
        "thermodynamic stability": "stability",
        "thermodynamic_stability": "stability",
        "energy above hull": "energy_above_hull",
        "energy_above_hull": "energy_above_hull",
    }

    return aliases.get(normalized, normalized)


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
    operator,
    minimum=None,
    maximum=None,
):
    """
    Deterministically evaluate a numerical constraint.

    Supports:
        <
        <=
        >
        >=
        =
        ==
        between
    """

    if value is None:
        return "UNAVAILABLE"

    operator = str(
        operator or ""
    ).strip().lower()

    if operator in {"between", "range"}:
        if minimum is not None and value < minimum:
            return "FAIL"

        if maximum is not None and value > maximum:
            return "FAIL"

        return "PASS"

    if operator in {"<", "lt", "less_than"}:
        if maximum is None:
            return "INCOMPLETE"

        return "PASS" if value < maximum else "FAIL"

    if operator in {
        "<=",
        "le",
        "less_than_or_equal",
    }:
        if maximum is None:
            return "INCOMPLETE"

        return "PASS" if value <= maximum else "FAIL"

    if operator in {">", "gt", "greater_than"}:
        if minimum is None:
            return "INCOMPLETE"

        return "PASS" if value > minimum else "FAIL"

    if operator in {
        ">=",
        "ge",
        "greater_than_or_equal",
    }:
        if minimum is None:
            return "INCOMPLETE"

        return "PASS" if value >= minimum else "FAIL"

    if operator in {
        "=",
        "==",
        "eq",
        "equals",
    }:
        target = (
            minimum
            if minimum is not None
            else maximum
        )

        if target is None:
            return "INCOMPLETE"

        return "PASS" if value == target else "FAIL"

    # Backward-compatible fallback.
    if minimum is not None and value < minimum:
        return "FAIL"

    if maximum is not None and value > maximum:
        return "FAIL"

    return "PASS"


def run(state: SearchState) -> SearchState:
    """
    Deterministically evaluate Materials Project candidates.

    No LLM is used here.

    Numerical requirements are evaluated directly against
    retrieved Materials Project SOURCE_VALUE data.

    Qualitative requirements such as "stable" are not converted
    into arbitrary numerical thresholds.
    """

    if state.get("status") == "failed":
        return state

    candidates = state.get(
        "candidates",
        [],
    )

    requirements = state.get(
        "requirements",
        {},
    )

    constraints = requirements.get(
        "constraints",
        [],
    )

    evaluations = []

    for candidate in candidates:
        material_id = candidate.get(
            "material_id"
        )

        checks = []
        overall_status = "PASS"

        for constraint in constraints:
            raw_property_name = constraint.get(
                "property"
            )

            property_name = _normalize_property_name(
                raw_property_name
            )

            minimum = constraint.get("min")
            maximum = constraint.get("max")
            operator = constraint.get("operator")

            # -------------------------------------------------
            # Band gap
            # -------------------------------------------------
            if property_name == "band_gap":

                value = _get_value(
                    candidate,
                    "band_gap",
                )

                result = _evaluate_range(
                    value=value,
                    operator=operator,
                    minimum=minimum,
                    maximum=maximum,
                )

                check = {
                    "property": "band_gap",
                    "result": result,
                    "value": value,
                    "unit": "eV",
                    "operator": operator,
                    "min": minimum,
                    "max": maximum,
                    "source_type": (
                        "SOURCE_VALUE"
                        if value is not None
                        else "UNAVAILABLE"
                    ),
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif (
                    result == "UNAVAILABLE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

                elif (
                    result == "INCOMPLETE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

            # -------------------------------------------------
            # Density
            # -------------------------------------------------
            elif property_name == "density":

                value = _get_value(
                    candidate,
                    "density",
                )

                result = _evaluate_range(
                    value=value,
                    operator=operator,
                    minimum=minimum,
                    maximum=maximum,
                )

                check = {
                    "property": "density",
                    "result": result,
                    "value": value,
                    "unit": "g/cm3",
                    "operator": operator,
                    "min": minimum,
                    "max": maximum,
                    "source_type": (
                        "SOURCE_VALUE"
                        if value is not None
                        else "UNAVAILABLE"
                    ),
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif (
                    result == "UNAVAILABLE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

                elif (
                    result == "INCOMPLETE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

            # -------------------------------------------------
            # Volume
            # -------------------------------------------------
            elif property_name == "volume":

                value = _get_value(
                    candidate,
                    "volume",
                )

                result = _evaluate_range(
                    value=value,
                    operator=operator,
                    minimum=minimum,
                    maximum=maximum,
                )

                check = {
                    "property": "volume",
                    "result": result,
                    "value": value,
                    "unit": "A^3",
                    "operator": operator,
                    "min": minimum,
                    "max": maximum,
                    "source_type": (
                        "SOURCE_VALUE"
                        if value is not None
                        else "UNAVAILABLE"
                    ),
                }

                checks.append(check)

                if result == "FAIL":
                    overall_status = "FAIL"

                elif (
                    result == "UNAVAILABLE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

                elif (
                    result == "INCOMPLETE"
                    and overall_status == "PASS"
                ):
                    overall_status = "INCOMPLETE"

            # -------------------------------------------------
            # Thermodynamic stability
            # -------------------------------------------------
            elif property_name in {
                "stability",
                "energy_above_hull",
            }:

                energy_above_hull = _get_value(
                    candidate,
                    "energy_above_hull",
                )

                if (
                    minimum is not None
                    or maximum is not None
                ):
                    result = _evaluate_range(
                        value=energy_above_hull,
                        operator=operator,
                        minimum=minimum,
                        maximum=maximum,
                    )

                    check = {
                        "property": "energy_above_hull",
                        "result": result,
                        "value": energy_above_hull,
                        "unit": "eV/atom",
                        "operator": operator,
                        "min": minimum,
                        "max": maximum,
                        "source_type": (
                            "SOURCE_VALUE"
                            if energy_above_hull is not None
                            else "UNAVAILABLE"
                        ),
                    }

                    checks.append(check)

                    if result == "FAIL":
                        overall_status = "FAIL"

                    elif (
                        result in {
                            "UNAVAILABLE",
                            "INCOMPLETE",
                        }
                        and overall_status == "PASS"
                    ):
                        overall_status = "INCOMPLETE"

                else:
                    checks.append({
                        "property": (
                            "thermodynamic_stability"
                        ),
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
                            "The requirement uses qualitative "
                            "stability wording without a "
                            "user-supplied numerical criterion. "
                            "No arbitrary threshold was assumed."
                        ),
                    })

                    if overall_status == "PASS":
                        overall_status = "INCOMPLETE"

            # -------------------------------------------------
            # Unknown property
            # -------------------------------------------------
            else:

                checks.append({
                    "property": raw_property_name,
                    "result": "UNAVAILABLE",
                    "value": None,
                    "unit": constraint.get("unit"),
                    "operator": operator,
                    "min": minimum,
                    "max": maximum,
                    "source_type": "UNAVAILABLE",
                    "reason": (
                        "No deterministic evaluator is "
                        "currently implemented for this property."
                    ),
                })

                if overall_status == "PASS":
                    overall_status = "INCOMPLETE"

        if not constraints:
            overall_status = "INCOMPLETE"

        if overall_status == "PASS":
            reason = (
                "All supplied numerical constraints passed."
            )

        elif overall_status == "FAIL":
            reason = (
                "One or more deterministic constraints failed."
            )

        else:
            reason = (
                "Candidate requires clarification or "
                "contains unavailable/ambiguous requirements."
            )

        evaluations.append({
            "material_id": material_id,
            "result": overall_status,
            "checks": checks,
            "reason": reason,
        })

    return {
        **state,
        "evaluations": evaluations,
        "current_step": "evaluating_candidates",
    }