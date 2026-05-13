from urllib.parse import urlparse

SKIP_DOMAINS = [
    "linkedin.com", "facebook.com", "instagram.com", "twitter.com",
    "youtube.com", "wikipedia.org", "reddit.com", "indeed.com",
    "glassdoor.com", "yelp.com", "tripadvisor.com", "google.com",
    "maps.google.com", "trustpilot.com"
]


def get_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "").lower()


def is_valid_business_url(url: str) -> bool:
    if not url or not url.startswith("http"):
        return False
    domain = get_domain(url)
    return not any(skip in domain for skip in SKIP_DOMAINS)


def normalize_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url
    return url
