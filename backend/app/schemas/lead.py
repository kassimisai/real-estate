from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "new"
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LeadResponse(LeadBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    last_contacted: Optional[datetime] = None

    class Config:
        from_attributes = True
