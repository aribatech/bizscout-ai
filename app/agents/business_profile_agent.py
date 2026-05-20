from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.text_cleaner import parse_json_safe

PROMPT = PromptTemplate(
    input_variables=["website", "full_text"],
    template="""
Analyze this business website content and create a structured profile.

Website: {website}
Content: {full_text}

Return a JSON object with these keys:
- "business_name": official name of the business
- "category": business type (e.g. Restaurant, Clinic, Gym, School, Salon)
- "location": city/area if mentioned (or null)
- "summary": what this business does in 1-2 sentences
- "detected_services": list of services they already offer (e.g. ["Dine-in", "Takeaway"])
- "has_website": true (since we are analyzing it)
- "has_contact_page": true/false — is there a contact page/form?
- "has_menu_page": true/false — for restaurants/cafes only, else false
- "has_online_ordering": true/false — can customers order online?
- "has_booking_system": true/false — can customers book appointments?
- "has_whatsapp_cta": true/false — is there a WhatsApp button/link?
- "has_social_links": true/false — are social media links visible?
- "has_contact_form": true/false — is there a contact form?

Return only valid JSON.
"""
)


async def run_business_profile_agent(website: str, full_text: str) -> dict:
    if not full_text or len(full_text) < 50:
        return {"business_name": None, "summary": None, "has_website": True}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = PROMPT | llm
    result = await chain.ainvoke({"website": website, "full_text": full_text[:3000]})
    try:
        return parse_json_safe(result.content)
    except Exception:
        return {"business_name": None, "summary": None, "has_website": True}
