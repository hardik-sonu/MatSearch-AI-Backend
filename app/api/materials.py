
import os

from fastapi import APIRouter, HTTPException
from mp_api.client import MPRester


router = APIRouter()


def _get_crystal_system(doc):
    """Safely extract crystal system from Materials Project symmetry data."""

    symmetry = getattr(doc, "symmetry", None)

    if symmetry is None:
        return None

    return getattr(symmetry, "crystal_system", None)


def _serialize_material(doc):
    """Convert a Materials Project SummaryDoc into a JSON-safe dictionary."""

    material_id = getattr(doc, "material_id", None)

    return {
        "material_id": str(material_id) if material_id is not None else None,

        "formula": getattr(
            doc,
            "formula_pretty",
            None,
        ),

        "density": {
            "value": getattr(
                doc,
                "density",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "volume": {
            "value": getattr(
                doc,
                "volume",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "band_gap": {
            "value": getattr(
                doc,
                "band_gap",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "formation_energy_per_atom": {
            "value": getattr(
                doc,
                "formation_energy_per_atom",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "energy_above_hull": {
            "value": getattr(
                doc,
                "energy_above_hull",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "is_stable": {
            "value": getattr(
                doc,
                "is_stable",
                None,
            ),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },

        "crystal_system": {
            "value": _get_crystal_system(doc),
            "provenance": "SOURCE_VALUE",
            "source": "Materials Project",
        },
    }


@router.get("/{material_id}")
def get_material(material_id: str):
    """
    Retrieve one real material from Materials Project.
    """

    api_key = os.getenv("MP_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="MP_API_KEY is not configured.",
        )

    material_id = material_id.strip()

    if not material_id:
        raise HTTPException(
            status_code=400,
            detail="Material ID cannot be empty.",
        )

    try:
        with MPRester(api_key) as mpr:
            docs = mpr.materials.summary.search(
                material_ids=[material_id],
                num_chunks=1,
                chunk_size=1,
            )

        if not docs:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Material '{material_id}' was not found "
                    "in Materials Project."
                ),
            )

        material = _serialize_material(docs[0])

        return {
            "status": "success",
            "source": "Materials Project",
            "material": material,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Materials Project request failed: "
                f"{str(exc)}"
            ),
        )
