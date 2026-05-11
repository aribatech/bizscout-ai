from datetime import datetime, timezone
from app.db.connection import get_db


def now():
    return datetime.now(timezone.utc)


async def create_campaign(data: dict) -> str:
    db = get_db()
    await db["campaigns"].insert_one(data)
    return data["id"]


async def get_campaign(campaign_id: str) -> dict | None:
    db = get_db()
    return await db["campaigns"].find_one({"id": campaign_id}, {"_id": 0})


async def get_all_campaigns() -> list:
    db = get_db()
    cursor = db["campaigns"].find({}, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(length=100)


async def update_campaign_status(campaign_id: str, status: str, extra: dict = None):
    db = get_db()
    update = {"status": status, "updated_at": now()}
    if extra:
        update.update(extra)
    await db["campaigns"].update_one({"id": campaign_id}, {"$set": update})


async def create_business(data: dict):
    db = get_db()
    await db["businesses"].insert_one(data)


async def get_businesses_by_campaign(campaign_id: str) -> list:
    db = get_db()
    cursor = db["businesses"].find({"campaign_id": campaign_id}, {"_id": 0}).sort("opportunity_score", -1)
    return await cursor.to_list(length=100)


async def get_business(business_id: str) -> dict | None:
    db = get_db()
    return await db["businesses"].find_one({"id": business_id}, {"_id": 0})


async def update_business_status(business_id: str, status: str):
    db = get_db()
    await db["businesses"].update_one(
        {"id": business_id},
        {"$set": {"status": status, "updated_at": now()}}
    )


async def add_business_note(business_id: str, note: str):
    db = get_db()
    await db["businesses"].update_one(
        {"id": business_id},
        {
            "$push": {"notes": {"text": note, "created_at": now()}},
            "$set": {"updated_at": now()}
        }
    )


