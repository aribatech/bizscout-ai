import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect

from app.schemas.campaign_schema import CreateCampaignRequest
from app.db.repositories import (
    create_campaign, get_campaign, get_all_campaigns, update_campaign_status
)
from app.services.websocket_service import manager
from app.workers.campaign_worker import run_campaign_workflow

router = APIRouter()


def now():
    return datetime.now(timezone.utc)


@router.post("/campaigns")
async def create_new_campaign(body: CreateCampaignRequest):
    campaign_id = str(uuid.uuid4())
    campaign = {
        "id": campaign_id,
        "business_niche": body.business_niche,
        "location": body.location,
        "service_offered": body.service_offered,
        "target_count": body.target_count,
        "status": "PENDING",
        "created_at": now(),
        "updated_at": now(),
        "completed_at": None
    }
    await create_campaign(campaign)
    return {"campaign_id": campaign_id, "status": "PENDING", "message": "Campaign created successfully."}


@router.post("/campaigns/{campaign_id}/run")
async def run_campaign(campaign_id: str, background_tasks: BackgroundTasks):
    campaign = await get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign["status"] == "RUNNING":
        raise HTTPException(status_code=400, detail="Campaign is already running")

    background_tasks.add_task(run_campaign_workflow, campaign_id)
    return {"campaign_id": campaign_id, "status": "RUNNING", "message": "Agent workflow started."}


@router.get("/campaigns/{campaign_id}")
async def get_campaign_detail(campaign_id: str):
    campaign = await get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/campaigns")
async def list_campaigns():
    return await get_all_campaigns()


@router.websocket("/campaigns/{campaign_id}/stream")
async def campaign_stream(websocket: WebSocket, campaign_id: str):
    await manager.connect(campaign_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(campaign_id, websocket)
