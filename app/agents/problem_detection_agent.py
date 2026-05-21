from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe
import json

PROMPT = PromptTemplate(
    input_variables=["service_offered", "business_profile", "full_text"],
    template="""
You are analyzing a business to find digital problems that the service provider can solve.

Service the provider offers: {service_offered}

Business profile:
{business_profile}

Additional website content:
{full_text}

Detect problems this business has that are relevant to the service offered.
Think about what features or digital capabilities they are MISSING.

Return a JSON object:
{{
  "problems": [
    {{
      "problem": "short problem name",
      "severity": "high" or "medium" or "low",
      "evidence": "what you saw on the website that proves this problem"
    }}
  ]
}}

Return only valid JSON. List 3 to 8 problems.
"""
)


async def run_problem_detection_agent(service_offered: str, business_profile: dict, full_text: str) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = PROMPT | llm
    result = await chain.ainvoke({
        "service_offered": service_offered,
        "business_profile": json.dumps(business_profile, indent=2),
        "full_text": full_text[:2000]
    })
    try:
        return parse_json_safe(result.content)
    except Exception:
        return {"problems": []}
