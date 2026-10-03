
from app.schemas.agent_state import SearchState
from app.services.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
import json


def _extract_text(content) -> str:
    """
    Convert LangChain/Gemini structured content into plain text.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                text = item.get("text")

                if text:
                    parts.append(str(text))

            elif isinstance(item, str):
                parts.append(item)

        return "\n".join(parts)

    return str(content)


def _clean_json_text(text: str) -> str:
    """
    Remove common Markdown JSON wrappers without modifying
    the actual JSON content.
    """
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    return cleaned


def _validate_requirements(requirements: dict) -> dict:
    """
    Ensure the LLM-produced requirement structure is safe.

    This function does NOT invent constraints.
    Invalid or missing information is represented explicitly.
    """

    if not isinstance(requirements, dict):
        return {
            "application": None,
            "constraints": [],
            "ambiguous_terms": [],
            "parsing_status": "INVALID",
        }

    application = requirements.get("application")

    constraints = requirements.get("constraints")

    if not isinstance(constraints, list):
        constraints = []

    ambiguous_terms = requirements.get("ambiguous_terms")

    if not isinstance(ambiguous_terms, list):
        ambiguous_terms = []

    validated_constraints = []

    for constraint in constraints:
        if not isinstance(constraint, dict):
            continue

        property_name = constraint.get("property")

        if not property_name:
            continue

        validated_constraints.append({
            "property": property_name,
            "operator": constraint.get("operator"),
            "min": constraint.get("min"),
            "max": constraint.get("max"),
            "unit": constraint.get("unit"),
            "priority": constraint.get("priority"),
        })

    return {
        "application": application,
        "constraints": validated_constraints,
        "ambiguous_terms": ambiguous_terms,
        "parsing_status": "VALID",
    }


def run(state: SearchState) -> SearchState:
    """
    Convert the user's natural-language requirement into a
    structured requirement representation.

    The LLM is used only for language interpretation.

    It must NOT invent numerical thresholds when the user
    did not provide them.
    """

    if state.get("status") == "failed":
        return state

    query = state.get("query", "").strip()

    if not query:
        return {
            **state,
            "requirements": {
                "application": None,
                "constraints": [],
                "ambiguous_terms": [],
                "parsing_status": "INVALID",
            },
            "errors": state.get("errors", []) + [
                "Requirement Agent: Empty user requirement."
            ],
            "status": "failed",
        }

    try:
        llm = get_llm()

        prompt = f"""
Convert the following materials engineering requirement into
structured JSON.

Return ONLY valid JSON.

Required schema:

{{
  "application": "string or null",
  "constraints": [
    {{
      "property": "string",
      "operator": "between | >= | <= | > | < | = | qualitative",
      "min": "number or null",
      "max": "number or null",
      "unit": "string or null",
      "priority": "high | medium | low"
    }}
  ],
  "ambiguous_terms": [
    "string"
  ]
}}

Rules:

1. Extract only information explicitly supported by the user's
   requirement.

2. NEVER invent a numerical threshold.

3. If the user says something qualitative such as:
   "good thermodynamic stability",
   "high strength",
   "low cost",
   or "excellent corrosion resistance",
   do NOT invent a numerical threshold.

4. Put qualitative or undefined requirements into
   ambiguous_terms.

5. A qualitative constraint may be represented with:
   "operator": "qualitative"
   and min/max set to null.

6. Preserve the user's intended property terminology.

7. Numerical ranges must use the units stated by the user.
   Do not silently convert or fabricate units.

8. If a property cannot be interpreted confidently,
   put it into ambiguous_terms rather than guessing.

User requirement:

{query}
"""

        response = llm.invoke([
            SystemMessage(
                content=(
                    "You are a scientific materials-engineering "
                    "requirement parser. Never invent numerical "
                    "material constraints."
                )
            ),
            HumanMessage(content=prompt),
        ])

        raw_text = _extract_text(response.content)
        cleaned_text = _clean_json_text(raw_text)

        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            return {
                **state,
                "requirements": {
                    "application": None,
                    "constraints": [],
                    "ambiguous_terms": [],
                    "parsing_status": "INVALID",
                    "raw": raw_text,
                },
                "errors": state.get("errors", []) + [
                    "Requirement Agent: Gemini returned invalid JSON: "
                    f"{str(exc)}"
                ],
                "status": "failed",
                "current_step": "understanding_requirement",
            }

        requirements = _validate_requirements(parsed)

        requirements["raw"] = raw_text

        return {
            **state,
            "requirements": requirements,
            "current_step": "understanding_requirement",
        }

    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [
                f"Requirement Agent Error: {str(e)}"
            ],
            "status": "failed",
        }