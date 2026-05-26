import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.db.repositories import get_campaign, get_businesses_by_campaign
from app.services.export_service import businesses_to_csv

router = APIRouter()


@router.get("/campaigns/{campaign_id}/export")
async def export_csv(campaign_id: str):
    campaign = await get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    businesses = await get_businesses_by_campaign(campaign_id)
    if not businesses:
        raise HTTPException(status_code=404, detail="No businesses found for this campaign")

    csv_content = businesses_to_csv(campaign, businesses)
    filename = f"bizscout_{campaign_id[:8]}.csv"

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
