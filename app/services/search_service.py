import httpx
from app.config import SERPER_API_KEY, SERPER_URL


async def run_search(query: str, num: int = 10) -> list:
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num}

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(SERPER_URL, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

    results = []
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", "")
        })
    return results
