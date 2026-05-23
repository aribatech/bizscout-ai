from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe
import json

PROMPT = PromptTemplate(
    input_variables=["service_offered", "business_profile", "problems"],
    template="""
Based on the business's detected problems, recommend the most suitable specific service to offer.

Service provider offers: {service_offered}

Business profile:
{business_profile}

Detected problems:
{problems}

Recommend the most relevant part of the service for this specific business.

Return a JSON object:
{{
  "recommended_service": "specific service name",
  "why_this_service": "one sentence — why this service fits their situation",
  "expected_business_value": [
    "benefit 1",
    "benefit 2",
    "benefit 3"
  ]
}}

Return only valid JSON.
"""
)


async def run_service_recommendation_agent(
    service_offered: str, business_profile: dict, problems: list
) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = PROMPT | llm
    result = await chain.ainvoke({
        "service_offered": service_offered,
        "business_profile": json.dumps(business_profile, indent=2),
        "problems": json.dumps(problems, indent=2)
    })
    try:
        return parse_json_safe(result.content)
    except Exception:
        return {
            "recommended_service": service_offered,
            "why_this_service": "Matches detected problems.",
            "expected_business_value": []
        }
