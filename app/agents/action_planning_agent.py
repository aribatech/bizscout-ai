from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe
import json

PROMPT = PromptTemplate(
    input_variables=["opportunity_score", "fit_level", "problems", "recommended_service"],
    template="""
Create a practical next action for following up with this business opportunity.

Opportunity score: {opportunity_score}/100
Fit level: {fit_level}
Recommended service: {recommended_service}
Detected problems: {problems}

Decide the best next step and suggest an initial status.

Return a JSON object:
{{
  "next_action": "what to do next — specific and practical",
  "action_reason": "why this action makes sense given the score and problems",
  "suggested_status": one of ["Qualified", "Reviewed", "Not Fit"],
  "follow_up_priority": "High" or "Medium" or "Low"
}}

Rules:
- Score 70+: suggest "Qualified" and high priority
- Score 50-69: suggest "Reviewed" and medium priority
- Score below 50: suggest "Not Fit" or "Reviewed" with low priority

Return only valid JSON.
"""
)


async def run_action_planning_agent(
    opportunity_score: int, fit_level: str, problems: list, recommended_service: str
) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = PROMPT | llm
    result = await chain.ainvoke({
        "opportunity_score": opportunity_score,
        "fit_level": fit_level,
        "problems": json.dumps(problems, indent=2),
        "recommended_service": recommended_service
    })
    try:
        return parse_json_safe(result.content)
    except Exception:
        return {
            "next_action": "Review business manually.",
            "action_reason": "Could not plan automatically.",
            "suggested_status": "Reviewed",
            "follow_up_priority": "Low"
        }
