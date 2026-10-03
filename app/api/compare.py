import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mp_api.client import MPRester

router = APIRouter()


class CompareRequest(BaseModel):
    material_ids: List[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Materials Project material IDs to compare.",
    )


def serialize_material(doc):
    symmetry = getattr(doc, "symmetry", None)
    crystal_system = None

    if symmetry is not None:
        crystal_system = getattr(
            symmetry,
            "crystal_system",
            None,
        )

    return {
        "material_id": getattr(doc, "material_id", None),
        "formula": getattr(doc, "formula_pretty", None),
        "density": getattr(doc, "density", None),
        "volume": getattr(doc, "volume", None),
        "band_gap": getattr(doc, "band_gap", None),
        "formation_energy_per_atom": getattr(
            doc,
            "formation_energy_per_atom",
            None,
        ),
        "energy_above_hull": getattr(
            doc,
            "energy_above_hull",
            None,
        ),
        "is_stable": getattr(
            doc,
            "is_stable",
            None,
        ),
        "crystal_system": crystal_system,
        "provenance": {
            "source": "Materials Project",
            "values": "SOURCE_VALUE",
        },
    }


@router.post("/")
def compare_materials(req: CompareRequest):
    """
    Compare multiple real Materials Project materials.
    """
    api_key = os.getenv("MP_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="MP_API_KEY is not configured.",
        )

    material_ids = [
        material_id.strip()
        for material_id in req.material_ids
        if material_id.strip()
    ]

    if len(material_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two valid material IDs are required.",
        )

    try:
        with MPRester(api_key) as mpr:
            docs = mpr.materials.summary.search(
                material_ids=material_ids,
                num_chunks=1,
                chunk_size=len(material_ids),
            )

        found_ids = {
            str(getattr(doc, "material_id", ""))
            for doc in docs
        }

        missing_ids = [
            material_id
            for material_id in material_ids
            if material_id not in found_ids
        ]

        materials = [
            serialize_material(doc)
            for doc in docs
        ]

        return {
            "status": "success",
            "source": "Materials Project",
            "requested_materials": material_ids,
            "returned_count": len(materials),
            "missing_materials": missing_ids,
            "materials": materials,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Materials Project comparison failed: {str(exc)}",
        ) from exc
