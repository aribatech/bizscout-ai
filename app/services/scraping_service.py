import httpx
from bs4 import BeautifulSoup
from app.config import SCRAPE_TIMEOUT
from app.utils.text_cleaner import clean_text, extract_emails, extract_phones, extract_whatsapp

PAGES_TO_TRY = ["", "/about", "/about-us", "/contact", "/services", "/menu", "/booking"]
MAX_CHARS_PER_PAGE = 1000
MAX_TOTAL_CHARS = 4000


async def collect_website_data(base_url: str) -> dict:
    all_text = ""
    found_links = []

    async with httpx.AsyncClient(timeout=SCRAPE_TIMEOUT, follow_redirects=True) as client:
        for path in PAGES_TO_TRY:
            try:
                url = base_url.rstrip("/") + path
                res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code != 200:
                    continue

                soup = BeautifulSoup(res.text, "html.parser")

                if path == "":
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if href.startswith("/") or base_url in href:
                            found_links.append(href)

                for tag in soup(["nav", "footer", "script", "style", "header"]):
                    tag.decompose()

                page_text = soup.get_text(separator=" ", strip=True)
                all_text += " " + page_text[:MAX_CHARS_PER_PAGE]

                if len(all_text) >= MAX_TOTAL_CHARS:
                    break
            except Exception:
                continue

    all_text = clean_text(all_text[:MAX_TOTAL_CHARS])

    return {
        "full_text": all_text,
        "detected_links": list(set(found_links))[:20],
        "detected_emails": extract_emails(all_text),
        "detected_phones": extract_phones(all_text),
        "has_whatsapp_link": extract_whatsapp(all_text)
    }
