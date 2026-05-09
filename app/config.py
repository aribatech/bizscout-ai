import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MAX_BUSINESSES = int(os.getenv("MAX_BUSINESSES_PER_CAMPAIGN", "20"))
SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT_SECONDS", "10"))

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

SERPER_URL = "https://google.serper.dev/search"
DB_NAME = "bizscout"
