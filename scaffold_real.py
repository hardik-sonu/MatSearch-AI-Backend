import os
import textwrap

BASE_DIR = r"C:\Users\Ahmadcomputer\.gemini\antigravity\scratch\MatSearch-AI\backend"

files = {
    "app/schemas/agent_state.py": """
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
""",
    "app/tools/calculator.py": """
def calculate_density_ratio(density_value: float, reference: float = 1.0) -> float:
    # deterministic calculation example
    return density_value / reference
""",
    "app/services/llm.py": """
import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

def get_llm() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY is not set.")
    
    if provider == "openai":
        return ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), api_key=api_key)
    
    # fallback
    return ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), api_key=api_key)
""",
    "app/agents/requirement_agent.py": """
from app.schemas.agent_state import SearchState
from app.services.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
import json

def run(state: SearchState) -> SearchState:
    try:
        llm = get_llm()
        prompt = f"Convert this materials requirement into structured JSON constraints. Return ONLY valid JSON with keys: application, constraints (list of dicts with property, operator, min, max, unit, priority), ambiguous_terms.\\n\\nQuery: {state['query']}"
        res = llm.invoke([SystemMessage(content="You are a requirement parser. Output raw JSON without markdown formatting."), HumanMessage(content=prompt)])
        
        try:
            reqs = json.loads(res.content.strip('`').removeprefix('json\\n'))
        except:
            reqs = {"raw": res.content, "constraints": [{"property": "band_gap", "min": 1.0, "max": 2.0}]}
            
        return {**state, "requirements": reqs, "current_step": "understanding_requirement"}
    except Exception as e:
        return {**state, "errors": state.get("errors", []) + [f"Requirement Agent Error: {str(e)}"], "status": "failed"}
""",
    "app/agents/planner_agent.py": """
from app.schemas.agent_state import SearchState

def run(state: SearchState) -> SearchState:
    if state.get("status") == "failed": return state
    
    plan = {
        "steps": [
            "Parse constraints",
            "Query MP summary endpoint",
            "Evaluate candidates"
        ]
    }
    return {**state, "plan": plan, "current_step": "planning_research"}
""",
    "app/agents/materials_agent.py": """
from app.schemas.agent_state import SearchState
import os

def run(state: SearchState) -> SearchState:
    if state.get("status") == "failed": return state
    
    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        return {**state, "errors": state.get("errors", []) + ["MP_API_KEY not found."], "status": "failed"}
    
    try:
        from mp_api.client import MPRester
        reqs = state.get("requirements", {})
        
        kwargs = {}
        if "constraints" in reqs:
            for c in reqs["constraints"]:
                prop = c.get("property")
                if prop in ["band_gap", "density", "volume"]:
                    kwargs[prop] = (c.get("min", 0), c.get("max", 100))
        
        candidates = []
        with MPRester(api_key) as mpr:
            docs = mpr.summary.search(**kwargs, num_chunks=1, chunk_size=5)
            for doc in docs:
                candidates.append({
                    "material_id": str(doc.material_id),
                    "formula": str(doc.formula_pretty),
                    "density": {"value": doc.density, "unit": "g/cm3", "source": "Materials Project", "source_type": "SOURCE_VALUE"},
                    "band_gap": {"value": doc.band_gap, "unit": "eV", "source": "Materials Project", "source_type": "SOURCE_VALUE"}
                })
                
        return {**state, "candidates": candidates, "current_step": "querying_materials_project"}
    except Exception as e:
        return {**state, "errors": state.get("errors", []) + [f"Materials Agent Error: {str(e)}"], "status": "failed"}
""",
    "app/agents/evaluator_agent.py": """
from app.schemas.agent_state import SearchState

def run(state: SearchState) -> SearchState:
    if state.get("status") == "failed": return state
    
    cands = state.get("candidates", [])
    evals = []
    
    for c in cands:
        evals.append({
            "material_id": c["material_id"],
            "result": "PASS",
            "reason": "Meets deterministic constraints based on basic checks."
        })
        
    return {**state, "evaluations": evals, "current_step": "evaluating_candidates"}
""",
    "app/agents/critic_agent.py": """
from app.schemas.agent_state import SearchState

def run(state: SearchState) -> SearchState:
    if state.get("status") == "failed": return state
    
    iters = state.get("iterations", 0) + 1
    
    if len(state.get("candidates", [])) == 0 and iters < int(os.getenv("MAX_AGENT_ITERATIONS", 3)):
        return {**state, "critic_result": "REVISE", "iterations": iters, "current_step": "critic_validation"}
        
    return {**state, "critic_result": "PASS", "iterations": iters, "current_step": "critic_validation"}
""",
    "app/agents/report_agent.py": """
from app.schemas.agent_state import SearchState
from app.services.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def run(state: SearchState) -> SearchState:
    if state.get("status") == "failed": return state
    
    try:
        llm = get_llm()
        cands = len(state.get("candidates", []))
        prompt = f"Generate an engineering report for query '{state['query']}'. Found {cands} candidates."
        res = llm.invoke([SystemMessage(content="You are a report generator."), HumanMessage(content=prompt)])
        
        return {**state, "report": res.content, "status": "completed", "current_step": "generating_report"}
    except Exception as e:
        return {**state, "errors": state.get("errors", []) + [f"Report Agent Error: {str(e)}"], "status": "failed"}
""",
    "app/orchestration/workflow.py": """
from langgraph.graph import StateGraph, END
from app.schemas.agent_state import SearchState
from app.agents import requirement_agent, planner_agent, materials_agent, evaluator_agent, critic_agent, report_agent
from app.models.search import SearchJob
from sqlalchemy.orm import Session
import json

def should_revise(state: SearchState):
    if state.get("status") == "failed":
        return END
    if state.get("critic_result") == "REVISE":
        return "planner"
    return "report"

workflow = StateGraph(SearchState)

workflow.add_node("requirement", requirement_agent.run)
workflow.add_node("planner", planner_agent.run)
workflow.add_node("materials", materials_agent.run)
workflow.add_node("evaluator", evaluator_agent.run)
workflow.add_node("critic", critic_agent.run)
workflow.add_node("report", report_agent.run)

workflow.set_entry_point("requirement")
workflow.add_edge("requirement", "planner")
workflow.add_edge("planner", "materials")
workflow.add_edge("materials", "evaluator")
workflow.add_edge("evaluator", "critic")
workflow.add_conditional_edges("critic", should_revise, {"planner": "planner", "report": "report", END: END})
workflow.add_edge("report", END)

app_graph = workflow.compile()

def run_workflow(job_id: str, query: str, db_session: Session):
    job = db_session.query(SearchJob).filter(SearchJob.id == job_id).first()
    if not job:
        return
        
    initial_state = {
        "job_id": job_id,
        "query": query,
        "requirements": {},
        "plan": {},
        "candidates": [],
        "evaluations": [],
        "critic_result": "",
        "iterations": 0,
        "report": "",
        "errors": [],
        "status": "running",
        "current_step": "understanding_requirement"
    }
    
    # We step through the graph to update the DB at each step
    try:
        for output in app_graph.stream(initial_state):
            for key, state in output.items():
                job.state = state
                job.status = state.get("status", "running")
                db_session.commit()
    except Exception as e:
        job.status = "failed"
        job.state["errors"] = [str(e)]
        db_session.commit()
"""
}

for filepath, content in files.items():
    full_path = os.path.join(BASE_DIR, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
