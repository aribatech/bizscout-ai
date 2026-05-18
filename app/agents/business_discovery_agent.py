from app.services.search_service import run_search
from app.utils.url_utils import get_domain, is_valid_business_url, normalize_url


async def run_business_discovery_agent(queries: list, target_count: int) -> list:
    seen_domains = set()
    businesses = []

    for query in queries:
        try:
            results = await run_search(query, num=10)
            for r in results:
                url = r.get("url", "")
                if not is_valid_business_url(url):
                    continue

                domain = get_domain(url)
                if domain in seen_domains:
                    continue

                seen_domains.add(domain)
                businesses.append({
                    "name": r.get("title", "").split(" - ")[0].split(" | ")[0].strip(),
                    "website": normalize_url(url),
                    "source_url": url,
                    "snippet": r.get("snippet", "")
                })

                if len(businesses) >= target_count:
                    break

        except Exception as e:
            print(f"[discovery] search failed for query '{query}': {e}")

        if len(businesses) >= target_count:
            break

    return businesses[:target_count]
