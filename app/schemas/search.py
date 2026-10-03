from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    search_id: str
    status: str

class MaterialDetail(BaseModel):
    material_id: str
    formula: str
    density: Optional[float] = None
    band_gap: Optional[float] = None
    source: str = "Materials Project"