# BizScout AI

AI-powered tool that finds local businesses in any niche and analyzes which ones need your services.

## Setup

1. Copy `.env.example` and fill in your keys:
```
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
MONGODB_URL=mongodb://localhost:27017
GOOGLE_MAPS_API_KEY=...
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run:
```bash
uvicorn app.main:app --reload
```

4. Open: http://localhost:8000

## How it works

1. Pick a business niche and location
2. Enter the service you offer
3. AI searches, scrapes, and analyzes each business
4. Get a scored list of opportunities with problems detected and recommended next actions
5. Export results as CSV
