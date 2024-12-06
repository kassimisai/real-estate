from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID
from ..models.transaction import TransactionStatus

class TransactionBase(BaseModel):
    property_address: str
    price: str
    closing_date: datetime
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    lead_id: UUID

class TransactionUpdate(BaseModel):
    property_address: Optional[str] = None
    price: Optional[str] = None
    closing_date: Optional[datetime] = None
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: UUID
    user_id: UUID
    lead_id: UUID
    status: TransactionStatus
    contract_date: datetime
    important_dates: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
