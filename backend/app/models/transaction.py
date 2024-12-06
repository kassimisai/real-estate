from sqlalchemy import Column, String, UUID, JSON, ForeignKey, DateTime, Enum as SQLEnum
from .base import Base, TimestampMixin
import uuid
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    UNDER_CONTRACT = "under_contract"
    CLOSING = "closing"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    lead_id = Column(UUID, ForeignKey("leads.id"))
    property_address = Column(String)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    price = Column(String)
    closing_date = Column(DateTime)
    contract_date = Column(DateTime)
    important_dates = Column(JSON, default={})  # For storing deadlines
    notes = Column(String)
    metadata = Column(JSON, default={})
