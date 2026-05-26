from fastapi import APIRouter, HTTPException

from app.schemas.campaign_schema import UpdateBusinessStatusRequest, AddNoteRequest
from app.db.repositories import (
    get_businesses_by_campaign, get_business,
    update_business_status, add_business_note
)

router = APIRouter()

VALID_STATUSES = ["New", "Reviewed", "Qualified", "Contacted", "Interested", "Not Fit", "Closed"]


@router.get("/campaigns/{campaign_id}/businesses")
async def list_businesses(campaign_id: str):
    businesses = await get_businesses_by_campaign(campaign_id)
    return businesses


@router.get("/businesses/{business_id}")
async def get_business_detail(business_id: str):
    business = await get_business(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.patch("/businesses/{business_id}/status")
async def update_status(business_id: str, body: UpdateBusinessStatusRequest):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use one of: {VALID_STATUSES}")
    business = await get_business(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    await update_business_status(business_id, body.status)
    return {"business_id": business_id, "status": body.status, "message": "Status updated successfully."}


@router.post("/businesses/{business_id}/notes")
async def add_note(business_id: str, body: AddNoteRequest):
    business = await get_business(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    await add_business_note(business_id, body.note)
    return {"business_id": business_id, "message": "Note added successfully."}
