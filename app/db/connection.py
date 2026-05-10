from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL, DB_NAME

_client = None
_db = None


def get_db():
    return _db


async def connect_db():
    global _client, _db
    _client = AsyncIOMotorClient(MONGODB_URL)
    _db = _client[DB_NAME]
    print("MongoDB connected")


async def close_db():
    global _client
    if _client:
        _client.close()
        print("MongoDB disconnected")
