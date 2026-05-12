from pydantic import BaseModel


class CreateCampaignRequest(BaseModel):
    business_niche: str
    location: str
    service_offered: str
    target_count: int = 10


class UpdateBusinessStatusRequest(BaseModel):
    status: str


class AddNoteRequest(BaseModel):
    note: str
