from sqlalchemy import Column, String, UUID, JSON, ForeignKey, Enum as SQLEnum
from .base import Base, TimestampMixin
import uuid
from enum import Enum

class DocumentType(str, Enum):
    PURCHASE_AGREEMENT = "purchase_agreement"
    LISTING_AGREEMENT = "listing_agreement"
    DISCLOSURE = "disclosure"
    AMENDMENT = "amendment"
    INSPECTION = "inspection"
    OTHER = "other"

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    transaction_id = Column(UUID, ForeignKey("transactions.id"))
    title = Column(String, nullable=False)
    type = Column(SQLEnum(DocumentType))
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    storage_path = Column(String)  # Path in cloud storage
    docusign_id = Column(String)  # DocuSign envelope ID
    signers = Column(JSON, default=[])  # List of required signers
    metadata = Column(JSON, default={})
