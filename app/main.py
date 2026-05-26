from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.connection import connect_db, close_db
from app.api.campaigns import router as campaigns_router
from app.api.businesses import router as businesses_router
from app.api.exports import router as exports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="BizScout AI",
    description="AI-powered business opportunity analyzer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns_router)
app.include_router(businesses_router)
app.include_router(exports_router)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/config")
async def get_config():
    from app.config import GOOGLE_MAPS_API_KEY
    return {"google_maps_key": GOOGLE_MAPS_API_KEY}


@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}
