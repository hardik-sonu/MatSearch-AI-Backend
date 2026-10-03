
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


def run(state: SearchState) -> SearchState:
    """
    Retrieve real candidate materials from the Materials Project.

    Important:
    - Materials Project is the source of numerical material properties.
    - No material properties are invented here.
    - Ambiguous natural-language requirements are not converted into
      arbitrary numerical thresholds.
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

        # Only use properties that have explicit deterministic
        # numerical constraints.
        search_kwargs = {}

        for constraint in constraints:
            prop = constraint.get("property")

            minimum = constraint.get("min")
            maximum = constraint.get("max")

            if prop == "band_gap":
                if minimum is not None:
                    search_kwargs["band_gap"] = (
                        minimum,
                        maximum if maximum is not None else 1000,
                    )

            elif prop == "density":
                if minimum is not None:
                    search_kwargs["density"] = (
                        minimum,
                        maximum if maximum is not None else 1000,
                    )

            elif prop == "volume":
                if minimum is not None:
                    search_kwargs["volume"] = (
                        minimum,
                        maximum if maximum is not None else 100000,
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
                    getattr(doc, "formation_energy_per_atom", None)
                )

                energy_above_hull_value = _safe_value(
                    getattr(doc, "energy_above_hull", None)
                )

                stability_value = _safe_value(
                    getattr(doc, "is_stable", None)
                )

                crystal_system = getattr(
                    doc,
                    "symmetry",
                    None,
                )

                crystal_system_value = None

                if crystal_system is not None:
                    crystal_system_value = getattr(
                        crystal_system,
                        "crystal_system",
                        None,
                    )

                candidate = {
                    "material_id": material_id,
                    "formula": str(
                        getattr(doc, "formula_pretty", "")
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
