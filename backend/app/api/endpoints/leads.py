from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.auth import get_current_user
from ...models.lead import Lead
from ...schemas.lead import LeadCreate, LeadUpdate, LeadResponse

router = APIRouter()

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_lead = Lead(**lead.dict(), user_id=current_user.id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    leads = db.query(Lead).filter(Lead.user_id == current_user.id).offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    for field, value in lead_update.dict(exclude_unset=True).items():
        setattr(db_lead, field, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead
