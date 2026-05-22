from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe
import json

PROMPT = PromptTemplate(
    input_variables=["niche", "location", "service_offered", "business_profile", "problems"],
    template="""
Score this business as a sales opportunity.

Campaign target:
- Niche: {niche}
- Location: {location}
- Service offered: {service_offered}

Business profile:
{business_profile}

Detected problems:
{problems}

Score using this formula (total 100 points):
- Niche match (0-20): Does the business match the target niche?
- Location match (0-15): Is the business in the right location?
- Problem strength (0-30): How serious and numerous are the problems detected?
- Service fit (0-25): How well does the service solve their problems?
- Contact availability (0-10): Can we actually reach them (email/phone/contact page)?

Return a JSON object:
{{
  "opportunity_score": integer 0-100,
  "fit_level": "High" or "Medium" or "Low" or "Not Fit",
  "priority": "High" or "Medium" or "Low",
  "score_breakdown": {{
    "niche_match": int,
    "location_match": int,
    "problem_strength": int,
    "service_fit": int,
    "contact_availability": int
  }},
  "reason": "one sentence explanation"
}}

Fit level guide: 80-100=High, 60-79=Medium, 40-59=Low, 0-39=Not Fit

Return only valid JSON.
"""
)


async def run_opportunity_scoring_agent(
    niche: str, location: str, service_offered: str,
    business_profile: dict, problems: list
) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = PROMPT | llm
    result = await chain.ainvoke({
        "niche": niche,
        "location": location,
        "service_offered": service_offered,
        "business_profile": json.dumps(business_profile, indent=2),
        "problems": json.dumps(problems, indent=2)
    })
    try:
        return parse_json_safe(result.content)
    except Exception:
        return {"opportunity_score": 0, "fit_level": "Not Fit", "priority": "Low", "reason": "Could not score."}
