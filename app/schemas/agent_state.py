from typing import TypedDict, List, Dict, Any, Optional
import operator
from typing_extensions import Annotated

class SearchState(TypedDict):
    job_id: str
    query: str
    requirements: Dict[str, Any]
    plan: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    evaluations: List[Dict[str, Any]]
    critic_result: str
    iterations: int
    report: str
    errors: List[str]
    status: str
    current_step: str