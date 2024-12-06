from sqlalchemy import Column, String, UUID, JSON, ForeignKey, DateTime
from .base import Base, TimestampMixin
import uuid

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    status = Column(String)
    source = Column(String)
    last_contacted = Column(DateTime)
    notes = Column(String)
    metadata = Column(JSON, default={})
