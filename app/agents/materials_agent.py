from app.schemas.agent_state import SearchState
import os


def _safe_value(value):
    """Convert Materials Project values into JSON-safe Python values."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _normalize_property_name(property_name):
    """
    Normalize natural-language property names into the canonical names
    used internally by MatSearch AI.
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


def _build_range(constraint):
    """
    Convert a parsed constraint into a Materials Project range.

    Materials Project supports tuple ranges such as:
        (minimum, maximum)
    with None allowed for an open side.
    """
    operator = str(constraint.get("operator", "")).strip().lower()

    minimum = constraint.get("min")
    maximum = constraint.get("max")

    if operator in {"between", "range"}:
        return (minimum, maximum)

    if operator in {"<", "lt", "less_than"}:
        return (None, maximum)

    if operator in {"<=", "le", "less_than_or_equal"}:
        return (None, maximum)

    if operator in {">", "gt", "greater_than"}:
        return (minimum, None)

    if operator in {">=", "ge", "greater_than_or_equal"}:
        return (minimum, None)

    if operator in {"=", "==", "eq", "equals"}:
        return (minimum, maximum if maximum is not None else minimum)

    # Safe fallback for a numerical min/max constraint.
    return (minimum, maximum)


def run(state: SearchState) -> SearchState:
    """
    Retrieve real candidate materials from the Materials Project.

    Materials Project is the source of numerical material properties.
    No material properties are invented here.
    """

    if state.get("status") == "failed":
        return state

    api_key = os.getenv("MP_API_KEY")

    if not api_key:
        return {
            **state,
            "errors": state.get("errors", []) + [
                "MP_API_KEY not found."
            ],
            "status": "failed",
        }

    try:
        from mp_api.client import MPRester

        requirements = state.get("requirements", {})
        constraints = requirements.get("constraints", [])

        search_kwargs = {}

        for constraint in constraints:
            prop = _normalize_property_name(
                constraint.get("property")
            )

            minimum = constraint.get("min")
            maximum = constraint.get("max")

            # Only numerical constraints should be sent to
            # Materials Project as property filters.
            if prop in {"band_gap", "density", "volume"}:
                if (
                    minimum is not None
                    or maximum is not None
                ):
                    search_kwargs[prop] = _build_range(
                        constraint
                    )

        candidates = []

        with MPRester(api_key) as mpr:
            docs = mpr.materials.summary.search(
                **search_kwargs,
                num_chunks=1,
                chunk_size=10,
            )

            for doc in docs:
                material_id = str(doc.material_id)

                density_value = _safe_value(
                    getattr(doc, "density", None)
                )

                band_gap_value = _safe_value(
                    getattr(doc, "band_gap", None)
                )

                formation_energy_value = _safe_value(
                    getattr(
                        doc,
                        "formation_energy_per_atom",
                        None,
                    )
                )

                energy_above_hull_value = _safe_value(
                    getattr(
                        doc,
                        "energy_above_hull",
                        None,
                    )
                )

                stability_value = _safe_value(
                    getattr(doc, "is_stable", None)
                )

                symmetry = getattr(
                    doc,
                    "symmetry",
                    None,
                )

                crystal_system_value = None

                if symmetry is not None:
                    crystal_system_value = getattr(
                        symmetry,
                        "crystal_system",
                        None,
                    )

                    if hasattr(
                        crystal_system_value,
                        "value",
                    ):
                        crystal_system_value = (
                            crystal_system_value.value
                        )

                    elif crystal_system_value is not None:
                        crystal_system_value = str(
                            crystal_system_value
                        )

                candidate = {
                    "material_id": material_id,

                    "formula": str(
                        getattr(
                            doc,
                            "formula_pretty",
                            "",
                        )
                    ),

                    "density": {
                        "value": density_value,
                        "unit": "g/cm3",
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },

                    "band_gap": {
                        "value": band_gap_value,
                        "unit": "eV",
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },

                    "formation_energy_per_atom": {
                        "value": formation_energy_value,
                        "unit": "eV/atom",
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },

                    "energy_above_hull": {
                        "value": energy_above_hull_value,
                        "unit": "eV/atom",
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },

                    "is_stable": {
                        "value": stability_value,
                        "unit": None,
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },

                    "crystal_system": {
                        "value": crystal_system_value,
                        "unit": None,
                        "source": "Materials Project",
                        "source_type": "SOURCE_VALUE",
                    },
                }

                candidates.append(candidate)

        return {
            **state,
            "candidates": candidates,
            "current_step": "querying_materials_project",
        }

    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [
                f"Materials Agent Error: {str(e)}"
            ],
            "status": "failed",
        }