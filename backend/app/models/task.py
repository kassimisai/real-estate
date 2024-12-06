from sqlalchemy import Column, String, UUID, JSON, ForeignKey, DateTime
from .base import Base, TimestampMixin
import uuid

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    lead_id = Column(UUID, ForeignKey("leads.id"))
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime)
    status = Column(String)
    priority = Column(String)
    assigned_to = Column(UUID, ForeignKey("users.id"))
    metadata = Column(JSON, default={})
