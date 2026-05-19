from app.services.scraping_service import collect_website_data


async def run_website_collection_agent(website: str) -> dict:
    try:
        data = await collect_website_data(website)
        return data
    except Exception as e:
        print(f"[website_collection] failed for {website}: {e}")
        return {
            "full_text": "",
            "detected_links": [],
            "detected_emails": [],
            "detected_phones": [],
            "has_whatsapp_link": False
        }
