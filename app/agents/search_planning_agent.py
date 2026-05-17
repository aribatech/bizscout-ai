import json
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe

PROMPT = PromptTemplate(
    input_variables=["niche", "location", "service"],
    template="""
Generate 5 different Google search queries to find {niche} businesses in {location}.
The person wants to offer them: {service}

Make queries varied — different angles, not just the same words.
Include at least one query targeting their official website or contact page.

Return a JSON array of 5 strings only. No explanation.

Example:
["restaurants in Lahore website", "Lahore restaurant contact menu", "best restaurants Lahore online ordering", "restaurant Lahore official site", "Lahore restaurant whatsapp order"]
"""
)


async def run_search_planning_agent(niche: str, location: str, service: str) -> list:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = PROMPT | llm
    result = await chain.ainvoke({"niche": niche, "location": location, "service": service})
    return parse_json_safe(result.content)
